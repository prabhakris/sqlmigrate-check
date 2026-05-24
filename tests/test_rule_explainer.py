"""Tests for rule_explainer and rule_explainer_formatter."""
from __future__ import annotations

import json

import pytest

from sqlmigrate_check.detector import Issue, Severity
from sqlmigrate_check.rule_explainer import (
    RuleExplanation,
    get_explanation,
    explain_issue,
    _EXPLANATIONS,
)
from sqlmigrate_check.rule_explainer_formatter import (
    format_explanation_text,
    format_explanation_json,
    format_all_explanations_text,
    format_all_explanations_json,
    format_explanation_for_rule,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def drop_table_exp() -> RuleExplanation:
    return get_explanation("drop_table")


def _make_issue(rule_id: str) -> Issue:
    return Issue(
        rule_id=rule_id,
        severity=Severity.DANGER,
        message="test",
        filepath="migration.sql",
        line_number=1,
    )


# ---------------------------------------------------------------------------
# get_explanation
# ---------------------------------------------------------------------------

def test_get_explanation_returns_object_for_known_rule(drop_table_exp):
    assert drop_table_exp is not None
    assert drop_table_exp.rule_id == "drop_table"


def test_get_explanation_returns_none_for_unknown_rule():
    assert get_explanation("nonexistent_rule") is None


def test_all_known_rules_have_explanations():
    expected = {"drop_table", "drop_column", "truncate", "add_not_null_without_default"}
    assert expected.issubset(_EXPLANATIONS.keys())


# ---------------------------------------------------------------------------
# explain_issue
# ---------------------------------------------------------------------------

def test_explain_issue_contains_rule_id():
    issue = _make_issue("drop_table")
    result = explain_issue(issue)
    assert "drop_table" in result


def test_explain_issue_contains_remediation():
    issue = _make_issue("drop_column")
    result = explain_issue(issue)
    assert "Fix" in result


def test_explain_issue_unknown_rule_returns_fallback():
    issue = _make_issue("unknown_rule")
    result = explain_issue(issue)
    assert "No detailed explanation" in result


# ---------------------------------------------------------------------------
# format_explanation_text
# ---------------------------------------------------------------------------

def test_format_explanation_text_includes_title(drop_table_exp):
    text = format_explanation_text(drop_table_exp)
    assert drop_table_exp.title in text


def test_format_explanation_text_includes_reference(drop_table_exp):
    text = format_explanation_text(drop_table_exp)
    assert "postgresql.org" in text


def test_format_explanation_text_no_reference_omits_ref_line():
    exp = get_explanation("truncate")
    text = format_explanation_text(exp)
    assert "Reference" not in text


# ---------------------------------------------------------------------------
# format_explanation_json
# ---------------------------------------------------------------------------

def test_format_explanation_json_is_valid_json(drop_table_exp):
    raw = format_explanation_json(drop_table_exp)
    data = json.loads(raw)
    assert data["rule_id"] == "drop_table"


def test_format_explanation_json_contains_remediation(drop_table_exp):
    data = json.loads(format_explanation_json(drop_table_exp))
    assert "remediation" in data
    assert len(data["remediation"]) > 0


# ---------------------------------------------------------------------------
# format_all_explanations_*
# ---------------------------------------------------------------------------

def test_format_all_explanations_text_contains_all_rules():
    text = format_all_explanations_text()
    for rule_id in _EXPLANATIONS:
        assert rule_id in text


def test_format_all_explanations_json_returns_list():
    data = json.loads(format_all_explanations_json())
    assert isinstance(data, list)
    assert len(data) == len(_EXPLANATIONS)


# ---------------------------------------------------------------------------
# format_explanation_for_rule
# ---------------------------------------------------------------------------

def test_format_explanation_for_rule_text_mode():
    result = format_explanation_for_rule("drop_column", fmt="text")
    assert "drop_column" in result


def test_format_explanation_for_rule_json_mode():
    result = format_explanation_for_rule("truncate", fmt="json")
    data = json.loads(result)
    assert data["rule_id"] == "truncate"


def test_format_explanation_for_rule_unknown_text():
    result = format_explanation_for_rule("no_such_rule", fmt="text")
    assert "Unknown rule" in result


def test_format_explanation_for_rule_unknown_json():
    result = format_explanation_for_rule("no_such_rule", fmt="json")
    data = json.loads(result)
    assert "error" in data
