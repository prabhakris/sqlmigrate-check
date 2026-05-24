"""Tests for rule_lint module."""
import pytest

from sqlmigrate_check.rule_lint import (
    LintReport,
    LintResult,
    LintViolation,
    lint_file,
    lint_files,
)


# ---------------------------------------------------------------------------
# LintViolation
# ---------------------------------------------------------------------------

def test_lint_violation_str():
    v = LintViolation("mig.sql", 3, "L001", "Double semicolon detected")
    assert "mig.sql:3" in str(v)
    assert "L001" in str(v)


# ---------------------------------------------------------------------------
# LintResult
# ---------------------------------------------------------------------------

def test_lint_result_no_violations_has_violations_false():
    r = LintResult(filepath="a.sql")
    assert not r.has_violations
    assert r.violation_count == 0


def test_lint_result_with_violation_has_violations_true():
    v = LintViolation("a.sql", 1, "L003", "Empty file")
    r = LintResult(filepath="a.sql", violations=[v])
    assert r.has_violations
    assert r.violation_count == 1


# ---------------------------------------------------------------------------
# LintReport
# ---------------------------------------------------------------------------

def test_lint_report_aggregates_totals():
    v1 = LintViolation("a.sql", 1, "L003", "Empty")
    v2 = LintViolation("b.sql", 2, "L002", "lowercase keyword")
    r1 = LintResult("a.sql", [v1])
    r2 = LintResult("b.sql", [v2])
    report = LintReport(results=[r1, r2])
    assert report.total_violations == 2
    assert report.files_with_violations == 2


def test_lint_report_all_violations_flattened():
    v1 = LintViolation("a.sql", 1, "L003", "Empty")
    v2 = LintViolation("a.sql", 5, "L002", "lowercase")
    r = LintResult("a.sql", [v1, v2])
    report = LintReport(results=[r])
    assert len(report.all_violations) == 2


# ---------------------------------------------------------------------------
# lint_file
# ---------------------------------------------------------------------------

def test_empty_file_triggers_l003():
    result = lint_file("empty.sql", "")
    codes = {v.code for v in result.violations}
    assert "L003" in codes


def test_whitespace_only_file_triggers_l003():
    result = lint_file("blank.sql", "   \n  \n")
    codes = {v.code for v in result.violations}
    assert "L003" in codes


def test_lowercase_keyword_triggers_l002():
    result = lint_file("mig.sql", "drop table users;\n")
    codes = {v.code for v in result.violations}
    assert "L002" in codes


def test_uppercase_keyword_no_l002():
    result = lint_file("mig.sql", "DROP TABLE users;\n")
    codes = {v.code for v in result.violations}
    assert "L002" not in codes


def test_double_semicolon_triggers_l001():
    result = lint_file("mig.sql", "DROP TABLE users;;\n")
    codes = {v.code for v in result.violations}
    assert "L001" in codes


def test_single_semicolon_no_l001():
    result = lint_file("mig.sql", "DROP TABLE users;\n")
    codes = {v.code for v in result.violations}
    assert "L001" not in codes


def test_comment_line_not_flagged_for_l002():
    result = lint_file("mig.sql", "-- drop table users\nDROP TABLE users;\n")
    codes = {v.code for v in result.violations}
    assert "L002" not in codes


# ---------------------------------------------------------------------------
# lint_files
# ---------------------------------------------------------------------------

def test_lint_files_multiple_inputs():
    contents = {
        "a.sql": "DROP TABLE x;\n",
        "b.sql": "",
    }
    report = lint_files(contents)
    assert report.files_with_violations == 1  # only b.sql (empty)
    assert report.total_violations == 1


def test_lint_files_empty_dict_returns_empty_report():
    report = lint_files({})
    assert report.total_violations == 0
    assert report.files_with_violations == 0
