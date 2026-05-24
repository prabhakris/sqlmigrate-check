"""Formatters for rule dependency reports."""
from __future__ import annotations

import json
from typing import List

from sqlmigrate_check.rule_dependency import DependencyHint, DependencyReport


def _hint_to_dict(hint: DependencyHint) -> dict:
    return hint.to_dict()


def format_dependency_text(report: DependencyReport) -> str:
    """Return a human-readable dependency report."""
    if report.is_empty:
        return "No rule co-occurrence hints."

    lines: List[str] = ["Rule Co-occurrence Hints", "=" * 24]
    for hint in report.hints:
        related = ", ".join(hint.related_rule_ids)
        lines.append(f"  [{hint.rule_id}] also triggered with: {related}")
        lines.append(f"    {hint.message}")
    return "\n".join(lines)


def format_dependency_json(report: DependencyReport) -> str:
    """Return a JSON-serialised dependency report."""
    payload = {
        "total_hints": report.total,
        "hints": [_hint_to_dict(h) for h in report.hints],
    }
    return json.dumps(payload, indent=2)


def format_dependency_for_rule(rule_id: str, report: DependencyReport) -> str:
    """Return text hints relevant to a single rule."""
    matching = [h for h in report.hints if h.rule_id == rule_id]
    if not matching:
        return f"No co-occurrence hints for rule '{rule_id}'."
    lines: List[str] = []
    for hint in matching:
        lines.append(hint.message)
    return "\n".join(lines)
