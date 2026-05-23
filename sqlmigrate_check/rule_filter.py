"""Filter issues by rule ID, severity, or file path patterns."""
from __future__ import annotations

import fnmatch
from typing import Iterable, List, Optional

from sqlmigrate_check.detector import Issue, Severity


def filter_by_severity(
    issues: Iterable[Issue],
    min_severity: Severity,
) -> List[Issue]:
    """Return issues whose severity is >= *min_severity* (DANGER > WARNING)."""
    order = {Severity.WARNING: 0, Severity.DANGER: 1}
    threshold = order[min_severity]
    return [i for i in issues if order[i.severity] >= threshold]


def filter_by_rule_ids(
    issues: Iterable[Issue],
    rule_ids: Iterable[str],
) -> List[Issue]:
    """Return only issues whose rule_id is in *rule_ids*."""
    wanted = set(rule_ids)
    return [i for i in issues if i.rule_id in wanted]


def exclude_rule_ids(
    issues: Iterable[Issue],
    rule_ids: Iterable[str],
) -> List[Issue]:
    """Return issues whose rule_id is NOT in *rule_ids*."""
    excluded = set(rule_ids)
    return [i for i in issues if i.rule_id not in excluded]


def filter_by_filepath(
    issues: Iterable[Issue],
    pattern: str,
) -> List[Issue]:
    """Return issues whose filepath matches *pattern* (fnmatch-style)."""
    return [i for i in issues if fnmatch.fnmatch(i.filepath, pattern)]


def apply_rule_filter(
    issues: Iterable[Issue],
    *,
    min_severity: Optional[Severity] = None,
    include_rules: Optional[Iterable[str]] = None,
    exclude_rules: Optional[Iterable[str]] = None,
    filepath_pattern: Optional[str] = None,
) -> List[Issue]:
    """Convenience wrapper that applies all active filters in sequence."""
    result: List[Issue] = list(issues)

    if min_severity is not None:
        result = filter_by_severity(result, min_severity)

    if include_rules is not None:
        result = filter_by_rule_ids(result, include_rules)

    if exclude_rules is not None:
        result = exclude_rule_ids(result, exclude_rules)

    if filepath_pattern is not None:
        result = filter_by_filepath(result, filepath_pattern)

    return result
