"""Tests for sqlmigrate_check.severity_filter."""
from __future__ import annotations

import pytest

from sqlmigrate_check.detector import Issue, Severity
from sqlmigrate_check.severity_filter import (
    filter_by_minimum_severity,
    highest_severity,
    meets_minimum,
    parse_severity,
    severity_rank,
)


def _issue(severity: Severity, rule: str = "R001") -> Issue:
    return Issue(
        filepath="migration.sql",
        line_number=1,
        rule_id=rule,
        severity=severity,
        message="test issue",
    )


# --- severity_rank ---

def test_warning_rank_less_than_danger():
    assert severity_rank(Severity.WARNING) < severity_rank(Severity.DANGER)


def test_danger_rank_is_positive():
    assert severity_rank(Severity.DANGER) >= 0


# --- meets_minimum ---

def test_danger_meets_minimum_warning():
    assert meets_minimum(_issue(Severity.DANGER), Severity.WARNING) is True


def test_danger_meets_minimum_danger():
    assert meets_minimum(_issue(Severity.DANGER), Severity.DANGER) is True


def test_warning_meets_minimum_warning():
    assert meets_minimum(_issue(Severity.WARNING), Severity.WARNING) is True


def test_warning_does_not_meet_minimum_danger():
    assert meets_minimum(_issue(Severity.WARNING), Severity.DANGER) is False


# --- filter_by_minimum_severity ---

def test_filter_keeps_danger_when_min_danger():
    issues = [_issue(Severity.WARNING), _issue(Severity.DANGER)]
    result = filter_by_minimum_severity(issues, Severity.DANGER)
    assert all(i.severity == Severity.DANGER for i in result)
    assert len(result) == 1


def test_filter_keeps_all_when_min_warning():
    issues = [_issue(Severity.WARNING), _issue(Severity.DANGER)]
    result = filter_by_minimum_severity(issues, Severity.WARNING)
    assert len(result) == 2


def test_filter_empty_input_returns_empty():
    assert filter_by_minimum_severity([], Severity.WARNING) == []


# --- parse_severity ---

def test_parse_severity_warning():
    assert parse_severity("warning") == Severity.WARNING


def test_parse_severity_danger_uppercase():
    assert parse_severity("DANGER") == Severity.DANGER


def test_parse_severity_mixed_case():
    assert parse_severity("Warning") == Severity.WARNING


def test_parse_severity_invalid_raises():
    with pytest.raises(ValueError, match="Unknown severity"):
        parse_severity("CRITICAL")


# --- highest_severity ---

def test_highest_severity_returns_danger():
    issues = [_issue(Severity.WARNING), _issue(Severity.DANGER)]
    assert highest_severity(issues) == Severity.DANGER


def test_highest_severity_all_warnings():
    issues = [_issue(Severity.WARNING), _issue(Severity.WARNING)]
    assert highest_severity(issues) == Severity.WARNING


def test_highest_severity_empty_returns_none():
    assert highest_severity([]) is None
