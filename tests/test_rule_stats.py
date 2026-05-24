"""Tests for rule_stats module."""
from __future__ import annotations

import pytest

from sqlmigrate_check.detector import Issue, Severity, DetectionResult
from sqlmigrate_check.pipeline import ScanSummary
from sqlmigrate_check.rule_stats import RuleStat, compute_rule_stats, sorted_stats


def _issue(rule_id: str, severity: Severity, line: int = 1) -> Issue:
    return Issue(rule_id=rule_id, severity=severity, line=line, message="msg", context="")


def _summary(*pairs) -> ScanSummary:
    """Build a ScanSummary from (filepath, [issues]) pairs."""
    results = {}
    for filepath, issues in pairs:
        results[filepath] = DetectionResult(filepath=filepath, issues=issues)
    return ScanSummary(results=results)


def test_empty_summary_returns_empty_stats():
    summary = _summary()
    stats = compute_rule_stats(summary)
    assert stats == {}


def test_single_danger_issue_counted():
    summary = _summary(("a.sql", [_issue("drop_table", Severity.DANGER)]))
    stats = compute_rule_stats(summary)
    assert "drop_table" in stats
    assert stats["drop_table"].danger_count == 1
    assert stats["drop_table"].warning_count == 0
    assert stats["drop_table"].total == 1


def test_single_warning_issue_counted():
    summary = _summary(("a.sql", [_issue("add_not_null", Severity.WARNING)]))
    stats = compute_rule_stats(summary)
    assert stats["add_not_null"].warning_count == 1
    assert stats["add_not_null"].danger_count == 0


def test_multiple_files_same_rule_aggregated():
    summary = _summary(
        ("a.sql", [_issue("drop_table", Severity.DANGER)]),
        ("b.sql", [_issue("drop_table", Severity.DANGER)]),
    )
    stats = compute_rule_stats(summary)
    assert stats["drop_table"].danger_count == 2
    assert sorted(stats["drop_table"].affected_files) == ["a.sql", "b.sql"]


def test_affected_files_deduplicated():
    summary = _summary(
        ("a.sql", [_issue("drop_table", Severity.DANGER), _issue("drop_table", Severity.DANGER, line=2)]),
    )
    stats = compute_rule_stats(summary)
    assert stats["drop_table"].affected_files == ["a.sql"]


def test_highest_severity_danger_when_any_danger():
    stat = RuleStat(rule_id="r", danger_count=1, warning_count=3)
    assert stat.highest_severity == Severity.DANGER


def test_highest_severity_warning_when_no_danger():
    stat = RuleStat(rule_id="r", danger_count=0, warning_count=2)
    assert stat.highest_severity == Severity.WARNING


def test_sorted_stats_by_total_descending():
    stats = {
        "a": RuleStat(rule_id="a", danger_count=1),
        "b": RuleStat(rule_id="b", danger_count=3),
        "c": RuleStat(rule_id="c", warning_count=2),
    }
    result = sorted_stats(stats)
    assert result[0].rule_id == "b"
    assert result[1].rule_id == "c"
    assert result[2].rule_id == "a"


def test_sorted_stats_tie_broken_by_rule_id():
    stats = {
        "z_rule": RuleStat(rule_id="z_rule", danger_count=2),
        "a_rule": RuleStat(rule_id="a_rule", danger_count=2),
    }
    result = sorted_stats(stats)
    assert result[0].rule_id == "a_rule"
    assert result[1].rule_id == "z_rule"
