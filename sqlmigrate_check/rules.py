"""Built-in detection rules for unsafe SQL migration patterns."""

import re
from typing import List

from sqlmigrate_check.detector import Issue, Severity


def _find_all(pattern: str, sql: str, flags: int = re.IGNORECASE) -> List[re.Match]:
    return list(re.finditer(pattern, sql, flags))


def check_drop_table(sql: str) -> List[Issue]:
    matches = _find_all(r"\bDROP\s+TABLE\b", sql)
    return [
        Issue(
            severity=Severity.DANGER,
            code="E001",
            message="DROP TABLE destroys all data permanently",
            line=sql[: m.start()].count("\n") + 1,
            snippet=m.group(),
        )
        for m in matches
    ]


def check_drop_column(sql: str) -> List[Issue]:
    matches = _find_all(r"\bDROP\s+COLUMN\b", sql)
    return [
        Issue(
            severity=Severity.DANGER,
            code="E002",
            message="DROP COLUMN removes data permanently",
            line=sql[: m.start()].count("\n") + 1,
            snippet=m.group(),
        )
        for m in matches
    ]


def check_truncate(sql: str) -> List[Issue]:
    matches = _find_all(r"\bTRUNCATE\b", sql)
    return [
        Issue(
            severity=Severity.DANGER,
            code="E003",
            message="TRUNCATE removes all rows without logging individual deletions",
            line=sql[: m.start()].count("\n") + 1,
            snippet=m.group(),
        )
        for m in matches
    ]


def check_add_not_null_without_default(sql: str) -> List[Issue]:
    issues = []
    for m in _find_all(r"\bADD\s+COLUMN\s+\w+\s+\w+\s+NOT\s+NULL\b", sql):
        snippet = sql[m.start(): m.end() + 60]
        if not re.search(r"\bDEFAULT\b", snippet, re.IGNORECASE):
            issues.append(
                Issue(
                    severity=Severity.DANGER,
                    code="E004",
                    message="ADD COLUMN NOT NULL without DEFAULT will fail on non-empty tables",
                    line=sql[: m.start()].count("\n") + 1,
                    snippet=m.group(),
                )
            )
    return issues


def check_full_table_lock(sql: str) -> List[Issue]:
    matches = _find_all(r"\bLOCK\s+TABLE\b", sql)
    return [
        Issue(
            severity=Severity.WARNING,
            code="W001",
            message="LOCK TABLE may cause prolonged downtime on busy tables",
            line=sql[: m.start()].count("\n") + 1,
            snippet=m.group(),
        )
        for m in matches
    ]


def check_rename_table(sql: str) -> List[Issue]:
    matches = _find_all(r"\bRENAME\s+TABLE\b|\bALTER\s+TABLE\b.+\bRENAME\s+TO\b", sql)
    return [
        Issue(
            severity=Severity.WARNING,
            code="W002",
            message="Renaming a table may break dependent views, queries, or ORM mappings",
            line=sql[: m.start()].count("\n") + 1,
            snippet=m.group(),
        )
        for m in matches
    ]


ALL_RULES = [
    check_drop_table,
    check_drop_column,
    check_truncate,
    check_add_not_null_without_default,
    check_full_table_lock,
    check_rename_table,
]
