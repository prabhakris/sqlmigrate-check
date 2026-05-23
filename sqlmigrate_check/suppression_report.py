"""Aggregated suppression statistics across a full scan."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from sqlmigrate_check.suppression import SuppressionSummary


@dataclass
class SuppressionReport:
    """Accumulates :class:`SuppressionSummary` objects per file."""
    _by_file: Dict[str, SuppressionSummary] = field(default_factory=dict, repr=False)

    def record(self, filepath: str, summary: SuppressionSummary) -> None:
        """Add *summary* for *filepath*, merging if already present."""
        if filepath in self._by_file:
            existing = self._by_file[filepath]
            self._by_file[filepath] = SuppressionSummary(
                suppressed_by_comment=existing.suppressed_by_comment + summary.suppressed_by_comment,
                suppressed_by_allowlist=existing.suppressed_by_allowlist + summary.suppressed_by_allowlist,
            )
        else:
            self._by_file[filepath] = summary

    @property
    def total_suppressed_by_comment(self) -> int:
        return sum(s.suppressed_by_comment for s in self._by_file.values())

    @property
    def total_suppressed_by_allowlist(self) -> int:
        return sum(s.suppressed_by_allowlist for s in self._by_file.values())

    @property
    def total_suppressed(self) -> int:
        return self.total_suppressed_by_comment + self.total_suppressed_by_allowlist

    @property
    def files_with_suppressions(self) -> int:
        return sum(1 for s in self._by_file.values() if s.total_suppressed > 0)

    def per_file(self) -> Dict[str, SuppressionSummary]:
        """Return a shallow copy of the per-file mapping."""
        return dict(self._by_file)

    def as_text(self) -> str:
        """Human-readable summary line."""
        if self.total_suppressed == 0:
            return "No issues were suppressed."
        return (
            f"Suppressed {self.total_suppressed} issue(s) total "
            f"({self.total_suppressed_by_comment} via comment, "
            f"{self.total_suppressed_by_allowlist} via allowlist) "
            f"across {self.files_with_suppressions} file(s)."
        )
