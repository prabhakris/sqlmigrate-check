"""Allowlist support: skip specific rules for specific files or patterns."""
from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set


@dataclass
class Allowlist:
    """Maps glob patterns to sets of rule IDs that should be skipped."""

    # e.g. {"migrations/legacy_*.sql": {"drop-table", "truncate"}}
    entries: Dict[str, Set[str]] = field(default_factory=dict)

    def is_allowed(self, filepath: str | Path, rule_id: str) -> bool:
        """Return True if *rule_id* is allowlisted for *filepath*."""
        fp = str(filepath)
        for pattern, rules in self.entries.items():
            if fnmatch.fnmatch(fp, pattern) or fnmatch.fnmatch(Path(fp).name, pattern):
                if "*" in rules or rule_id in rules:
                    return True
        return False

    def allowed_rules_for(self, filepath: str | Path) -> Set[str]:
        """Return the union of all rule IDs allowlisted for *filepath*."""
        fp = str(filepath)
        result: Set[str] = set()
        for pattern, rules in self.entries.items():
            if fnmatch.fnmatch(fp, pattern) or fnmatch.fnmatch(Path(fp).name, pattern):
                result |= rules
        return result


def _parse_rule_list(raw: str) -> Set[str]:
    """Parse a comma-separated list of rule IDs, supporting '*' wildcard."""
    return {r.strip() for r in raw.split(",") if r.strip()}


def allowlist_from_config(raw: Dict[str, str]) -> Allowlist:
    """Build an :class:`Allowlist` from a plain dict (e.g. from config file).

    Expected format::

        {"migrations/legacy_*.sql": "drop-table,truncate",
         "migrations/initial.sql": "*"}
    """
    entries: Dict[str, Set[str]] = {}
    for pattern, rule_str in raw.items():
        entries[pattern] = _parse_rule_list(rule_str)
    return Allowlist(entries=entries)
