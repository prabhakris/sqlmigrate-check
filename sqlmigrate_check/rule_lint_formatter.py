"""Formatters for LintReport output."""
from __future__ import annotations

import json
from typing import Any, Dict, List

from sqlmigrate_check.rule_lint import LintReport, LintViolation


def _violation_to_dict(v: LintViolation) -> Dict[str, Any]:
    return {
        "filepath": v.filepath,
        "line": v.line_number,
        "code": v.code,
        "message": v.message,
    }


def format_lint_text(report: LintReport) -> str:
    if report.total_violations == 0:
        return "Lint: no violations found.\n"
    lines: List[str] = []
    lines.append(f"Lint violations ({report.total_violations} total, {report.files_with_violations} file(s)):\n")
    for result in report.results:
        if not result.has_violations:
            continue
        lines.append(f"  {result.filepath}")
        for v in result.violations:
            lines.append(f"    Line {v.line_number}: [{v.code}] {v.message}")
    return "\n".join(lines) + "\n"


def format_lint_json(report: LintReport) -> str:
    data: Dict[str, Any] = {
        "total_violations": report.total_violations,
        "files_with_violations": report.files_with_violations,
        "violations": [_violation_to_dict(v) for v in report.all_violations],
    }
    return json.dumps(data, indent=2)


def format_lint_github(report: LintReport) -> str:
    """Emit GitHub Actions annotation lines."""
    lines: List[str] = []
    for v in report.all_violations:
        lines.append(
            f"::warning file={v.filepath},line={v.line_number},title=sqlmigrate-lint [{v.code}]::{v.message}"
        )
    return "\n".join(lines) + ("\n" if lines else "")
