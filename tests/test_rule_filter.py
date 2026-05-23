"""Tests for sqlmigrate_check.rule_filter."""
from __future__ import annotations

import pytest

from sqlmigrate_check.detector import Issue, Severity
from sqlmigrate_check.rule_filter import (
    apply_rule_filter,
    exclude_rule_ids,
    filter_by_filepath,
    filter_by_rule_ids,
    filter_by_severity,
)


def _issue(
    rule_id: str = "DROP_TABLE",
    severity: Severity = Severity.DANGER,
    filepath: str = "migrations/0001.sql",
    line: int = 1,
) -> Issue:
    return Issue(
        rule_id=rule_id,
        severity=severity,
        message="test",
        filepath=filepath,
        line_number=line,
    )


# ---------------------------------------------------------------------------
# filter_by_severity
# ---------------------------------------------------------------------------

def test_filter_by_severity_keeps_danger_when_min_danger():
    issues = [_issue(severity=Severity.DANGER), _issue(severity=Severity.WARNING)]
    result = filter_by_severity(issues, Severity.DANGER)
    assert len(result) == 1
    assert result[0].severity == Severity.DANGER


def test_filter_by_severity_keeps_all_when_min_warning():
    issues = [_issue(severity=Severity.DANGER), _issue(severity=Severity.WARNING)]
    result = filter_by_severity(issues, Severity.WARNING)
    assert len(result) == 2


def test_filter_by_severity_empty_input():
    assert filter_by_severity([], Severity.DANGER) == []


# ---------------------------------------------------------------------------
# filter_by_rule_ids
# ---------------------------------------------------------------------------

def test_filter_by_rule_ids_returns_matching():
    issues = [_issue(rule_id="DROP_TABLE"), _issue(rule_id="TRUNCATE")]
    result = filter_by_rule_ids(issues, ["DROP_TABLE"])
    assert len(result) == 1
    assert result[0].rule_id == "DROP_TABLE"


def test_filter_by_rule_ids_no_match_returns_empty():
    issues = [_issue(rule_id="DROP_TABLE")]
    assert filter_by_rule_ids(issues, ["TRUNCATE"]) == []


# ---------------------------------------------------------------------------
# exclude_rule_ids
# ---------------------------------------------------------------------------

def test_exclude_rule_ids_removes_matching():
    issues = [_issue(rule_id="DROP_TABLE"), _issue(rule_id="TRUNCATE")]
    result = exclude_rule_ids(issues, ["DROP_TABLE"])
    assert len(result) == 1
    assert result[0].rule_id == "TRUNCATE"


def test_exclude_rule_ids_no_match_keeps_all():
    issues = [_issue(rule_id="DROP_TABLE")]
    result = exclude_rule_ids(issues, ["TRUNCATE"])
    assert len(result) == 1


# ---------------------------------------------------------------------------
# filter_by_filepath
# ---------------------------------------------------------------------------

def test_filter_by_filepath_glob_match():
    issues = [
        _issue(filepath="migrations/0001.sql"),
        _issue(filepath="other/schema.sql"),
    ]
    result = filter_by_filepath(issues, "migrations/*.sql")
    assert len(result) == 1
    assert "migrations" in result[0].filepath


def test_filter_by_filepath_no_match_returns_empty():
    issues = [_issue(filepath="migrations/0001.sql")]
    assert filter_by_filepath(issues, "archive/*.sql") == []


# ---------------------------------------------------------------------------
# apply_rule_filter (combined)
# ---------------------------------------------------------------------------

def test_apply_rule_filter_no_filters_returns_all():
    issues = [_issue(), _issue(rule_id="TRUNCATE", severity=Severity.WARNING)]
    assert apply_rule_filter(issues) == issues


def test_apply_rule_filter_combined():
    issues = [
        _issue(rule_id="DROP_TABLE", severity=Severity.DANGER, filepath="migrations/a.sql"),
        _issue(rule_id="TRUNCATE", severity=Severity.WARNING, filepath="migrations/b.sql"),
        _issue(rule_id="DROP_COLUMN", severity=Severity.DANGER, filepath="other/c.sql"),
    ]
    result = apply_rule_filter(
        issues,
        min_severity=Severity.DANGER,
        exclude_rules=["DROP_COLUMN"],
        filepath_pattern="migrations/*.sql",
    )
    assert len(result) == 1
    assert result[0].rule_id == "DROP_TABLE"
