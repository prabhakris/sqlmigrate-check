"""Summarise detected issues grouped by severity for quick reporting."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from sqlmigrate_check.detector import Issue, Severity
from sqlmigrate_check.pipeline import ScanSummary


@dataclass
class SeverityBucket:
    severity: Severity
    issues: List[Issue] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.issues)

    @property
    def rule_ids(self) -> List[str]:
        seen: Dict[str, None] = {}
        for issue in self.issues:
            seen[issue.rule_id] = None
        return list(seen)


@dataclass
class RuleSummary:
    danger_bucket: SeverityBucket = field(
        default_factory=lambda: SeverityBucket(Severity.DANGER)
    )
    warning_bucket: SeverityBucket = field(
        default_factory=lambda: SeverityBucket(Severity.WARNING)
    )

    @property
    def total(self) -> int:
        return self.danger_bucket.count + self.warning_bucket.count

    @property
    def has_danger(self) -> bool:
        return self.danger_bucket.count > 0

    @property
    def has_warnings(self) -> bool:
        return self.warning_bucket.count > 0

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "danger": {
                "count": self.danger_bucket.count,
                "rules": self.danger_bucket.rule_ids,
            },
            "warning": {
                "count": self.warning_bucket.count,
                "rules": self.warning_bucket.rule_ids,
            },
        }


def build_rule_summary(issues: Iterable[Issue]) -> RuleSummary:
    summary = RuleSummary()
    for issue in issues:
        if issue.severity == Severity.DANGER:
            summary.danger_bucket.issues.append(issue)
        else:
            summary.warning_bucket.issues.append(issue)
    return summary


def rule_summary_from_scan(scan: ScanSummary) -> RuleSummary:
    all_issues: List[Issue] = []
    for result in scan.results:
        all_issues.extend(result.issues)
    return build_rule_summary(all_issues)
