"""Tests for rule_dependency and rule_dependency_formatter."""
from __future__ import annotations

import json

import pytest

from sqlmigrate_check.detector import Issue, Severity
from sqlmigrate_check.rule_dependency import (
    DependencyReport,
    build_dependency_report,
    related_rules_for,
)
from sqlmigrate_check.rule_dependency_formatter import (
    format_dependency_json,
    format_dependency_text,
    format_dependency_for_rule,
)


def _issue(rule_id: str, filepath: str = "migration.sql", line: int = 1) -> Issue:
    return Issue(
        rule_id=rule_id,
        severity=Severity.DANGER,
        message=f"Issue for {rule_id}",
        filepath=filepath,
        line_number=line,
    )


# ---------------------------------------------------------------------------
# related_rules_for
# ---------------------------------------------------------------------------

def test_related_rules_for_known_rule_returns_nonempty():
    result = related_rules_for("drop-table")
    assert len(result) > 0


def test_related_rules_for_unknown_rule_returns_empty():
    result = related_rules_for("nonexistent-rule")
    assert result == frozenset()


def test_related_rules_for_drop_table_includes_truncate():
    result = related_rules_for("drop-table")
    assert "truncate" in result


# ---------------------------------------------------------------------------
# build_dependency_report
# ---------------------------------------------------------------------------

def test_empty_issues_returns_empty_report():
    report = build_dependency_report([])
    assert report.is_empty
    assert report.total == 0


def test_single_issue_no_related_rules():
    issues = [_issue("drop-table")]
    report = build_dependency_report(issues)
    # Only one rule active — no co-occurrence possible
    assert report.is_empty


def test_cooccurring_rules_produce_hint():
    issues = [_issue("drop-table"), _issue("truncate")]
    report = build_dependency_report(issues)
    assert not report.is_empty
    rule_ids = {h.rule_id for h in report.hints}
    assert "drop-table" in rule_ids or "truncate" in rule_ids


def test_hint_contains_related_rule_ids():
    issues = [_issue("drop-table"), _issue("truncate")]
    report = build_dependency_report(issues)
    hint = next(h for h in report.hints if h.rule_id == "drop-table")
    assert "truncate" in hint.related_rule_ids


def test_hint_message_is_nonempty():
    issues = [_issue("drop-table"), _issue("truncate")]
    report = build_dependency_report(issues)
    for hint in report.hints:
        assert len(hint.message) > 0


def test_no_duplicate_hints():
    issues = [_issue("drop-table"), _issue("truncate")]
    report = build_dependency_report(issues)
    rule_ids = [h.rule_id for h in report.hints]
    assert len(rule_ids) == len(set(rule_ids))


# ---------------------------------------------------------------------------
# formatters
# ---------------------------------------------------------------------------

def test_format_text_no_issues():
    report = DependencyReport()
    text = format_dependency_text(report)
    assert "No rule" in text


def test_format_text_with_hints():
    issues = [_issue("drop-table"), _issue("truncate")]
    report = build_dependency_report(issues)
    text = format_dependency_text(report)
    assert "drop-table" in text or "truncate" in text


def test_format_json_valid_structure():
    issues = [_issue("drop-table"), _issue("truncate")]
    report = build_dependency_report(issues)
    data = json.loads(format_dependency_json(report))
    assert "total_hints" in data
    assert "hints" in data
    assert data["total_hints"] == report.total


def test_format_json_empty_report():
    report = DependencyReport()
    data = json.loads(format_dependency_json(report))
    assert data["total_hints"] == 0
    assert data["hints"] == []


def test_format_for_rule_no_match():
    report = DependencyReport()
    text = format_dependency_for_rule("drop-table", report)
    assert "No co-occurrence" in text


def test_format_for_rule_with_match():
    issues = [_issue("drop-table"), _issue("truncate")]
    report = build_dependency_report(issues)
    text = format_dependency_for_rule("drop-table", report)
    assert len(text) > 0
