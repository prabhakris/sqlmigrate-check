"""Parse structured annotations embedded in SQL migration comments.

Annotations take the form:  -- @sqlmigrate:<key>=<value>
Example:
    -- @sqlmigrate:ticket=PROJ-123
    -- @sqlmigrate:reviewed-by=alice
    ALTER TABLE users DROP COLUMN legacy_flag;
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

_ANNOTATION_RE = re.compile(
    r"--\s*@sqlmigrate:(?P<key>[\w-]+)=(?P<value>[^\n]+)",
    re.IGNORECASE,
)


@dataclass
class Annotation:
    """A single key/value annotation extracted from a SQL comment."""

    key: str
    value: str
    line_number: int

    def __repr__(self) -> str:  # pragma: no cover
        return f"Annotation(key={self.key!r}, value={self.value!r}, line={self.line_number})"


@dataclass
class AnnotationMap:
    """All annotations found in a single migration file."""

    annotations: List[Annotation] = field(default_factory=list)

    def get(self, key: str) -> List[str]:
        """Return all values for *key* (case-insensitive)."""
        key_lower = key.lower()
        return [a.value.strip() for a in self.annotations if a.key.lower() == key_lower]

    def first(self, key: str, default: str = "") -> str:
        """Return the first value for *key*, or *default* if absent."""
        values = self.get(key)
        return values[0] if values else default

    def as_dict(self) -> Dict[str, List[str]]:
        """Return a plain dict mapping each key to its list of values."""
        result: Dict[str, List[str]] = {}
        for annotation in self.annotations:
            result.setdefault(annotation.key.lower(), []).append(annotation.value.strip())
        return result


def parse_annotations(sql: str) -> AnnotationMap:
    """Extract all @sqlmigrate annotations from *sql* text.

    Args:
        sql: Raw SQL content of a migration file.

    Returns:
        An :class:`AnnotationMap` containing every annotation found.
    """
    annotations: List[Annotation] = []
    for line_number, line in enumerate(sql.splitlines(), start=1):
        match = _ANNOTATION_RE.search(line)
        if match:
            annotations.append(
                Annotation(
                    key=match.group("key").lower(),
                    value=match.group("value"),
                    line_number=line_number,
                )
            )
    return AnnotationMap(annotations=annotations)
