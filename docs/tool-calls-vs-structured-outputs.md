# Tool-Call vs. Structured-Output Rates

Each `models/{name}.json` file carries **two separate rankings** for the same model:

1. **Top-level (`metric: "invalid_tool_call_rate"`)** — for requests that use function/tool
   calling (`tools`).
2. **`structured_outputs` (`metric: "structured_output_error_rate"`)** — for requests that ask
   for a structured output (`response_format`). Can be `null` when structured outputs are not
   measured.

> **Never mix the two metrics.** A provider with near-zero tool-call errors can have a high
> structured-output error rate, and vice versa. Always check the block that matches the
> request type, including its own `status`, `as_of`, `valid_until`, and `recommendation`.

## Key field comparison

| Concept | Tool calls (top-level) | Structured outputs (`doc["structured_outputs"]`) |
| --- | --- | --- |
| Error rate (fraction `0..1`) | `providers[].invalid_tool_call_rate` | `providers[].structured_output_error_rate` |
| 95% Wilson CI | `providers[].invalid_tool_call_rate_ci95` | `providers[].structured_output_error_rate_ci95` |
| Sample size & failures | `sample_size`, `failures` | `sample_size`, `failures` |
| Daily traffic | `tool_calls_per_day` | `structured_outputs_per_day` |
| Ignore bar | `thresholds.ignore_at_or_above` (`0.03`, 3%) | `thresholds.ignore_at_or_above` (`0.03`, 3%) |
| Status & expiry | `status`, `status_reason`, `as_of`, `valid_until` | Own `status`, `status_reason`, `as_of`, `valid_until` |
| Routing recommendation | `recommendation` (`order`, `ignore`) | Own `recommendation` (`order`, `ignore`) |
| Non-dominated tradeoffs | `choices` (up to 4) | Not present — compute from joined `providers` |
| Price, throughput, uptime, data policy | On each top-level `providers[]` item | Join top-level `providers[]` by `id` |

## How to interpret `role`, `confidence`, `others`, and `free`

- **The 3% ignore bar (`thresholds.ignore_at_or_above`):** Providers breaking 3% or more are
  placed in `ignore`; the three most reliable providers under 3% are placed in `order`.
- **`role` (`recommended`, `ignored`, `neutral`):**
  - `recommended`: all of the provider's `slugs` are in `recommendation.order`.
  - `ignored`: skipped by `recommendation.ignore` (either directly or by prefix match).
  - `neutral`: neither in `order` nor `ignore`. Note that a provider at or above 3% stays
    `neutral` when ignoring its slug would also skip a reliable variant under 3% (for example,
    ignoring `baseten` would also skip `baseten/fast`). Because it is not in `order`,
    OpenRouter reaches it only after every provider in `order` fails.
- **`confidence` (`high`, `low`, `none`):**
  - `high`: every recommended provider's 95% Wilson interval lies strictly below 3%, and every
    ignored provider's 95% interval lies at or above 3%.
  - `low`: at least one recommended or ignored provider's 95% interval straddles 3%. Still
    actionable when `status == "ok"`, but report `confidence: low` and sample sizes clearly.
  - `none`: `status` is not `ok`.
- **Missing numbers:** Treat `null` (such as `uptime: null` or `tokens_per_second: null`) as
  **unknown**, never as zero.
- **Percentage-point differences:** Compare error rates in percentage points (for example,
  `0.40%` vs `2.10%` is `+1.70 percentage points`, not "slightly worse").

## Python example: Joining `structured_outputs` with price, throughput, and policy

Because `structured_outputs.providers` omits price, throughput, uptime, and data-policy fields
to avoid duplication, join them from top-level `providers` (and `others`) by `id`:

```python
from __future__ import annotations


def summarize_structured_output_providers(doc: dict) -> list[dict]:
    """Combine structured-output reliability with price, throughput, uptime, and data policy."""
    so = doc.get("structured_outputs")
    if not so:
        return []

    meta_by_id = {
        p["id"]: p
        for p in doc.get("providers", []) + doc.get("others", [])
    }
    rows = []
    for sp in so["providers"]:
        meta = meta_by_id.get(sp["id"], {})
        rows.append(
            {
                "id": sp["id"],
                "name": sp["name"],
                "variant": sp["variant"],
                "slugs": sp["slugs"],
                "rank": sp["rank"],
                "role": sp["role"],
                "error_rate_pct": round(sp["structured_output_error_rate"] * 100, 2),
                "ci95_pct": [round(x * 100, 2) for x in sp["structured_output_error_rate_ci95"]],
                "sample_size": sp["sample_size"],
                "input_price_per_million": meta.get("input_price_per_million"),
                "output_price_per_million": meta.get("output_price_per_million"),
                "tokens_per_second": meta.get("tokens_per_second"),
                "uptime": meta.get("uptime"),
                "retains_prompts": meta.get("retains_prompts"),
                "trains_on_prompts": meta.get("trains_on_prompts"),
            }
        )
    return rows
```

## Handling `:free` variants

Free endpoints (`author/model:free`) live in `doc["free"]` and `doc["structured_outputs"]["free"]`.
They are a separate pool reached only by setting `"model": entry["openrouter_id"]`:

```python
def inspect_free_variant(doc: dict) -> list[dict]:
    """Inspect free-tier endpoints without putting them into provider.order/ignore."""
    return [
        {
            "openrouter_id": p["openrouter_id"],
            "provider": p["name"],
            "invalid_tool_call_rate_pct": round(p["invalid_tool_call_rate"] * 100, 2),
            "sample_size": p["sample_size"],
            "retains_prompts": p["retains_prompts"],
            "trains_on_prompts": p["trains_on_prompts"],
        }
        for p in doc.get("free", [])
    ]
```
