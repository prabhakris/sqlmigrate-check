"""Command-line interface for sqlmigrate-check."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlmigrate_check.detector import detect
from sqlmigrate_check.formatter import OutputFormat, format_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sqlmigrate-check",
        description="Detect unsafe SQL migrations before deployment.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="SQL migration file(s) to check.",
    )
    parser.add_argument(
        "--format",
        choices=[f.value for f in OutputFormat],
        default=OutputFormat.TEXT.value,
        dest="fmt",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Exit 0 even when dangerous migrations are found.",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    fmt = OutputFormat(args.fmt)

    exit_code = 0

    for filepath in args.files:
        path = Path(filepath)
        if not path.exists():
            print(f"Error: file not found: {filepath}", file=sys.stderr)
            exit_code = 2
            continue

        sql = path.read_text(encoding="utf-8")
        result = detect(sql)
        output = format_result(result, fmt=fmt, filename=filepath)

        if output:
            print(output)

        if result.has_danger and not args.warn_only:
            exit_code = 1

    return exit_code


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
