"""Tests for sqlmigrate_check.snapshot_store."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from sqlmigrate_check.snapshot_store import (
    append_snapshot,
    latest_snapshot,
    load_snapshots,
    save_snapshots,
)
from sqlmigrate_check.trend import TrendSnapshot


def _snap(dangers: int = 0, warnings: int = 1, ts: str = "2024-01-01T00:00:00") -> TrendSnapshot:
    return TrendSnapshot(timestamp=ts, total_dangers=dangers, total_warnings=warnings, total_files=1)


def test_load_snapshots_missing_file_returns_empty(tmp_path: Path) -> None:
    result = load_snapshots(tmp_path / "nonexistent.json")
    assert result == []


def test_load_snapshots_invalid_json_returns_empty(tmp_path: Path) -> None:
    p = tmp_path / "store.json"
    p.write_text("not-json", encoding="utf-8")
    assert load_snapshots(p) == []


def test_load_snapshots_non_list_json_returns_empty(tmp_path: Path) -> None:
    p = tmp_path / "store.json"
    p.write_text(json.dumps({"key": "value"}), encoding="utf-8")
    assert load_snapshots(p) == []


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    p = tmp_path / "store.json"
    snaps = [_snap(0, 1, "2024-01-01T00:00:00"), _snap(1, 0, "2024-01-02T00:00:00")]
    save_snapshots(snaps, path=p)
    loaded = load_snapshots(p)
    assert len(loaded) == 2
    assert loaded[0].total_warnings == 1
    assert loaded[1].total_dangers == 1


def test_save_snapshots_trims_to_max(tmp_path: Path) -> None:
    p = tmp_path / "store.json"
    snaps = [_snap(ts=f"2024-01-{i:02d}T00:00:00") for i in range(1, 11)]
    save_snapshots(snaps, path=p, max_snapshots=5)
    loaded = load_snapshots(p)
    assert len(loaded) == 5
    assert loaded[0].timestamp == "2024-01-06T00:00:00"


def test_save_snapshots_max_zero_stores_nothing(tmp_path: Path) -> None:
    """Saving with max_snapshots=0 should result in an empty store."""
    p = tmp_path / "store.json"
    snaps = [_snap(ts="2024-01-01T00:00:00"), _snap(ts="2024-01-02T00:00:00")]
    save_snapshots(snaps, path=p, max_snapshots=0)
    loaded = load_snapshots(p)
    assert loaded == []


def test_append_snapshot_creates_store(tmp_path: Path) -> None:
    p = tmp_path / "store.json"
    result = append_snapshot(_snap(), path=p)
    assert len(result) == 1
    assert p.exists()


def test_append_snapshot_accumulates(tmp_path: Path) -> None:
    p = tmp_path / "store.json"
    append_snapshot(_snap(ts="2024-01-01T00:00:00"), path=p)
    result = append_snapshot(_snap(ts="2024-01-02T00:00:00"), path=p)
    assert len(result) == 2


def test_latest_snapshot_returns_none_when_empty(tmp_path: Path) -> None:
    assert latest_snapshot(tmp_path / "missing.json") is None


def test_latest_snapshot_returns_last_entry(tmp_path: Path) -> None:
    p = tmp_path / "store.json"
    append_snapshot(_snap(ts="2024-01-01T00:00:00"), path=p)
    append_snapshot(_snap(ts="2024-01-02T00:00:00"), path=p)
    snap = latest_snapshot(p)
    assert snap is not None
    assert snap.timestamp == "2024-01-02T00:00:00"
