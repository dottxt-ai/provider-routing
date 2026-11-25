# dottxt Provider Routing (Claude Code Plugin)

Official Claude Code plugin for the [dottxt Tool-call Index](https://providers.dottxt.ai).

On open-weight models served through OpenRouter, inference providers break tool calls and
structured outputs at dramatically different rates. This plugin bundles the `openrouter-provider-routing`
skill so Claude Code fetches live per-provider reliability, price, throughput, uptime, and
data-policy evidence from `https://providers.dottxt.ai` whenever you choose, update, or debug
OpenRouter provider routing — without embedding static rankings that go stale.

## What the plugin includes

- **Skill:** `openrouter-provider-routing` (`skills/openrouter-provider-routing/SKILL.md`)
- **Zero local scripts, zero hooks, zero MCP servers, and zero API keys required.** All lookups
  are read-only HTTPS GET requests to public JSON and Markdown endpoints on
  `https://providers.dottxt.ai`.

## When `openrouter-provider-routing` activates

- Selecting OpenRouter providers for an open-weight model that uses tool calling or structured
  outputs (`response_format`).
- Updating an existing OpenRouter `provider` routing object while preserving privacy (`zdr`,
  `data_collection`), residency, allowlist (`only`), quantization, throughput, latency, and
  `max_price` constraints.
- Diagnosing OpenRouter invalid tool calls (malformed JSON arguments, unknown function names,
  schema mismatches) or structured-output failures.

It is scoped to OpenRouter provider routing and does not activate for unrelated local JSON
parsing or schema bugs.

## How it works

1. Fetches live per-model evidence directly from
   `https://providers.dottxt.ai/m/{openrouter_id}.json?via=skill` (or `.md?via=skill`), falling
   back to `https://providers.dottxt.ai/llms.txt?via=skill` when checking coverage or resolving
   an unknown model ID.
2. Validates `status == "ok"`, checks that current UTC time is before `valid_until`, verifies
   that `order` and `ignore` do not contradict each other, and cites the `as_of` observation
   date, sample size, and confidence.
3. Uses `invalid_tool_call_rate` for tool-calling workloads and `structured_outputs`
   (`structured_output_error_rate`) for `response_format` workloads.
4. Preserves existing OpenRouter routing and privacy constraints, surfacing conflicts explicitly
   rather than weakening them.

## Installation

Install directly from this repository's Claude Code marketplace:

```sh
claude plugin install dottxt-provider-routing --marketplace dottxt-ai/provider-routing
```

Or inside an interactive Claude Code session:

```text
/plugin marketplace add dottxt-ai/provider-routing
/plugin install dottxt-provider-routing@dottxt-provider-routing
```

## Links

- Live index: https://providers.dottxt.ai
- Discovery catalog: https://providers.dottxt.ai/llms.txt
- Source repository and documentation: https://github.com/dottxt-ai/provider-routing

## License

MIT — see [LICENSE](LICENSE).
