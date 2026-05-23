"""Formatters for ScanProfiler output (text and JSON)."""
from __future__ import annotations

import json
from typing import List

from sqlmigrate_check.profiler import RuleProfile, ScanProfiler


def format_profiler_text(profiler: ScanProfiler) -> str:
    """Render profiler data as a human-readable table."""
    profiles: List[RuleProfile] = profiler.sorted_by_time()
    if not profiles:
        return "No profiling data collected."

    lines = [
        f"{'Rule':<40} {'Calls':>6} {'Total ms':>10} {'Avg ms':>10} {'Hits':>6}",
        "-" * 76,
    ]
    for p in profiles:
        lines.append(
            f"{p.rule_id:<40} {p.total_calls:>6} "
            f"{p.total_elapsed_ms:>10.3f} {p.avg_elapsed_ms:>10.3f} {p.hit_count:>6}"
        )
    return "\n".join(lines)


def format_profiler_json(profiler: ScanProfiler) -> str:
    """Render profiler data as a JSON string."""
    return json.dumps({"rule_profiles": profiler.to_dict()}, indent=2)


def format_profiler(profiler: ScanProfiler, fmt: str = "text") -> str:
    """Dispatch to the correct formatter based on *fmt* ('text' or 'json')."""
    if fmt == "json":
        return format_profiler_json(profiler)
    return format_profiler_text(profiler)
