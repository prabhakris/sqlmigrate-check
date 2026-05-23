"""Tests for sqlmigrate_check.allowlist."""
from __future__ import annotations

import pytest

from sqlmigrate_check.allowlist import Allowlist, allowlist_from_config, _parse_rule_list


# ---------------------------------------------------------------------------
# _parse_rule_list
# ---------------------------------------------------------------------------

def test_parse_rule_list_single():
    assert _parse_rule_list("drop-table") == {"drop-table"}


def test_parse_rule_list_multiple():
    assert _parse_rule_list("drop-table, truncate, drop-column") == {
        "drop-table", "truncate", "drop-column"
    }


def test_parse_rule_list_wildcard():
    assert _parse_rule_list("*") == {"*"}


def test_parse_rule_list_empty_string():
    assert _parse_rule_list("") == set()


# ---------------------------------------------------------------------------
# Allowlist.is_allowed
# ---------------------------------------------------------------------------

@pytest.fixture()
def allowlist() -> Allowlist:
    return allowlist_from_config({
        "migrations/legacy_*.sql": "drop-table,truncate",
        "initial.sql": "*",
    })


def test_is_allowed_matching_pattern_and_rule(allowlist):
    assert allowlist.is_allowed("migrations/legacy_001.sql", "drop-table") is True


def test_is_allowed_matching_pattern_wrong_rule(allowlist):
    assert allowlist.is_allowed("migrations/legacy_001.sql", "drop-column") is False


def test_is_allowed_wildcard_rule_allows_any(allowlist):
    assert allowlist.is_allowed("initial.sql", "drop-table") is True
    assert allowlist.is_allowed("initial.sql", "truncate") is True
    assert allowlist.is_allowed("initial.sql", "anything") is True


def test_is_allowed_no_matching_pattern(allowlist):
    assert allowlist.is_allowed("migrations/safe_001.sql", "drop-table") is False


def test_is_allowed_filename_only_match(allowlist):
    # Pattern "initial.sql" should match even with a leading path.
    assert allowlist.is_allowed("db/migrations/initial.sql", "drop-column") is True


# ---------------------------------------------------------------------------
# Allowlist.allowed_rules_for
# ---------------------------------------------------------------------------

def test_allowed_rules_for_returns_union(allowlist):
    rules = allowlist.allowed_rules_for("migrations/legacy_002.sql")
    assert rules == {"drop-table", "truncate"}


def test_allowed_rules_for_no_match_returns_empty(allowlist):
    assert allowlist.allowed_rules_for("migrations/new_001.sql") == set()


# ---------------------------------------------------------------------------
# allowlist_from_config
# ---------------------------------------------------------------------------

def test_allowlist_from_config_empty_dict():
    al = allowlist_from_config({})
    assert al.entries == {}
    assert al.is_allowed("any.sql", "drop-table") is False


def test_allowlist_from_config_preserves_all_entries():
    al = allowlist_from_config({
        "a.sql": "drop-table",
        "b.sql": "truncate",
    })
    assert len(al.entries) == 2
