"""Tests for sqlmigrate_check.watch."""
from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sqlmigrate_check.watch import (
    WatchSession,
    _changed,
    _snapshot,
)


# ---------------------------------------------------------------------------
# _snapshot helpers
# ---------------------------------------------------------------------------


def test_snapshot_existing_file(tmp_path: Path) -> None:
    f = tmp_path / "migration.sql"
    f.write_text("SELECT 1;")
    snap = _snapshot([f])
    assert f in snap
    assert isinstance(snap[f], float)


def test_snapshot_missing_file_skipped(tmp_path: Path) -> None:
    ghost = tmp_path / "ghost.sql"
    snap = _snapshot([ghost])
    assert ghost not in snap


# ---------------------------------------------------------------------------
# _changed helpers
# ---------------------------------------------------------------------------


def test_changed_detects_mtime_update(tmp_path: Path) -> None:
    f = tmp_path / "m.sql"
    f.write_text("A")
    old = _snapshot([f])
    # Bump mtime manually
    new = {f: old[f] + 1.0}
    assert f in _changed(old, new)


def test_changed_detects_new_file(tmp_path: Path) -> None:
    f = tmp_path / "new.sql"
    old: dict[Path, float] = {}
    f.write_text("B")
    new = _snapshot([f])
    assert f in _changed(old, new)


def test_changed_detects_deleted_file(tmp_path: Path) -> None:
    f = tmp_path / "del.sql"
    f.write_text("C")
    old = _snapshot([f])
    new: dict[Path, float] = {}
    assert f in _changed(old, new)


def test_changed_no_difference(tmp_path: Path) -> None:
    f = tmp_path / "same.sql"
    f.write_text("D")
    snap = _snapshot([f])
    assert _changed(snap, snap.copy()) == []


# ---------------------------------------------------------------------------
# WatchSession
# ---------------------------------------------------------------------------


def test_watch_session_calls_callback_on_change(tmp_path: Path) -> None:
    f = tmp_path / "watch.sql"
    f.write_text("SELECT 1;")

    callback = MagicMock()

    session = WatchSession(paths=[f], callback=callback, interval=0.0)

    original_snapshot = _snapshot([f])

    def fake_sleep(_: float) -> None:
        # Simulate a file modification on first iteration
        f.write_text("SELECT 2;")
        f.touch()  # ensure mtime advances

    with patch("sqlmigrate_check.watch.time.sleep", side_effect=fake_sleep):
        session.start(max_iterations=1)

    callback.assert_called_once()


def test_watch_session_stop_exits_loop(tmp_path: Path) -> None:
    callback = MagicMock()
    session = WatchSession(paths=[], callback=callback, interval=0.0)

    with patch("sqlmigrate_check.watch.time.sleep"):
        session.start(max_iterations=3)

    # No files -> no changes -> callback never called
    callback.assert_not_called()
