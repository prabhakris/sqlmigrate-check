"""Formatters that render RuleExplanation objects as text or JSON."""
from __future__ import annotations

import json
from typing import List

from sqlmigrate_check.rule_explainer import RuleExplanation, get_explanation, _EXPLANATIONS


def format_explanation_text(exp: RuleExplanation) -> str:
    """Render a single RuleExplanation as a human-readable text block."""
    sep = "-" * 60
    lines = [
        sep,
        f"Rule ID     : {exp.rule_id}",
        f"Title       : {exp.title}",
        "",
        "Explanation :",
        f"  {exp.explanation}",
        "",
        "Remediation :",
        f"  {exp.remediation}",
    ]
    if exp.reference:
        lines += ["", f"Reference   : {exp.reference}"]
    lines.append(sep)
    return "\n".join(lines)


def format_explanation_json(exp: RuleExplanation) -> str:
    """Render a single RuleExplanation as a JSON string."""
    return json.dumps(exp.to_dict(), indent=2)


def format_all_explanations_text() -> str:
    """Render all known rule explanations as a concatenated text report."""
    blocks = [format_explanation_text(exp) for exp in _EXPLANATIONS.values()]
    return "\n".join(blocks)


def format_all_explanations_json() -> str:
    """Render all known rule explanations as a JSON array."""
    data = [exp.to_dict() for exp in _EXPLANATIONS.values()]
    return json.dumps(data, indent=2)


def format_explanation_for_rule(rule_id: str, fmt: str = "text") -> str:
    """Return formatted explanation for *rule_id* in the given *fmt* ('text'|'json').

    Returns an error string when the rule is unknown.
    """
    exp = get_explanation(rule_id)
    if exp is None:
        msg = f"Unknown rule: '{rule_id}'"
        if fmt == "json":
            return json.dumps({"error": msg})
        return msg
    if fmt == "json":
        return format_explanation_json(exp)
    return format_explanation_text(exp)
