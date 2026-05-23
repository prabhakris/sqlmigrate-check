"""Tests for sqlmigrate_check.diff_reporter."""
from __future__ import annotations

import pytest

from sqlmigrate_check.detector import DetectionResult, Issue, Severity
from sqlmigrate_check.pipeline import ScanSummary
from sqlmigrate_check.diff_reporter import (
    FileDiff,
    ScanDiff,
    compute_diff,
    format_diff_text,
)


def _issue(rule_id: str, line: int, msg: str, sev: Severity = Severity.DANGER) -> Issue:
    return Issue(rule_id=rule_id, severity=sev, message=msg, line_number=line)


def _summary(*results: DetectionResult) -> ScanSummary:
    return ScanSummary(results=list(results))


def _result(filepath: str, *issues: Issue) -> DetectionResult:
    return DetectionResult(filepath=filepath, issues=list(issues))


# ---------------------------------------------------------------------------
# FileDiff
# ---------------------------------------------------------------------------

def test_file_diff_has_changes_when_added():
    fd = FileDiff(filepath="a.sql", added=[_issue("DROP_TABLE", 1, "drop")])
    assert fd.has_changes is True


def test_file_diff_no_changes_when_empty():
    fd = FileDiff(filepath="a.sql")
    assert fd.has_changes is False


# ---------------------------------------------------------------------------
# ScanDiff aggregates
# ---------------------------------------------------------------------------

def test_scan_diff_totals():
    fd = FileDiff(
        filepath="a.sql",
        added=[_issue("DROP_TABLE", 1, "drop")],
        resolved=[_issue("TRUNCATE", 2, "trunc"), _issue("TRUNCATE", 3, "trunc2")],
    )
    sd = ScanDiff(file_diffs={"a.sql": fd})
    assert sd.total_added == 1
    assert sd.total_resolved == 2
    assert sd.has_changes is True


def test_scan_diff_empty_has_no_changes():
    assert ScanDiff().has_changes is False


# ---------------------------------------------------------------------------
# compute_diff
# ---------------------------------------------------------------------------

def test_compute_diff_no_changes():
    issue = _issue("DROP_TABLE", 5, "Drops table")
    prev = _summary(_result("m.sql", issue))
    curr = _summary(_result("m.sql", issue))
    diff = compute_diff(prev, curr)
    assert not diff.has_changes


def test_compute_diff_new_issue_detected():
    prev = _summary(_result("m.sql"))
    new_issue = _issue("DROP_TABLE", 5, "Drops table")
    curr = _summary(_result("m.sql", new_issue))
    diff = compute_diff(prev, curr)
    assert diff.total_added == 1
    assert diff.total_resolved == 0
    assert "m.sql" in diff.file_diffs


def test_compute_diff_resolved_issue():
    old_issue = _issue("TRUNCATE", 3, "Truncate")
    prev = _summary(_result("m.sql", old_issue))
    curr = _summary(_result("m.sql"))
    diff = compute_diff(prev, curr)
    assert diff.total_resolved == 1
    assert diff.total_added == 0


def test_compute_diff_new_file():
    prev = _summary()
    curr = _summary(_result("new.sql", _issue("DROP_COLUMN", 1, "drop col")))
    diff = compute_diff(prev, curr)
    assert diff.total_added == 1


def test_compute_diff_removed_file():
    prev = _summary(_result("old.sql", _issue("DROP_TABLE", 1, "drop")))
    curr = _summary()
    diff = compute_diff(prev, curr)
    assert diff.total_resolved == 1


# ---------------------------------------------------------------------------
# format_diff_text
# ---------------------------------------------------------------------------

def test_format_diff_text_no_changes():
    text = format_diff_text(ScanDiff())
    assert "No changes" in text


def test_format_diff_text_shows_added_and_resolved():
    fd = FileDiff(
        filepath="m.sql",
        added=[_issue("DROP_TABLE", 10, "Drops table")],
        resolved=[_issue("TRUNCATE", 2, "Truncate")],
    )
    sd = ScanDiff(file_diffs={"m.sql": fd})
    text = format_diff_text(sd)
    assert "+1 added" in text
    assert "-1 resolved" in text
    assert "NEW" in text
    assert "RESOLVED" in text
    assert "m.sql" in text
