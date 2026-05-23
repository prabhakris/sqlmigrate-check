"""Tests for sqlmigrate_check.profiler and sqlmigrate_check.profiler_formatter."""
import json
import pytest

from sqlmigrate_check.profiler import RuleProfile, ScanProfiler
from sqlmigrate_check.profiler_formatter import (
    format_profiler,
    format_profiler_json,
    format_profiler_text,
)


# ---------------------------------------------------------------------------
# RuleProfile
# ---------------------------------------------------------------------------

def test_rule_profile_avg_zero_when_no_calls():
    p = RuleProfile(rule_id="drop_table")
    assert p.avg_elapsed_ms == 0.0


def test_rule_profile_avg_computed_correctly():
    p = RuleProfile(rule_id="drop_table", total_calls=4, total_elapsed_ms=8.0)
    assert p.avg_elapsed_ms == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# ScanProfiler – basic recording
# ---------------------------------------------------------------------------

def test_profile_rule_increments_call_count():
    sp = ScanProfiler()
    with sp.profile_rule("drop_table"):
        pass
    profiles = sp.all_profiles()
    assert len(profiles) == 1
    assert profiles[0].total_calls == 1


def test_profile_rule_accumulates_multiple_calls():
    sp = ScanProfiler()
    for _ in range(3):
        with sp.profile_rule("truncate"):
            pass
    assert sp.all_profiles()[0].total_calls == 3


def test_record_hit_increments_hit_count():
    sp = ScanProfiler()
    with sp.profile_rule("drop_column"):
        pass
    sp.record_hit("drop_column")
    sp.record_hit("drop_column")
    assert sp.all_profiles()[0].hit_count == 2


def test_multiple_rules_tracked_independently():
    sp = ScanProfiler()
    with sp.profile_rule("drop_table"):
        pass
    with sp.profile_rule("truncate"):
        pass
    rule_ids = {p.rule_id for p in sp.all_profiles()}
    assert rule_ids == {"drop_table", "truncate"}


# ---------------------------------------------------------------------------
# ScanProfiler – sorting
# ---------------------------------------------------------------------------

def test_sorted_by_hits_descending():
    sp = ScanProfiler()
    sp._get_or_create("a").hit_count = 1
    sp._get_or_create("b").hit_count = 5
    sp._get_or_create("c").hit_count = 3
    ordered = [p.rule_id for p in sp.sorted_by_hits()]
    assert ordered == ["b", "c", "a"]


def test_to_dict_contains_expected_keys():
    sp = ScanProfiler()
    with sp.profile_rule("drop_table"):
        pass
    d = sp.to_dict()
    assert "drop_table" in d
    assert set(d["drop_table"].keys()) == {
        "total_calls", "total_elapsed_ms", "avg_elapsed_ms", "hit_count"
    }


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def test_format_profiler_text_empty():
    sp = ScanProfiler()
    result = format_profiler_text(sp)
    assert result == "No profiling data collected."


def test_format_profiler_text_contains_rule_id():
    sp = ScanProfiler()
    with sp.profile_rule("drop_table"):
        pass
    result = format_profiler_text(sp)
    assert "drop_table" in result


def test_format_profiler_json_valid():
    sp = ScanProfiler()
    with sp.profile_rule("truncate"):
        pass
    data = json.loads(format_profiler_json(sp))
    assert "rule_profiles" in data
    assert "truncate" in data["rule_profiles"]


def test_format_profiler_dispatch_json():
    sp = ScanProfiler()
    with sp.profile_rule("drop_column"):
        pass
    result = format_profiler(sp, fmt="json")
    assert result.startswith("{")


def test_format_profiler_dispatch_text_default():
    sp = ScanProfiler()
    with sp.profile_rule("drop_column"):
        pass
    result = format_profiler(sp)
    assert "drop_column" in result
