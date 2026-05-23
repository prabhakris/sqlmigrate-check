"""Human-readable and JSON rendering of ScanMetrics."""
from __future__ import annotations

import json
from typing import Any, Dict

from sqlmigrate_check.metrics import ScanMetrics


def metrics_to_dict(m: ScanMetrics) -> Dict[str, Any]:
    """Serialise ScanMetrics to a plain dict (JSON-safe)."""
    return {
        "files_scanned": m.files_scanned,
        "files_with_issues": m.files_with_issues,
        "total_issues": m.total_issues,
        "danger_count": m.danger_count,
        "warning_count": m.warning_count,
        "suppressed_count": m.suppressed_count,
        "elapsed_seconds": round(m.elapsed_seconds, 4),
        "rules": [
            {
                "rule_id": r.rule_id,
                "danger": r.danger_count,
                "warning": r.warning_count,
                "total": r.total,
            }
            for r in m.sorted_rules()
        ],
    }


def format_metrics_json(m: ScanMetrics) -> str:
    """Return a pretty-printed JSON string of the metrics."""
    return json.dumps(metrics_to_dict(m), indent=2)


def format_metrics_text(m: ScanMetrics) -> str:
    """Return a compact human-readable summary of the metrics."""
    lines = [
        f"Scanned {m.files_scanned} file(s) in {m.elapsed_seconds:.3f}s",
        f"  Issues   : {m.total_issues} "
        f"(danger={m.danger_count}, warning={m.warning_count})",
        f"  Suppressed: {m.suppressed_count}",
        f"  Files with issues: {m.files_with_issues}",
    ]
    if m.rules:
        lines.append("  Top rules:")
        for r in m.sorted_rules()[:5]:
            lines.append(
                f"    {r.rule_id}: {r.total} hit(s) "
                f"(D={r.danger_count} W={r.warning_count})"
            )
    return "\n".join(lines)
