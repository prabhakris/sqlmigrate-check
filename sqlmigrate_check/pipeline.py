"""High-level pipeline: scan paths → detect issues → return summary."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from sqlmigrate_check.baseline import filter_new_issues, load_baseline
from sqlmigrate_check.config import Config
from sqlmigrate_check.detector import DetectionResult, detect
from sqlmigrate_check.scanner import collect_sql_from_file, iter_migration_files


@dataclass
class ScanSummary:
    """Aggregated result of scanning one or more migration paths."""

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

    def should_fail(self, fail_on: str = "danger") -> bool:
        """Return True when the run should exit with a non-zero code."""
        if fail_on == "warning":
            return self.has_danger or self.has_warnings
        return self.has_danger


def run_pipeline(
    paths: List[str],
    *,
    config: Optional[Config] = None,
    recursive: Optional[bool] = None,
) -> ScanSummary:
    """Scan *paths*, apply baseline filtering, and return a :class:`ScanSummary`.

    Parameters
    ----------
    paths:
        File or directory paths to scan.
    config:
        Optional :class:`~sqlmigrate_check.config.Config` instance.  When
        *None* a default config is used.
    recursive:
        Override ``config.recursive`` when explicitly provided.
    """
    cfg = config or Config()
    should_recurse = recursive if recursive is not None else cfg.recursive

    baseline = load_baseline(Path(cfg.baseline_file)) if cfg.baseline_file else set()

    summary = ScanSummary()
    for path_str in paths:
        for filepath in iter_migration_files(path_str, recursive=should_recurse):
            # Apply exclude globs
            if any(
                filepath.match(pattern) for pattern in cfg.exclude
            ):
                continue
            sql = collect_sql_from_file(filepath)
            result = detect(sql, filepath=str(filepath))
            if baseline:
                result = DetectionResult(
                    filepath=result.filepath,
                    issues=filter_new_issues(result.issues, baseline, str(filepath)),
                )
            summary.results[str(filepath)] = result

    return summary
