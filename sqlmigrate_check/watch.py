"""File-system watcher that re-runs the scan pipeline on SQL migration changes."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Iterable, Optional

_POLL_INTERVAL = 1.0  # seconds


def _snapshot(paths: Iterable[Path]) -> dict[Path, float]:
    """Return a mapping of path -> mtime for every path that exists."""
    result: dict[Path, float] = {}
    for p in paths:
        try:
            result[p] = p.stat().st_mtime
        except FileNotFoundError:
            pass
    return result


def _changed(old: dict[Path, float], new: dict[Path, float]) -> list[Path]:
    """Return paths whose mtime changed or that are new/deleted."""
    changed: list[Path] = []
    all_keys = set(old) | set(new)
    for p in all_keys:
        if old.get(p) != new.get(p):
            changed.append(p)
    return changed


class WatchSession:
    """Poll *paths* for modifications and invoke *callback* on changes.

    Parameters
    ----------
    paths:
        Iterable of :class:`~pathlib.Path` objects to monitor.
    callback:
        Callable that receives the list of changed paths.
    interval:
        Poll interval in seconds (default 1.0).
    """

    def __init__(
        self,
        paths: Iterable[Path],
        callback: Callable[[list[Path]], None],
        interval: float = _POLL_INTERVAL,
    ) -> None:
        self._paths = list(paths)
        self._callback = callback
        self._interval = interval
        self._running = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self, max_iterations: Optional[int] = None) -> None:
        """Begin polling.  Blocks until :meth:`stop` is called or
        *max_iterations* is reached (useful for tests)."""
        self._running = True
        snapshot = _snapshot(self._paths)
        iterations = 0
        while self._running:
            time.sleep(self._interval)
            new_snapshot = _snapshot(self._paths)
            changed = _changed(snapshot, new_snapshot)
            if changed:
                self._callback(changed)
            snapshot = new_snapshot
            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                break

    def stop(self) -> None:
        """Signal the polling loop to exit."""
        self._running = False
