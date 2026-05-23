"""Profiler module: tracks per-rule timing and hit counts during a scan."""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, Generator, List, Tuple


@dataclass
class RuleProfile:
    """Accumulated timing and hit data for a single rule."""

    rule_id: str
    total_calls: int = 0
    total_elapsed_ms: float = 0.0
    hit_count: int = 0

    @property
    def avg_elapsed_ms(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.total_elapsed_ms / self.total_calls


@dataclass
class ScanProfiler:
    """Collects profiling data across all rules during a scan."""

    _profiles: Dict[str, RuleProfile] = field(default_factory=dict)

    def _get_or_create(self, rule_id: str) -> RuleProfile:
        if rule_id not in self._profiles:
            self._profiles[rule_id] = RuleProfile(rule_id=rule_id)
        return self._profiles[rule_id]

    @contextmanager
    def profile_rule(self, rule_id: str, hit: bool = False) -> Generator[None, None, None]:
        """Context manager that times a rule execution and records a hit if requested."""
        profile = self._get_or_create(rule_id)
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            profile.total_calls += 1
            profile.total_elapsed_ms += elapsed_ms

    def record_hit(self, rule_id: str) -> None:
        """Increment hit counter for a rule (call after issues are found)."""
        self._get_or_create(rule_id).hit_count += 1

    def sorted_by_time(self) -> List[RuleProfile]:
        """Return profiles sorted by total elapsed time descending."""
        return sorted(self._profiles.values(), key=lambda p: p.total_elapsed_ms, reverse=True)

    def sorted_by_hits(self) -> List[RuleProfile]:
        """Return profiles sorted by hit count descending."""
        return sorted(self._profiles.values(), key=lambda p: p.hit_count, reverse=True)

    def all_profiles(self) -> List[RuleProfile]:
        return list(self._profiles.values())

    def to_dict(self) -> dict:
        return {
            p.rule_id: {
                "total_calls": p.total_calls,
                "total_elapsed_ms": round(p.total_elapsed_ms, 4),
                "avg_elapsed_ms": round(p.avg_elapsed_ms, 4),
                "hit_count": p.hit_count,
            }
            for p in self.sorted_by_time()
        }
