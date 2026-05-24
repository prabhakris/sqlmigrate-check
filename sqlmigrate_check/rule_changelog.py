"""Rule changelog: tracks version history and migration notes for each rule."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ChangelogEntry:
    version: str
    description: str
    breaking: bool = False

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "description": self.description,
            "breaking": self.breaking,
        }


@dataclass
class RuleChangelog:
    rule_id: str
    entries: List[ChangelogEntry] = field(default_factory=list)

    def latest(self) -> Optional[ChangelogEntry]:
        return self.entries[0] if self.entries else None

    def has_breaking_changes(self) -> bool:
        return any(e.breaking for e in self.entries)

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "entries": [e.to_dict() for e in self.entries],
            "has_breaking_changes": self.has_breaking_changes(),
        }


_CHANGELOGS: Dict[str, RuleChangelog] = {
    "drop-table": RuleChangelog(
        rule_id="drop-table",
        entries=[
            ChangelogEntry("1.1.0", "Improved detection for quoted table names."),
            ChangelogEntry("1.0.0", "Initial rule added.", breaking=False),
        ],
    ),
    "drop-column": RuleChangelog(
        rule_id="drop-column",
        entries=[
            ChangelogEntry("1.0.0", "Initial rule added."),
        ],
    ),
    "truncate": RuleChangelog(
        rule_id="truncate",
        entries=[
            ChangelogEntry("1.2.0", "Now flags TRUNCATE ... RESTART IDENTITY variants.", breaking=True),
            ChangelogEntry("1.0.0", "Initial rule added."),
        ],
    ),
    "add-not-null-without-default": RuleChangelog(
        rule_id="add-not-null-without-default",
        entries=[
            ChangelogEntry("1.1.0", "Handles multi-column ADD COLUMN statements."),
            ChangelogEntry("1.0.0", "Initial rule added."),
        ],
    ),
}


def get_changelog(rule_id: str) -> Optional[RuleChangelog]:
    return _CHANGELOGS.get(rule_id)


def all_changelogs() -> List[RuleChangelog]:
    return list(_CHANGELOGS.values())
