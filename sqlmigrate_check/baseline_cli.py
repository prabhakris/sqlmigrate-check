"""CLI helpers for baseline management (update / diff sub-commands)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from sqlmigrate_check.baseline import (
    build_baseline_from_results,
    load_baseline,
    save_baseline,
)
from sqlmigrate_check.pipeline import run_pipeline


def _collect_paths(raw: List[str]) -> List[Path]:
    return [Path(p) for p in raw]


def cmd_update_baseline(args: argparse.Namespace) -> int:
    """Scan targets and write all current issues to the baseline file.

    Returns 0 on success.
    """
    paths = _collect_paths(args.targets)
    summary = run_pipeline(paths, recursive=args.recursive)
    fingerprints = build_baseline_from_results(
        {fp: res for fp, res in summary.results.items()}
    )
    save_baseline(fingerprints, args.baseline)
    total = len(fingerprints)
    print(
        f"Baseline updated: {total} issue(s) recorded → {args.baseline}",
        file=sys.stderr,
    )
    return 0


def cmd_diff_baseline(args: argparse.Namespace) -> int:
    """Show issues that are NOT yet in the baseline.

    Returns 1 if new issues exist, 0 otherwise.
    """
    from sqlmigrate_check.baseline import filter_new_issues  # local import to avoid cycles

    paths = _collect_paths(args.targets)
    baseline = load_baseline(args.baseline)
    summary = run_pipeline(paths, recursive=args.recursive)

    new_found = False
    for filepath, result in summary.results.items():
        new_issues = filter_new_issues(filepath, result.issues, baseline)
        if new_issues:
            new_found = True
            print(f"[NEW] {filepath}")
            for issue in new_issues:
                print(f"  {issue}")

    if not new_found:
        print("No new issues compared to baseline.", file=sys.stderr)
    return 1 if new_found else 0


def build_baseline_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register 'baseline update' and 'baseline diff' sub-commands."""
    baseline_parser = subparsers.add_parser("baseline", help="Manage issue baseline")
    baseline_parser.add_argument(
        "--baseline",
        default=".sqlmigrate_baseline.json",
        metavar="FILE",
        help="Path to baseline JSON file (default: .sqlmigrate_baseline.json)",
    )
    baseline_parser.add_argument(
        "--recursive", "-r", action="store_true", help="Recurse into directories"
    )
    baseline_parser.add_argument(
        "targets", nargs="+", metavar="PATH", help="SQL files or directories to scan"
    )
    sub = baseline_parser.add_subparsers(dest="baseline_cmd", required=True)
    sub.add_parser("update", help="Record all current issues as the new baseline")
    sub.add_parser("diff", help="Show issues not yet in the baseline")

    baseline_parser.set_defaults(func=_dispatch_baseline)


def _dispatch_baseline(args: argparse.Namespace) -> int:
    if args.baseline_cmd == "update":
        return cmd_update_baseline(args)
    return cmd_diff_baseline(args)
