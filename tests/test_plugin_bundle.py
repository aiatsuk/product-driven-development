from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills/product-driven-development"
MIRRORED_ASSETS = (
    Path("SKILL.md"),
    Path("agents/openai.yaml"),
    Path("references/artifacts.md"),
    Path("references/session-evidence.md"),
    Path("scripts/session_evidence.py"),
)


class ProductDrivenDevelopmentBundleTest(unittest.TestCase):
    def test_plugin_is_self_contained(self) -> None:
        required = [SKILL_ROOT / relative for relative in MIRRORED_ASSETS]
        self.assertEqual([], [str(path) for path in required if not path.is_file()])

    def test_manifest_versions_agree(self) -> None:
        claude_manifest = json.loads(
            (PLUGIN_ROOT / ".claude-plugin/plugin.json").read_text()
        )
        marketplace = json.loads(
            (PLUGIN_ROOT / ".claude-plugin/marketplace.json").read_text()
        )
        codex_manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text()
        )
        marketplace_entry = marketplace["plugins"][0]

        self.assertEqual("0.5.0", claude_manifest["version"])
        self.assertEqual(claude_manifest["version"], marketplace_entry["version"])
        self.assertEqual(
            claude_manifest["version"],
            codex_manifest["version"].split("+", 1)[0],
        )

    def test_manifest_points_at_bundled_skills(self) -> None:
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text()
        )
        self.assertEqual("./skills/", manifest["skills"])

    def test_plugin_starter_prompts_invoke_the_bundled_skill(self) -> None:
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text()
        )
        prompts = manifest["interface"]["defaultPrompt"]
        self.assertGreater(len(prompts), 0)
        self.assertTrue(
            all("$product-driven-development" in prompt for prompt in prompts)
        )

    def test_no_lifecycle_hooks_are_shipped(self) -> None:
        forbidden = [
            PLUGIN_ROOT / "hooks.json",
            PLUGIN_ROOT / "hooks",
            PLUGIN_ROOT / "hooks/hooks.json",
            PLUGIN_ROOT / "hooks/product_hook.py",
        ]
        self.assertEqual([], [str(path) for path in forbidden if path.exists()])

    def test_no_native_command_is_claimed(self) -> None:
        commands = PLUGIN_ROOT / "commands"
        self.assertEqual([], list(commands.glob("*.md")))
        skill = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertIn("$product-driven-development", skill)
        self.assertIn("do not claim that the plugin registers", skill)

    def test_only_on_demand_helper_is_bundled(self) -> None:
        scripts = sorted(
            path.name for path in (SKILL_ROOT / "scripts").glob("*.py")
        )
        self.assertEqual(["session_evidence.py"], scripts)

        forbidden_names = {"daemon.py", "server.py", "runtime.py"}
        database_suffixes = {".db", ".sqlite", ".sqlite3"}
        files = [path for path in PLUGIN_ROOT.rglob("*") if path.is_file()]
        self.assertEqual(
            [],
            [str(path) for path in files if path.name in forbidden_names],
        )
        self.assertEqual(
            [],
            [str(path) for path in files if path.suffix in database_suffixes],
        )

    def test_bundled_helper_has_a_safe_cli_failure_contract(self) -> None:
        helper = SKILL_ROOT / "scripts/session_evidence.py"
        proc = subprocess.run(
            [sys.executable, "-B", str(helper)],
            cwd=PLUGIN_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(2, proc.returncode, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual("invalid_request", payload["code"])
        self.assertEqual("not_read", payload["source_state"])

    def test_canonical_and_bundled_assets_are_byte_identical_in_source_tree(
        self,
    ) -> None:
        canonical = (
            PLUGIN_ROOT.parents[1] / "skills/product-driven-development"
        )
        if not canonical.is_dir():
            self.skipTest("canonical standalone skill is unavailable")

        mismatches = [
            str(relative)
            for relative in MIRRORED_ASSETS
            if (canonical / relative).read_bytes()
            != (SKILL_ROOT / relative).read_bytes()
        ]
        self.assertEqual([], mismatches)


if __name__ == "__main__":
    unittest.main()
