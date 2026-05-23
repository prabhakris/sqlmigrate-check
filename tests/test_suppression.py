"""Tests for sqlmigrate_check.suppression."""
from __future__ import annotations

import pytest

from sqlmigrate_check.allowlist import Allowlist
from sqlmigrate_check.config import Config
from sqlmigrate_check.detector import DetectionResult, Issue, Severity
from sqlmigrate_check.suppression import (
    SuppressionSummary,
    apply_suppressions,
    apply_suppressions_with_config,
)


def _issue(rule_id: str, line: int, filepath: str = "mig.sql") -> Issue:
    return Issue(
        rule_id=rule_id,
        message=f"issue {rule_id}",
        severity=Severity.DANGER,
        line_number=line,
        filepath=filepath,
    )


def _result(*issues: Issue, filepath: str = "mig.sql") -> DetectionResult:
    return DetectionResult(filepath=filepath, issues=list(issues))


# ---------------------------------------------------------------------------
# SuppressionSummary
# ---------------------------------------------------------------------------

def test_summary_total_suppressed():
    s = SuppressionSummary(suppressed_by_comment=2, suppressed_by_allowlist=3)
    assert s.total_suppressed == 5


def test_summary_zero_by_default():
    s = SuppressionSummary()
    assert s.total_suppressed == 0


# ---------------------------------------------------------------------------
# Comment suppression
# ---------------------------------------------------------------------------

def test_inline_comment_suppresses_issue():
    sql = "DROP TABLE foo; -- sqlmigrate-ignore"
    issue = _issue("drop_table", line=1)
    result, summary = apply_suppressions(_result(issue), sql, Allowlist({}))
    assert result.issues == []
    assert summary.suppressed_by_comment == 1
    assert summary.suppressed_by_allowlist == 0


def test_no_comment_keeps_issue():
    sql = "DROP TABLE foo;"
    issue = _issue("drop_table", line=1)
    result, summary = apply_suppressions(_result(issue), sql, Allowlist({}))
    assert len(result.issues) == 1
    assert summary.total_suppressed == 0


def test_comment_on_different_line_does_not_suppress():
    sql = "SELECT 1; -- sqlmigrate-ignore\nDROP TABLE foo;"
    issue = _issue("drop_table", line=2)
    result, summary = apply_suppressions(_result(issue), sql, Allowlist({}))
    assert len(result.issues) == 1


# ---------------------------------------------------------------------------
# Allowlist suppression
# ---------------------------------------------------------------------------

def test_allowlist_suppresses_matching_rule():
    sql = "DROP TABLE foo;"
    issue = _issue("drop_table", line=1, filepath="mig.sql")
    allowlist = Allowlist({"mig.sql": ["drop_table"]})
    result, summary = apply_suppressions(_result(issue), sql, allowlist)
    assert result.issues == []
    assert summary.suppressed_by_allowlist == 1


def test_allowlist_wildcard_suppresses_any_rule():
    sql = "DROP TABLE foo;"
    issue = _issue("drop_table", line=1, filepath="mig.sql")
    allowlist = Allowlist({"mig.sql": ["*"]})
    result, summary = apply_suppressions(_result(issue), sql, allowlist)
    assert result.issues == []


# ---------------------------------------------------------------------------
# Config convenience wrapper
# ---------------------------------------------------------------------------

def test_apply_suppressions_with_config_no_allowlist():
    sql = "DROP TABLE foo;"
    issue = _issue("drop_table", line=1)
    config = Config()
    result, summary = apply_suppressions_with_config(_result(issue), sql, config)
    assert len(result.issues) == 1
    assert summary.total_suppressed == 0


def test_apply_suppressions_with_config_with_inline_ignore():
    sql = "DROP TABLE foo; -- sqlmigrate-ignore"
    issue = _issue("drop_table", line=1)
    config = Config()
    result, summary = apply_suppressions_with_config(_result(issue), sql, config)
    assert result.issues == []
    assert summary.suppressed_by_comment == 1
