"""Tests for sqlmigrate_check.rule_doc."""
import pytest

from sqlmigrate_check.rule_doc import (
    RuleDoc,
    all_docs,
    format_doc_text,
    get_doc,
)


# ---------------------------------------------------------------------------
# get_doc
# ---------------------------------------------------------------------------

def test_get_doc_returns_rule_doc_for_known_rule():
    doc = get_doc("drop-table")
    assert doc is not None
    assert isinstance(doc, RuleDoc)
    assert doc.rule_id == "drop-table"


def test_get_doc_returns_none_for_unknown_rule():
    assert get_doc("nonexistent-rule-xyz") is None


def test_get_doc_drop_column():
    doc = get_doc("drop-column")
    assert doc is not None
    assert "column" in doc.title.lower()


def test_get_doc_truncate():
    doc = get_doc("truncate")
    assert doc is not None
    assert doc.rule_id == "truncate"


def test_get_doc_add_not_null_without_default():
    doc = get_doc("add-not-null-without-default")
    assert doc is not None
    assert "NOT NULL" in doc.title


# ---------------------------------------------------------------------------
# all_docs
# ---------------------------------------------------------------------------

def test_all_docs_returns_dict():
    docs = all_docs()
    assert isinstance(docs, dict)


def test_all_docs_contains_known_rules():
    docs = all_docs()
    for rule_id in ("drop-table", "drop-column", "truncate", "add-not-null-without-default"):
        assert rule_id in docs


def test_all_docs_returns_copy():
    docs1 = all_docs()
    docs1["injected"] = None  # type: ignore[assignment]
    docs2 = all_docs()
    assert "injected" not in docs2


# ---------------------------------------------------------------------------
# RuleDoc.to_dict
# ---------------------------------------------------------------------------

def test_to_dict_contains_required_keys():
    doc = get_doc("drop-table")
    assert doc is not None
    d = doc.to_dict()
    assert set(d.keys()) == {"rule_id", "title", "description", "remediation", "references"}


def test_to_dict_references_is_list():
    doc = get_doc("drop-table")
    assert doc is not None
    assert isinstance(doc.to_dict()["references"], list)


def test_to_dict_no_references_is_empty_list():
    doc = get_doc("truncate")
    assert doc is not None
    assert doc.to_dict()["references"] == []


# ---------------------------------------------------------------------------
# format_doc_text
# ---------------------------------------------------------------------------

def test_format_doc_text_includes_rule_id():
    doc = get_doc("drop-table")
    assert doc is not None
    text = format_doc_text(doc)
    assert "drop-table" in text


def test_format_doc_text_includes_remediation():
    doc = get_doc("drop-column")
    assert doc is not None
    text = format_doc_text(doc)
    assert "Remediation" in text


def test_format_doc_text_includes_references_when_present():
    doc = get_doc("drop-table")
    assert doc is not None
    text = format_doc_text(doc)
    assert "References" in text
    assert "postgresql.org" in text


def test_format_doc_text_no_references_section_when_empty():
    doc = get_doc("truncate")
    assert doc is not None
    text = format_doc_text(doc)
    assert "References" not in text
