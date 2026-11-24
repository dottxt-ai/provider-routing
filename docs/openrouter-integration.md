# Applying OpenRouter Routing While Preserving Constraints

OpenRouter provider routing lives in the request body's `provider` object for both Chat
Completions and Responses requests. It does **not** replace `model`, `messages`, `input`,
`tools`, or `response_format`.

## Merge rules

When updating an existing OpenRouter `provider` configuration:

1. **Start from the existing `provider` object.**
2. **Replace `order` and `ignore`** with the validated recommendation (or chosen tradeoff's
   `recommendation`).
3. **Remove `sort`**, because an explicit `order` defines provider priority.
4. **Preserve policy and capability constraints** unless the user explicitly asks to change
   them:
   - `allow_fallbacks`
   - `require_parameters`
   - `data_collection`
   - `zdr`
   - `enforce_distillable_text`
   - `quantizations`
   - `max_price`
   - `preferred_min_throughput`
   - `preferred_max_latency`
5. **Treat `only` and user-authored exclusions as hard constraints.** If `only` excludes
   providers in the new `order`, or if a required privacy policy (`zdr: true`,
   `data_collection: "deny"`) excludes providers with `retains_prompts: true` or
   `trains_on_prompts: true`, surface the conflict and ask which constraint to change. Never
   silently weaken privacy, residency, price, or capability rules.
6. **Fallback behavior:** OpenRouter tries `order` first and then falls back to any provider
   not in `ignore` (including providers excluded from the index). Set
   `"allow_fallbacks": false` to strictly limit requests to `order`.

---

## Safe constraint-preserving merge helper (Python)

```python
from __future__ import annotations

PRESERVED_KEYS = (
    "allow_fallbacks",
    "require_parameters",
    "data_collection",
    "zdr",
    "enforce_distillable_text",
    "quantizations",
    "max_price",
    "preferred_min_throughput",
    "preferred_max_latency",
)


def merge_provider_config(
    existing: dict | None,
    recommendation: dict,
    *,
    providers_meta: list[dict] | None = None,
) -> tuple[dict, list[str]]:
    """Merge a validated dottxt recommendation into an existing OpenRouter provider object.

    Returns (merged_provider_object, conflicts). When conflicts is non-empty, explain them to
    the user before applying changes.
    """
    existing = dict(existing or {})
    conflicts: list[str] = []

    order = list(recommendation["order"])
    ignore = list(recommendation["ignore"])

    # Respect user-authored `only` allowlist as a hard constraint.
    if "only" in existing:
        allowed = set(existing["only"])
        blocked = [slug for slug in order if slug not in allowed and slug.split("/")[0] not in allowed]
        if blocked:
            conflicts.append(
                f"Existing 'only' allowlist {existing['only']} conflicts with recommended order "
                f"entries: {blocked}."
            )

    # Check data-policy compatibility when ZDR or data_collection='deny' is configured.
    strict_privacy = bool(existing.get("zdr")) or existing.get("data_collection") == "deny"
    if strict_privacy and providers_meta:
        by_slug = {s: p for p in providers_meta for s in p.get("slugs", [])}
        for slug in order:
            meta = by_slug.get(slug)
            if meta and (meta.get("retains_prompts") is True or meta.get("trains_on_prompts") is True):
                conflicts.append(
                    f"Provider '{slug}' retains or trains on prompts, conflicting with "
                    "existing ZDR / data_collection='deny' policy."
                )

    merged: dict = {"order": order, "ignore": ignore}
    for key in PRESERVED_KEYS:
        if key in existing:
            merged[key] = existing[key]
    if "only" in existing:
        merged["only"] = existing["only"]
    # Note: `sort` is intentionally dropped because `order` sets explicit priority.
    return merged, conflicts
```

---

## SDK request shapes

### Direct OpenRouter HTTP request

```json
{
  "model": "deepseek/deepseek-v3.2",
  "messages": [
    { "role": "user", "content": "Look up the current weather in Paris." }
  ],
  "tools": [],
  "provider": {
    "order": ["provider-a", "provider-b", "provider-c"],
    "ignore": ["provider-d"],
    "allow_fallbacks": false,
    "data_collection": "deny"
  }
}
```

### OpenAI Python SDK pointed at OpenRouter

Pass `provider` inside `extra_body` and merge into any existing `extra_body` dictionary instead
of overwriting other keys:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

# `provider_config` comes from merging the live validated recommendation from providers.dottxt.ai.
existing_extra_body = {"transforms": ["middle-out"]}
extra_body = {**existing_extra_body, "provider": provider_config}

response = client.chat.completions.create(
    model="deepseek/deepseek-v3.2",
    messages=[{"role": "user", "content": "Call the search tool."}],
    tools=tools,
    extra_body=extra_body,
)
```

### OpenAI TypeScript SDK pointed at OpenRouter

```ts
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: process.env.OPENROUTER_API_KEY,
});

// Merge validated live provider_config into the request body.
const response = await client.chat.completions.create({
  model: "deepseek/deepseek-v3.2",
  messages: [{ role: "user", content: "Call the search tool." }],
  tools,
  // OpenRouter extension field
  provider: providerConfig,
} as OpenAI.ChatCompletionCreateParamsNonStreaming & {
  provider: Record<string, unknown>;
});
```

---

## In-region routing (`eu.openrouter.ai`, `us.openrouter.ai`)

Recommendations in `models/{name}.json` target OpenRouter's **global** routing. On OpenRouter's
in-region endpoints (`eu.openrouter.ai`, `us.openrouter.ai`), a provider's base slug does not
pin its regional endpoints — use the explicit regional tag from `provider["endpoints"][i]["tag"]`
(for example `amazon-bedrock/eu-west-1`):

```python
def regional_tags_for_provider(provider_entry: dict, region_hint: str) -> list[str]:
    """Extract regional endpoint tags (e.g. 'eu-') for in-region OpenRouter routing."""
    return [
        ep["tag"]
        for ep in provider_entry.get("endpoints", [])
        if region_hint in ep["tag"]
    ]
```

Consult the current
[OpenRouter provider routing documentation](https://openrouter.ai/docs/guides/routing/provider-selection)
if your framework wraps request-level OpenRouter options differently.
