"""Aggregated reporting: combine pipeline results with baseline filtering and formatting."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from sqlmigrate_check.baseline import filter_new_issues, load_baseline
from sqlmigrate_check.detector import DetectionResult, Severity
from sqlmigrate_check.formatter import OutputFormat, format_result
from sqlmigrate_check.pipeline import ScanSummary


@dataclass
class ReportOptions:
    output_format: OutputFormat = OutputFormat.TEXT
    baseline_path: Optional[Path] = None
    show_suppressed_count: bool = True


@dataclass
class Report:
    summary: ScanSummary
    options: ReportOptions
    suppressed_count: int = 0
    filtered_results: list[DetectionResult] = field(default_factory=list)

    @property
    def has_danger(self) -> bool:
        return any(
            any(i.severity == Severity.DANGER for i in r.issues)
            for r in self.filtered_results
        )

    @property
    def has_warnings(self) -> bool:
        return any(
            any(i.severity == Severity.WARNING for i in r.issues)
            for r in self.filtered_results
        )

    @property
    def issue_count(self) -> int:
        """Total number of issues across all filtered results."""
        return sum(len(r.issues) for r in self.filtered_results)

    def render(self) -> str:
        lines: list[str] = []
        for result in self.filtered_results:
            lines.append(format_result(result, self.options.output_format))
        if self.options.show_suppressed_count and self.suppressed_count > 0:
            lines.append(
                f"# {self.suppressed_count} issue(s) suppressed by baseline."
            )
        return "\n".join(lines)


def build_report(summary: ScanSummary, options: ReportOptions) -> Report:
    """Apply baseline filtering and build a Report from a ScanSummary."""
    baseline = set()
    if options.baseline_path is not None:
        baseline = load_baseline(options.baseline_path)

    filtered: list[DetectionResult] = []
    suppressed = 0

    for result in summary.results:
        if not baseline:
            filtered.append(result)
            continue
        new_issues = filter_new_issues(result.issues, result.filepath, baseline)
        suppressed += len(result.issues) - len(new_issues)
        if new_issues:
            filtered.append(
                DetectionResult(filepath=result.filepath, issues=new_issues)
            )

    return Report(
        summary=summary,
        options=options,
        suppressed_count=suppressed,
        filtered_results=filtered,
    )
