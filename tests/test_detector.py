"""Tests for sqlmigrate_check.detector."""

import pytest

from sqlmigrate_check.detector import Severity, detect


# ---------------------------------------------------------------------------
# Dangerous operations
# ---------------------------------------------------------------------------

def test_drop_table_is_danger():
    result = detect("DROP TABLE users;")
    assert result.has_danger
    assert any("DROP TABLE" in i.message for i in result.issues)


def test_drop_column_is_danger():
    result = detect("ALTER TABLE orders DROP COLUMN legacy_id;")
    assert result.has_danger


def test_truncate_is_danger():
    result = detect("TRUNCATE TABLE sessions;")
    assert result.has_danger


def test_add_not_null_column_without_default_is_danger():
    result = detect("ALTER TABLE users ADD COLUMN verified BOOLEAN NOT NULL;")
    assert result.has_danger


def test_add_not_null_column_with_default_is_safe():
    result = detect(
        "ALTER TABLE users ADD COLUMN verified BOOLEAN NOT NULL DEFAULT FALSE;"
    )
    # Should NOT trigger the NOT NULL danger rule
    danger_msgs = [i.message for i in result.issues if i.severity == Severity.DANGER]
    assert not any("NOT NULL" in m for m in danger_msgs)


# ---------------------------------------------------------------------------
# Warning operations
# ---------------------------------------------------------------------------

def test_alter_column_type_is_warning():
    result = detect("ALTER TABLE products ALTER COLUMN price TYPE NUMERIC(12,4);")
    assert result.has_issues
    assert any(i.severity == Severity.WARNING for i in result.issues)


def test_create_index_without_concurrently_is_warning():
    result = detect("CREATE INDEX idx_email ON users (email);")
    assert result.has_issues
    assert any(i.severity == Severity.WARNING for i in result.issues)


def test_create_index_concurrently_is_safe():
    result = detect("CREATE INDEX CONCURRENTLY idx_email ON users (email);")
    warning_msgs = [i.message for i in result.issues if i.severity == Severity.WARNING]
    assert not any("CONCURRENTLY" in m or "locks" in m for m in warning_msgs)


def test_drop_index_without_concurrently_is_warning():
    result = detect("DROP INDEX idx_email;")
    assert any(i.severity == Severity.WARNING for i in result.issues)


# ---------------------------------------------------------------------------
# Clean migrations
# ---------------------------------------------------------------------------

def test_safe_migration_has_no_issues():
    sql = """
    CREATE TABLE IF NOT EXISTS audit_log (
        id SERIAL PRIMARY KEY,
        event TEXT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    result = detect(sql)
    assert not result.has_issues


def test_comments_are_ignored():
    result = detect("-- DROP TABLE users;")
    assert not result.has_issues


def test_issue_str_representation():
    result = detect("DROP TABLE users;")
    assert len(result.issues) == 1
    text = str(result.issues[0])
    assert "DANGER" in text.upper()
    assert "Line 1" in text
