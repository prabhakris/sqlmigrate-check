"""Rule documentation: human-readable descriptions and remediation hints for each rule."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class RuleDoc:
    rule_id: str
    title: str
    description: str
    remediation: str
    references: tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "description": self.description,
            "remediation": self.remediation,
            "references": list(self.references),
        }


_DOCS: Dict[str, RuleDoc] = {
    "drop-table": RuleDoc(
        rule_id="drop-table",
        title="DROP TABLE",
        description="Dropping a table is irreversible and will permanently delete all data.",
        remediation="Ensure the table is no longer referenced by any application code before dropping. "
                    "Consider renaming the table first and dropping it in a later release.",
        references=("https://www.postgresql.org/docs/current/sql-droptable.html",),
    ),
    "drop-column": RuleDoc(
        rule_id="drop-column",
        title="DROP COLUMN",
        description="Dropping a column removes it and all its data permanently.",
        remediation="Deploy application changes that stop referencing the column before running "
                    "this migration.",
        references=("https://www.postgresql.org/docs/current/sql-altertable.html",),
    ),
    "truncate": RuleDoc(
        rule_id="truncate",
        title="TRUNCATE",
        description="TRUNCATE removes all rows from a table without logging individual row deletions.",
        remediation="Use DELETE with a WHERE clause if partial removal is intended, or ensure "
                    "TRUNCATE is intentional and the table can be safely emptied.",
    ),
    "add-not-null-without-default": RuleDoc(
        rule_id="add-not-null-without-default",
        title="ADD NOT NULL column without DEFAULT",
        description="Adding a NOT NULL column without a DEFAULT value will fail on non-empty tables "
                    "in most databases.",
        remediation="Provide a DEFAULT value, or add the column as nullable first, backfill data, "
                    "then add the NOT NULL constraint.",
        references=("https://www.postgresql.org/docs/current/sql-altertable.html",),
    ),
}


def get_doc(rule_id: str) -> Optional[RuleDoc]:
    """Return the RuleDoc for *rule_id*, or None if not documented."""
    return _DOCS.get(rule_id)


def all_docs() -> Dict[str, RuleDoc]:
    """Return a copy of the full documentation registry."""
    return dict(_DOCS)


def format_doc_text(doc: RuleDoc) -> str:
    """Render a RuleDoc as a human-readable text block."""
    lines = [
        f"Rule:         {doc.rule_id}",
        f"Title:        {doc.title}",
        f"Description:  {doc.description}",
        f"Remediation:  {doc.remediation}",
    ]
    if doc.references:
        lines.append("References:")
        for ref in doc.references:
            lines.append(f"  - {ref}")
    return "\n".join(lines)
