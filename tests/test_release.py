from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "scripts/release.py"

spec = importlib.util.spec_from_file_location("release", SCRIPT)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseScriptTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        for relative, _kind, _key in release.VERSION_FILES:
            target = self.tmp / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PLUGIN_ROOT / relative, target)
        self.version = release.primary_version(PLUGIN_ROOT)
        self.tag = f"v{self.version}"
        (self.tmp / "CHANGELOG.md").write_text(
            "# Changelog\n\n"
            "## 9.9.9 — 2099-01-01\n\n- Later.\n\n"
            f"## {self.version} — 2026-01-01\n\n- First line.\n- Second line.\n\n"
            "## 0.0.1 — 2025-01-01\n\n- Earlier.\n",
            encoding="utf-8",
        )

    def test_repository_versions_agree_with_changelog(self) -> None:
        self.assertEqual([], release.check(PLUGIN_ROOT, self.tag))

    def test_cli_check_passes_for_current_version(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "check", "--tag", self.tag],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, proc.returncode, proc.stderr)

    def test_cli_version_prints_primary_version(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "version"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(self.version, proc.stdout.strip())

    def test_agreement_passes_in_copy(self) -> None:
        self.assertEqual([], release.check(self.tmp, self.tag))

    def test_mismatched_version_file_fails(self) -> None:
        manifest = self.tmp / ".codex-plugin/plugin.json"
        manifest.write_text(
            manifest.read_text().replace(
                f'"version": "{self.version}"', '"version": "9.9.9"', 1
            )
        )
        problems = release.check(self.tmp, self.tag)
        self.assertEqual(1, len(problems), problems)
        self.assertIn(".codex-plugin/plugin.json", problems[0])
        with contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(1, release.main(["check", "--tag", self.tag], self.tmp))
        self.assertIn("9.9.9", errors.getvalue())

    def test_mismatched_test_pin_fails(self) -> None:
        pin = self.tmp / "tests/test_plugin_bundle.py"
        pin.write_text(pin.read_text().replace(f'"{self.version}"', '"9.9.9"', 1))
        problems = release.check(self.tmp, self.tag)
        self.assertEqual(1, len(problems), problems)
        self.assertIn("tests/test_plugin_bundle.py", problems[0])

    def test_missing_changelog_section_fails(self) -> None:
        problems = release.check(self.tmp, "v1.2.3")
        self.assertTrue(any("CHANGELOG.md" in item for item in problems), problems)
        (self.tmp / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
        problems = release.check(self.tmp, self.tag)
        self.assertEqual(1, len(problems), problems)
        self.assertIn("CHANGELOG.md", problems[0])

    def test_malformed_tag_fails(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(
                1, release.main(["check", "--tag", self.version], self.tmp)
            )
        self.assertIn("vX.Y.Z", errors.getvalue())

    def test_notes_return_exact_section_body(self) -> None:
        self.assertEqual(
            "- First line.\n- Second line.\n",
            release.changelog_section(self.tmp, self.version),
        )
        self.assertEqual("- Earlier.\n", release.changelog_section(self.tmp, "0.0.1"))
        self.assertEqual("- Later.\n", release.changelog_section(self.tmp, "9.9.9"))

if __name__ == "__main__":
    unittest.main()
