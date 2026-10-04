#!/usr/bin/env python3
"""Read the plugin version, check release readiness, and print release notes.

Commands:
  version                 print the version from the primary version file
  check --tag vX.Y.Z      fail unless every version file and CHANGELOG.md agree
  notes --tag vX.Y.Z      print the CHANGELOG.md section body for that version
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Version files kept in sync, mirroring tests/test_plugin_bundle.py.
# Each entry: (relative path, kind, key). The first entry is the primary file.
VERSION_FILES = (
    (".claude-plugin/plugin.json", "json", ("version",)),
    (".claude-plugin/marketplace.json", "json", ("plugins", 0, "version")),
    (".codex-plugin/plugin.json", "json", ("version",)),
    ("tests/test_plugin_bundle.py", "pin", None),
)

CHANGELOG = "CHANGELOG.md"
TAG_PATTERN = re.compile(r"^v(\d+\.\d+\.\d+)$")
PIN_PATTERN = re.compile(
    r'assertEqual\(\s*"([^"]+)",\s*claude_manifest\["version"\]\s*\)'
)
HEADING_PATTERN = re.compile(r"^## (\S+) — ", re.MULTILINE)


class ReleaseError(Exception):
    """A release precondition is not met."""


def read_version(root: Path, relative: str, kind: str, key) -> str:
    path = root / relative
    if not path.is_file():
        raise ReleaseError(f"{relative}: file is missing")
    text = path.read_text(encoding="utf-8")
    if kind == "json":
        value = json.loads(text)
        try:
            for part in key:
                value = value[part]
        except (KeyError, IndexError, TypeError):
            raise ReleaseError(f"{relative}: no version field") from None
        if not isinstance(value, str):
            raise ReleaseError(f"{relative}: version is not a string")
        # A build suffix such as 0.5.0+local does not change the release.
        return value.split("+", 1)[0]
    match = PIN_PATTERN.search(text)
    if not match:
        raise ReleaseError(f"{relative}: version pin not found")
    return match.group(1)


def primary_version(root: Path = ROOT) -> str:
    relative, kind, key = VERSION_FILES[0]
    return read_version(root, relative, kind, key)


def parse_tag(tag: str) -> str:
    match = TAG_PATTERN.match(tag)
    if not match:
        raise ReleaseError(f"tag {tag!r} is not of the form vX.Y.Z")
    return match.group(1)


def changelog_section(root: Path, version: str) -> str:
    path = root / CHANGELOG
    if not path.is_file():
        raise ReleaseError(f"{CHANGELOG}: file is missing")
    text = path.read_text(encoding="utf-8")
    headings = list(HEADING_PATTERN.finditer(text))
    for index, heading in enumerate(headings):
        if heading.group(1) != version:
            continue
        line_end = text.find("\n", heading.end())
        start = len(text) if line_end == -1 else line_end + 1
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        return text[start:end].strip("\n") + "\n"
    raise ReleaseError(f"{CHANGELOG}: no '## {version} — ' section")


def check(root: Path, tag: str) -> list[str]:
    version = parse_tag(tag)
    problems: list[str] = []
    for relative, kind, key in VERSION_FILES:
        try:
            found = read_version(root, relative, kind, key)
        except ReleaseError as error:
            problems.append(str(error))
            continue
        if found != version:
            problems.append(f"{relative}: version {found} does not match {version}")
    try:
        changelog_section(root, version)
    except ReleaseError as error:
        problems.append(str(error))
    return problems


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("version", help="print the current version")
    for name in ("check", "notes"):
        sub = commands.add_parser(name)
        sub.add_argument("--tag", required=True, help="release tag, vX.Y.Z")
    args = parser.parse_args(argv)

    try:
        if args.command == "version":
            print(primary_version(root))
            return 0
        if args.command == "check":
            problems = check(root, args.tag)
            if problems:
                print(f"release check failed for {args.tag}:", file=sys.stderr)
                for problem in problems:
                    print(f"- {problem}", file=sys.stderr)
                return 1
            print(f"release check passed for {args.tag}")
            return 0
        sys.stdout.write(changelog_section(root, parse_tag(args.tag)))
        return 0
    except ReleaseError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
