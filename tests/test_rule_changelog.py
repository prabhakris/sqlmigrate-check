"""Tests for rule_changelog and rule_changelog_formatter."""
import json

import pytest

from sqlmigrate_check.rule_changelog import (
    ChangelogEntry,
    RuleChangelog,
    all_changelogs,
    get_changelog,
)
from sqlmigrate_check.rule_changelog_formatter import (
    format_all_changelogs_json,
    format_all_changelogs_text,
    format_changelog_for_rule,
    format_changelog_json,
    format_changelog_text,
)


def test_get_changelog_known_rule_returns_object():
    cl = get_changelog("drop-table")
    assert cl is not None
    assert cl.rule_id == "drop-table"


def test_get_changelog_unknown_rule_returns_none():
    assert get_changelog("nonexistent-rule") is None


def test_all_changelogs_returns_list():
    changelogs = all_changelogs()
    assert isinstance(changelogs, list)
    assert len(changelogs) >= 4


def test_changelog_latest_returns_first_entry():
    cl = get_changelog("drop-table")
    assert cl is not None
    latest = cl.latest()
    assert latest is not None
    assert latest.version == "1.1.0"


def test_changelog_latest_empty_returns_none():
    cl = RuleChangelog(rule_id="empty-rule", entries=[])
    assert cl.latest() is None


def test_has_breaking_changes_true():
    cl = get_changelog("truncate")
    assert cl is not None
    assert cl.has_breaking_changes() is True


def test_has_breaking_changes_false():
    cl = get_changelog("drop-column")
    assert cl is not None
    assert cl.has_breaking_changes() is False


def test_changelog_to_dict_structure():
    cl = get_changelog("drop-table")
    assert cl is not None
    d = cl.to_dict()
    assert "rule_id" in d
    assert "entries" in d
    assert "has_breaking_changes" in d
    assert isinstance(d["entries"], list)


def test_entry_to_dict_keys():
    entry = ChangelogEntry(version="1.0.0", description="Initial.", breaking=True)
    d = entry.to_dict()
    assert d["version"] == "1.0.0"
    assert d["description"] == "Initial."
    assert d["breaking"] is True


def test_format_changelog_text_contains_rule_id():
    cl = get_changelog("drop-table")
    assert cl is not None
    text = format_changelog_text(cl)
    assert "drop-table" in text


def test_format_changelog_text_breaking_tag():
    cl = get_changelog("truncate")
    assert cl is not None
    text = format_changelog_text(cl)
    assert "[BREAKING]" in text


def test_format_changelog_text_empty_entries():
    cl = RuleChangelog(rule_id="empty", entries=[])
    text = format_changelog_text(cl)
    assert "(no entries)" in text


def test_format_changelog_json_valid():
    cl = get_changelog("drop-table")
    assert cl is not None
    parsed = json.loads(format_changelog_json(cl))
    assert parsed["rule_id"] == "drop-table"


def test_format_all_changelogs_text_contains_all_rules():
    text = format_all_changelogs_text()
    for rule_id in ("drop-table", "drop-column", "truncate", "add-not-null-without-default"):
        assert rule_id in text


def test_format_all_changelogs_json_is_list():
    parsed = json.loads(format_all_changelogs_json())
    assert isinstance(parsed, list)
    assert len(parsed) >= 4


def test_format_changelog_for_rule_text():
    result = format_changelog_for_rule("drop-table", fmt="text")
    assert "drop-table" in result


def test_format_changelog_for_rule_json():
    result = format_changelog_for_rule("truncate", fmt="json")
    parsed = json.loads(result)
    assert parsed["rule_id"] == "truncate"


def test_format_changelog_for_unknown_rule_text():
    result = format_changelog_for_rule("unknown", fmt="text")
    assert "No changelog found" in result


def test_format_changelog_for_unknown_rule_json():
    result = format_changelog_for_rule("unknown", fmt="json")
    parsed = json.loads(result)
    assert "error" in parsed
