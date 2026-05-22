"""Core SQL migration safety detector.

Detects potentially unsafe SQL operations that could cause downtime
or data loss when applied to a production database.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Severity(str, Enum):
    WARNING = "warning"
    DANGER = "danger"


@dataclass
class Issue:
    line: int
    statement: str
    message: str
    severity: Severity

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] Line {self.line}: {self.message}\n  → {self.statement.strip()}"


@dataclass
class DetectionResult:
    issues: List[Issue] = field(default_factory=list)

    @property
    def has_danger(self) -> bool:
        return any(i.severity == Severity.DANGER for i in self.issues)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0


# Pattern: (regex, message, severity)
UNSAFE_PATTERNS = [
    (
        re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE),
        "DROP TABLE destroys data permanently",
        Severity.DANGER,
    ),
    (
        re.compile(r"\bDROP\s+COLUMN\b", re.IGNORECASE),
        "DROP COLUMN removes data permanently",
        Severity.DANGER,
    ),
    (
        re.compile(r"\bTRUNCATE\b", re.IGNORECASE),
        "TRUNCATE removes all rows without logging individual deletions",
        Severity.DANGER,
    ),
    (
        re.compile(r"\bADD\s+COLUMN\b.+\bNOT\s+NULL\b(?!.+\bDEFAULT\b)", re.IGNORECASE),
        "Adding NOT NULL column without DEFAULT locks table on some databases",
        Severity.DANGER,
    ),
    (
        re.compile(r"\bALTER\s+COLUMN\b.+\bTYPE\b", re.IGNORECASE),
        "Changing column type may lock the table and cause data loss",
        Severity.WARNING,
    ),
    (
        re.compile(r"\bCREATE\s+INDEX(?!\s+CONCURRENTLY)\b", re.IGNORECASE),
        "CREATE INDEX without CONCURRENTLY locks the table during index build",
        Severity.WARNING,
    ),
    (
        re.compile(r"\bDROP\s+INDEX(?!\s+CONCURRENTLY)\b", re.IGNORECASE),
        "DROP INDEX without CONCURRENTLY locks the table",
        Severity.WARNING,
    ),
]


def detect(sql: str) -> DetectionResult:
    """Analyse *sql* text and return a DetectionResult with any found issues."""
    result = DetectionResult()
    for line_no, line in enumerate(sql.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        for pattern, message, severity in UNSAFE_PATTERNS:
            if pattern.search(line):
                result.issues.append(
                    Issue(
                        line=line_no,
                        statement=line,
                        message=message,
                        severity=severity,
                    )
                )
    return result
