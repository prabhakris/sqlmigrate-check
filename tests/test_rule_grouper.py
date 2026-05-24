"""Tests for rule_grouper and rule_grouper_formatter."""
import json

import pytest

from sqlmigrate_check.detector import Issue, Severity
from sqlmigrate_check.rule_grouper import RuleGroup, group_by_rule, sorted_groups
from sqlmigrate_check.rule_grouper_formatter import format_groups_json, format_groups_text


def _issue(rule_id: str, severity: Severity = Severity.DANGER, filepath: str = "a.sql", line: int = 1) -> Issue:
    return Issue(rule_id=rule_id, severity=severity, message="msg", filepath=filepath, line_number=line)


# --- group_by_rule ---

def test_group_by_rule_empty_input():
    assert group_by_rule([]) == {}


def test_group_by_rule_single_issue():
    issues = [_issue("drop_table")]
    groups = group_by_rule(issues)
    assert "drop_table" in groups
    assert groups["drop_table"].count == 1


def test_group_by_rule_multiple_same_rule():
    issues = [_issue("drop_table"), _issue("drop_table", filepath="b.sql")]
    groups = group_by_rule(issues)
    assert groups["drop_table"].count == 2


def test_group_by_rule_multiple_rules():
    issues = [_issue("drop_table"), _issue("truncate")]
    groups = group_by_rule(issues)
    assert set(groups.keys()) == {"drop_table", "truncate"}


# --- RuleGroup properties ---

def test_rule_group_highest_severity_danger():
    g = RuleGroup(rule_id="r", issues=[_issue("r", Severity.WARNING), _issue("r", Severity.DANGER)])
    assert g.highest_severity == Severity.DANGER


def test_rule_group_highest_severity_warning_when_no_danger():
    g = RuleGroup(rule_id="r", issues=[_issue("r", Severity.WARNING)])
    assert g.highest_severity == Severity.WARNING


def test_rule_group_affected_files_deduped_and_sorted():
    issues = [_issue("r", filepath="b.sql"), _issue("r", filepath="a.sql"), _issue("r", filepath="a.sql")]
    g = RuleGroup(rule_id="r", issues=issues)
    assert g.affected_files == ["a.sql", "b.sql"]


# --- sorted_groups ---

def test_sorted_groups_danger_before_warning():
    groups = {
        "warn_rule": RuleGroup(rule_id="warn_rule", issues=[_issue("warn_rule", Severity.WARNING)]),
        "danger_rule": RuleGroup(rule_id="danger_rule", issues=[_issue("danger_rule", Severity.DANGER)]),
    }
    ordered = sorted_groups(groups)
    assert ordered[0].rule_id == "danger_rule"


def test_sorted_groups_higher_count_first_within_same_severity():
    groups = {
        "a": RuleGroup(rule_id="a", issues=[_issue("a"), _issue("a")]),
        "b": RuleGroup(rule_id="b", issues=[_issue("b")]),
    }
    ordered = sorted_groups(groups)
    assert ordered[0].rule_id == "a"


# --- formatters ---

def test_format_groups_text_empty():
    result = format_groups_text({})
    assert "No issues" in result


def test_format_groups_text_contains_rule_id():
    groups = group_by_rule([_issue("drop_table")])
    text = format_groups_text(groups)
    assert "drop_table" in text
    assert "DANGER" in text


def test_format_groups_json_valid_structure():
    groups = group_by_rule([_issue("truncate", Severity.WARNING, filepath="m.sql")])
    raw = format_groups_json(groups)
    data = json.loads(raw)
    assert isinstance(data, list)
    assert data[0]["rule_id"] == "truncate"
    assert data[0]["count"] == 1
    assert "m.sql" in data[0]["affected_files"]


def test_format_groups_json_empty():
    raw = format_groups_json({})
    assert json.loads(raw) == []
