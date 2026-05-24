"""Persistent snapshot store for trend tracking across scans."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from sqlmigrate_check.trend import TrendSnapshot

_DEFAULT_PATH = Path(".sqlmigrate_snapshots.json")
_MAX_SNAPSHOTS = 50


def load_snapshots(path: Path = _DEFAULT_PATH) -> List[TrendSnapshot]:
    """Load all stored snapshots from *path*. Returns empty list if missing."""
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            return []
        return [TrendSnapshot.from_dict(item) for item in raw]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def save_snapshots(
    snapshots: List[TrendSnapshot],
    path: Path = _DEFAULT_PATH,
    max_snapshots: int = _MAX_SNAPSHOTS,
) -> None:
    """Persist *snapshots* to *path*, keeping at most *max_snapshots* entries."""
    trimmed = snapshots[-max_snapshots:]
    path.write_text(
        json.dumps([s.to_dict() for s in trimmed], indent=2),
        encoding="utf-8",
    )


def append_snapshot(
    snapshot: TrendSnapshot,
    path: Path = _DEFAULT_PATH,
    max_snapshots: int = _MAX_SNAPSHOTS,
) -> List[TrendSnapshot]:
    """Load existing snapshots, append *snapshot*, save and return the list."""
    existing = load_snapshots(path)
    existing.append(snapshot)
    save_snapshots(existing, path, max_snapshots)
    return existing


def latest_snapshot(path: Path = _DEFAULT_PATH) -> Optional[TrendSnapshot]:
    """Return the most recently stored snapshot, or *None* if the store is empty."""
    snapshots = load_snapshots(path)
    return snapshots[-1] if snapshots else None
