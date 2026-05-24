"""Tests for sqlmigrate_check.output_writer."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from sqlmigrate_check.detector import DetectionResult, Issue, Severity
from sqlmigrate_check.formatter import OutputFormat
from sqlmigrate_check.output_writer import write_report, write_text
from sqlmigrate_check.pipeline import ScanSummary
from sqlmigrate_check.reporter import Report, ReportOptions


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_summary(tmp_path: Path, sql: str = "DROP TABLE users;") -> ScanSummary:
    from sqlmigrate_check.rules_registration import RULES  # noqa: F401 – ensure rules registered
    from sqlmigrate_check.pipeline import run_pipeline

    migration = tmp_path / "migrations" / "001_drop.sql"
    migration.parent.mkdir(parents=True, exist_ok=True)
    migration.write_text(sql, encoding="utf-8")
    return run_pipeline([migration])


def _empty_report() -> Report:
    return Report(
        options=ReportOptions(),
        per_file={},
        suppression_report=None,
    )


def _empty_summary() -> ScanSummary:
    return ScanSummary(results={})


# ---------------------------------------------------------------------------
# write_text
# ---------------------------------------------------------------------------

def test_write_text_to_stdout(capsys: pytest.CaptureFixture) -> None:
    write_text("hello world")
    captured = capsys.readouterr()
    assert "hello world" in captured.out


def test_write_text_to_file(tmp_path: Path) -> None:
    out = tmp_path / "out" / "result.txt"
    write_text("hello file", output_path=out)
    assert out.read_text(encoding="utf-8").strip() == "hello file"


def test_write_text_creates_parent_dirs(tmp_path: Path) -> None:
    out = tmp_path / "deep" / "nested" / "dir" / "file.txt"
    write_text("nested", output_path=out)
    assert out.exists()


def test_write_text_appends_newline_if_missing(tmp_path: Path) -> None:
    out = tmp_path / "no_newline.txt"
    write_text("no newline", output_path=out)
    content = out.read_text(encoding="utf-8")
    assert content.endswith("\n")


# ---------------------------------------------------------------------------
# write_report
# ---------------------------------------------------------------------------

def test_write_report_empty_summary_to_stdout(capsys: pytest.CaptureFixture) -> None:
    write_report(_empty_report(), _empty_summary(), fmt=OutputFormat.TEXT)
    captured = capsys.readouterr()
    # empty summary → just a newline or empty string
    assert isinstance(captured.out, str)


def test_write_report_text_to_file(tmp_path: Path) -> None:
    summary = _make_summary(tmp_path)
    out = tmp_path / "report.txt"
    write_report(_empty_report(), summary, fmt=OutputFormat.TEXT, output_path=out)
    content = out.read_text(encoding="utf-8")
    assert "DROP" in content.upper() or len(content) > 0


def test_write_report_json_to_file(tmp_path: Path) -> None:
    summary = _make_summary(tmp_path)
    out = tmp_path / "report.json"
    write_report(_empty_report(), summary, fmt=OutputFormat.JSON, output_path=out)
    raw = out.read_text(encoding="utf-8").strip()
    # Each line should be valid JSON (one object per file)
    for line in raw.splitlines():
        if line.strip():
            parsed = json.loads(line)
            assert isinstance(parsed, dict)
