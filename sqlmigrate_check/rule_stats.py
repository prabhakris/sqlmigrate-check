"""Aggregate per-rule statistics across a full scan."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from sqlmigrate_check.detector import Issue, Severity
from sqlmigrate_check.pipeline import ScanSummary


@dataclass
class RuleStat:
    rule_id: str
    danger_count: int = 0
    warning_count: int = 0
    affected_files: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.danger_count + self.warning_count

    @property
    def highest_severity(self) -> Severity:
        if self.danger_count > 0:
            return Severity.DANGER
        return Severity.WARNING


def compute_rule_stats(summary: ScanSummary) -> Dict[str, RuleStat]:
    """Return a mapping of rule_id -> RuleStat from a ScanSummary."""
    stats: Dict[str, RuleStat] = {}
    for filepath, result in summary.results.items():
        for issue in result.issues:
            if issue.rule_id not in stats:
                stats[issue.rule_id] = RuleStat(rule_id=issue.rule_id)
            stat = stats[issue.rule_id]
            if issue.severity == Severity.DANGER:
                stat.danger_count += 1
            else:
                stat.warning_count += 1
            if filepath not in stat.affected_files:
                stat.affected_files.append(filepath)
    return stats


def sorted_stats(stats: Dict[str, RuleStat]) -> List[RuleStat]:
    """Return stats sorted by total descending, then rule_id ascending."""
    return sorted(stats.values(), key=lambda s: (-s.total, s.rule_id))
