"""Tests for sqlmigrate_check.baseline."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from sqlmigrate_check.baseline import (
    _issue_fingerprint,
    build_baseline_from_results,
    filter_new_issues,
    load_baseline,
    save_baseline,
)
from sqlmigrate_check.detector import DetectionResult, Issue, Severity


def _make_issue(rule: str = "DROP_TABLE", line: str = "DROP TABLE foo;", lineno: int = 1) -> Issue:
    return Issue(severity=Severity.DANGER, rule=rule, message="test", line=line, line_number=lineno)


# ---------------------------------------------------------------------------
# _issue_fingerprint
# ---------------------------------------------------------------------------

def test_fingerprint_is_stable():
    issue = _make_issue()
    fp1 = _issue_fingerprint("migrations/001.sql", issue)
    fp2 = _issue_fingerprint("migrations/001.sql", issue)
    assert fp1 == fp2


def test_fingerprint_differs_by_filepath():
    issue = _make_issue()
    assert _issue_fingerprint("a.sql", issue) != _issue_fingerprint("b.sql", issue)


def test_fingerprint_differs_by_line_number():
    issue_a = _make_issue(lineno=1)
    issue_b = _make_issue(lineno=2)
    assert _issue_fingerprint("a.sql", issue_a) != _issue_fingerprint("a.sql", issue_b)


# ---------------------------------------------------------------------------
# load_baseline / save_baseline
# ---------------------------------------------------------------------------

def test_load_baseline_missing_file_returns_empty_set(tmp_path):
    result = load_baseline(tmp_path / "nonexistent.json")
    assert result == set()


def test_save_and_load_roundtrip(tmp_path):
    baseline_file = tmp_path / "baseline.json"
    fingerprints = {"abc123", "def456", "ghi789"}
    save_baseline(fingerprints, baseline_file)
    loaded = load_baseline(baseline_file)
    assert loaded == fingerprints


def test_save_baseline_creates_valid_json(tmp_path):
    baseline_file = tmp_path / "baseline.json"
    save_baseline({"aaa", "bbb"}, baseline_file)
    data = json.loads(baseline_file.read_text())
    assert isinstance(data, list)
    assert set(data) == {"aaa", "bbb"}


# ---------------------------------------------------------------------------
# build_baseline_from_results
# ---------------------------------------------------------------------------

def test_build_baseline_empty_results():
    assert build_baseline_from_results({}) == set()


def test_build_baseline_creates_fingerprints_for_all_issues():
    issue1 = _make_issue(lineno=1)
    issue2 = _make_issue(rule="DROP_COLUMN", lineno=5)
    result = DetectionResult(issues=[issue1, issue2])
    fps = build_baseline_from_results({"mig.sql": result})
    assert len(fps) == 2


# ---------------------------------------------------------------------------
# filter_new_issues
# ---------------------------------------------------------------------------

def test_filter_new_issues_empty_baseline_returns_all():
    issues = [_make_issue(lineno=1), _make_issue(lineno=2)]
    assert filter_new_issues("mig.sql", issues, set()) == issues


def test_filter_new_issues_suppresses_known():
    issue = _make_issue(lineno=1)
    fp = _issue_fingerprint("mig.sql", issue)
    result = filter_new_issues("mig.sql", [issue], {fp})
    assert result == []


def test_filter_new_issues_keeps_unknown():
    known = _make_issue(lineno=1)
    new = _make_issue(lineno=3)
    fp = _issue_fingerprint("mig.sql", known)
    result = filter_new_issues("mig.sql", [known, new], {fp})
    assert result == [new]
