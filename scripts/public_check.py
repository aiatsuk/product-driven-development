#!/usr/bin/env python3
"""Reject private or machine-specific material from the public bundle."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".toml", ".txt"}
CYRILLIC = re.compile(r"[\u0400-\u04ff]")
MACHINE_PATH = re.compile(
    r"(?:/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+|[A-Z]:\\Users\\[^\\\s]+)"
)
SECRET_VALUE = re.compile(
    r"(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|"
    r"-----BEGIN [A-Z ]+PRIVATE KEY-----)"
)
VENDOR_TOKENS = tuple(
    part.lower()
    for part in (
        "yan" + "dex",
        "arca" + "dia",
        "arca" + "num",
        "tan" + "ker",
        "pre" + "orders",
        "y" + "0_",
    )
)
FORBIDDEN_NAMES = {".DS_Store", ".env"}
FORBIDDEN_SUFFIXES = {".pyc", ".p12", ".jks", ".pem", ".key"}


def main() -> int:
    failures: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if ".git" in path.parts or path == Path(__file__).resolve():
            continue
        if path.is_dir():
            if path.name == "__pycache__":
                failures.append(f"generated directory: {path.relative_to(ROOT)}")
            continue
        relative = path.relative_to(ROOT)
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"unsafe file: {relative}")
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        if CYRILLIC.search(text):
            failures.append(f"Cyrillic text: {relative}")
        if any(token in lowered for token in VENDOR_TOKENS):
            failures.append(f"vendor-specific text: {relative}")
        if MACHINE_PATH.search(text):
            failures.append(f"machine-specific path: {relative}")
        if SECRET_VALUE.search(text):
            failures.append(f"secret-like value: {relative}")
    if failures:
        raise SystemExit("FAIL:\n" + "\n".join(f"- {item}" for item in failures))
    print("PASS: public bundle contains no blocked material")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
