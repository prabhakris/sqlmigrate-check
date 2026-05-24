"""Tag-based categorisation for rules.

Each rule can carry zero or more string tags (e.g. ``"destructive"``,
``"locking"``, ``"data-loss"``).  This module provides helpers to query
the tag catalogue and filter issues by tag.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List

from sqlmigrate_check.detector import Issue

# ---------------------------------------------------------------------------
# Tag catalogue – maps rule_id -> frozenset of tags
# ---------------------------------------------------------------------------

_RULE_TAGS: Dict[str, FrozenSet[str]] = {
    "drop_table": frozenset({"destructive", "data-loss", "ddl"}),
    "drop_column": frozenset({"destructive", "data-loss", "ddl"}),
    "truncate": frozenset({"destructive", "data-loss", "dml"}),
    "add_not_null_without_default": frozenset({"locking", "ddl", "compatibility"}),
    "create_index_without_concurrent": frozenset({"locking", "ddl"}),
    "rename_table": frozenset({"ddl", "compatibility"}),
}


def tags_for_rule(rule_id: str) -> FrozenSet[str]:
    """Return the tag set for *rule_id*, or an empty frozenset if unknown."""
    return _RULE_TAGS.get(rule_id, frozenset())


def all_tags() -> FrozenSet[str]:
    """Return the union of every tag used across all registered rules."""
    result: set[str] = set()
    for tags in _RULE_TAGS.values():
        result |= tags
    return frozenset(result)


def rules_with_tag(tag: str) -> List[str]:
    """Return a sorted list of rule IDs that carry *tag*."""
    return sorted(rid for rid, tags in _RULE_TAGS.items() if tag in tags)


# ---------------------------------------------------------------------------
# Issue filtering
# ---------------------------------------------------------------------------


@dataclass
class TagFilterResult:
    matched: List[Issue] = field(default_factory=list)
    unmatched: List[Issue] = field(default_factory=list)

    @property
    def total_matched(self) -> int:
        return len(self.matched)


def filter_issues_by_tag(
    issues: Iterable[Issue],
    tags: Iterable[str],
) -> TagFilterResult:
    """Partition *issues* into those whose rule carries ANY of *tags*."""
    tag_set = frozenset(tags)
    result = TagFilterResult()
    for issue in issues:
        rule_tags = tags_for_rule(issue.rule_id)
        if rule_tags & tag_set:
            result.matched.append(issue)
        else:
            result.unmatched.append(issue)
    return result
