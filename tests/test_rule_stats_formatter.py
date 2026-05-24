"""Tests for rule_stats_formatter module."""
from __future__ import annotations

import json

import pytest

from sqlmigrate_check.rule_stats import RuleStat
from sqlmigrate_check.rule_stats_formatter import (
    _stat_to_dict,
    format_stats_text,
    format_stats_json,
)


@pytest.fixture()
def sample_stats():
    return {
        "drop_table": RuleStat(
            rule_id="drop_table",
            danger_count=3,
            warning_count=0,
            affected_files=["b.sql", "a.sql"],
        ),
        "add_not_null": RuleStat(
            rule_id="add_not_null",
            danger_count=0,
            warning_count=2,
            affected_files=["c.sql"],
        ),
    }


def test_stat_to_dict_keys(sample_stats):
    d = _stat_to_dict(sample_stats["drop_table"])
    assert set(d.keys()) == {
        "rule_id", "total", "danger_count", "warning_count",
        "affected_files", "highest_severity",
    }


def test_stat_to_dict_affected_files_sorted(sample_stats):
    d = _stat_to_dict(sample_stats["drop_table"])
    assert d["affected_files"] == ["a.sql", "b.sql"]


def test_format_stats_text_no_stats():
    result = format_stats_text({})
    assert "No rule hits" in result


def test_format_stats_text_contains_rule_ids(sample_stats):
    result = format_stats_text(sample_stats)
    assert "drop_table" in result
    assert "add_not_null" in result


def test_format_stats_text_danger_appears_before_warning(sample_stats):
    result = format_stats_text(sample_stats)
    idx_drop = result.index("drop_table")
    idx_add = result.index("add_not_null")
    assert idx_drop < idx_add


def test_format_stats_json_valid(sample_stats):
    raw = format_stats_json(sample_stats)
    parsed = json.loads(raw)
    assert "rule_stats" in parsed
    assert isinstance(parsed["rule_stats"], list)


def test_format_stats_json_rule_ids_present(sample_stats):
    parsed = json.loads(format_stats_json(sample_stats))
    ids = [r["rule_id"] for r in parsed["rule_stats"]]
    assert "drop_table" in ids
    assert "add_not_null" in ids


def test_format_stats_json_empty():
    parsed = json.loads(format_stats_json({}))
    assert parsed["rule_stats"] == []
