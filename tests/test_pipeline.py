"""Tests for sqlmigrate_check.pipeline."""

from pathlib import Path

import pytest

from sqlmigrate_check.pipeline import run_pipeline, ScanSummary


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_run_pipeline_no_files(tmp_path):
    summary = run_pipeline([str(tmp_path)])
    assert summary.total_files == 0
    assert not summary.has_danger


def test_run_pipeline_safe_migration(tmp_path):
    _write(tmp_path, "safe.sql", "CREATE INDEX idx_email ON users(email);")
    summary = run_pipeline([str(tmp_path)])
    assert summary.total_files == 1
    assert not summary.has_danger
    assert not summary.has_warnings


def test_run_pipeline_dangerous_migration(tmp_path):
    _write(tmp_path, "danger.sql", "DROP TABLE users;")
    summary = run_pipeline([str(tmp_path)])
    assert summary.has_danger
    assert summary.files_with_issues == 1


def test_run_pipeline_multiple_files(tmp_path):
    _write(tmp_path, "ok.sql", "SELECT 1;")
    _write(tmp_path, "bad.sql", "TRUNCATE TABLE logs;")
    summary = run_pipeline([str(tmp_path)])
    assert summary.total_files == 2
    assert summary.files_with_issues == 1


def test_run_pipeline_skips_empty_sql(tmp_path):
    _write(tmp_path, "empty.sql", "   ")
    summary = run_pipeline([str(tmp_path)])
    assert summary.total_files == 0


def test_run_pipeline_direct_file_path(tmp_path):
    f = _write(tmp_path, "migration.sql", "DROP COLUMN email;")
    summary = run_pipeline([str(f)])
    assert summary.total_files == 1


def test_scan_summary_has_warnings(tmp_path):
    _write(tmp_path, "warn.sql", "ALTER TABLE t ADD COLUMN c TEXT NOT NULL;")
    summary = run_pipeline([str(tmp_path)])
    assert isinstance(summary, ScanSummary)
