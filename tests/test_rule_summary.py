"""Tests for sqlmigrate_check.rule_summary."""
from __future__ import annotations

import pytest

from sqlmigrate_check.detector import Issue, Severity, DetectionResult
from sqlmigrate_check.pipeline import ScanSummary
from sqlmigrate_check.rule_summary import (
    SeverityBucket,
    RuleSummary,
    build_rule_summary,
    rule_summary_from_scan,
)


def _danger(rule_id: str = "DROP_TABLE", line: int = 1) -> Issue:
    return Issue(rule_id=rule_id, severity=Severity.DANGER, message="danger", line=line, filepath="f.sql")


def _warning(rule_id: str = "ADD_INDEX", line: int = 2) -> Issue:
    return Issue(rule_id=rule_id, severity=Severity.WARNING, message="warn", line=line, filepath="f.sql")


def test_empty_issues_gives_zero_totals():
    summary = build_rule_summary([])
    assert summary.total == 0
    assert not summary.has_danger
    assert not summary.has_warnings


def test_danger_issue_counted_correctly():
    summary = build_rule_summary([_danger()])
    assert summary.total == 1
    assert summary.has_danger
    assert not summary.has_warnings


def test_warning_issue_counted_correctly():
    summary = build_rule_summary([_warning()])
    assert summary.total == 1
    assert not summary.has_danger
    assert summary.has_warnings


def test_mixed_issues_split_into_buckets():
    summary = build_rule_summary([_danger(), _warning()])
    assert summary.danger_bucket.count == 1
    assert summary.warning_bucket.count == 1
    assert summary.total == 2


def test_rule_ids_deduplicated_within_bucket():
    issues = [_danger("DROP_TABLE", 1), _danger("DROP_TABLE", 5)]
    summary = build_rule_summary(issues)
    assert summary.danger_bucket.rule_ids == ["DROP_TABLE"]


def test_multiple_distinct_rule_ids_preserved():
    issues = [_danger("DROP_TABLE"), _danger("DROP_COLUMN")]
    summary = build_rule_summary(issues)
    assert set(summary.danger_bucket.rule_ids) == {"DROP_TABLE", "DROP_COLUMN"}


def test_to_dict_structure():
    summary = build_rule_summary([_danger(), _warning()])
    d = summary.to_dict()
    assert d["total"] == 2
    assert d["danger"]["count"] == 1
    assert d["warning"]["count"] == 1
    assert isinstance(d["danger"]["rules"], list)
    assert isinstance(d["warning"]["rules"], list)


def test_rule_summary_from_scan_aggregates_all_results():
    r1 = DetectionResult(filepath="a.sql", issues=[_danger()])
    r2 = DetectionResult(filepath="b.sql", issues=[_warning()])
    scan = ScanSummary(results=[r1, r2])
    summary = rule_summary_from_scan(scan)
    assert summary.total == 2
    assert summary.has_danger
    assert summary.has_warnings


def test_rule_summary_from_scan_empty():
    scan = ScanSummary(results=[])
    summary = rule_summary_from_scan(scan)
    assert summary.total == 0
