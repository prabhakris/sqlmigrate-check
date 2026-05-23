"""CLI helpers to add rule-filter arguments and build filter kwargs."""
from __future__ import annotations

import argparse
from typing import Any, Dict, List, Optional

from sqlmigrate_check.detector import Severity


def add_filter_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach rule-filter flags to *parser*."""
    parser.add_argument(
        "--min-severity",
        choices=["warning", "danger"],
        default=None,
        help="Only report issues at or above this severity level.",
    )
    parser.add_argument(
        "--include-rules",
        metavar="RULE_ID",
        nargs="+",
        default=None,
        help="Whitelist: only report issues for these rule IDs.",
    )
    parser.add_argument(
        "--exclude-rules",
        metavar="RULE_ID",
        nargs="+",
        default=None,
        help="Blacklist: skip issues for these rule IDs.",
    )
    parser.add_argument(
        "--filepath-pattern",
        metavar="PATTERN",
        default=None,
        help="Only report issues for files matching this fnmatch pattern.",
    )


def filter_kwargs_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    """Convert parsed CLI args into kwargs suitable for *apply_rule_filter*."""
    kwargs: Dict[str, Any] = {}

    if getattr(args, "min_severity", None):
        kwargs["min_severity"] = (
            Severity.DANGER if args.min_severity == "danger" else Severity.WARNING
        )

    include: Optional[List[str]] = getattr(args, "include_rules", None)
    if include:
        kwargs["include_rules"] = [r.upper() for r in include]

    exclude: Optional[List[str]] = getattr(args, "exclude_rules", None)
    if exclude:
        kwargs["exclude_rules"] = [r.upper() for r in exclude]

    pattern: Optional[str] = getattr(args, "filepath_pattern", None)
    if pattern:
        kwargs["filepath_pattern"] = pattern

    return kwargs
