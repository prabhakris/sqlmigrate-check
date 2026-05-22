"""Output formatters for migration check results."""
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlmigrate_check.detector import DetectionResult


class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"
    GITHUB = "github"


def format_text(result: "DetectionResult", filename: str = "") -> str:
    """Human-readable text output."""
    if not result.issues:
        return "✅ No unsafe SQL migrations detected."

    lines = []
    prefix = f"{filename}: " if filename else ""
    for issue in result.issues:
        lines.append(f"{prefix}[{issue.severity.value.upper()}] {issue}")

    summary = f"\n{len(result.issues)} issue(s) found."
    if result.has_danger:
        summary += " ❌ Dangerous migrations detected."
    else:
        summary += " ⚠️  Warnings only."

    return "\n".join(lines) + summary


def format_json(result: "DetectionResult", filename: str = "") -> str:
    """JSON output for machine consumption."""
    import json

    data = {
        "filename": filename,
        "has_danger": result.has_danger,
        "issue_count": len(result.issues),
        "issues": [
            {
                "severity": issue.severity.value,
                "message": issue.message,
                "line": issue.line,
            }
            for issue in result.issues
        ],
    }
    return json.dumps(data, indent=2)


def format_github(result: "DetectionResult", filename: str = "") -> str:
    """GitHub Actions annotation format."""
    if not result.issues:
        return ""

    lines = []
    for issue in result.issues:
        level = "error" if issue.severity.value == "danger" else "warning"
        file_part = f"file={filename}," if filename else ""
        line_part = f"line={issue.line}," if issue.line else ""
        lines.append(f"::{level} {file_part}{line_part}title=sqlmigrate-check::{issue.message}")

    return "\n".join(lines)


def format_result(
    result: "DetectionResult",
    fmt: OutputFormat = OutputFormat.TEXT,
    filename: str = "",
) -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == OutputFormat.JSON:
        return format_json(result, filename)
    if fmt == OutputFormat.GITHUB:
        return format_github(result, filename)
    return format_text(result, filename)
