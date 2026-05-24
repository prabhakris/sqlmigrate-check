"""Trend tracking: compare current scan metrics against a stored baseline snapshot."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from sqlmigrate_check.metrics import ScanMetrics


@dataclass
class TrendSnapshot:
    """A persisted point-in-time snapshot of scan metrics."""

    total_files: int = 0
    total_danger: int = 0
    total_warnings: int = 0
    rule_hits: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "total_files": self.total_files,
            "total_danger": self.total_danger,
            "total_warnings": self.total_warnings,
            "rule_hits": self.rule_hits,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TrendSnapshot":
        return cls(
            total_files=int(data.get("total_files", 0)),
            total_danger=int(data.get("total_danger", 0)),
            total_warnings=int(data.get("total_warnings", 0)),
            rule_hits={str(k): int(v) for k, v in data.get("rule_hits", {}).items()},
        )


@dataclass
class TrendDelta:
    """Difference between two snapshots."""

    danger_delta: int = 0
    warning_delta: int = 0
    file_delta: int = 0
    rule_deltas: Dict[str, int] = field(default_factory=dict)

    @property
    def is_regressing(self) -> bool:
        """True when danger or warning count increased."""
        return self.danger_delta > 0 or self.warning_delta > 0

    @property
    def is_improving(self) -> bool:
        """True when danger or warning count decreased."""
        return self.danger_delta < 0 or self.warning_delta < 0


def snapshot_from_metrics(metrics: ScanMetrics) -> TrendSnapshot:
    """Build a TrendSnapshot from a live ScanMetrics object."""
    rule_hits: Dict[str, int] = {
        rule_id: rm.danger_count + rm.warning_count
        for rule_id, rm in metrics.rules.items()
    }
    return TrendSnapshot(
        total_files=metrics.total_files,
        total_danger=metrics.total_danger,
        total_warnings=metrics.total_warnings,
        rule_hits=rule_hits,
    )


def compute_delta(previous: TrendSnapshot, current: TrendSnapshot) -> TrendDelta:
    """Return the element-wise delta between two snapshots."""
    all_rules = set(previous.rule_hits) | set(current.rule_hits)
    rule_deltas = {
        r: current.rule_hits.get(r, 0) - previous.rule_hits.get(r, 0)
        for r in all_rules
    }
    return TrendDelta(
        danger_delta=current.total_danger - previous.total_danger,
        warning_delta=current.total_warnings - previous.total_warnings,
        file_delta=current.total_files - previous.total_files,
        rule_deltas=rule_deltas,
    )


def load_snapshot(path: Path) -> Optional[TrendSnapshot]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return TrendSnapshot.from_dict(data)
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def save_snapshot(path: Path, snapshot: TrendSnapshot) -> None:
    path.write_text(json.dumps(snapshot.to_dict(), indent=2), encoding="utf-8")
