"""Provides human-readable explanations and remediation advice for rule violations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlmigrate_check.detector import Issue, Severity


@dataclass(frozen=True)
class RuleExplanation:
    rule_id: str
    title: str
    explanation: str
    remediation: str
    reference: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "explanation": self.explanation,
            "remediation": self.remediation,
            "reference": self.reference,
        }


_EXPLANATIONS: dict[str, RuleExplanation] = {
    "drop_table": RuleExplanation(
        rule_id="drop_table",
        title="DROP TABLE destroys data permanently",
        explanation=(
            "Dropping a table removes all rows and the schema definition "
            "immediately. This operation cannot be rolled back in most databases "
            "once the transaction commits."
        ),
        remediation=(
            "Rename the table first and keep it for at least one release cycle. "
            "Only drop it after confirming no application code references it."
        ),
        reference="https://www.postgresql.org/docs/current/sql-droptable.html",
    ),
    "drop_column": RuleExplanation(
        rule_id="drop_column",
        title="DROP COLUMN removes data permanently",
        explanation=(
            "Dropping a column deletes all data stored in that column across every "
            "row. Concurrent reads may also fail if the application still references "
            "the column name."
        ),
        remediation=(
            "Remove application references to the column in a prior deployment, "
            "then drop the column in a subsequent migration."
        ),
        reference="https://www.postgresql.org/docs/current/sql-altertable.html",
    ),
    "truncate": RuleExplanation(
        rule_id="truncate",
        title="TRUNCATE removes all rows without logging individual deletes",
        explanation=(
            "TRUNCATE is a fast bulk-delete that bypasses row-level triggers and "
            "cannot be easily audited. On some databases it acquires an exclusive "
            "table lock, blocking concurrent reads and writes."
        ),
        remediation=(
            "Use a batched DELETE with a WHERE clause if you need to preserve "
            "audit trails or avoid lock contention."
        ),
        reference=None,
    ),
    "add_not_null_without_default": RuleExplanation(
        rule_id="add_not_null_without_default",
        title="Adding NOT NULL column without DEFAULT blocks writes on large tables",
        explanation=(
            "Adding a NOT NULL column without a DEFAULT requires a full-table rewrite "
            "on older PostgreSQL versions and will reject any INSERT that omits the "
            "column before a default is set."
        ),
        remediation=(
            "Add the column as nullable first, back-fill values, then apply the "
            "NOT NULL constraint. Alternatively supply a server-side DEFAULT."
        ),
        reference="https://www.postgresql.org/docs/current/sql-altertable.html",
    ),
}


def get_explanation(rule_id: str) -> Optional[RuleExplanation]:
    """Return the RuleExplanation for *rule_id*, or None if unknown."""
    return _EXPLANATIONS.get(rule_id)


def explain_issue(issue: Issue) -> str:
    """Return a formatted explanation string for a single Issue."""
    exp = get_explanation(issue.rule_id)
    if exp is None:
        return f"No detailed explanation available for rule '{issue.rule_id}'."
    lines = [
        f"Rule   : {exp.rule_id}",
        f"Title  : {exp.title}",
        f"Why    : {exp.explanation}",
        f"Fix    : {exp.remediation}",
    ]
    if exp.reference:
        lines.append(f"Ref    : {exp.reference}")
    return "\n".join(lines)
