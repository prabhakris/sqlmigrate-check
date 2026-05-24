"""Format rule statistics for human-readable and JSON output."""
from __future__ import annotations

import json
from typing import Dict, List

from sqlmigrate_check.rule_stats import RuleStat, sorted_stats


def _stat_to_dict(stat: RuleStat) -> dict:
    return {
        "rule_id": stat.rule_id,
        "total": stat.total,
        "danger_count": stat.danger_count,
        "warning_count": stat.warning_count,
        "affected_files": sorted(stat.affected_files),
        "highest_severity": stat.highest_severity.value,
    }


def format_stats_text(stats: Dict[str, RuleStat]) -> str:
    """Return a plain-text table of rule statistics."""
    rows = sorted_stats(stats)
    if not rows:
        return "No rule hits recorded."
    lines = [f"{'Rule':<40} {'Total':>6} {'Danger':>7} {'Warning':>8} {'Files':>6}"]
    lines.append("-" * 72)
    for s in rows:
        lines.append(
            f"{s.rule_id:<40} {s.total:>6} {s.danger_count:>7} "
            f"{s.warning_count:>8} {len(s.affected_files):>6}"
        )
    return "\n".join(lines)


def format_stats_json(stats: Dict[str, RuleStat]) -> str:
    """Return a JSON string of rule statistics."""
    payload = [_stat_to_dict(s) for s in sorted_stats(stats)]
    return json.dumps({"rule_stats": payload}, indent=2)
