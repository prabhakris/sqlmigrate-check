"""Configuration loading for sqlmigrate-check.

Supports reading settings from pyproject.toml or a dedicated
.sqlmigrate-check.toml file.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

_CONFIG_FILES = [".sqlmigrate-check.toml", "pyproject.toml"]
_PYPROJECT_SECTION = "tool.sqlmigrate-check"


@dataclass
class Config:
    """Runtime configuration for sqlmigrate-check."""

    # Severity threshold: 'warning' | 'danger'
    fail_on: str = "danger"
    # Extra glob patterns to ignore (e.g. ["**/seed_*.sql"])
    exclude: List[str] = field(default_factory=list)
    # Path to baseline file
    baseline_file: Optional[str] = None
    # Recurse into subdirectories when scanning
    recursive: bool = True

    def __post_init__(self) -> None:
        if self.fail_on not in ("warning", "danger"):
            raise ValueError(f"Invalid fail_on value: {self.fail_on!r}")


def _extract_section(data: dict) -> dict:
    """Navigate dotted key path inside *data*, return {} if missing."""
    keys = _PYPROJECT_SECTION.split(".")
    node: dict = data
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            return {}
        node = node[key]
    return node if isinstance(node, dict) else {}


def load_config(start_dir: Optional[Path] = None) -> Config:
    """Search *start_dir* (default: cwd) and parents for a config file.

    Returns a default :class:`Config` when no file is found.
    """
    search_dir = Path(start_dir) if start_dir else Path.cwd()

    for directory in [search_dir, *search_dir.parents]:
        for filename in _CONFIG_FILES:
            candidate = directory / filename
            if not candidate.is_file():
                continue
            with candidate.open("rb") as fh:
                raw = tomllib.load(fh)
            section = raw if filename != "pyproject.toml" else _extract_section(raw)
            if not section and filename == "pyproject.toml":
                continue
            return _config_from_dict(section)

    return Config()


def _config_from_dict(data: dict) -> Config:
    return Config(
        fail_on=data.get("fail_on", "danger"),
        exclude=list(data.get("exclude", [])),
        baseline_file=data.get("baseline_file"),
        recursive=bool(data.get("recursive", True)),
    )
