"""Validate the public provider-routing package: skill, rules, context7.json, links, and
runnable documentation code examples."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SAMPLE_LLMS = """# dottxt Tool-call Index

## Models

- [DeepSeek V4.1 Flash](https://providers.dottxt.ai/models/deepseek-v4.1-flash.json): `deepseek/deepseek-v4.1-flash`, by DeepSeek
- [Kimi K3](https://providers.dottxt.ai/m/moonshotai/kimi-k3.json): `moonshotai/kimi-k3`, by Moonshot AI
- [Gemma 3 27B](https://providers.dottxt.ai/models/gemma-3-27b-it.json): `google/gemma-3-27b-it`, by Google; no recommendation: fewer than two providers

## Providers

- [DeepSeek](https://providers.dottxt.ai/providers/deepseek.json): `deepseek`, 0.50% across 1 model
"""

SAMPLE_MODEL_DOC = {
    "methodology_version": "2.0",
    "generated_at": "2026-10-16T12:00:00Z",
    "as_of": "2026-10-15T19:00:00Z",
    "valid_until": "2026-10-17T19:00:00Z",
    "model": {
        "id": "deepseek/deepseek-v4.1-flash",
        "permaslug": "deepseek/deepseek-v4.1-flash-20260910",
        "name": "DeepSeek V4.1 Flash",
        "maker": "DeepSeek",
        "file": "models/deepseek-v4.1-flash.json",
    },
    "metric": "invalid_tool_call_rate",
    "status": "ok",
    "status_reason": None,
    "confidence": "high",
    "recommendation": {
        "order": ["provider-a/fp8", "provider-b"],
        "ignore": ["provider-c/fp8"],
    },
    "thresholds": {
        "min_tool_calls_per_day_to_recommend": 1000,
        "median_invalid_tool_call_rate": 0.015,
        "ignore_at_or_above": 0.03,
    },
    "providers": [
        {
            "id": "provider-a/fp8",
            "slugs": ["provider-a/fp8"],
            "name": "Provider A",
            "variant": "fp8",
            "rank": 1,
            "role": "recommended",
            "makers_api": False,
            "retains_prompts": False,
            "trains_on_prompts": False,
            "sample_size": 50000,
            "failures": 50,
            "invalid_tool_call_rate": 0.001,
            "invalid_tool_call_rate_ci95": [0.0007, 0.0013],
            "tool_calls_per_day": 7000,
            "input_price_per_million": 0.2,
            "output_price_per_million": 0.6,
            "tokens_per_second": 95.0,
            "uptime": 0.998,
            "quantizations": ["fp8"],
            "endpoints": [
                {
                    "tag": "provider-a/fp8",
                    "tier": False,
                    "name": "Provider A",
                    "quantization": "fp8",
                    "sample_size": 50000,
                    "failures": 50,
                    "invalid_tool_call_rate": 0.001,
                }
            ],
        },
        {
            "id": "provider-b",
            "slugs": ["provider-b"],
            "name": "Provider B",
            "variant": None,
            "rank": 2,
            "role": "recommended",
            "makers_api": True,
            "retains_prompts": True,
            "trains_on_prompts": True,
            "sample_size": 40000,
            "failures": 200,
            "invalid_tool_call_rate": 0.005,
            "invalid_tool_call_rate_ci95": [0.0043, 0.0057],
            "tool_calls_per_day": 5700,
            "input_price_per_million": 0.15,
            "output_price_per_million": 0.45,
            "tokens_per_second": 80.0,
            "uptime": 0.995,
            "quantizations": ["fp8"],
            "endpoints": [
                {
                    "tag": "provider-b",
                    "tier": False,
                    "name": "Provider B",
                    "quantization": "fp8",
                    "sample_size": 25000,
                    "failures": 125,
                    "invalid_tool_call_rate": 0.005,
                },
                {
                    "tag": "provider-b/eu-west-1",
                    "tier": False,
                    "name": "Provider B EU",
                    "quantization": "fp8",
                    "sample_size": 15000,
                    "failures": 75,
                    "invalid_tool_call_rate": 0.005,
                },
            ],
        },
        {
            "id": "provider-c/fp8",
            "slugs": ["provider-c/fp8"],
            "name": "Provider C",
            "variant": "fp8",
            "rank": 3,
            "role": "ignored",
            "makers_api": False,
            "retains_prompts": False,
            "trains_on_prompts": False,
            "sample_size": 20000,
            "failures": 1200,
            "invalid_tool_call_rate": 0.06,
            "invalid_tool_call_rate_ci95": [0.0568, 0.0634],
            "tool_calls_per_day": 2800,
            "input_price_per_million": 0.1,
            "output_price_per_million": 0.3,
            "tokens_per_second": 110.0,
            "uptime": 0.99,
            "quantizations": ["fp8"],
            "endpoints": [
                {
                    "tag": "provider-c/fp8",
                    "tier": False,
                    "name": "Provider C",
                    "quantization": "fp8",
                    "sample_size": 20000,
                    "failures": 1200,
                    "invalid_tool_call_rate": 0.06,
                }
            ],
        },
    ],
    "others": [],
    "free": [
        {
            "id": "provider-free",
            "slugs": ["provider-free"],
            "name": "Provider Free",
            "variant": None,
            "openrouter_id": "deepseek/deepseek-v4.1-flash:free",
            "retains_prompts": True,
            "trains_on_prompts": True,
            "sample_size": 10000,
            "failures": 250,
            "invalid_tool_call_rate": 0.025,
        }
    ],
    "structured_outputs": {
        "metric": "structured_output_error_rate",
        "as_of": "2026-10-15T19:00:00Z",
        "valid_until": "2026-10-17T19:00:00Z",
        "status": "ok",
        "status_reason": None,
        "confidence": "high",
        "recommendation": {
            "order": ["provider-b"],
            "ignore": ["provider-a/fp8"],
        },
        "thresholds": {
            "min_structured_outputs_per_day_to_recommend": 1000,
            "median_structured_output_error_rate": 0.02,
            "ignore_at_or_above": 0.03,
        },
        "providers": [
            {
                "id": "provider-b",
                "slugs": ["provider-b"],
                "name": "Provider B",
                "variant": None,
                "rank": 1,
                "role": "recommended",
                "sample_size": 30000,
                "failures": 60,
                "structured_output_error_rate": 0.002,
                "structured_output_error_rate_ci95": [0.0015, 0.0026],
                "structured_outputs_per_day": 4200,
                "endpoints": [{"tag": "provider-b", "tier": False}],
            },
            {
                "id": "provider-a/fp8",
                "slugs": ["provider-a/fp8"],
                "name": "Provider A",
                "variant": "fp8",
                "rank": 2,
                "role": "ignored",
                "sample_size": 15000,
                "failures": 750,
                "structured_output_error_rate": 0.05,
                "structured_output_error_rate_ci95": [0.0466, 0.0536],
                "structured_outputs_per_day": 2100,
                "endpoints": [{"tag": "provider-a/fp8", "tier": False}],
            },
        ],
        "others": [],
        "free": [],
    },
}


def extract_fenced_blocks(path: Path, lang: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(rf"```{re.escape(lang)}\n(.*?)```", re.DOTALL)
    return pattern.findall(text)


class PackageStructureTests(unittest.TestCase):
    def test_context7_json(self) -> None:
        cfg = json.loads((ROOT / "context7.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["$schema"], "https://context7.com/schema/context7.json")
        self.assertTrue(cfg["projectTitle"])
        self.assertTrue(cfg["description"])
        self.assertTrue(cfg["folders"])
        for folder in cfg["folders"]:
            self.assertTrue((ROOT / folder).is_dir(), f"Missing Context7 folder: {folder}")
        joined_rules = "\n".join(cfg["rules"])
        self.assertIn("https://providers.dottxt.ai/llms.txt", joined_rules)
        self.assertIn("valid_until", joined_rules)
        self.assertIn("as_of", joined_rules)
        self.assertIn("structured_outputs", joined_rules)

    def test_skill_and_rules_present_and_free_of_stale_rankings(self) -> None:
        skill_path = ROOT / "skills/choose-provider/SKILL.md"
        skill_text = skill_path.read_text(encoding="utf-8")
        self.assertLess(len(skill_text), 10_000)
        self.assertTrue(skill_text.startswith("---\n"))
        _, fm, body = skill_text.split("---\n", 2)
        self.assertIn("name: choose-provider", fm)
        self.assertIn("unrelated local JSON", fm)
        self.assertIn("https://providers.dottxt.ai/llms.txt?via=skill", body)
        self.assertIn("`as_of`", body)
        self.assertIn("`valid_until`", body)

        rule_paths = [
            ROOT / "rules/cursor/dottxt-provider-routing.mdc",
            ROOT / "rules/agents-md/dottxt-provider-routing.md",
            ROOT / "rules/cline/dottxt-provider-routing.md",
            ROOT / "rules/kilo/dottxt-provider-routing.md",
        ]
        bodies = []
        for path in rule_paths:
            text = path.read_text(encoding="utf-8")
            self.assertIn("https://providers.dottxt.ai/llms.txt", text, path)
            self.assertIn("`valid_until`", text, path)
            self.assertIn("`as_of`", text, path)
            self.assertIn("unrelated local JSON", text, path)
            self.assertNotIn("Data as of", text, path)
            self.assertNotIn("## Current models", text, path)
            if path.suffix == ".mdc":
                _, r_fm, r_body = text.split("---\n", 2)
                self.assertIn("alwaysApply: false", r_fm)
                self.assertIn("description:", r_fm)
                bodies.append(r_body.strip())
            else:
                bodies.append(text.strip())
        self.assertEqual(len(set(bodies)), 1, "Standing rule bodies must agree across agents")

    def test_docs_have_no_hardcoded_rankings_and_relative_links_resolve(self) -> None:
        md_files = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
        for path in md_files:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("Data as of", text, path)
            self.assertNotIn("## Current models", text, path)
            self.assertFalse(
                re.findall(r"\]\(https://providers\.dottxt\.ai/models/[^)]+\.json\)", text),
                f"Static doc {path} should not hardcode a specific model JSON link",
            )
            for link in re.findall(r"\]\(([^)#]+)", text):
                if link.startswith(("http://", "https://", "mailto:")):
                    continue
                target = (path.parent / link).resolve()
                self.assertTrue(target.exists(), f"Broken link {link} in {path}")


class DocCodeExamplesTests(unittest.TestCase):
    def test_live_lookup_python_example(self) -> None:
        blocks = extract_fenced_blocks(ROOT / "docs/live-lookup.md", "python")
        self.assertEqual(len(blocks), 1)
        ns: dict = {}
        exec(blocks[0], ns)

        url = ns["resolve_model_url"]("deepseek/deepseek-v4.1-flash", SAMPLE_LLMS)
        self.assertEqual(url, "https://providers.dottxt.ai/models/deepseek-v4.1-flash.json")
        self.assertEqual(
            ns["resolve_model_url"]("moonshotai/kimi-k3", SAMPLE_LLMS),
            "https://providers.dottxt.ai/m/moonshotai/kimi-k3.json",
        )
        self.assertIsNone(ns["resolve_model_url"]("deepseek", SAMPLE_LLMS))
        self.assertIsNone(ns["resolve_model_url"]("missing/model", SAMPLE_LLMS))

        fresh = datetime(2026, 10, 16, 12, tzinfo=UTC)
        ok, msg, rec = ns["validate_recommendation"](SAMPLE_MODEL_DOC, now=fresh)
        self.assertTrue(ok)
        self.assertIn("2026-10-15T19:00:00Z", msg)
        self.assertEqual(rec, {"order": ["provider-a/fp8", "provider-b"], "ignore": ["provider-c/fp8"]})

        # Expired data must be refused
        expired = datetime(2026, 10, 18, 0, tzinfo=UTC)
        ok, msg, rec = ns["validate_recommendation"](SAMPLE_MODEL_DOC, now=expired)
        self.assertFalse(ok)
        self.assertIsNone(rec)
        self.assertIn("expired", msg.lower())

        # Non-ok status must be refused
        bad_status = {**SAMPLE_MODEL_DOC, "status": "no_reliable_provider", "status_reason": "all >= 3%", "recommendation": None}
        ok, msg, rec = ns["validate_recommendation"](bad_status, now=fresh)
        self.assertFalse(ok)
        self.assertIsNone(rec)
        self.assertIn("no_reliable_provider", msg)

        # Contradictory ignore covering an order slug (prefix match) must be refused
        contradictory = {
            **SAMPLE_MODEL_DOC,
            "recommendation": {"order": ["provider-a/fp8"], "ignore": ["provider-a"]},
        }
        ok, msg, rec = ns["validate_recommendation"](contradictory, now=fresh)
        self.assertFalse(ok)
        self.assertIsNone(rec)
        self.assertIn("Contradictory", msg)

        # Structured outputs branch uses its own recommendation
        ok, _, rec = ns["validate_recommendation"](
            SAMPLE_MODEL_DOC, structured_outputs=True, now=fresh
        )
        self.assertTrue(ok)
        self.assertEqual(rec, {"order": ["provider-b"], "ignore": ["provider-a/fp8"]})

    def test_live_lookup_typescript_example(self) -> None:
        blocks = extract_fenced_blocks(ROOT / "docs/live-lookup.md", "ts")
        self.assertEqual(len(blocks), 1)
        harness = blocks[0] + """
import assert from "node:assert/strict";
const llms = """ + json.dumps(SAMPLE_LLMS) + """;
const doc = """ + json.dumps(SAMPLE_MODEL_DOC) + """;
assert.equal(
  resolveModelUrl("deepseek/deepseek-v4.1-flash", llms),
  "https://providers.dottxt.ai/models/deepseek-v4.1-flash.json",
);
assert.equal(
  resolveModelUrl("moonshotai/kimi-k3", llms),
  "https://providers.dottxt.ai/m/moonshotai/kimi-k3.json",
);
assert.equal(resolveModelUrl("deepseek", llms), null);
const fresh = validateRoutingBlock(doc, new Date("2026-10-16T12:00:00Z"));
assert.equal(fresh.actionable, true);
assert.equal(fresh.asOf, "2026-10-15T19:00:00Z");
const stale = validateRoutingBlock(doc, new Date("2026-10-18T00:00:00Z"));
assert.equal(stale.actionable, false);
assert.equal(stale.provider, null);
const bad = validateRoutingBlock(
  { ...doc, recommendation: { order: ["provider-a/fp8"], ignore: ["provider-a"] } },
  new Date("2026-10-16T12:00:00Z"),
);
assert.equal(bad.actionable, false);
"""
        with tempfile.TemporaryDirectory() as tmp:
            ts_file = Path(tmp) / "check.ts"
            ts_file.write_text(harness, encoding="utf-8")
            proc = subprocess.run(
                ["node", str(ts_file)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)

    def test_structured_outputs_and_free_python_examples(self) -> None:
        blocks = extract_fenced_blocks(ROOT / "docs/tool-calls-vs-structured-outputs.md", "python")
        self.assertEqual(len(blocks), 2)
        ns: dict = {}
        for block in blocks:
            exec(block, ns)

        rows = ns["summarize_structured_output_providers"](SAMPLE_MODEL_DOC)
        self.assertEqual([r["id"] for r in rows], ["provider-b", "provider-a/fp8"])
        self.assertEqual(rows[0]["error_rate_pct"], 0.2)
        self.assertEqual(rows[0]["input_price_per_million"], 0.15)
        self.assertTrue(rows[0]["retains_prompts"])

        free_rows = ns["inspect_free_variant"](SAMPLE_MODEL_DOC)
        self.assertEqual(len(free_rows), 1)
        self.assertEqual(free_rows[0]["openrouter_id"], "deepseek/deepseek-v4.1-flash:free")

    def test_merge_and_regional_python_examples(self) -> None:
        blocks = extract_fenced_blocks(ROOT / "docs/openrouter-integration.md", "python")
        ns: dict = {}
        exec(blocks[0], ns)
        exec(blocks[-1], ns)

        existing = {
            "order": ["old-provider"],
            "ignore": [],
            "sort": "price",
            "allow_fallbacks": False,
            "data_collection": "deny",
            "zdr": True,
            "max_price": {"prompt": 0.5},
            "only": ["provider-a/fp8"],
        }
        merged, conflicts = ns["merge_provider_config"](
            existing,
            SAMPLE_MODEL_DOC["recommendation"],
            providers_meta=SAMPLE_MODEL_DOC["providers"],
        )
        self.assertNotIn("sort", merged)
        self.assertEqual(merged["order"], ["provider-a/fp8", "provider-b"])
        self.assertEqual(merged["ignore"], ["provider-c/fp8"])
        self.assertFalse(merged["allow_fallbacks"])
        self.assertEqual(merged["data_collection"], "deny")
        self.assertTrue(merged["zdr"])
        self.assertEqual(merged["max_price"], {"prompt": 0.5})
        self.assertEqual(merged["only"], ["provider-a/fp8"])
        # Both `only` conflict and ZDR conflict on provider-b should be flagged.
        self.assertEqual(len(conflicts), 2)

        tags = ns["regional_tags_for_provider"](SAMPLE_MODEL_DOC["providers"][1], "eu-")
        self.assertEqual(tags, ["provider-b/eu-west-1"])

    def test_debugging_helper_python_example(self) -> None:
        blocks = extract_fenced_blocks(ROOT / "docs/debugging-tool-calls.md", "python")
        self.assertEqual(len(blocks), 1)
        ns: dict = {}
        exec(blocks[0], ns)

        fresh = datetime(2026, 10, 16, 12, tzinfo=UTC)
        diag = ns["diagnose_provider_failure"](
            SAMPLE_MODEL_DOC,
            failing_provider_slug="provider-c/fp8",
            now=fresh,
        )
        self.assertTrue(diag["actionable"])
        self.assertEqual(diag["as_of"], "2026-10-15T19:00:00Z")
        self.assertEqual(diag["failing_provider"]["rate_pct"], 6.0)
        self.assertEqual(diag["failing_provider"]["delta_vs_best_pp"], 5.9)
        self.assertTrue(diag["failing_provider"]["at_or_above_ignore_bar"])


if __name__ == "__main__":
    unittest.main()
