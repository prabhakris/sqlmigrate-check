"""Tests for sqlmigrate_check.scanner."""

from pathlib import Path

import pytest

from sqlmigrate_check.scanner import (
    collect_sql_from_file,
    iter_migration_files,
    read_migration_file,
)


# ---------------------------------------------------------------------------
# iter_migration_files
# ---------------------------------------------------------------------------

def test_iter_migration_files_single_sql_file(tmp_path):
    f = tmp_path / "001_create.sql"
    f.write_text("SELECT 1;")
    found = list(iter_migration_files([str(f)]))
    assert found == [f]


def test_iter_migration_files_directory(tmp_path):
    (tmp_path / "a.sql").write_text("SELECT 1;")
    (tmp_path / "b.sql").write_text("SELECT 2;")
    (tmp_path / "readme.md").write_text("# docs")
    found = list(iter_migration_files([str(tmp_path)]))
    assert len(found) == 2
    assert all(p.suffix == ".sql" for p in found)


def test_iter_migration_files_recursive(tmp_path):
    sub = tmp_path / "migrations"
    sub.mkdir()
    (sub / "001.sql").write_text("SELECT 1;")
    found = list(iter_migration_files([str(tmp_path)], recursive=True))
    assert len(found) == 1


def test_iter_migration_files_non_recursive(tmp_path):
    sub = tmp_path / "migrations"
    sub.mkdir()
    (sub / "001.sql").write_text("SELECT 1;")
    found = list(iter_migration_files([str(tmp_path)], recursive=False))
    assert len(found) == 0


# ---------------------------------------------------------------------------
# read_migration_file
# ---------------------------------------------------------------------------

def test_read_migration_file_returns_content(tmp_path):
    f = tmp_path / "migration.sql"
    f.write_text("DROP TABLE users;")
    assert read_migration_file(f) == "DROP TABLE users;"


def test_read_migration_file_missing_raises(tmp_path):
    with pytest.raises(RuntimeError, match="Cannot read"):
        read_migration_file(tmp_path / "nonexistent.sql")


# ---------------------------------------------------------------------------
# collect_sql_from_file
# ---------------------------------------------------------------------------

def test_collect_sql_from_sql_file(tmp_path):
    f = tmp_path / "drop.sql"
    f.write_text("DROP TABLE orders;")
    assert collect_sql_from_file(f) == "DROP TABLE orders;"


def test_collect_sql_from_python_file(tmp_path):
    f = tmp_path / "0001_migration.py"
    f.write_text('op.execute("DROP TABLE legacy")\n')
    sql = collect_sql_from_file(f)
    assert "DROP TABLE legacy" in sql
