"""Tests for sqlmigrate_check.rule_tag."""
from __future__ import annotations

import pytest

from sqlmigrate_check.detector import Issue, Severity
from sqlmigrate_check.rule_tag import (
    TagFilterResult,
    all_tags,
    filter_issues_by_tag,
    rules_with_tag,
    tags_for_rule,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _issue(rule_id: str, severity: Severity = Severity.DANGER) -> Issue:
    return Issue(
        rule_id=rule_id,
        severity=severity,
        message=f"{rule_id} issue",
        filepath="migration.sql",
        line_number=1,
    )


# ---------------------------------------------------------------------------
# tags_for_rule
# ---------------------------------------------------------------------------

def test_tags_for_known_rule_returns_nonempty_set():
    tags = tags_for_rule("drop_table")
    assert len(tags) > 0


def test_tags_for_drop_table_contains_destructive():
    assert "destructive" in tags_for_rule("drop_table")


def test_tags_for_drop_table_contains_data_loss():
    assert "data-loss" in tags_for_rule("drop_table")


def test_tags_for_unknown_rule_returns_empty():
    assert tags_for_rule("nonexistent_rule") == frozenset()


def test_tags_for_add_not_null_contains_locking():
    assert "locking" in tags_for_rule("add_not_null_without_default")


# ---------------------------------------------------------------------------
# all_tags
# ---------------------------------------------------------------------------

def test_all_tags_contains_destructive():
    assert "destructive" in all_tags()


def test_all_tags_contains_locking():
    assert "locking" in all_tags()


def test_all_tags_is_frozenset():
    assert isinstance(all_tags(), frozenset)


# ---------------------------------------------------------------------------
# rules_with_tag
# ---------------------------------------------------------------------------

def test_rules_with_destructive_tag_includes_drop_table():
    assert "drop_table" in rules_with_tag("destructive")


def test_rules_with_destructive_tag_includes_drop_column():
    assert "drop_column" in rules_with_tag("destructive")


def test_rules_with_locking_tag_includes_add_not_null():
    assert "add_not_null_without_default" in rules_with_tag("locking")


def test_rules_with_unknown_tag_returns_empty():
    assert rules_with_tag("totally_unknown_tag_xyz") == []


def test_rules_with_tag_returns_sorted_list():
    result = rules_with_tag("destructive")
    assert result == sorted(result)


# ---------------------------------------------------------------------------
# filter_issues_by_tag
# ---------------------------------------------------------------------------

def test_filter_matches_issue_with_matching_tag():
    issue = _issue("drop_table")
    result = filter_issues_by_tag([issue], ["destructive"])
    assert issue in result.matched
    assert issue not in result.unmatched


def test_filter_unmatched_issue_with_no_tag_overlap():
    issue = _issue("drop_table")
    result = filter_issues_by_tag([issue], ["locking"])
    assert issue not in result.matched
    assert issue in result.unmatched


def test_filter_empty_issues_returns_empty_result():
    result = filter_issues_by_tag([], ["destructive"])
    assert result.total_matched == 0
    assert result.unmatched == []


def test_filter_multiple_tags_uses_any_match():
    issue = _issue("add_not_null_without_default")
    result = filter_issues_by_tag([issue], ["destructive", "locking"])
    assert issue in result.matched


def test_filter_total_matched_counts_correctly():
    issues = [_issue("drop_table"), _issue("drop_column"), _issue("add_not_null_without_default")]
    result = filter_issues_by_tag(issues, ["data-loss"])
    assert result.total_matched == 2
