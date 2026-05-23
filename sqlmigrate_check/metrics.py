"""Metrics collection for scan runs — counts, timings, and per-rule tallies."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List

from sqlmigrate_check.detector import Severity


@dataclass
class RuleMetrics:
    """Per-rule hit counts broken down by severity."""
    rule_id: str
    danger_count: int = 0
    warning_count: int = 0

    @property
    def total(self) -> int:
        return self.danger_count + self.warning_count


@dataclass
class ScanMetrics:
    """Aggregated metrics for a complete scan run."""
    files_scanned: int = 0
    files_with_issues: int = 0
    total_issues: int = 0
    danger_count: int = 0
    warning_count: int = 0
    suppressed_count: int = 0
    elapsed_seconds: float = 0.0
    rules: Dict[str, RuleMetrics] = field(default_factory=dict)

    def record_rule_hit(self, rule_id: str, severity: Severity) -> None:
        if rule_id not in self.rules:
            self.rules[rule_id] = RuleMetrics(rule_id=rule_id)
        rm = self.rules[rule_id]
        if severity == Severity.DANGER:
            rm.danger_count += 1
            self.danger_count += 1
        else:
            rm.warning_count += 1
            self.warning_count += 1
        self.total_issues += 1

    def sorted_rules(self) -> List[RuleMetrics]:
        """Return rule metrics sorted by total hits descending."""
        return sorted(self.rules.values(), key=lambda r: r.total, reverse=True)


class ScanTimer:
    """Context manager that measures elapsed wall-clock time."""

    def __init__(self) -> None:
        self._start: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self) -> "ScanTimer":
        self._start = time.monotonic()
        return self

    def __exit__(self, *_: object) -> None:
        self.elapsed = time.monotonic() - self._start


def build_metrics_from_pipeline(
    summary: object,
    suppressed_count: int = 0,
    elapsed: float = 0.0,
) -> ScanMetrics:
    """Construct a ScanMetrics from a pipeline ScanSummary."""
    m = ScanMetrics(
        files_scanned=summary.total_files,  # type: ignore[attr-defined]
        files_with_issues=summary.files_with_issues,  # type: ignore[attr-defined]
        suppressed_count=suppressed_count,
        elapsed_seconds=elapsed,
    )
    for result in summary.results:  # type: ignore[attr-defined]
        for issue in result.issues:
            m.record_rule_hit(issue.rule_id, issue.severity)
    if m.files_with_issues > 0:
        pass  # already counted above
    return m
