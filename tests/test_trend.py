"""Tests for trend.py and trend_formatter.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from sqlmigrate_check.trend import (
    TrendSnapshot,
    TrendDelta,
    compute_delta,
    load_snapshot,
    save_snapshot,
    snapshot_from_metrics,
)
from sqlmigrate_check.trend_formatter import format_trend_text, format_trend_json
from sqlmigrate_check.metrics import ScanMetrics


# ---------------------------------------------------------------------------
# TrendSnapshot serialisation
# ---------------------------------------------------------------------------

def test_snapshot_to_dict_round_trip():
    snap = TrendSnapshot(total_files=3, total_danger=1, total_warnings=2, rule_hits={"drop_table": 1})
    restored = TrendSnapshot.from_dict(snap.to_dict())
    assert restored.total_files == 3
    assert restored.total_danger == 1
    assert restored.total_warnings == 2
    assert restored.rule_hits == {"drop_table": 1}


def test_snapshot_from_dict_missing_keys_uses_defaults():
    snap = TrendSnapshot.from_dict({})
    assert snap.total_files == 0
    assert snap.rule_hits == {}


# ---------------------------------------------------------------------------
# snapshot_from_metrics
# ---------------------------------------------------------------------------

def test_snapshot_from_metrics_counts():
    m = ScanMetrics()
    m.total_files = 5
    m.record_rule_hit("drop_table", severity="danger")
    m.record_rule_hit("drop_table", severity="danger")
    m.record_rule_hit("add_not_null", severity="warning")
    snap = snapshot_from_metrics(m)
    assert snap.total_files == 5
    assert snap.total_danger == 2
    assert snap.total_warnings == 1
    assert snap.rule_hits["drop_table"] == 2
    assert snap.rule_hits["add_not_null"] == 1


# ---------------------------------------------------------------------------
# compute_delta
# ---------------------------------------------------------------------------

def test_compute_delta_regression():
    prev = TrendSnapshot(total_danger=0, total_warnings=0)
    curr = TrendSnapshot(total_danger=2, total_warnings=1)
    delta = compute_delta(prev, curr)
    assert delta.danger_delta == 2
    assert delta.warning_delta == 1
    assert delta.is_regressing is True
    assert delta.is_improving is False


def test_compute_delta_improvement():
    prev = TrendSnapshot(total_danger=3, total_warnings=2)
    curr = TrendSnapshot(total_danger=1, total_warnings=0)
    delta = compute_delta(prev, curr)
    assert delta.danger_delta == -2
    assert delta.is_improving is True
    assert delta.is_regressing is False


def test_compute_delta_no_change():
    snap = TrendSnapshot(total_danger=1, total_warnings=1)
    delta = compute_delta(snap, snap)
    assert delta.is_regressing is False
    assert delta.is_improving is False


def test_compute_delta_rule_deltas():
    prev = TrendSnapshot(rule_hits={"drop_table": 2, "truncate": 1})
    curr = TrendSnapshot(rule_hits={"drop_table": 1, "add_not_null": 3})
    delta = compute_delta(prev, curr)
    assert delta.rule_deltas["drop_table"] == -1
    assert delta.rule_deltas["truncate"] == -1
    assert delta.rule_deltas["add_not_null"] == 3


# ---------------------------------------------------------------------------
# load / save snapshot
# ---------------------------------------------------------------------------

def test_save_and_load_snapshot(tmp_path):
    p = tmp_path / "trend.json"
    snap = TrendSnapshot(total_files=7, total_danger=2, total_warnings=3, rule_hits={"drop_column": 2})
    save_snapshot(p, snap)
    loaded = load_snapshot(p)
    assert loaded is not None
    assert loaded.total_files == 7
    assert loaded.rule_hits == {"drop_column": 2}


def test_load_snapshot_missing_file_returns_none(tmp_path):
    result = load_snapshot(tmp_path / "nonexistent.json")
    assert result is None


def test_load_snapshot_corrupt_file_returns_none(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("not json", encoding="utf-8")
    assert load_snapshot(p) is None


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def test_format_trend_text_no_delta():
    snap = TrendSnapshot(total_files=4, total_danger=1, total_warnings=2)
    text = format_trend_text(snap)
    assert "Trend Report" in text
    assert "4" in text


def test_format_trend_text_with_regression():
    prev = TrendSnapshot(total_danger=0)
    curr = TrendSnapshot(total_danger=3)
    delta = compute_delta(prev, curr)
    text = format_trend_text(curr, delta)
    assert "Regression" in text
    assert "+3" in text


def test_format_trend_json_structure():
    snap = TrendSnapshot(total_files=2, total_danger=1, total_warnings=0)
    prev = TrendSnapshot(total_danger=0)
    delta = compute_delta(prev, snap)
    raw = format_trend_json(snap, delta)
    data = json.loads(raw)
    assert "current" in data
    assert "delta" in data
    assert data["delta"]["is_regressing"] is True


def test_format_trend_json_no_delta():
    snap = TrendSnapshot()
    raw = format_trend_json(snap)
    data = json.loads(raw)
    assert "delta" not in data
