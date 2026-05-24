"""Rule lint: validate SQL migration files for style and structural issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class LintViolation:
    filepath: str
    line_number: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.filepath}:{self.line_number} [{self.code}] {self.message}"


@dataclass
class LintResult:
    filepath: str
    violations: List[LintViolation] = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        return len(self.violations) > 0

    @property
    def violation_count(self) -> int:
        return len(self.violations)


@dataclass
class LintReport:
    results: List[LintResult] = field(default_factory=list)

    @property
    def total_violations(self) -> int:
        return sum(r.violation_count for r in self.results)

    @property
    def files_with_violations(self) -> int:
        return sum(1 for r in self.results if r.has_violations)

    @property
    def all_violations(self) -> List[LintViolation]:
        out: List[LintViolation] = []
        for r in self.results:
            out.extend(r.violations)
        return out


def _check_trailing_semicolon(filepath: str, lines: List[str]) -> List[LintViolation]:
    violations: List[LintViolation] = []
    for i, line in enumerate(lines, start=1):
        stripped = line.rstrip()
        if stripped.endswith(";") and stripped.endswith(";;"): 
            violations.append(LintViolation(filepath, i, "L001", "Double semicolon detected"))
    return violations


def _check_uppercase_keywords(filepath: str, lines: List[str]) -> List[LintViolation]:
    keywords = ("select", "insert", "update", "delete", "drop", "alter", "create", "truncate")
    violations: List[LintViolation] = []
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        lower = stripped.lower()
        for kw in keywords:
            if lower.startswith(kw) and not stripped.startswith(kw.upper()):
                violations.append(
                    LintViolation(filepath, i, "L002", f"SQL keyword '{kw}' should be uppercase")
                )
                break
    return violations


def _check_empty_file(filepath: str, lines: List[str]) -> List[LintViolation]:
    non_empty = [l for l in lines if l.strip()]
    if not non_empty:
        return [LintViolation(filepath, 1, "L003", "Migration file is empty")]
    return []


def lint_file(filepath: str, content: str) -> LintResult:
    lines = content.splitlines()
    violations: List[LintViolation] = []
    violations.extend(_check_empty_file(filepath, lines))
    violations.extend(_check_trailing_semicolon(filepath, lines))
    violations.extend(_check_uppercase_keywords(filepath, lines))
    violations.sort(key=lambda v: v.line_number)
    return LintResult(filepath=filepath, violations=violations)


def lint_files(file_contents: dict) -> LintReport:
    """Accept a mapping of filepath -> content and return a LintReport."""
    results = [lint_file(fp, content) for fp, content in file_contents.items()]
    return LintReport(results=results)
