"""Formatters for rule changelog output."""
from __future__ import annotations

import json
from typing import List

from sqlmigrate_check.rule_changelog import RuleChangelog, all_changelogs, get_changelog


def format_changelog_text(changelog: RuleChangelog) -> str:
    lines: List[str] = [f"Changelog for rule: {changelog.rule_id}"]
    if not changelog.entries:
        lines.append("  (no entries)")
        return "\n".join(lines)
    for entry in changelog.entries:
        breaking_tag = " [BREAKING]" if entry.breaking else ""
        lines.append(f"  {entry.version}{breaking_tag}: {entry.description}")
    return "\n".join(lines)


def format_changelog_json(changelog: RuleChangelog) -> str:
    return json.dumps(changelog.to_dict(), indent=2)


def format_all_changelogs_text() -> str:
    sections = [format_changelog_text(cl) for cl in all_changelogs()]
    return "\n\n".join(sections)


def format_all_changelogs_json() -> str:
    return json.dumps([cl.to_dict() for cl in all_changelogs()], indent=2)


def format_changelog_for_rule(rule_id: str, fmt: str = "text") -> str:
    changelog = get_changelog(rule_id)
    if changelog is None:
        if fmt == "json":
            return json.dumps({"error": f"No changelog found for rule '{rule_id}'"})
        return f"No changelog found for rule '{rule_id}'."
    if fmt == "json":
        return format_changelog_json(changelog)
    return format_changelog_text(changelog)
