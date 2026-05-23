"""CLI helpers for the --watch / watch sub-command."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Sequence

from sqlmigrate_check.watch import WatchSession


def add_watch_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach ``--watch`` and ``--watch-interval`` arguments to *parser*."""
    parser.add_argument(
        "--watch",
        action="store_true",
        default=False,
        help="Re-run the scan whenever a monitored file changes.",
    )
    parser.add_argument(
        "--watch-interval",
        type=float,
        default=1.0,
        metavar="SECONDS",
        help="Polling interval used with --watch (default: 1.0 s).",
    )


def build_watch_session(
    paths: Sequence[Path],
    callback: Callable[[list[Path]], None],
    interval: float = 1.0,
) -> WatchSession:
    """Convenience factory so callers don't import :mod:`watch` directly."""
    return WatchSession(paths=paths, callback=callback, interval=interval)


def watch_callback_factory(
    rescan: Callable[[], None],
) -> Callable[[list[Path]], None]:
    """Return a callback that prints changed files then calls *rescan*."""

    def _cb(changed: list[Path]) -> None:
        names = ", ".join(str(p) for p in changed)
        print(f"[watch] change detected: {names}")
        rescan()

    return _cb
