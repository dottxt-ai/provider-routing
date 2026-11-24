# Debugging OpenRouter Tool-Call and Structured-Output Failures

Use this guide when an OpenRouter request fails with:

- **Invalid tool calls**: malformed JSON arguments, unknown function names, or arguments that
  violate your tool schema.
- **Broken structured outputs**: responses failing `response_format` JSON Schema validation.
- **Intermittent reliability regressions**: tool calls that work on one request and fail on the
  next because OpenRouter routed the two requests to different providers or quantizations.

> **Scope check:** This workflow applies only to OpenRouter API / inference-provider failures.
> Do **not** blame provider routing for unrelated local JSON parsing bugs, typos in local
> application code, or invalid tool schemas in your own codebase.

## Diagnostic workflow

When debugging an OpenRouter failure, give a direct diagnosis and targeted fix rather than a
generic four-option comparison menu:

1. **Identify the model and (if available) the provider that served the failing response.**
   OpenRouter includes the `provider` name on response objects (and in OpenRouter Activity logs).
2. **Fetch live data from `providers.dottxt.ai`:**
   - Fetch `https://providers.dottxt.ai/m/{openrouter_id}.json` directly (or
     `https://providers.dottxt.ai/m/{openrouter_id}.md` for answer-first Markdown). Check
     `https://providers.dottxt.ai/llms.txt` if you need to confirm coverage or look up an
     unknown OpenRouter model ID.
   - Check `status == "ok"` and `now_utc < valid_until` on the right block:
     - Top-level block for tool calls (`tools`).
     - `doc["structured_outputs"]` for structured outputs (`response_format`).
3. **Compare the failing provider against the model's reliable providers:**
   - Look up the provider (and its quantization/tier variant) in `providers` or `others`.
   - Report its measured error rate (`invalid_tool_call_rate` or
     `structured_output_error_rate`), 95% confidence interval, `sample_size`, `confidence`, and
     the file's **`as_of` observation date**.
   - Compare in **percentage points** against the top recommended provider.
4. **Decide whether provider routing is the cause:**
   - If the provider's error rate is elevated (especially at or above the 3% `ignore_at_or_above`
     bar, or dramatically higher than the best provider on the same model), provider routing is
     a likely cause: recommend pinning `recommendation.order` and ignoring `recommendation.ignore`
     (plus `"allow_fallbacks": false` if strict isolation is needed), while preserving existing
     constraints (`zdr`, `data_collection`, `only`, `max_price`, etc.).
   - If the serving provider already has a very low error rate with high sample size (or the
     error reproduces identically across reliable providers), tell the user clearly that the
     root cause is likely the prompt, tool schema, or model capability rather than provider
     routing.

## Python diagnostic helper

```python
from __future__ import annotations

from datetime import UTC, datetime


def diagnose_provider_failure(
    doc: dict,
    *,
    failing_provider_slug: str | None = None,
    structured_outputs: bool = False,
    now: datetime | None = None,
) -> dict:
    """Diagnose whether an OpenRouter failure aligns with elevated provider error rates."""
    now = now or datetime.now(UTC)
    view = doc.get("structured_outputs") if structured_outputs else doc
    rate_key = "structured_output_error_rate" if structured_outputs else "invalid_tool_call_rate"

    if view is None:
        return {"actionable": False, "diagnosis": "Structured outputs are not measured for this model."}

    valid_until = datetime.fromisoformat(view["valid_until"].replace("Z", "+00:00"))
    if now >= valid_until:
        return {
            "actionable": False,
            "as_of": view["as_of"],
            "diagnosis": f"Live data expired at {view['valid_until']}; refetch before acting.",
        }

    if view["status"] != "ok":
        return {
            "actionable": False,
            "as_of": view["as_of"],
            "diagnosis": f"No actionable routing ({view['status']}): {view['status_reason']}.",
        }

    providers = view["providers"]
    best = providers[0]
    bar = view["thresholds"]["ignore_at_or_above"]

    match = None
    if failing_provider_slug:
        every = providers + view.get("others", [])
        match = next(
            (
                p for p in every
                if failing_provider_slug == p["id"]
                or failing_provider_slug in p["slugs"]
                or any(ep["tag"] == failing_provider_slug for ep in p.get("endpoints", []))
            ),
            None,
        )

    result = {
        "actionable": True,
        "model": doc["model"]["id"],
        "metric": rate_key,
        "as_of": view["as_of"],
        "valid_until": view["valid_until"],
        "confidence": view["confidence"],
        "best_provider": {
            "id": best["id"],
            "rate_pct": round(best[rate_key] * 100, 2),
            "sample_size": best["sample_size"],
        },
        "recommended_provider_config": view["recommendation"],
    }

    if match:
        diff_pp = (match[rate_key] - best[rate_key]) * 100
        result["failing_provider"] = {
            "id": match["id"],
            "role": match["role"],
            "rate_pct": round(match[rate_key] * 100, 2),
            "sample_size": match["sample_size"],
            "delta_vs_best_pp": round(diff_pp, 2),
            "at_or_above_ignore_bar": match[rate_key] >= bar,
        }
    return result
```
