"""Attach annotation metadata to scan results for richer reporting."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from sqlmigrate_check.annotation_parser import AnnotationMap, parse_annotations
from sqlmigrate_check.detector import DetectionResult


@dataclass
class AnnotatedResult:
    """A :class:`DetectionResult` paired with its :class:`AnnotationMap`."""

    result: DetectionResult
    annotations: AnnotationMap

    @property
    def filepath(self) -> str:
        return self.result.filepath

    @property
    def ticket(self) -> str:
        """Convenience accessor for the first *ticket* annotation value."""
        return self.annotations.first("ticket", default="")

    @property
    def reviewed_by(self) -> List[str]:
        """All *reviewed-by* annotation values."""
        return self.annotations.get("reviewed-by")

    def has_annotation(self, key: str) -> bool:
        """Return True if at least one annotation with *key* is present."""
        return bool(self.annotations.get(key))


@dataclass
class AnnotationScanReport:
    """Aggregate annotation data across all scanned files."""

    annotated_results: List[AnnotatedResult] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        return len(self.annotated_results)

    @property
    def files_with_ticket(self) -> int:
        return sum(1 for r in self.annotated_results if r.ticket)

    @property
    def files_without_ticket(self) -> List[str]:
        return [r.filepath for r in self.annotated_results if not r.ticket]

    def tickets(self) -> Dict[str, List[str]]:
        """Map each ticket to the list of filepaths that reference it."""
        mapping: Dict[str, List[str]] = {}
        for ar in self.annotated_results:
            for ticket in ar.annotations.get("ticket"):
                mapping.setdefault(ticket, []).append(ar.filepath)
        return mapping


def annotate_result(result: DetectionResult, sql: str) -> AnnotatedResult:
    """Wrap *result* with annotations parsed from *sql*."""
    return AnnotatedResult(result=result, annotations=parse_annotations(sql))


def build_annotation_report(
    pairs: List[tuple],  # [(DetectionResult, sql_str), ...]
) -> AnnotationScanReport:
    """Build an :class:`AnnotationScanReport` from result/SQL pairs."""
    annotated = [annotate_result(result, sql) for result, sql in pairs]
    return AnnotationScanReport(annotated_results=annotated)
