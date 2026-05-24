"""Tests for sqlmigrate_check.annotation_report."""
from __future__ import annotations

import pytest

from sqlmigrate_check.detector import DetectionResult
from sqlmigrate_check.annotation_report import (
    AnnotatedResult,
    AnnotationScanReport,
    annotate_result,
    build_annotation_report,
)


def _result(filepath: str = "migrations/0001.sql") -> DetectionResult:
    return DetectionResult(filepath=filepath, issues=[])


SQL_WITH_TICKET = "-- @sqlmigrate:ticket=PROJ-99\nALTER TABLE t ADD COLUMN x INT;"
SQL_WITH_REVIEWER = "-- @sqlmigrate:reviewed-by=alice\nSELECT 1;"
SQL_PLAIN = "SELECT 1;"


# ---------------------------------------------------------------------------
# annotate_result
# ---------------------------------------------------------------------------

def test_annotate_result_filepath_preserved():
    ar = annotate_result(_result("migrations/abc.sql"), SQL_PLAIN)
    assert ar.filepath == "migrations/abc.sql"


def test_annotate_result_ticket_extracted():
    ar = annotate_result(_result(), SQL_WITH_TICKET)
    assert ar.ticket == "PROJ-99"


def test_annotate_result_no_ticket_returns_empty_string():
    ar = annotate_result(_result(), SQL_PLAIN)
    assert ar.ticket == ""


def test_annotate_result_reviewed_by():
    ar = annotate_result(_result(), SQL_WITH_REVIEWER)
    assert ar.reviewed_by == ["alice"]


def test_annotate_result_has_annotation_true():
    ar = annotate_result(_result(), SQL_WITH_TICKET)
    assert ar.has_annotation("ticket") is True


def test_annotate_result_has_annotation_false():
    ar = annotate_result(_result(), SQL_PLAIN)
    assert ar.has_annotation("ticket") is False


# ---------------------------------------------------------------------------
# AnnotationScanReport
# ---------------------------------------------------------------------------

def test_report_total_files():
    pairs = [
        (_result("a.sql"), SQL_WITH_TICKET),
        (_result("b.sql"), SQL_PLAIN),
    ]
    report = build_annotation_report(pairs)
    assert report.total_files == 2


def test_report_files_with_ticket_count():
    pairs = [
        (_result("a.sql"), SQL_WITH_TICKET),
        (_result("b.sql"), SQL_PLAIN),
    ]
    report = build_annotation_report(pairs)
    assert report.files_with_ticket == 1


def test_report_files_without_ticket_lists_filepath():
    pairs = [
        (_result("a.sql"), SQL_WITH_TICKET),
        (_result("b.sql"), SQL_PLAIN),
    ]
    report = build_annotation_report(pairs)
    assert report.files_without_ticket == ["b.sql"]


def test_report_tickets_mapping():
    pairs = [
        (_result("a.sql"), SQL_WITH_TICKET),
        (_result("b.sql"), "-- @sqlmigrate:ticket=PROJ-99\nSELECT 2;"),
        (_result("c.sql"), "-- @sqlmigrate:ticket=PROJ-1\nSELECT 3;"),
    ]
    report = build_annotation_report(pairs)
    tickets = report.tickets()
    assert set(tickets["PROJ-99"]) == {"a.sql", "b.sql"}
    assert tickets["PROJ-1"] == ["c.sql"]


def test_empty_report():
    report = build_annotation_report([])
    assert report.total_files == 0
    assert report.files_with_ticket == 0
    assert report.files_without_ticket == []
    assert report.tickets() == {}
