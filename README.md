# dottxt Provider Routing (Tool-call Index)

Portable Agent Skill, native plugin/extension manifests, standing agent rules, and stable
live-lookup documentation for the [dottxt Tool-call Index](https://providers.dottxt.ai).

On open-weight models served through OpenRouter, inference providers break tool calls and
structured outputs at dramatically different rates. This repository gives coding agents and
developers stable instructions and runnable code examples for fetching **live** reliability,
price, throughput, uptime, and data-policy evidence from `https://providers.dottxt.ai` —
without ever caching daily rankings that go stale.

> **Important:** Do not treat cached documentation or memorized provider lists as current
> routing advice. Always fetch `https://providers.dottxt.ai/m/{openrouter_id}.json` (or
> `m/{openrouter_id}.md`, or check `https://providers.dottxt.ai/llms.txt` for coverage),
> verify `status == "ok"` and `valid_until`, and cite the `as_of` observation date.

## Install the `choose-provider` Agent Skill

### Universal (`skills` CLI — Claude Code, Codex, Cursor, Antigravity, Gemini CLI, OpenCode)

Install from the canonical domain (recommended):

```sh
npx skills add https://providers.dottxt.ai --skill choose-provider
```

Or directly from this repository (same generated `SKILL.md`):

```sh
npx skills add dottxt-ai/provider-routing --skill choose-provider
```

### Native installs

- **Claude Code plugin** (`.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`):
  ```sh
  claude plugin install dottxt-provider-routing --marketplace dottxt-ai/provider-routing
  ```
  Or inside an interactive Claude Code session:
  ```text
  /plugin marketplace add dottxt-ai/provider-routing
  /plugin install dottxt-provider-routing@dottxt-provider-routing
  ```
- **Gemini CLI extension** (`gemini-extension.json`, auto-discovers `skills/choose-provider/SKILL.md`):
  ```sh
  gemini extensions install https://github.com/dottxt-ai/provider-routing
  ```
- **Pi coding agent package** (`package.json` `"pi.skills"`):
  ```sh
  pi install git:github.com/dottxt-ai/provider-routing
  ```
- **Antigravity plugin** (`plugin.json` + `skills/choose-provider/SKILL.md`): clone into
  `~/.gemini/config/plugins/dottxt-provider-routing` or install the skill with `npx skills add`.
- **Context7** (`/dottxt-ai/provider-routing`): verified library at
  `https://context7.com/dottxt-ai/provider-routing`.

## Standing agent rules

Copy the rule file for your coding agent into your project (all variants are generated from the
same source and never embed changing rankings):

| Agent | File in this repo | Where to copy it |
| --- | --- | --- |
| **Cursor** | [`rules/cursor/dottxt-provider-routing.mdc`](rules/cursor/dottxt-provider-routing.mdc) | `.cursor/rules/dottxt-provider-routing.mdc` |
| **Claude Code** | [`rules/claude/dottxt-provider-routing.md`](rules/claude/dottxt-provider-routing.md) | `.claude/rules/dottxt-provider-routing.md` (or append to `CLAUDE.md`) |
| **Codex / OpenCode / Antigravity / Pi** | [`rules/agents-md/dottxt-provider-routing.md`](rules/agents-md/dottxt-provider-routing.md) | Append to `AGENTS.md` |
| **Gemini CLI / Antigravity** | [`rules/gemini/dottxt-provider-routing.md`](rules/gemini/dottxt-provider-routing.md) | Append to `GEMINI.md` (or `.agents/rules/dottxt-provider-routing.md` in Antigravity) |
| **Cline** | [`rules/cline/dottxt-provider-routing.md`](rules/cline/dottxt-provider-routing.md) | `.clinerules/dottxt-provider-routing.md` |
| **Kilo Code** | [`rules/kilo/dottxt-provider-routing.md`](rules/kilo/dottxt-provider-routing.md) | `.kilocode/rules/dottxt-provider-routing.md` |

## Documentation (stable live-lookup guides)

These guides are indexed by Context7 and contain runnable Python, TypeScript, and `curl`/`jq`
examples with zero hardcoded daily rankings:

- [**Overview & coverage**](docs/overview.md): what `providers.dottxt.ai` measures, deployment
  units (`provider/variant`), regions, `:free` pools, excluded providers, and update cadence.
- [**Live model lookup & validation**](docs/live-lookup.md): resolving a model via `llms.txt`
  to its live JSON file, validating `status`, `valid_until`, invariants, and citing `as_of`.
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

- `https://providers.dottxt.ai/m/{openrouter_id}.json` — direct per-model JSON at the exact OpenRouter model ID (e.g. `m/deepseek/deepseek-v3.2.json`)
- `https://providers.dottxt.ai/m/{openrouter_id}.md` — direct answer-first Markdown summary (recommendation, `provider` JSON, `as_of`/`valid_until`, provider table)
- `https://providers.dottxt.ai/m/{openrouter_id}/` — canonical HTML model page (returns `m/{openrouter_id}.md` directly when sent `Accept: text/markdown`)
- `https://providers.dottxt.ai/llms.txt` — discovery map with links to every measured model and provider
- `https://providers.dottxt.ai/providers/{slug}.json` — single-provider measurements across models
- `https://providers.dottxt.ai/schema.json` — JSON Schema (2020-12) for all data files
- `https://providers.dottxt.ai/.well-known/agent-skills/choose-provider/SKILL.md` — domain-hosted skill

## License

MIT — see [LICENSE](LICENSE).
