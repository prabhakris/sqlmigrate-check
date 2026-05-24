"""CLI helpers for snapshot-store commands."""
from __future__ import annotations

import argparse
from pathlib import Path

from sqlmigrate_check.snapshot_store import (
    _DEFAULT_PATH,
    append_snapshot,
    latest_snapshot,
    load_snapshots,
)
from sqlmigrate_check.trend import TrendSnapshot
from sqlmigrate_check.trend_formatter import format_trend_text, format_trend_json


def add_snapshot_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach snapshot-store flags to *parser*."""
    parser.add_argument(
        "--snapshot-store",
        metavar="FILE",
        default=str(_DEFAULT_PATH),
        help="Path to the JSON snapshot store (default: %(default)s).",
    )
    parser.add_argument(
        "--save-snapshot",
        action="store_true",
        default=False,
        help="Append the current scan result to the snapshot store.",
    )
    parser.add_argument(
        "--show-trend",
        action="store_true",
        default=False,
        help="Print trend delta between the last two stored snapshots.",
    )


def maybe_save_snapshot(
    args: argparse.Namespace,
    snapshot: TrendSnapshot,
) -> None:
    """If ``--save-snapshot`` is set, persist *snapshot* to the store."""
    if getattr(args, "save_snapshot", False):
        store_path = Path(args.snapshot_store)
        append_snapshot(snapshot, path=store_path)


def maybe_show_trend(
    args: argparse.Namespace,
    fmt: str = "text",
) -> None:
    """If ``--show-trend`` is set, print a delta between the last two snapshots."""
    if not getattr(args, "show_trend", False):
        return
    store_path = Path(args.snapshot_store)
    snapshots = load_snapshots(store_path)
    if len(snapshots) < 2:
        print("[trend] Not enough snapshots to compute a delta.")
        return
    prev, curr = snapshots[-2], snapshots[-1]
    if fmt == "json":
        print(format_trend_json(prev, curr))
    else:
        print(format_trend_text(prev, curr))
