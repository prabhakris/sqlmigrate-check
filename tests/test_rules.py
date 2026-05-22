"""Tests for built-in SQL migration detection rules."""

import pytest

from sqlmigrate_check.detector import Severity
from sqlmigrate_check.rules import (
    ALL_RULES,
    check_add_not_null_without_default,
    check_drop_column,
    check_drop_table,
    check_full_table_lock,
    check_rename_table,
    check_truncate,
)


def test_drop_table_detected():
    issues = check_drop_table("DROP TABLE users;")
    assert len(issues) == 1
    assert issues[0].severity == Severity.DANGER
    assert issues[0].code == "E001"
    assert issues[0].line == 1


def test_drop_table_case_insensitive():
    issues = check_drop_table("drop table orders;")
    assert len(issues) == 1


def test_drop_column_detected():
    issues = check_drop_column("ALTER TABLE users DROP COLUMN email;")
    assert len(issues) == 1
    assert issues[0].severity == Severity.DANGER
    assert issues[0].code == "E002"


def test_truncate_detected():
    issues = check_truncate("TRUNCATE TABLE logs;")
    assert len(issues) == 1
    assert issues[0].severity == Severity.DANGER
    assert issues[0].code == "E003"


def test_add_not_null_without_default_detected():
    sql = "ALTER TABLE users ADD COLUMN age INTEGER NOT NULL;"
    issues = check_add_not_null_without_default(sql)
    assert len(issues) == 1
    assert issues[0].severity == Severity.DANGER
    assert issues[0].code == "E004"


def test_add_not_null_with_default_is_safe():
    sql = "ALTER TABLE users ADD COLUMN age INTEGER NOT NULL DEFAULT 0;"
    issues = check_add_not_null_without_default(sql)
    assert issues == []


def test_full_table_lock_is_warning():
    issues = check_full_table_lock("LOCK TABLE payments IN EXCLUSIVE MODE;")
    assert len(issues) == 1
    assert issues[0].severity == Severity.WARNING
    assert issues[0].code == "W001"


def test_rename_table_alter_syntax():
    issues = check_rename_table("ALTER TABLE old_name RENAME TO new_name;")
    assert len(issues) == 1
    assert issues[0].severity == Severity.WARNING
    assert issues[0].code == "W002"


def test_rename_table_rename_syntax():
    issues = check_rename_table("RENAME TABLE old_name TO new_name;")
    assert len(issues) == 1
    assert issues[0].code == "W002"


def test_no_issues_for_safe_sql():
    sql = "ALTER TABLE users ADD COLUMN nickname VARCHAR(50) DEFAULT '';"
    for rule in ALL_RULES:
        assert rule(sql) == [], f"Rule {rule.__name__} falsely flagged safe SQL"


def test_multiple_issues_in_one_statement():
    sql = "DROP TABLE a;\nDROP TABLE b;\n"
    issues = check_drop_table(sql)
    assert len(issues) == 2
    assert issues[0].line == 1
    assert issues[1].line == 2


def test_all_rules_list_is_complete():
    assert len(ALL_RULES) == 6
