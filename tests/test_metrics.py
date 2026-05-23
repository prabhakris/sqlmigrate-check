"""Tests for sqlmigrate_check.metrics."""
from __future__ import annotations

import pytest

from sqlmigrate_check.detector import Severity
from sqlmigrate_check.metrics import (
    RuleMetrics,
    ScanMetrics,
    ScanTimer,
    build_metrics_from_pipeline,
)


def test_rule_metrics_total() -> None:
    rm = RuleMetrics(rule_id="drop_table", danger_count=3, warning_count=1)
    assert rm.total == 4


def test_scan_metrics_record_danger() -> None:
    m = ScanMetrics()
    m.record_rule_hit("drop_table", Severity.DANGER)
    assert m.danger_count == 1
    assert m.warning_count == 0
    assert m.total_issues == 1
    assert "drop_table" in m.rules


def test_scan_metrics_record_warning() -> None:
    m = ScanMetrics()
    m.record_rule_hit("add_not_null", Severity.WARNING)
    assert m.warning_count == 1
    assert m.danger_count == 0


def test_scan_metrics_multiple_rules() -> None:
    m = ScanMetrics()
    m.record_rule_hit("drop_table", Severity.DANGER)
    m.record_rule_hit("drop_table", Severity.DANGER)
    m.record_rule_hit("truncate", Severity.DANGER)
    assert m.total_issues == 3
    assert m.rules["drop_table"].danger_count == 2
    assert m.rules["truncate"].danger_count == 1


def test_sorted_rules_order() -> None:
    m = ScanMetrics()
    for _ in range(3):
        m.record_rule_hit("drop_table", Severity.DANGER)
    m.record_rule_hit("truncate", Severity.DANGER)
    ordered = m.sorted_rules()
    assert ordered[0].rule_id == "drop_table"
    assert ordered[1].rule_id == "truncate"


def test_scan_timer_measures_elapsed() -> None:
    with ScanTimer() as t:
        pass
    assert t.elapsed >= 0.0


def test_build_metrics_from_pipeline_empty(tmp_path) -> None:
    """build_metrics_from_pipeline works with a zero-result summary."""
    from sqlmigrate_check.pipeline import ScanSummary

    summary = ScanSummary(results=[])
    m = build_metrics_from_pipeline(summary, suppressed_count=0, elapsed=1.23)
    assert m.files_scanned == 0
    assert m.total_issues == 0
    assert m.elapsed_seconds == 1.23


def test_build_metrics_from_pipeline_with_issues(tmp_path) -> None:
    from sqlmigrate_check.detector import DetectionResult, Issue
    from sqlmigrate_check.pipeline import ScanSummary

    issue = Issue(
        rule_id="drop_table",
        severity=Severity.DANGER,
        message="DROP TABLE detected",
        line_number=1,
        line_content="DROP TABLE users;",
        filepath="migration.sql",
    )
    result = DetectionResult(filepath="migration.sql", issues=[issue])
    summary = ScanSummary(results=[result])
    m = build_metrics_from_pipeline(summary, suppressed_count=2, elapsed=0.5)
    assert m.total_issues == 1
    assert m.danger_count == 1
    assert m.suppressed_count == 2
    assert m.rules["drop_table"].danger_count == 1
