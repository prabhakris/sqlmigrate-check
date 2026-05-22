"""Orchestration pipeline: scan files -> detect issues -> return results."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from sqlmigrate_check.detector import DetectionResult, detect
from sqlmigrate_check.scanner import collect_sql_from_file, iter_migration_files


@dataclass
class ScanSummary:
    """Aggregate result of scanning multiple migration files."""

    results: Dict[str, DetectionResult] = field(default_factory=dict)

    @property
    def total_files(self) -> int:
        return len(self.results)

    @property
    def files_with_issues(self) -> int:
        return sum(1 for r in self.results.values() if r.has_issues)

    @property
    def has_danger(self) -> bool:
        return any(r.has_danger for r in self.results.values())

    @property
    def has_warnings(self) -> bool:
        return any(r.has_warnings for r in self.results.values())


def run_pipeline(
    paths: List[str],
    extensions: tuple[str, ...] | None = None,
    recursive: bool = True,
) -> ScanSummary:
    """Scan *paths* for migration files, detect issues, and return a summary."""
    summary = ScanSummary()

    for file_path in iter_migration_files(paths, extensions=extensions, recursive=recursive):
        try:
            sql = collect_sql_from_file(file_path)
        except RuntimeError:
            # Skip unreadable files; callers may log the error separately
            continue

        if not sql.strip():
            continue

        result = detect(sql)
        summary.results[str(file_path)] = result

    return summary
