"""Tests for sqlmigrate_check.reporter."""
from __future__ import annotations

from pathlib import Path

import pytest

from sqlmigrate_check.baseline import save_baseline, build_baseline_from_results
from sqlmigrate_check.detector import DetectionResult, Issue, Severity
from sqlmigrate_check.formatter import OutputFormat
from sqlmigrate_check.pipeline import ScanSummary
from sqlmigrate_check.reporter import ReportOptions, build_report


def _make_result(path: str, *issues: Issue) -> DetectionResult:
    return DetectionResult(filepath=Path(path), issues=list(issues))


def _danger(line: int = 1) -> Issue:
    return Issue(severity=Severity.DANGER, rule="drop_table", message="DROP TABLE", line=line)


def _warning(line: int = 2) -> Issue:
    return Issue(severity=Severity.WARNING, rule="add_not_null", message="NOT NULL", line=line)


@pytest.fixture
def simple_summary() -> ScanSummary:
    results = [
        _make_result("migrations/0001.sql", _danger()),
        _make_result("migrations/0002.sql", _warning()),
    ]
    return ScanSummary(results=results)


def test_build_report_no_baseline(simple_summary):
    opts = ReportOptions()
    report = build_report(simple_summary, opts)
    assert len(report.filtered_results) == 2
    assert report.suppressed_count == 0
    assert report.has_danger
    assert report.has_warnings


def test_build_report_with_baseline_suppresses_known(simple_summary, tmp_path):
    baseline_file = tmp_path / ".sqlmigrate_baseline.json"
    save_baseline(baseline_file, build_baseline_from_results(simple_summary.results))

    opts = ReportOptions(baseline_path=baseline_file)
    report = build_report(simple_summary, opts)
    assert len(report.filtered_results) == 0
    assert report.suppressed_count == 2
    assert not report.has_danger
    assert not report.has_warnings


def test_build_report_partial_baseline(tmp_path):
    danger_result = _make_result("migrations/0001.sql", _danger())
    warning_result = _make_result("migrations/0002.sql", _warning())
    summary = ScanSummary(results=[danger_result, warning_result])

    baseline_file = tmp_path / ".sqlmigrate_baseline.json"
    save_baseline(baseline_file, build_baseline_from_results([danger_result]))

    opts = ReportOptions(baseline_path=baseline_file)
    report = build_report(summary, opts)
    assert report.suppressed_count == 1
    assert len(report.filtered_results) == 1
    assert report.filtered_results[0].filepath == Path("migrations/0002.sql")


def test_render_includes_suppressed_note(simple_summary, tmp_path):
    baseline_file = tmp_path / ".sqlmigrate_baseline.json"
    save_baseline(baseline_file, build_baseline_from_results([simple_summary.results[0]]))

    opts = ReportOptions(baseline_path=baseline_file, show_suppressed_count=True)
    report = build_report(simple_summary, opts)
    rendered = report.render()
    assert "suppressed" in rendered
    assert "1" in rendered


def test_render_no_suppressed_note_when_disabled(simple_summary, tmp_path):
    baseline_file = tmp_path / ".sqlmigrate_baseline.json"
    save_baseline(baseline_file, build_baseline_from_results([simple_summary.results[0]]))

    opts = ReportOptions(baseline_path=baseline_file, show_suppressed_count=False)
    report = build_report(simple_summary, opts)
    rendered = report.render()
    assert "suppressed" not in rendered


def test_render_empty_summary_returns_empty():
    summary = ScanSummary(results=[])
    opts = ReportOptions(output_format=OutputFormat.TEXT)
    report = build_report(summary, opts)
    assert report.render().strip() == ""
