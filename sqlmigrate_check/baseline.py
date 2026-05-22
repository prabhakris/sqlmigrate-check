"""Baseline management: record known issues to suppress in future runs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set

from sqlmigrate_check.detector import Issue

DEFAULT_BASELINE_FILE = ".sqlmigrate_baseline.json"


def _issue_fingerprint(filepath: str, issue: Issue) -> str:
    """Return a stable hash identifying a specific issue in a file."""
    raw = f"{filepath}:{issue.rule}:{issue.line_number}:{issue.line.strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def load_baseline(baseline_path: str | Path = DEFAULT_BASELINE_FILE) -> Set[str]:
    """Load fingerprints from an existing baseline file.

    Returns an empty set if the file does not exist.
    """
    path = Path(baseline_path)
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8") as fh:
        data: List[str] = json.load(fh)
    return set(data)


def save_baseline(
    fingerprints: Set[str],
    baseline_path: str | Path = DEFAULT_BASELINE_FILE,
) -> None:
    """Persist a set of fingerprints to disk as a JSON file."""
    path = Path(baseline_path)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(sorted(fingerprints), fh, indent=2)
        fh.write("\n")


def build_baseline_from_results(
    results: Dict[str, "DetectionResult"],  # noqa: F821
) -> Set[str]:
    """Create a full set of fingerprints from a mapping of filepath -> DetectionResult."""
    fingerprints: Set[str] = set()
    for filepath, result in results.items():
        for issue in result.issues:
            fingerprints.add(_issue_fingerprint(filepath, issue))
    return fingerprints


def filter_new_issues(
    filepath: str,
    issues: List[Issue],
    baseline: Set[str],
) -> List[Issue]:
    """Return only issues whose fingerprint is NOT present in the baseline."""
    return [
        issue
        for issue in issues
        if _issue_fingerprint(filepath, issue) not in baseline
    ]
