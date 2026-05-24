"""Tests for rule_lint_formatter module."""
import json

import pytest

from sqlmigrate_check.rule_lint import LintReport, LintResult, LintViolation
from sqlmigrate_check.rule_lint_formatter import (
    format_lint_github,
    format_lint_json,
    format_lint_text,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def empty_report() -> LintReport:
    return LintReport(results=[])


@pytest.fixture()
def report_with_violations() -> LintReport:
    v1 = LintViolation("mig/001.sql", 2, "L002", "Lowercase keyword")
    v2 = LintViolation("mig/002.sql", 1, "L003", "Empty file")
    r1 = LintResult("mig/001.sql", [v1])
    r2 = LintResult("mig/002.sql", [v2])
    return LintReport(results=[r1, r2])


# ---------------------------------------------------------------------------
# format_lint_text
# ---------------------------------------------------------------------------

def test_format_lint_text_no_violations(empty_report):
    out = format_lint_text(empty_report)
    assert "no violations" in out.lower()


def test_format_lint_text_shows_violation_count(report_with_violations):
    out = format_lint_text(report_with_violations)
    assert "2" in out


def test_format_lint_text_shows_filepath(report_with_violations):
    out = format_lint_text(report_with_violations)
    assert "mig/001.sql" in out


def test_format_lint_text_shows_code(report_with_violations):
    out = format_lint_text(report_with_violations)
    assert "L002" in out
    assert "L003" in out


# ---------------------------------------------------------------------------
# format_lint_json
# ---------------------------------------------------------------------------

def test_format_lint_json_is_valid_json(report_with_violations):
    raw = format_lint_json(report_with_violations)
    data = json.loads(raw)
    assert isinstance(data, dict)


def test_format_lint_json_total_violations_key(report_with_violations):
    data = json.loads(format_lint_json(report_with_violations))
    assert data["total_violations"] == 2


def test_format_lint_json_violations_list(report_with_violations):
    data = json.loads(format_lint_json(report_with_violations))
    assert len(data["violations"]) == 2
    first = data["violations"][0]
    assert {"filepath", "line", "code", "message"} <= set(first.keys())


def test_format_lint_json_empty_report(empty_report):
    data = json.loads(format_lint_json(empty_report))
    assert data["total_violations"] == 0
    assert data["violations"] == []


# ---------------------------------------------------------------------------
# format_lint_github
# ---------------------------------------------------------------------------

def test_format_lint_github_no_violations_empty_string(empty_report):
    out = format_lint_github(empty_report)
    assert out == ""


def test_format_lint_github_annotation_format(report_with_violations):
    out = format_lint_github(report_with_violations)
    assert "::warning" in out
    assert "mig/001.sql" in out
    assert "L002" in out


def test_format_lint_github_one_line_per_violation(report_with_violations):
    out = format_lint_github(report_with_violations)
    annotation_lines = [l for l in out.splitlines() if l.startswith("::warning")]
    assert len(annotation_lines) == 2
