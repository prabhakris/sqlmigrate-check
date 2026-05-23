"""Detection rules for unsafe SQL patterns.

Each rule is a callable with signature::

    check_*(sql: str, filepath: str = "") -> list[Issue]

Rules should use :func:`ignored_lines` to skip suppressed lines.
"""
from __future__ import annotations

import re
from typing import List

from sqlmigrate_check.detector import Issue, Severity
from sqlmigrate_check.ignore_comments import ignored_lines


def _find_all(pattern: str, sql: str, flags: int = re.IGNORECASE):
    """Yield (lineno, match) for every match in *sql*."""
    compiled = re.compile(pattern, flags)
    for lineno, line in enumerate(sql.splitlines(), start=1):
        m = compiled.search(line)
        if m:
            yield lineno, m


def check_drop_table(sql: str, filepath: str = "") -> List[Issue]:
    issues: List[Issue] = []
    suppressed = ignored_lines(sql)
    for lineno, _ in _find_all(r"\bDROP\s+TABLE\b", sql):
        if lineno in suppressed:
            continue
        issues.append(
            Issue(
                filepath=filepath,
                line=lineno,
                rule="drop-table",
                message="DROP TABLE destroys all data permanently.",
                severity=Severity.DANGER,
            )
        )
    return issues


def check_drop_column(sql: str, filepath: str = "") -> List[Issue]:
    issues: List[Issue] = []
    suppressed = ignored_lines(sql)
    for lineno, _ in _find_all(r"\bDROP\s+COLUMN\b", sql):
        if lineno in suppressed:
            continue
        issues.append(
            Issue(
                filepath=filepath,
                line=lineno,
                rule="drop-column",
                message="DROP COLUMN removes data that cannot be recovered.",
                severity=Severity.DANGER,
            )
        )
    return issues


def check_truncate(sql: str, filepath: str = "") -> List[Issue]:
    issues: List[Issue] = []
    suppressed = ignored_lines(sql)
    for lineno, _ in _find_all(r"\bTRUNCATE\b", sql):
        if lineno in suppressed:
            continue
        issues.append(
            Issue(
                filepath=filepath,
                line=lineno,
                rule="truncate",
                message="TRUNCATE removes all rows without logging individual deletes.",
                severity=Severity.DANGER,
            )
        )
    return issues


def check_add_not_null_without_default(sql: str, filepath: str = "") -> List[Issue]:
    """Warn when ADD COLUMN ... NOT NULL appears without a DEFAULT clause."""
    issues: List[Issue] = []
    suppressed = ignored_lines(sql)
    pattern = re.compile(
        r"\bADD\s+COLUMN\b[^;]*?\bNOT\s+NULL\b",
        re.IGNORECASE | re.DOTALL,
    )
    default_pattern = re.compile(r"\bDEFAULT\b", re.IGNORECASE)
    for lineno, match in _find_all(
        r"\bADD\s+COLUMN\b[^;\n]*\bNOT\s+NULL\b", sql
    ):
        if lineno in suppressed:
            continue
        if not default_pattern.search(match.group(0)):
            issues.append(
                Issue(
                    filepath=filepath,
                    line=lineno,
                    rule="add-not-null-without-default",
                    message=(
                        "ADD COLUMN NOT NULL without DEFAULT will fail on "
                        "non-empty tables."
                    ),
                    severity=Severity.DANGER,
                )
            )
    return issues


def check_rename_table(sql: str, filepath: str = "") -> List[Issue]:
    issues: List[Issue] = []
    suppressed = ignored_lines(sql)
    for lineno, _ in _find_all(r"\bRENAME\s+TO\b", sql):
        if lineno in suppressed:
            continue
        issues.append(
            Issue(
                filepath=filepath,
                line=lineno,
                rule="rename-table",
                message="RENAME TABLE may break dependent views, FKs, or application code.",
                severity=Severity.WARNING,
            )
        )
    return issues


def check_rename_column(sql: str, filepath: str = "") -> List[Issue]:
    issues: List[Issue] = []
    suppressed = ignored_lines(sql)
    for lineno, _ in _find_all(r"\bRENAME\s+COLUMN\b", sql):
        if lineno in suppressed:
            continue
        issues.append(
            Issue(
                filepath=filepath,
                line=lineno,
                rule="rename-column",
                message="RENAME COLUMN may break application queries or ORM mappings.",
                severity=Severity.WARNING,
            )
        )
    return issues
