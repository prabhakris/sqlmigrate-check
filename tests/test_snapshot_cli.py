"""Tests for sqlmigrate_check.snapshot_cli."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from sqlmigrate_check.snapshot_cli import (
    add_snapshot_arguments,
    maybe_save_snapshot,
    maybe_show_trend,
)
from sqlmigrate_check.snapshot_store import append_snapshot, load_snapshots
from sqlmigrate_check.trend import TrendSnapshot


def _args(**kwargs) -> argparse.Namespace:
    defaults = {"snapshot_store": ".snapshots.json", "save_snapshot": False, "show_trend": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _snap(ts: str = "2024-01-01T00:00:00") -> TrendSnapshot:
    return TrendSnapshot(timestamp=ts, total_dangers=0, total_warnings=0, total_files=1)


def test_add_snapshot_arguments_registers_flags() -> None:
    parser = argparse.ArgumentParser()
    add_snapshot_arguments(parser)
    parsed = parser.parse_args([])
    assert hasattr(parsed, "snapshot_store")
    assert hasattr(parsed, "save_snapshot")
    assert hasattr(parsed, "show_trend")
    assert parsed.save_snapshot is False
    assert parsed.show_trend is False


def test_maybe_save_snapshot_does_nothing_when_flag_false(tmp_path: Path) -> None:
    p = tmp_path / "store.json"
    args = _args(snapshot_store=str(p), save_snapshot=False)
    maybe_save_snapshot(args, _snap())
    assert not p.exists()


def test_maybe_save_snapshot_persists_when_flag_true(tmp_path: Path) -> None:
    p = tmp_path / "store.json"
    args = _args(snapshot_store=str(p), save_snapshot=True)
    maybe_save_snapshot(args, _snap())
    snaps = load_snapshots(p)
    assert len(snaps) == 1


def test_maybe_show_trend_does_nothing_when_flag_false(tmp_path: Path, capsys) -> None:
    p = tmp_path / "store.json"
    args = _args(snapshot_store=str(p), show_trend=False)
    maybe_show_trend(args)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_maybe_show_trend_prints_not_enough_when_one_snapshot(tmp_path: Path, capsys) -> None:
    p = tmp_path / "store.json"
    append_snapshot(_snap(), path=p)
    args = _args(snapshot_store=str(p), show_trend=True)
    maybe_show_trend(args)
    captured = capsys.readouterr()
    assert "Not enough" in captured.out


def test_maybe_show_trend_prints_text_delta(tmp_path: Path, capsys) -> None:
    p = tmp_path / "store.json"
    append_snapshot(_snap("2024-01-01T00:00:00"), path=p)
    append_snapshot(
        TrendSnapshot(timestamp="2024-01-02T00:00:00", total_dangers=1, total_warnings=0, total_files=1),
        path=p,
    )
    args = _args(snapshot_store=str(p), show_trend=True)
    maybe_show_trend(args, fmt="text")
    captured = capsys.readouterr()
    assert captured.out.strip() != ""


def test_maybe_show_trend_prints_json_delta(tmp_path: Path, capsys) -> None:
    p = tmp_path / "store.json"
    append_snapshot(_snap("2024-01-01T00:00:00"), path=p)
    append_snapshot(_snap("2024-01-02T00:00:00"), path=p)
    args = _args(snapshot_store=str(p), show_trend=True)
    maybe_show_trend(args, fmt="json")
    captured = capsys.readouterr()
    import json
    data = json.loads(captured.out)
    assert "delta" in data or "dangers" in str(data)
