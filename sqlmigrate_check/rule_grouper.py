"""Group issues by rule ID for summary reporting."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from sqlmigrate_check.detector import Issue, Severity


@dataclass
class RuleGroup:
    """All issues that share the same rule_id."""

    rule_id: str
    issues: List[Issue] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.issues)

    @property
    def highest_severity(self) -> Severity:
        """Return the most severe Severity found in the group."""
        if any(i.severity == Severity.DANGER for i in self.issues):
            return Severity.DANGER
        if any(i.severity == Severity.WARNING for i in self.issues):
            return Severity.WARNING
        return Severity.INFO

    @property
    def affected_files(self) -> List[str]:
        """Sorted, deduplicated list of file paths that contain this rule's issues."""
        return sorted({i.filepath for i in self.issues})


def group_by_rule(issues: Sequence[Issue]) -> Dict[str, RuleGroup]:
    """Return a mapping of rule_id -> RuleGroup for the given issues."""
    groups: Dict[str, RuleGroup] = defaultdict(lambda: RuleGroup(rule_id=""))
    for issue in issues:
        rid = issue.rule_id
        if rid not in groups:
            groups[rid] = RuleGroup(rule_id=rid)
        else:
            # fix up the sentinel created by defaultdict
            if groups[rid].rule_id == "":
                groups[rid].rule_id = rid
        groups[rid].rule_id = rid
        groups[rid].issues.append(issue)
    return dict(groups)


def sorted_groups(groups: Dict[str, RuleGroup]) -> List[RuleGroup]:
    """Return groups sorted by (severity desc, count desc, rule_id asc)."""
    severity_order = {Severity.DANGER: 0, Severity.WARNING: 1, Severity.INFO: 2}
    return sorted(
        groups.values(),
        key=lambda g: (severity_order[g.highest_severity], -g.count, g.rule_id),
    )
