"""Parse and respect inline ignore comments in SQL migration files.

Supports:
    -- sqlmigrate-check: ignore
    -- sqlmigrate-check: ignore-next-line
"""
from __future__ import annotations

import re
from typing import Set

_INLINE_IGNORE = re.compile(
    r"--\s*sqlmigrate-check:\s*ignore\s*$", re.IGNORECASE
)
_NEXT_LINE_IGNORE = re.compile(
    r"--\s*sqlmigrate-check:\s*ignore-next-line\s*$", re.IGNORECASE
)


def ignored_lines(sql: str) -> Set[int]:
    """Return a set of 1-based line numbers that should be ignored.

    A line is ignored when:
    - it contains an inline ``-- sqlmigrate-check: ignore`` comment, OR
    - the *previous* line contains ``-- sqlmigrate-check: ignore-next-line``.
    """
    lines = sql.splitlines()
    result: Set[int] = set()
    for idx, line in enumerate(lines, start=1):
        if _INLINE_IGNORE.search(line):
            result.add(idx)
        if _NEXT_LINE_IGNORE.search(line):
            # mark the following line (if it exists)
            next_lineno = idx + 1
            if next_lineno <= len(lines):
                result.add(next_lineno)
    return result


def is_line_ignored(lineno: int, sql: str) -> bool:
    """Return True if *lineno* (1-based) should be suppressed."""
    return lineno in ignored_lines(sql)
