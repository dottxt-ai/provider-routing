# Overview and Coverage

The [dottxt Tool-call Index](https://providers.dottxt.ai) publishes daily reliability, price,
throughput, uptime, and data-policy measurements for **open-weight models served through
OpenRouter**.

> **Live evidence rule:** Rankings change daily as providers deploy fixes or regress. Never
> recommend providers from cached docs or memory. Always fetch live data from
> `https://providers.dottxt.ai/m/{openrouter_id}.json` (or `m/{openrouter_id}.md`, or check
> `https://providers.dottxt.ai/llms.txt` for coverage), verify `status == "ok"` and
> `valid_until`, and cite the file's `as_of` observation date.

## What is measured

Each model file covers a rolling **7-day window** of OpenRouter's published hourly error rates:

- **Tool-call error rate (`invalid_tool_call_rate`)**: of requests that finished with tool
  calls, the share with at least one invalid tool call (invalid JSON, an unknown function, or
  arguments that do not match the tool's schema).
- **Structured-output error rate (`structured_outputs.structured_output_error_rate`)**: of
  requests asking for a structured output (`response_format`), the share whose answer
  OpenRouter counts as failed.

Both metrics are measured **per model and provider deployment**, never globally for a model or
a provider across all models. A provider reliable on one model can break tool calls on another.

## Provider units, variants, and regions

In the index, a **provider** is an OpenRouter provider together with its quantization, service
tier, and other labels (`baseten/fp8`, `baseten/fast`, `mistral/zdr`):

- **Variants are measured and routed separately.** Different quantizations or tiers of the same
  company often have very different error rates.
- **Regions are pooled.** Endpoints in different regions (for example `fireworks` and
  `fireworks/us`) are assumed to be the same deployment and are aggregated together. Do not use
  this index to prefer one region over another.
- **`slugs` vs. `id`:** `slugs` is the minimal list of OpenRouter routing tags that reach the
  provider's endpoints (`["baseten/fp8"]`, or two tags when no single slug covers all regions).
  `id` is `slugs` joined by `" + "`. Always put elements of `slugs` — never `id` — into
  OpenRouter's `provider.order` and `provider.ignore`.

## Traffic floor, `:free` pools, and excluded providers

- **Ranked `providers` vs. `others`:** Providers with at least
  `thresholds.min_tool_calls_per_day_to_recommend` (currently 1,000 calls/day) appear in
  `providers` and are ranked. Lower-traffic providers appear in `others`: they are not ranked
  or put in `order`, but an `others` provider at or above the 3% bar can appear in `ignore` so
  it cannot contaminate a prefix-matched entry in `order`.
- **Free variant (`:free`):** Listed separately in `free` (and `structured_outputs.free`).
  Requests reach free endpoints via `openrouter_id` (for example `author/model:free`), never
  via `provider` settings. Never place a `free` provider in `provider.order` or
  `provider.ignore`, and always inspect `retains_prompts` and `trains_on_prompts` before
  suggesting one.
- **`:batch` variants** are not measured.
- **Excluded providers:** Providers whose own documentation does not document tool calling are
  excluded from `providers`, `others`, and `recommendation.ignore` (see `llms.txt` for the
  current excluded list). Because `ignore` does not name them, add `"allow_fallbacks": false`
  when you want OpenRouter strictly restricted to `provider.order`.

## Live feed endpoints

| Endpoint | Purpose | When to fetch |
| --- | --- | --- |
| `https://providers.dottxt.ai/m/{openrouter_id}.json` | Direct full JSON measurements and routing for one model | Primary endpoint for programmatic single-model routing or debugging |
| `https://providers.dottxt.ai/m/{openrouter_id}.md` | Direct answer-first Markdown (recommendation, `provider` JSON, `as_of`/`valid_until`, provider table) | Fast agent-friendly reading for one model (also served by `m/{openrouter_id}/` with `Accept: text/markdown`) |
| `https://providers.dottxt.ai/m/{openrouter_id}/` | Canonical HTML model page | Human review or `Accept: text/markdown` content negotiation |
| `https://providers.dottxt.ai/llms.txt` | Complete index of every measured model and provider | Checking coverage or finding an unknown OpenRouter model ID |
| `https://providers.dottxt.ai/providers/{slug}.json` | One provider's rates across all models it serves | Auditing one provider across models (use the model file for routing) |
| `https://providers.dottxt.ai/schema.json` | JSON Schema (2020-12) contract | Programmatic validation |
| `https://providers.dottxt.ai/data.json` | All models in one large JSON file | Bulk offline analysis only — do not fetch for a single model |

`m/{openrouter_id}.json`, `m/{openrouter_id}.md`, and `m/{openrouter_id}/` are served directly
at the lowercased OpenRouter model ID (not redirects). Non-canonical variations — uppercase
paths, dated permaslugs, unambiguous org-less names, or `:free`/`:nitro` suffixes — redirect
to the canonical `/m/{openrouter_id}` URL. The legacy `models/{name}.json` path also remains
available with identical JSON.

## Update cadence and expiry

`providers.dottxt.ai` rebuilds daily. Every model JSON carries:

- `as_of`: end of the 7-day measurement window (ISO 8601 UTC).
- `generated_at`: timestamp when the file was built (ISO 8601 UTC).
- `valid_until`: 48 hours after `as_of`. If current UTC time is past `valid_until`, treat the
  file as expired and do not emit a routing recommendation.
