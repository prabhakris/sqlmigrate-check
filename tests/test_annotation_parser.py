"""Tests for sqlmigrate_check.annotation_parser."""
from __future__ import annotations

import pytest

from sqlmigrate_check.annotation_parser import (
    Annotation,
    AnnotationMap,
    parse_annotations,
)


# ---------------------------------------------------------------------------
# parse_annotations
# ---------------------------------------------------------------------------

def test_no_annotations_returns_empty_map():
    sql = "ALTER TABLE users ADD COLUMN age INT;"
    result = parse_annotations(sql)
    assert result.annotations == []


def test_single_annotation_detected():
    sql = "-- @sqlmigrate:ticket=PROJ-42\nALTER TABLE t DROP COLUMN c;"
    result = parse_annotations(sql)
    assert len(result.annotations) == 1
    ann = result.annotations[0]
    assert ann.key == "ticket"
    assert ann.value.strip() == "PROJ-42"
    assert ann.line_number == 1


def test_multiple_annotations_detected():
    sql = (
        "-- @sqlmigrate:ticket=PROJ-7\n"
        "-- @sqlmigrate:reviewed-by=alice\n"
        "DROP TABLE legacy;\n"
    )
    result = parse_annotations(sql)
    assert len(result.annotations) == 2
    keys = [a.key for a in result.annotations]
    assert "ticket" in keys
    assert "reviewed-by" in keys


def test_annotation_case_insensitive_key():
    sql = "-- @SQLMIGRATE:Ticket=PROJ-1"
    result = parse_annotations(sql)
    assert result.annotations[0].key == "ticket"


def test_annotation_line_number_is_correct():
    sql = "SELECT 1;\n-- @sqlmigrate:ticket=X\nSELECT 2;"
    result = parse_annotations(sql)
    assert result.annotations[0].line_number == 2


def test_non_annotation_comment_ignored():
    sql = "-- This is a regular comment\nSELECT 1;"
    result = parse_annotations(sql)
    assert result.annotations == []


# ---------------------------------------------------------------------------
# AnnotationMap.get
# ---------------------------------------------------------------------------

def test_get_returns_all_values_for_key():
    sql = (
        "-- @sqlmigrate:reviewed-by=alice\n"
        "-- @sqlmigrate:reviewed-by=bob\n"
    )
    amap = parse_annotations(sql)
    assert amap.get("reviewed-by") == ["alice", "bob"]


def test_get_missing_key_returns_empty_list():
    amap = AnnotationMap()
    assert amap.get("ticket") == []


# ---------------------------------------------------------------------------
# AnnotationMap.first
# ---------------------------------------------------------------------------

def test_first_returns_first_value():
    sql = "-- @sqlmigrate:ticket=PROJ-1\n-- @sqlmigrate:ticket=PROJ-2"
    amap = parse_annotations(sql)
    assert amap.first("ticket") == "PROJ-1"


def test_first_returns_default_when_missing():
    amap = AnnotationMap()
    assert amap.first("ticket", default="N/A") == "N/A"


# ---------------------------------------------------------------------------
# AnnotationMap.as_dict
# ---------------------------------------------------------------------------

def test_as_dict_groups_values_by_key():
    sql = (
        "-- @sqlmigrate:ticket=PROJ-5\n"
        "-- @sqlmigrate:reviewed-by=carol\n"
        "-- @sqlmigrate:ticket=PROJ-6\n"
    )
    amap = parse_annotations(sql)
    d = amap.as_dict()
    assert set(d["ticket"]) == {"PROJ-5", "PROJ-6"}
    assert d["reviewed-by"] == ["carol"]


def test_as_dict_empty_when_no_annotations():
    amap = AnnotationMap()
    assert amap.as_dict() == {}
