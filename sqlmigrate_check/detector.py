"""Core detection logic: run all rules against SQL and aggregate results."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from sqlmigrate_check import rules


class Severity(str, Enum):
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    severity: Severity
    rule: str
    message: str
    line: int | None = None

    def __str__(self) -> str:
        location = f" (line {self.line})" if self.line else ""
        return f"[{self.severity.value.upper()}] {self.rule}{location}: {self.message}"


@dataclass
class DetectionResult:
    issues: List[Issue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def has_danger(self) -> bool:
        return any(i.severity == Severity.DANGER for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == Severity.WARNING for i in self.issues)

    def add(self, issue: Issue) -> None:
        self.issues.append(issue)

    def __len__(self) -> int:
        return len(self.issues)


_RULE_FUNCTIONS = [
    rules.check_drop_table,
    rules.check_drop_column,
    rules.check_truncate,
    rules.check_add_not_null_without_default,
    rules.check_rename_table,
    rules.check_rename_column,
]


def detect(sql: str) -> DetectionResult:
    """Run all registered rules against *sql* and return a DetectionResult."""
    result = DetectionResult()
    for rule_fn in _RULE_FUNCTIONS:
        for issue in rule_fn(sql):
            result.add(issue)
    return result
