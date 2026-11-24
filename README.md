# dottxt Provider Routing (Tool-call Index)

Portable Agent Skill, standing agent rules, and stable live-lookup documentation for the
[dottxt Tool-call Index](https://providers.dottxt.ai).

On open-weight models served through OpenRouter, inference providers break tool calls and
structured outputs at dramatically different rates. This repository gives coding agents and
developers stable instructions and runnable code examples for fetching **live** reliability,
price, throughput, uptime, and data-policy evidence from `https://providers.dottxt.ai` —
without ever caching daily rankings that go stale.

> **Important:** Do not treat cached documentation or memorized provider lists as current
> routing advice. Always fetch `https://providers.dottxt.ai/llms.txt` and the target model's
> live `models/{name}.json` file, verify `status == "ok"` and `valid_until`, and cite the
> `as_of` observation date.

## Install the `choose-provider` Agent Skill

Install from the canonical domain (recommended):

```sh
npx skills add https://providers.dottxt.ai --skill choose-provider
```

Or install directly from this repository (same generated `SKILL.md`):

```sh
npx skills add dottxt-ai/provider-routing --skill choose-provider
```

## Standing agent rules

Copy the rule file for your coding agent into your project (all variants are generated from the
same source and never embed changing rankings):

| Agent | File in this repo | Where to copy it |
| --- | --- | --- |
| **Cursor** | [`rules/cursor/dottxt-provider-routing.mdc`](rules/cursor/dottxt-provider-routing.mdc) | `.cursor/rules/dottxt-provider-routing.mdc` |
| **Codex / OpenCode** | [`rules/agents-md/dottxt-provider-routing.md`](rules/agents-md/dottxt-provider-routing.md) | Append to `AGENTS.md` |
| **Cline** | [`rules/cline/dottxt-provider-routing.md`](rules/cline/dottxt-provider-routing.md) | `.clinerules/dottxt-provider-routing.md` |
| **Kilo Code** | [`rules/kilo/dottxt-provider-routing.md`](rules/kilo/dottxt-provider-routing.md) | `.kilocode/rules/dottxt-provider-routing.md` |

## Documentation (stable live-lookup guides)

These guides are indexed by Context7 and contain runnable Python, TypeScript, and `curl`/`jq`
examples with zero hardcoded daily rankings:

- [**Overview & coverage**](docs/overview.md): what `providers.dottxt.ai` measures, deployment
  units (`provider/variant`), regions, `:free` pools, excluded providers, and update cadence.
- [**Live model lookup & validation**](docs/live-lookup.md): resolving a model via `llms.txt`
  to `models/{name}.json`, validating `status`, `valid_until`, invariants, and citing `as_of`.
- [**Tool calls vs. structured outputs**](docs/tool-calls-vs-structured-outputs.md):
  interpreting `invalid_tool_call_rate` vs. `structured_outputs.structured_output_error_rate`,
  Wilson 95% confidence intervals, the 3% ignore bar, `neutral` slugs, `others`, and `free`.
- [**OpenRouter integration & constraint preservation**](docs/openrouter-integration.md):
  merging `provider.order` and `provider.ignore` across direct HTTP, OpenAI Python SDK, OpenAI
  TypeScript SDK, and regional endpoints while preserving `zdr`, `data_collection`, `only`,
  `max_price`, and other constraints.
- [**Debugging OpenRouter tool-call failures**](docs/debugging-tool-calls.md): diagnosing
  invalid JSON, unknown function names, schema mismatches, and broken structured outputs on
  OpenRouter without false positives on unrelated local JSON bugs.

## Live endpoints on `providers.dottxt.ai`

- `https://providers.dottxt.ai/llms.txt` — discovery map with links to every model's JSON file
- `https://providers.dottxt.ai/models/{name}.json` — single-model measurements and routing
- `https://providers.dottxt.ai/providers/{slug}.json` — single-provider measurements across models
- `https://providers.dottxt.ai/schema.json` — JSON Schema (2020-12) for all data files
- `https://providers.dottxt.ai/.well-known/agent-skills/choose-provider/SKILL.md` — domain-hosted skill

## License

MIT — see [LICENSE](LICENSE).
