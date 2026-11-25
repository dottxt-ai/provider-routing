---
name: openrouter-provider-routing
description: "Choose, debug, and update OpenRouter provider routing when configuring open-weight models or diagnosing OpenRouter invalid tool calls, broken tool arguments, or structured-output failures using live reliability, price, throughput, uptime, and data-policy evidence from providers.dottxt.ai. Do not trigger for unrelated local JSON parsing or schema bugs."
---

# Choose an OpenRouter provider

Fetch `https://providers.dottxt.ai/m/{openrouter_id}.json?via=skill` directly when you know the model's OpenRouter id (or `m/{openrouter_id}.md?via=skill` for answer-first Markdown); fetch `https://providers.dottxt.ai/llms.txt?via=skill` first when you need to check coverage or find an unknown model id. Use those live files rather than cached measurements or the large `data.json` file, verify `status` and `valid_until` before recommending a routing, and always cite the file's `as_of` observation date.

## Workflow

You are helping the user choose, debug, or update an OpenRouter provider-routing
configuration for a specific model. Use this workflow only for OpenRouter
provider selection, routing updates, or OpenRouter tool-call and
structured-output failures — not for unrelated local JSON parsing or schema bugs.

Use the live dottxt Tool-call Index data at `https://providers.dottxt.ai` as the
source of truth for provider reliability, price, throughput, uptime, and data
policy. Always cite the model file's `as_of` observation date when reporting
numbers, diagnosing a provider, or proposing a routing.

Gather what you need first:

- The model's live file: fetch `https://providers.dottxt.ai/m/{openrouter_id}.json`
  directly (or `m/{openrouter_id}.md` for answer-first Markdown), or check
  `llms.txt` when verifying coverage or resolving an unknown id. Do not fetch
  `data.json` for a single model.
- The user's current `provider` configuration, failing provider (if debugging),
  and any stated constraints or priorities.

Before making recommendations:

- Verify that the data covers the requested model.
- Check `as_of`, `valid_until`, `confidence`, and `sample_size`.
- If `status` is not `ok`, or the current time is past `valid_until`, say so,
  give `status_reason`, and do not recommend a configuration.
- Reject data that lists a provider in both `order` and `ignore`. A slug in
  `ignore` also skips the providers it matches: `baseten` skips `baseten/fp8`.
- A provider is an OpenRouter provider with its quantization, tier and other
  labels (`baseten/fp8`, `baseten/fast`), measured and routed apart. Regions are
  measured together, so don't recommend one region over another from this data.
  A tag with a region (`baseten/fp8/us`) belongs to the provider whose
  `endpoints` list it. Name a provider in config by its `slugs`, and name its
  variant when presenting it.
- Recommendations are for OpenRouter's global routing. On in-region routing
  (`eu.openrouter.ai`, `us.openrouter.ai`), name the regional tag from the
  provider's `endpoints` (`amazon-bedrock/eu-west-1`): base slugs don't pin
  regional endpoints there.
- A provider at or above the threshold is left out of `ignore` when ignoring its
  slug would also skip one under it (`role` is `neutral`): it is never in
  `order`, so OpenRouter reaches it only past `order`.
- A model's `free` lists its free variant's providers (`:free`), reached by
  `openrouter_id`, never by `provider` settings: never put a free provider in
  `order` or `ignore`. If the user asks about `:free` or only `free` providers
  exist, report their measured rates and data policy (`retains_prompts`,
  `trains_on_prompts`).
- Treat missing measurements as unknown, never zero. Exclude stale,
  contradictory, or insufficiently supported data. Never invent measurements or
  infer facts not present in the data, and say clearly when evidence is
  insufficient.

In the data, `invalid_tool_call_rate` (a fraction) is OpenRouter's published
share of tool-call-finishing requests with at least one invalid tool call
(invalid JSON, an unknown function, or arguments that don't match the tool's
schema), with 95% interval `invalid_tool_call_rate_ci95` and `sample_size`.
`confidence` is `low` when a recommended or ignored provider's interval
straddles `thresholds.ignore_at_or_above`.

Each model's file also carries `structured_outputs`: the same providers measured
on OpenRouter's published `structured_output_error_rate` (with
`structured_output_error_rate_ci95`, `sample_size`, and
`structured_outputs_per_day`), with its own `status`, `as_of`, `valid_until`,
`recommendation`, and `others` under the same rules; null when not measured. Use
`structured_outputs` (not tool-call rates) for requests asking for a structured
output (`response_format`): a provider reliable on tool calls can break
structured outputs, and vice versa. It has no `choices`: take price, throughput,
and uptime from top-level `providers`, by `id`.

Match the response to the user's task:

1. **Debugging an OpenRouter tool-call or structured-output failure**: Do not
   stall in a four-option comparison dialogue. Inspect the relevant metric
   (tool calls or `structured_outputs`), report whether the failing provider
   has an elevated error rate versus the model's reliable providers (citing
   `as_of`, rate, confidence, and sample size), explain whether provider routing
   is the likely cause, and give the targeted `provider` fix (or ask to apply
   it if editing code wasn't yet authorized).
2. **Already constrained or explicitly authorized implementation**: If the user
   already stated hard constraints (maximum price, minimum uptime or throughput,
   maximum failure rate, zero data retention, or no training on prompts) or
   explicitly asked you to apply the recommended or a chosen routing, do not
   stall in an unnecessary comparison dialogue. Filter out providers violating
   constraints (including `retains_prompts` or `trains_on_prompts` when privacy
   settings exclude them), explain any tradeoffs or conflicts, cite `as_of`, and
   go straight to producing the `provider` configuration and proposed diff.
3. **Open-ended provider selection (no constraints or choice stated)**:
   - Do not invent constraints or silently pick one "best" configuration.
   - Present up to four non-dominated choices conversationally (not as JSON),
     preferring: (1) Most reliable, (2) Lowest cost, (3) Highest throughput,
     (4) Balanced tradeoff if there is a clear knee point, plus "Keep current"
     if current config is known and changing gives only marginal gain. Omit
     strictly dominated or effectively identical categories.
   - For each choice, show: label, primary provider/order, failure rate (use
     percentage-point differences, never vague words), input/output price,
     throughput, uptime, confidence, sample size, data policy warnings if a
     provider retains or trains on prompts, and a one-sentence tradeoff vs the
     most reliable option. Cite `as_of` and ask which option they prefer.

When producing or applying a `provider` configuration:

- Note that OpenRouter tries `order` first and falls back to any provider not in
  `ignore`, and that adding `"allow_fallbacks": false` restricts requests to
  `order` (and keeps traffic off excluded providers).
- Do not modify files, open a pull request, or deploy unless authorized.
- Update the OpenRouter configuration as follows:
  1. Find the code building the OpenRouter request. Provider routing belongs in
     the request body's `provider` object for both Responses and Chat
     Completions; it does not replace `model`, `messages`, `input`, `tools`, or
     `response_format`.
  2. Start from the existing `provider` object. Replace its `order` and `ignore`
     with the chosen routing. Remove `sort`, because an explicit `order`
     determines provider priority.
  3. Preserve policy and capability constraints unless the user explicitly asks
     to change them: `allow_fallbacks`, `require_parameters`, `data_collection`,
     `zdr`, `enforce_distillable_text`, `quantizations`, `max_price`,
     `preferred_min_throughput`, and `preferred_max_latency`.
  4. Treat `only` and user-authored exclusions as hard constraints. If they
     conflict with the new `order` or `ignore`, explain the conflict and ask
     which constraint to change. Never silently weaken privacy, residency,
     price, or capability requirements.
  5. Show the proposed diff before editing unless already explicitly authorized.
     Make the smallest local change and run the project's relevant tests.

Direct OpenRouter request or native SDK:

```json
{
  "model": "author/model",
  "messages": [],
  "provider": {
    "order": ["provider-a", "provider-b"],
    "ignore": ["provider-c"],
    "allow_fallbacks": true,
    "data_collection": "deny"
  }
}
```

With an OpenAI-compatible Python client pointed at OpenRouter, pass
`extra_body={"provider": provider_config}` (merging the `provider` key if
`extra_body` already exists). For other frameworks, find their documented
equivalent of OpenRouter's request-level `provider` field; do not guess. Use the
[OpenRouter provider routing documentation](https://openrouter.ai/docs/guides/routing/provider-selection)
when the SDK shape or fields differ.
