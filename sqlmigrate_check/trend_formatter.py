"""Format TrendDelta and TrendSnapshot for human-readable and JSON output."""
from __future__ import annotations

import json
from typing import Optional

from sqlmigrate_check.trend import TrendDelta, TrendSnapshot


def _sign(n: int) -> str:
    return f"+{n}" if n > 0 else str(n)


def format_trend_text(
    current: TrendSnapshot,
    delta: Optional[TrendDelta] = None,
) -> str:
    lines = [
        "Trend Report",
        "============",
        f"  Files scanned : {current.total_files}",
        f"  Danger issues : {current.total_danger}",
        f"  Warnings      : {current.total_warnings}",
    ]

    if delta is not None:
        lines.append("")
        lines.append("Changes vs previous snapshot:")
        lines.append(f"  Files   : {_sign(delta.file_delta)}")
        lines.append(f"  Danger  : {_sign(delta.danger_delta)}")
        lines.append(f"  Warning : {_sign(delta.warning_delta)}")

        changed_rules = {
            rule: d for rule, d in delta.rule_deltas.items() if d != 0
        }
        if changed_rules:
            lines.append("  Rule changes:")
            for rule, d in sorted(changed_rules.items()):
                lines.append(f"    {rule}: {_sign(d)}")

        if delta.is_regressing:
            lines.append("  ⚠  Regression detected.")
        elif delta.is_improving:
            lines.append("  ✓  Improvement detected.")
        else:
            lines.append("  –  No change.")

    return "\n".join(lines)


def format_trend_json(
    current: TrendSnapshot,
    delta: Optional[TrendDelta] = None,
) -> str:
    payload: dict = {"current": current.to_dict()}
    if delta is not None:
        payload["delta"] = {
            "danger_delta": delta.danger_delta,
            "warning_delta": delta.warning_delta,
            "file_delta": delta.file_delta,
            "rule_deltas": delta.rule_deltas,
            "is_regressing": delta.is_regressing,
            "is_improving": delta.is_improving,
        }
    return json.dumps(payload, indent=2)
