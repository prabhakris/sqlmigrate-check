"""Utilities for filtering and comparing Severity levels."""
from __future__ import annotations

from typing import Iterable, List

from sqlmigrate_check.detector import Issue, Severity


# Ordered from least to most severe
_SEVERITY_ORDER: list[Severity] = [Severity.WARNING, Severity.DANGER]


def severity_rank(severity: Severity) -> int:
    """Return a numeric rank for a severity level (higher = more severe)."""
    try:
        return _SEVERITY_ORDER.index(severity)
    except ValueError:
        return -1


def meets_minimum(issue: Issue, minimum: Severity) -> bool:
    """Return True if *issue* severity is >= *minimum*."""
    return severity_rank(issue.severity) >= severity_rank(minimum)


def filter_by_minimum_severity(
    issues: Iterable[Issue],
    minimum: Severity,
) -> List[Issue]:
    """Return only issues whose severity meets or exceeds *minimum*."""
    return [i for i in issues if meets_minimum(i, minimum)]


def parse_severity(value: str) -> Severity:
    """Parse a string into a Severity enum, raising ValueError on unknown values."""
    normalised = value.strip().upper()
    try:
        return Severity[normalised]
    except KeyError:
        valid = ", ".join(s.name for s in Severity)
        raise ValueError(
            f"Unknown severity {value!r}. Valid values: {valid}"
        )


def highest_severity(issues: Iterable[Issue]) -> Severity | None:
    """Return the most severe Severity found in *issues*, or None if empty."""
    found: Severity | None = None
    for issue in issues:
        if found is None or severity_rank(issue.severity) > severity_rank(found):
            found = issue.severity
    return found
