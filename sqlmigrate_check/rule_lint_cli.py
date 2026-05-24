"""CLI integration for the rule lint feature."""
from __future__ import annotations

import argparse
from typing import List

from sqlmigrate_check.rule_lint import lint_files
from sqlmigrate_check.rule_lint_formatter import (
    format_lint_github,
    format_lint_json,
    format_lint_text,
)


def add_lint_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--lint",
        action="store_true",
        default=False,
        help="Run SQL style lint checks on migration files.",
    )
    parser.add_argument(
        "--lint-format",
        choices=["text", "json", "github"],
        default="text",
        help="Output format for lint results (default: text).",
    )
    parser.add_argument(
        "--lint-fail-on-violations",
        action="store_true",
        default=False,
        help="Exit with non-zero code when lint violations are found.",
    )


def run_lint(
    paths: List[str],
    fmt: str = "text",
    fail_on_violations: bool = False,
) -> int:
    """Read files, run lint, print results. Returns exit code."""
    file_contents: dict = {}
    for p in paths:
        try:
            with open(p, encoding="utf-8") as fh:
                file_contents[p] = fh.read()
        except OSError as exc:
            print(f"[lint] Could not read {p}: {exc}")

    report = lint_files(file_contents)

    if fmt == "json":
        print(format_lint_json(report))
    elif fmt == "github":
        print(format_lint_github(report), end="")
    else:
        print(format_lint_text(report), end="")

    if fail_on_violations and report.total_violations > 0:
        return 1
    return 0
