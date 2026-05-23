"""Tests for sqlmigrate_check.suppression_report."""
from __future__ import annotations

import pytest

from sqlmigrate_check.suppression import SuppressionSummary
from sqlmigrate_check.suppression_report import SuppressionReport


def _summary(comment: int = 0, allowlist: int = 0) -> SuppressionSummary:
    return SuppressionSummary(
        suppressed_by_comment=comment,
        suppressed_by_allowlist=allowlist,
    )


def test_empty_report_totals_are_zero():
    report = SuppressionReport()
    assert report.total_suppressed == 0
    assert report.total_suppressed_by_comment == 0
    assert report.total_suppressed_by_allowlist == 0
    assert report.files_with_suppressions == 0


def test_record_single_file():
    report = SuppressionReport()
    report.record("a.sql", _summary(comment=1, allowlist=2))
    assert report.total_suppressed == 3
    assert report.total_suppressed_by_comment == 1
    assert report.total_suppressed_by_allowlist == 2
    assert report.files_with_suppressions == 1


def test_record_multiple_files():
    report = SuppressionReport()
    report.record("a.sql", _summary(comment=1))
    report.record("b.sql", _summary(allowlist=3))
    assert report.total_suppressed == 4
    assert report.files_with_suppressions == 2


def test_record_same_file_merges():
    report = SuppressionReport()
    report.record("a.sql", _summary(comment=1, allowlist=1))
    report.record("a.sql", _summary(comment=2, allowlist=0))
    per = report.per_file()
    assert per["a.sql"].suppressed_by_comment == 3
    assert per["a.sql"].suppressed_by_allowlist == 1
    assert report.files_with_suppressions == 1


def test_files_with_suppressions_excludes_zero_files():
    report = SuppressionReport()
    report.record("a.sql", _summary(comment=0, allowlist=0))
    report.record("b.sql", _summary(comment=1))
    assert report.files_with_suppressions == 1


def test_per_file_returns_copy():
    report = SuppressionReport()
    report.record("a.sql", _summary(comment=1))
    copy = report.per_file()
    copy["extra"] = _summary()
    assert "extra" not in report.per_file()


def test_as_text_no_suppressions():
    report = SuppressionReport()
    assert report.as_text() == "No issues were suppressed."


def test_as_text_with_suppressions():
    report = SuppressionReport()
    report.record("a.sql", _summary(comment=2, allowlist=1))
    text = report.as_text()
    assert "3 issue(s)" in text
    assert "2 via comment" in text
    assert "1 via allowlist" in text
    assert "1 file(s)" in text
