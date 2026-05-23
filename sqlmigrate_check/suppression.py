"""Suppression logic: combine ignore-comments and allowlist filtering."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from sqlmigrate_check.allowlist import Allowlist, allowlist_from_config
from sqlmigrate_check.config import Config
from sqlmigrate_check.detector import DetectionResult, Issue
from sqlmigrate_check.ignore_comments import is_line_ignored


@dataclass
class SuppressionSummary:
    """Records how many issues were suppressed and by which mechanism."""
    suppressed_by_comment: int = 0
    suppressed_by_allowlist: int = 0

    @property
    def total_suppressed(self) -> int:
        return self.suppressed_by_comment + self.suppressed_by_allowlist


def _is_comment_suppressed(issue: Issue, sql: str) -> bool:
    """Return True when the issue's line carries an inline-ignore marker."""
    lines = sql.splitlines()
    if issue.line_number is None:
        return False
    idx = issue.line_number - 1
    if idx < 0 or idx >= len(lines):
        return False
    return is_line_ignored(lines[idx])


def apply_suppressions(
    result: DetectionResult,
    sql: str,
    allowlist: Allowlist,
) -> tuple[DetectionResult, SuppressionSummary]:
    """Filter *result* through comment-suppression then allowlist.

    Returns a new :class:`DetectionResult` containing only surviving issues
    together with a :class:`SuppressionSummary`.
    """
    summary = SuppressionSummary()
    surviving: List[Issue] = []

    for issue in result.issues:
        if _is_comment_suppressed(issue, sql):
            summary.suppressed_by_comment += 1
            continue
        if allowlist.is_allowed(issue.filepath or "", issue.rule_id):
            summary.suppressed_by_allowlist += 1
            continue
        surviving.append(issue)

    new_result = DetectionResult(filepath=result.filepath, issues=surviving)
    return new_result, summary


def apply_suppressions_with_config(
    result: DetectionResult,
    sql: str,
    config: Config,
) -> tuple[DetectionResult, SuppressionSummary]:
    """Convenience wrapper that builds an :class:`Allowlist` from *config*."""
    allowlist = allowlist_from_config(config)
    return apply_suppressions(result, sql, allowlist)
