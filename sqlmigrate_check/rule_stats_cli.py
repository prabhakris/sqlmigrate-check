"""CLI helpers for emitting rule statistics."""
from __future__ import annotations

import argparse
from typing import Dict

from sqlmigrate_check.rule_stats import RuleStat, compute_rule_stats
from sqlmigrate_check.rule_stats_formatter import format_stats_json, format_stats_text
from sqlmigrate_check.pipeline import ScanSummary


def add_stats_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach --stats and --stats-format flags to an existing parser."""
    parser.add_argument(
        "--stats",
        action="store_true",
        default=False,
        help="Print per-rule hit statistics after scanning.",
    )
    parser.add_argument(
        "--stats-format",
        choices=["text", "json"],
        default="text",
        help="Output format for rule statistics (default: text).",
    )


def emit_rule_stats(args: argparse.Namespace, summary: ScanSummary) -> None:
    """Compute and print rule statistics if --stats flag is set."""
    if not getattr(args, "stats", False):
        return
    stats: Dict[str, RuleStat] = compute_rule_stats(summary)
    fmt = getattr(args, "stats_format", "text")
    if fmt == "json":
        print(format_stats_json(stats))
    else:
        print(format_stats_text(stats))
