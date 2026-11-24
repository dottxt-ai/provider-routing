# Live Model Lookup and Expiry Validation

Always resolve and fetch live evidence from `https://providers.dottxt.ai` at request time.
Never use cached rankings, and never fetch the large `data.json` file when you only need one
model.

## Step-by-step protocol

1. **Resolve the model file URL** from `https://providers.dottxt.ai/llms.txt`. Match the exact
   OpenRouter model ID in backticks (for example `` `deepseek/deepseek-v4.1-flash` ``) under
   `## Models` to get its canonical JSON link (follow the link in `llms.txt` rather than
   guessing a path, so URL or slug changes never break lookup).
2. **Fetch that model JSON URL** directly.
3. **Validate status, expiry, and invariants** before recommending a routing:
   - `status == "ok"` (otherwise report `status_reason` and do **not** recommend a routing).
   - Current UTC time `< valid_until` (ISO 8601 UTC).
   - `recommendation` is non-null with `order` and `ignore`.
   - No slug in `recommendation.ignore` matches any slug in `recommendation.order` (accounting
     for prefix matching, e.g. `baseten` matches `baseten/fp8`).
4. **Cite the observation date (`as_of`)** alongside `confidence`, `sample_size`, and measured
   error rates in your response.

### Non-`ok` statuses

| `status` | Meaning | Required behavior |
| --- | --- | --- |
| `ok` | Actionable recommendation (when before `valid_until`) | Safe to recommend, citing `as_of` and `confidence` |
| `insufficient_data` | Fewer than 3 observed days in the window | Report `status_reason`; do not recommend |
| `single_provider` | Fewer than two providers at the traffic floor | Report `status_reason`; do not recommend |
| `stale` | Build already marked the window past `valid_until` | Report `status_reason`; do not recommend |
| `no_reliable_provider` | Every ranked provider breaks 3% or more | Report `status_reason`; do not recommend |

---

## Python example (stdlib only)

```python
from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from urllib.request import Request, urlopen

BASE_URL = "https://providers.dottxt.ai"


def fetch_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "dottxt-provider-routing-example/1.0"})
    with urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8")


def resolve_model_url(openrouter_model_id: str, llms_txt: str) -> str | None:
    """Find the live model JSON URL for an OpenRouter model id under ``## Models`` in llms.txt.

    Follows whatever canonical JSON URL ``llms.txt`` publishes (e.g. ``/models/{name}.json`` or
    ``/m/{org}/{model}.json``) rather than assuming a fixed path layout.
    """
    in_models = False
    line_re = re.compile(r"^- \[[^\]]+\]\((https?://[^)]+\.json)\):\s*`([^`]+)`")
    for line in llms_txt.splitlines():
        if line.startswith("## "):
            in_models = line.strip() == "## Models"
            continue
        if not in_models:
            continue
        if match := line_re.match(line):
            url, model_id = match.groups()
            if model_id == openrouter_model_id:
                return url
    return None


def slug_covers(ignore_slug: str, target_tag: str, target_is_tier: bool) -> bool:
    """OpenRouter slug matching: base slug matches variants and tiers; tier endpoints are
    matched only by their own slug or the provider's base slug."""
    if target_tag == ignore_slug:
        return True
    if not target_tag.startswith(ignore_slug + "/"):
        return False
    return (not target_is_tier) or ("/" not in ignore_slug)


def validate_recommendation(
    doc: dict,
    *,
    structured_outputs: bool = False,
    now: datetime | None = None,
) -> tuple[bool, str, dict | None]:
    """Validate status, expiry (valid_until), and order/ignore invariants.

    Returns (actionable, reason_or_summary, recommendation_or_none).
    """
    now = now or datetime.now(UTC)
    view = doc.get("structured_outputs") if structured_outputs else doc
    if view is None:
        return False, "Structured outputs are not measured for this model.", None

    valid_until = datetime.fromisoformat(view["valid_until"].replace("Z", "+00:00"))
    if now >= valid_until:
        return (
            False,
            f"Data expired at {view['valid_until']} (as_of {view['as_of']}); "
            "refusing to recommend stale routing.",
            None,
        )

    if view["status"] != "ok":
        reason = view.get("status_reason") or view["status"]
        return False, f"Status is {view['status']}: {reason} (as_of {view['as_of']}).", None

    rec = view.get("recommendation")
    if not rec:
        return False, "Missing recommendation despite status 'ok'.", None

    # Reject contradictory data where an ignore slug covers any endpoint of an order slug.
    every = view.get("providers", []) + view.get("others", [])
    tier_by_tag = {e["tag"]: e["tier"] for p in every for e in p.get("endpoints", [])}
    for ignored in rec["ignore"]:
        for ordered in rec["order"]:
            if slug_covers(ignored, ordered, tier_by_tag.get(ordered, False)):
                return (
                    False,
                    f"Contradictory routing data: ignore '{ignored}' skips order '{ordered}'.",
                    None,
                )

    summary = (
        f"Valid recommendation as of {view['as_of']} "
        f"(valid until {view['valid_until']}, confidence: {view['confidence']})."
    )
    return True, summary, rec


def lookup_live_routing(openrouter_model_id: str, *, structured_outputs: bool = False) -> dict:
    llms_txt = fetch_text(f"{BASE_URL}/llms.txt")
    model_url = resolve_model_url(openrouter_model_id, llms_txt)
    if not model_url:
        raise LookupError(f"{openrouter_model_id} is not listed in {BASE_URL}/llms.txt")

    doc = json.loads(fetch_text(model_url))
    ok, message, rec = validate_recommendation(doc, structured_outputs=structured_outputs)
    return {
        "model_id": doc["model"]["id"],
        "as_of": (doc["structured_outputs"] if structured_outputs else doc)["as_of"],
        "actionable": ok,
        "message": message,
        "provider": rec,
    }
```

---

## TypeScript / Node 20+ example (native `fetch`)

```ts
const BASE_URL = "https://providers.dottxt.ai";

interface Endpoint {
  tag: string;
  tier: boolean;
}

interface ProviderEntry {
  id: string;
  slugs: string[];
  endpoints: Endpoint[];
}

interface RoutingBlock {
  as_of: string;
  valid_until: string;
  status: string;
  status_reason: string | null;
  confidence: "high" | "low" | "none";
  recommendation: { order: string[]; ignore: string[] } | null;
  providers: ProviderEntry[];
  others: ProviderEntry[];
}

export function resolveModelUrl(openrouterModelId: string, llmsTxt: string): string | null {
  let inModels = false;
  const lineRe = /^- \[[^\]]+\]\((https?:\/\/[^)]+\.json)\):\s*`([^`]+)`/;
  for (const line of llmsTxt.split(/\r?\n/)) {
    if (line.startsWith("## ")) {
      inModels = line.trim() === "## Models";
      continue;
    }
    if (!inModels) continue;
    const match = line.match(lineRe);
    if (match && match[2] === openrouterModelId) {
      return match[1];
    }
  }
  return null;
}

function slugCovers(ignoreSlug: string, targetTag: string, targetIsTier: boolean): boolean {
  if (targetTag === ignoreSlug) return true;
  if (!targetTag.startsWith(`${ignoreSlug}/`)) return false;
  return !targetIsTier || !ignoreSlug.includes("/");
}

export function validateRoutingBlock(block: RoutingBlock | null, now = new Date()) {
  if (!block) {
    return { actionable: false, reason: "Metric not measured for this model.", provider: null };
  }
  if (now >= new Date(block.valid_until)) {
    return {
      actionable: false,
      reason: `Expired at ${block.valid_until} (as_of ${block.as_of}).`,
      provider: null,
    };
  }
  if (block.status !== "ok" || !block.recommendation) {
    return {
      actionable: false,
      reason: `Status ${block.status}: ${block.status_reason ?? "not actionable"} (as_of ${block.as_of}).`,
      provider: null,
    };
  }

  const tierByTag = new Map<string, boolean>();
  for (const p of [...block.providers, ...block.others]) {
    for (const ep of p.endpoints) tierByTag.set(ep.tag, ep.tier);
  }
  for (const ignored of block.recommendation.ignore) {
    for (const ordered of block.recommendation.order) {
      if (slugCovers(ignored, ordered, tierByTag.get(ordered) ?? false)) {
        return {
          actionable: false,
          reason: `Contradictory data: ignore '${ignored}' covers order '${ordered}'.`,
          provider: null,
        };
      }
    }
  }

  return {
    actionable: true,
    asOf: block.as_of,
    validUntil: block.valid_until,
    confidence: block.confidence,
    provider: block.recommendation,
  };
}

export async function fetchLiveProviderRouting(
  openrouterModelId: string,
  { structuredOutputs = false } = {},
) {
  const llmsTxt = await (await fetch(`${BASE_URL}/llms.txt`)).text();
  const modelUrl = resolveModelUrl(openrouterModelId, llmsTxt);
  if (!modelUrl) {
    throw new Error(`${openrouterModelId} is not covered by ${BASE_URL}/llms.txt`);
  }
  const doc = await (await fetch(modelUrl)).json();
  const block: RoutingBlock | null = structuredOutputs ? doc.structured_outputs : doc;
  return validateRoutingBlock(block);
}
```

---

## Shell (`curl` + `jq`) quick check

```sh
MODEL_ID="deepseek/deepseek-v3.2"

# 1. Resolve the model's live JSON URL from llms.txt
MODEL_URL=$(curl -fsSL https://providers.dottxt.ai/llms.txt \
  | grep "\`${MODEL_ID}\`" \
  | sed -E 's/.*\((https:\/\/[^)]+\.json)\).*/\1/' \
  | head -n 1)

# 2. Fetch the model file, verify status == "ok" and valid_until > now, and print as_of + routing
curl -fsSL "$MODEL_URL" | jq '
  if .status != "ok" then
    error("Not actionable (\(.status)): \(.status_reason) [as_of \(.as_of)]")
  elif (.valid_until | fromdateiso8601) <= now then
    error("Expired at \(.valid_until) [as_of \(.as_of)]")
  else
    {as_of, valid_until, confidence, provider: .recommendation}
  end
'
```
