# dottxt Provider Routing (Cursor Plugin)

Official Cursor plugin for the [dottxt Tool-call Index](https://providers.dottxt.ai).

On open-weight models served through OpenRouter, inference providers break tool calls and
structured outputs at dramatically different rates. This plugin bundles the `choose-provider`
Agent Skill and an apply-intelligently Cursor rule (`alwaysApply: false`) so Cursor fetches
live per-provider reliability, price, throughput, uptime, and data-policy evidence from
`https://providers.dottxt.ai` whenever you choose, update, or debug OpenRouter provider routing
— without embedding static rankings that go stale.

## Included components

- **Skill:** `choose-provider` (`skills/choose-provider/SKILL.md`) — full live lookup,
  validation, debugging, and constraint-preserving OpenRouter routing workflow.
- **Rule:** `dottxt-provider-routing.mdc` (`rules/dottxt-provider-routing.mdc`,
  `alwaysApply: false`) — concise standing guidance that triggers only on OpenRouter provider
  routing, invalid tool-call debugging, or structured-output failures (never on unrelated local
  JSON parsing or schema bugs).
- **Zero local scripts, zero hooks, zero MCP servers, and zero API keys required.** All lookups
  are read-only HTTPS GET requests to public endpoints on `https://providers.dottxt.ai`.

## How it works

1. Fetches live per-model evidence from
   `https://providers.dottxt.ai/m/{openrouter_id}.json?via=skill` (or `.md?via=skill`), falling
   back to `https://providers.dottxt.ai/llms.txt?via=skill` to check coverage or resolve an
   unknown model ID.
2. Checks `status == "ok"`, confirms current UTC time is before `valid_until`, rejects
   contradictory `order`/`ignore` overlaps, and cites the `as_of` observation date, sample size,
   and confidence.
3. Uses `invalid_tool_call_rate` for tool calling and `structured_outputs`
   (`structured_output_error_rate`) for `response_format` workloads.
4. Preserves existing OpenRouter routing and privacy constraints (`zdr`, `data_collection`,
   `only`, `allow_fallbacks`, `require_parameters`, `quantizations`, `max_price`,
   `preferred_min_throughput`, `preferred_max_latency`), flagging conflicts explicitly instead
   of weakening them.

## Installation

Install from the Cursor Marketplace once listed, or install the same skill directly via the
Agent Skills CLI:

```sh
npx skills add https://providers.dottxt.ai --skill choose-provider
```

Or copy [`rules/dottxt-provider-routing.mdc`](rules/dottxt-provider-routing.mdc) into your
project's `.cursor/rules/` directory.

## Links

- Live index: https://providers.dottxt.ai
- Discovery catalog: https://providers.dottxt.ai/llms.txt
- Source repository and documentation: https://github.com/dottxt-ai/provider-routing

## License

MIT — see [LICENSE](LICENSE).
