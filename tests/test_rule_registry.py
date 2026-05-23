"""Tests for the central rule registry."""
from __future__ import annotations

import pytest

import sqlmigrate_check.rule_registry as registry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dummy_rule(sql: str, filepath: str):
    return []


@pytest.fixture(autouse=True)
def isolated_registry():
    """Save and restore registry state around each test."""
    snapshot = dict(registry._REGISTRY)
    yield
    registry._REGISTRY.clear()
    registry._REGISTRY.update(snapshot)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_register_adds_entry():
    registry.register("test-rule", "A test rule")(lambda sql, fp: [])
    assert registry.is_registered("test-rule")


def test_get_returns_entry():
    registry.register("get-rule", "desc")(_dummy_rule)
    entry = registry.get("get-rule")
    assert entry is not None
    assert entry.rule_id == "get-rule"
    assert entry.description == "desc"
    assert entry.func is _dummy_rule


def test_get_missing_rule_returns_none():
    assert registry.get("no-such-rule") is None


def test_default_severity_is_danger():
    registry.register("sev-rule", "desc")(_dummy_rule)
    assert registry.get("sev-rule").severity_default == "danger"


def test_custom_severity_stored():
    registry.register("warn-rule", "desc", severity_default="warning")(_dummy_rule)
    assert registry.get("warn-rule").severity_default == "warning"


def test_all_rules_returns_list():
    registry.register("r1", "d1")(_dummy_rule)
    registry.register("r2", "d2")(_dummy_rule)
    ids = registry.all_rule_ids()
    assert "r1" in ids
    assert "r2" in ids


def test_all_rules_preserves_insertion_order():
    for i in range(5):
        registry.register(f"ord-{i}", "d")(_dummy_rule)
    ids = registry.all_rule_ids()
    ord_ids = [i for i in ids if i.startswith("ord-")]
    assert ord_ids == [f"ord-{i}" for i in range(5)]


def test_register_decorator_returns_original_function():
    result = registry.register("ret-rule", "desc")(_dummy_rule)
    assert result is _dummy_rule


def test_rules_registration_populates_builtin_rules():
    import sqlmigrate_check.rules_registration  # noqa: F401 – side-effect import
    builtin_ids = registry.all_rule_ids()
    for expected in ["drop-table", "drop-column", "truncate", "add-not-null-without-default", "rename-table"]:
        assert expected in builtin_ids
