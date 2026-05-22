"""Tests for output formatters."""
import json

import pytest

from sqlmigrate_check.detector import DetectionResult, Issue, Severity
from sqlmigrate_check.formatter import (
    OutputFormat,
    format_result,
    format_text,
    format_json,
    format_github,
)


@pytest.fixture
def danger_result():
    return DetectionResult(
        issues=[
            Issue(severity=Severity.DANGER, message="DROP TABLE detected", line=3),
        ]
    )


@pytest.fixture
def warning_result():
    return DetectionResult(
        issues=[
            Issue(severity=Severity.WARNING, message="Adding index without CONCURRENTLY", line=5),
        ]
    )


@pytest.fixture
def empty_result():
    return DetectionResult(issues=[])


def test_format_text_no_issues(empty_result):
    output = format_text(empty_result)
    assert "No unsafe" in output
    assert "✅" in output


def test_format_text_with_danger(danger_result):
    output = format_text(danger_result, filename="migration.sql")
    assert "DANGER" in output
    assert "DROP TABLE detected" in output
    assert "migration.sql" in output
    assert "❌" in output


def test_format_text_warning_only(warning_result):
    output = format_text(warning_result)
    assert "WARNING" in output
    assert "⚠️" in output


def test_format_json_structure(danger_result):
    output = format_json(danger_result, filename="migration.sql")
    data = json.loads(output)
    assert data["filename"] == "migration.sql"
    assert data["has_danger"] is True
    assert data["issue_count"] == 1
    assert data["issues"][0]["severity"] == "danger"
    assert data["issues"][0]["line"] == 3


def test_format_json_empty(empty_result):
    output = format_json(empty_result)
    data = json.loads(output)
    assert data["issue_count"] == 0
    assert data["issues"] == []
    assert data["has_danger"] is False


def test_format_github_danger(danger_result):
    output = format_github(danger_result, filename="migration.sql")
    assert "::error" in output
    assert "file=migration.sql" in output
    assert "line=3" in output
    assert "DROP TABLE detected" in output


def test_format_github_warning(warning_result):
    output = format_github(warning_result)
    assert "::warning" in output


def test_format_github_empty(empty_result):
    assert format_github(empty_result) == ""


def test_format_result_dispatch(danger_result):
    assert format_result(danger_result, OutputFormat.TEXT) == format_text(danger_result)
    assert format_result(danger_result, OutputFormat.JSON) == format_json(danger_result)
    assert format_result(danger_result, OutputFormat.GITHUB) == format_github(danger_result)
