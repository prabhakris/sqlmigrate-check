"""Format RuleGroup summaries as text or JSON."""
from __future__ import annotations

import json
from typing import Dict, List

from sqlmigrate_check.rule_grouper import RuleGroup, sorted_groups


def _group_to_dict(group: RuleGroup) -> dict:
    return {
        "rule_id": group.rule_id,
        "severity": group.highest_severity.value,
        "count": group.count,
        "affected_files": group.affected_files,
    }


def format_groups_text(groups: Dict[str, RuleGroup]) -> str:
    """Human-readable summary table of rule groups."""
    ordered = sorted_groups(groups)
    if not ordered:
        return "No issues grouped by rule."

    lines: List[str] = ["Rule summary:", ""]
    for g in ordered:
        sev = g.highest_severity.value.upper()
        files_str = ", ".join(g.affected_files) if g.affected_files else "-"
        lines.append(f"  [{sev}] {g.rule_id}: {g.count} issue(s) in {files_str}")
    return "\n".join(lines)


def format_groups_json(groups: Dict[str, RuleGroup]) -> str:
    """JSON array of rule group summaries, sorted by severity then count."""
    ordered = sorted_groups(groups)
    payload = [_group_to_dict(g) for g in ordered]
    return json.dumps(payload, indent=2)
