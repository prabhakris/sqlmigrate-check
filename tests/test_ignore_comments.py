"""Tests for sqlmigrate_check.ignore_comments."""
import pytest

from sqlmigrate_check.ignore_comments import ignored_lines, is_line_ignored


def test_no_comments_returns_empty_set():
    sql = "DROP TABLE users;\nALTER TABLE orders DROP COLUMN total;"
    assert ignored_lines(sql) == set()


def test_inline_ignore_marks_own_line():
    sql = "DROP TABLE users; -- sqlmigrate-check: ignore\nSELECT 1;"
    assert ignored_lines(sql) == {1}


def test_inline_ignore_case_insensitive():
    sql = "DROP TABLE users; -- SQLMIGRATE-CHECK: IGNORE"
    assert 1 in ignored_lines(sql)


def test_ignore_next_line_marks_following_line():
    sql = (
        "-- sqlmigrate-check: ignore-next-line\n"
        "DROP TABLE users;\n"
        "SELECT 1;"
    )
    result = ignored_lines(sql)
    assert 2 in result
    assert 1 not in result
    assert 3 not in result


def test_ignore_next_line_at_end_does_not_raise():
    sql = "SELECT 1;\n-- sqlmigrate-check: ignore-next-line"
    # line 3 does not exist; should return empty set for target lines
    result = ignored_lines(sql)
    assert 2 not in result  # the directive line itself is not marked


def test_multiple_ignores():
    sql = (
        "DROP TABLE a; -- sqlmigrate-check: ignore\n"
        "-- sqlmigrate-check: ignore-next-line\n"
        "DROP TABLE b;\n"
        "DROP TABLE c;"
    )
    result = ignored_lines(sql)
    assert result == {1, 3}
    assert 4 not in result


def test_is_line_ignored_true():
    sql = "DROP TABLE x; -- sqlmigrate-check: ignore"
    assert is_line_ignored(1, sql) is True


def test_is_line_ignored_false():
    sql = "DROP TABLE x;"
    assert is_line_ignored(1, sql) is False


def test_inline_ignore_extra_whitespace():
    sql = "ALTER TABLE t DROP COLUMN c;  --  sqlmigrate-check :  ignore  "
    # extra spaces around colon — should still match
    # (regex allows \s* around the colon)
    assert 1 in ignored_lines(sql)
