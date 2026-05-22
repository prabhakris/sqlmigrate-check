"""File system scanner for discovering SQL migration files."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator, List, Optional


DEFAULT_PATTERNS = ("*.sql", "*migration*.py", "*migrate*.py")


def iter_migration_files(
    paths: List[str],
    extensions: Optional[tuple[str, ...]] = None,
    recursive: bool = True,
) -> Iterator[Path]:
    """Yield migration file paths discovered under the given root paths."""
    if extensions is None:
        extensions = (".sql", ".py")

    for raw_path in paths:
        root = Path(raw_path)
        if root.is_file():
            if root.suffix in extensions:
                yield root
        elif root.is_dir():
            pattern = "**/*" if recursive else "*"
            for candidate in root.glob(pattern):
                if candidate.is_file() and candidate.suffix in extensions:
                    yield candidate


def read_migration_file(path: Path) -> str:
    """Read and return the text content of a migration file."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"Cannot read migration file '{path}': {exc}") from exc


def collect_sql_from_file(path: Path) -> str:
    """Return SQL content extracted from a file.

    For .sql files the content is returned as-is.
    For .py files a naive extraction of string literals following
    common Django/Alembic patterns is performed.
    """
    content = read_migration_file(path)
    if path.suffix == ".sql":
        return content
    # Extract raw SQL strings from Python migration files
    import re
    sql_blocks = re.findall(
        r'(?:op\.execute|cursor\.execute|connection\.execute)\s*\(\s*[\'\"]\s*([^\'"]+)[\'\"]',
        content,
        re.IGNORECASE | re.DOTALL,
    )
    return "\n".join(sql_blocks)
