"""Produce a human-readable diff-style summary between two scan results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from sqlmigrate_check.detector import DetectionResult, Issue
from sqlmigrate_check.pipeline import ScanSummary


@dataclass
class FileDiff:
    """Issues added or resolved for a single file."""

    filepath: str
    added: List[Issue] = field(default_factory=list)
    resolved: List[Issue] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.resolved)


@dataclass
class ScanDiff:
    """Diff between a previous and current scan summary."""

    file_diffs: Dict[str, FileDiff] = field(default_factory=dict)

    @property
    def total_added(self) -> int:
        return sum(len(fd.added) for fd in self.file_diffs.values())

    @property
    def total_resolved(self) -> int:
        return sum(len(fd.resolved) for fd in self.file_diffs.values())

    @property
    def has_changes(self) -> bool:
        return self.total_added > 0 or self.total_resolved > 0


def _issues_by_file(summary: ScanSummary) -> Dict[str, List[Issue]]:
    result: Dict[str, List[Issue]] = {}
    for dr in summary.results:
        result[dr.filepath] = list(dr.issues)
    return result


def _issue_key(issue: Issue) -> str:
    return f"{issue.rule_id}:{issue.line_number}:{issue.message}"


def compute_diff(previous: ScanSummary, current: ScanSummary) -> ScanDiff:
    """Compare two scan summaries and return a ScanDiff."""
    prev_by_file = _issues_by_file(previous)
    curr_by_file = _issues_by_file(current)

    all_files = set(prev_by_file) | set(curr_by_file)
    diff = ScanDiff()

    for filepath in sorted(all_files):
        prev_keys = {_issue_key(i): i for i in prev_by_file.get(filepath, [])}
        curr_keys = {_issue_key(i): i for i in curr_by_file.get(filepath, [])}

        added = [curr_keys[k] for k in curr_keys if k not in prev_keys]
        resolved = [prev_keys[k] for k in prev_keys if k not in curr_keys]

        if added or resolved:
            diff.file_diffs[filepath] = FileDiff(
                filepath=filepath, added=added, resolved=resolved
            )

    return diff


def format_diff_text(diff: ScanDiff) -> str:
    """Render a ScanDiff as plain text."""
    if not diff.has_changes:
        return "No changes detected between scans."

    lines: List[str] = []
    for fd in diff.file_diffs.values():
        lines.append(f"  {fd.filepath}")
        for issue in fd.added:
            lines.append(f"    + [NEW]      line {issue.line_number}: {issue.message}")
        for issue in fd.resolved:
            lines.append(f"    - [RESOLVED] line {issue.line_number}: {issue.message}")

    summary = f"+{diff.total_added} added, -{diff.total_resolved} resolved"
    return "\n".join([summary, ""] + lines)
