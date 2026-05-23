"""Integration: allowlist wired into the pipeline via Config."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from sqlmigrate_check.allowlist import Allowlist, allowlist_from_config
from sqlmigrate_check.detector import DetectionResult, Issue, Severity


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_issue(rule_id: str, filepath: str = "migrations/001.sql", line: int = 1) -> Issue:
    return Issue(
        rule_id=rule_id,
        severity=Severity.DANGER,
        message=f"Detected {rule_id}",
        filepath=filepath,
        line_number=line,
        line_content=f"-- {rule_id}",
    )


def _filter_with_allowlist(issues: list[Issue], allowlist: Allowlist) -> list[Issue]:
    """Simulate what a pipeline step would do: drop allowlisted issues."""
    return [
        issue for issue in issues
        if not allowlist.is_allowed(issue.filepath, issue.rule_id)
    ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_allowlist_removes_matching_issue():
    al = allowlist_from_config({"001.sql": "drop-table"})
    issues = [_make_issue("drop-table"), _make_issue("truncate")]
    filtered = _filter_with_allowlist(issues, al)
    assert len(filtered) == 1
    assert filtered[0].rule_id == "truncate"


def test_allowlist_wildcard_removes_all_issues():
    al = allowlist_from_config({"001.sql": "*"})
    issues = [
        _make_issue("drop-table"),
        _make_issue("truncate"),
        _make_issue("drop-column"),
    ]
    filtered = _filter_with_allowlist(issues, al)
    assert filtered == []


def test_allowlist_no_match_keeps_all_issues():
    al = allowlist_from_config({"legacy_*.sql": "drop-table"})
    issues = [_make_issue("drop-table", filepath="migrations/new_001.sql")]
    filtered = _filter_with_allowlist(issues, al)
    assert len(filtered) == 1


def test_allowlist_empty_keeps_all_issues():
    al = Allowlist()
    issues = [_make_issue("drop-table"), _make_issue("truncate")]
    assert _filter_with_allowlist(issues, al) == issues


def test_allowlist_multiple_patterns_combined():
    al = allowlist_from_config({
        "001.sql": "drop-table",
        "migrations/*.sql": "truncate",
    })
    issues = [
        _make_issue("drop-table", filepath="migrations/001.sql"),
        _make_issue("truncate", filepath="migrations/001.sql"),
        _make_issue("drop-column", filepath="migrations/001.sql"),
    ]
    filtered = _filter_with_allowlist(issues, al)
    # drop-table matched by filename, truncate matched by glob — only drop-column remains
    assert len(filtered) == 1
    assert filtered[0].rule_id == "drop-column"
