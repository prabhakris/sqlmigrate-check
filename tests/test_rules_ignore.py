"""Integration tests: rules must respect inline ignore comments."""
from sqlmigrate_check.rules import (
    check_drop_column,
    check_drop_table,
    check_rename_column,
    check_rename_table,
    check_truncate,
)


def test_drop_table_inline_ignore_suppresses_issue():
    sql = "DROP TABLE users; -- sqlmigrate-check: ignore"
    assert check_drop_table(sql) == []


def test_drop_table_ignore_next_line_suppresses_issue():
    sql = "-- sqlmigrate-check: ignore-next-line\nDROP TABLE users;"
    assert check_drop_table(sql) == []


def test_drop_table_no_ignore_still_detected():
    sql = "DROP TABLE users;"
    issues = check_drop_table(sql)
    assert len(issues) == 1


def test_drop_column_inline_ignore_suppresses():
    sql = "ALTER TABLE t DROP COLUMN c; -- sqlmigrate-check: ignore"
    assert check_drop_column(sql) == []


def test_truncate_inline_ignore_suppresses():
    sql = "TRUNCATE orders; -- sqlmigrate-check: ignore"
    assert check_truncate(sql) == []


def test_rename_table_ignore_next_line():
    sql = "-- sqlmigrate-check: ignore-next-line\nALTER TABLE a RENAME TO b;"
    assert check_rename_table(sql) == []


def test_rename_column_inline_ignore():
    sql = "ALTER TABLE t RENAME COLUMN old TO new; -- sqlmigrate-check: ignore"
    assert check_rename_column(sql) == []


def test_only_matching_line_suppressed():
    """Ignore on line 1 must not suppress a different issue on line 2."""
    sql = (
        "DROP TABLE a; -- sqlmigrate-check: ignore\n"
        "DROP TABLE b;"
    )
    issues = check_drop_table(sql)
    assert len(issues) == 1
    assert issues[0].line == 2
