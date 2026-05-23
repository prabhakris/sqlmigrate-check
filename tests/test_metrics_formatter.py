"""Tests for sqlmigrate_check.metrics_formatter."""
from __future__ import annotations

import json

import pytest

from sqlmigrate_check.detector import Severity
from sqlmigrate_check.metrics import ScanMetrics
from sqlmigrate_check.metrics_formatter import (
    format_metrics_json,
    format_metrics_text,
    metrics_to_dict,
)


@pytest.fixture()
def populated_metrics() -> ScanMetrics:
    m = ScanMetrics(files_scanned=3, files_with_issues=2, suppressed_count=1, elapsed_seconds=0.42)
    m.record_rule_hit("drop_table", Severity.DANGER)
    m.record_rule_hit("drop_table", Severity.DANGER)
    m.record_rule_hit("truncate", Severity.DANGER)
    m.record_rule_hit("add_not_null", Severity.WARNING)
    return m


def test_metrics_to_dict_keys(populated_metrics: ScanMetrics) -> None:
    d = metrics_to_dict(populated_metrics)
    assert d["files_scanned"] == 3
    assert d["danger_count"] == 3
    assert d["warning_count"] == 1
    assert d["suppressed_count"] == 1
    assert isinstance(d["rules"], list)


def test_metrics_to_dict_rules_sorted(populated_metrics: ScanMetrics) -> None:
    d = metrics_to_dict(populated_metrics)
    totals = [r["total"] for r in d["rules"]]
    assert totals == sorted(totals, reverse=True)


def test_format_metrics_json_valid(populated_metrics: ScanMetrics) -> None:
    output = format_metrics_json(populated_metrics)
    parsed = json.loads(output)
    assert parsed["total_issues"] == 4


def test_format_metrics_json_elapsed_rounded(populated_metrics: ScanMetrics) -> None:
    output = format_metrics_json(populated_metrics)
    parsed = json.loads(output)
    assert parsed["elapsed_seconds"] == 0.42


def test_format_metrics_text_contains_summary(populated_metrics: ScanMetrics) -> None:
    text = format_metrics_text(populated_metrics)
    assert "3 file(s)" in text
    assert "danger=3" in text
    assert "warning=1" in text


def test_format_metrics_text_lists_top_rules(populated_metrics: ScanMetrics) -> None:
    text = format_metrics_text(populated_metrics)
    assert "drop_table" in text


def test_format_metrics_text_no_rules() -> None:
    m = ScanMetrics(files_scanned=1, elapsed_seconds=0.01)
    text = format_metrics_text(m)
    assert "Top rules" not in text
    assert "1 file(s)" in text
