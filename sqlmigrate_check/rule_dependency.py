"""Rule dependency tracking: detect when issues co-occur and suggest related rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Sequence

from sqlmigrate_check.detector import Issue

# Known rule pairs that commonly appear together or imply each other
_RELATED_RULES: Dict[str, FrozenSet[str]] = {
    "drop-table": frozenset({"drop-column", "truncate"}),
    "drop-column": frozenset({"drop-table", "add-not-null-without-default"}),
    "truncate": frozenset({"drop-table"}),
    "add-not-null-without-default": frozenset({"drop-column"}),
    "add-unique-index-concurrently": frozenset({"drop-column"}),
    "rename-table": frozenset({"drop-table", "drop-column"}),
}


@dataclass
class DependencyHint:
    rule_id: str
    related_rule_ids: List[str]
    message: str

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "related_rule_ids": self.related_rule_ids,
            "message": self.message,
        }


@dataclass
class DependencyReport:
    hints: List[DependencyHint] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.hints)

    @property
    def is_empty(self) -> bool:
        return not self.hints


def related_rules_for(rule_id: str) -> FrozenSet[str]:
    """Return the set of rule IDs related to the given rule."""
    return _RELATED_RULES.get(rule_id, frozenset())


def _active_rule_ids(issues: Sequence[Issue]) -> FrozenSet[str]:
    return frozenset(issue.rule_id for issue in issues)


def build_dependency_report(issues: Sequence[Issue]) -> DependencyReport:
    """Analyse issues and produce hints about co-occurring or related rules."""
    active = _active_rule_ids(issues)
    seen: set[str] = set()
    hints: List[DependencyHint] = []

    for rule_id in sorted(active):
        related = related_rules_for(rule_id) & active
        if not related:
            continue
        key = rule_id
        if key in seen:
            continue
        seen.add(key)
        related_list = sorted(related)
        msg = (
            f"Rule '{rule_id}' co-occurs with: {', '.join(related_list)}. "
            "Review these together to assess combined risk."
        )
        hints.append(DependencyHint(
            rule_id=rule_id,
            related_rule_ids=related_list,
            message=msg,
        ))

    return DependencyReport(hints=hints)
