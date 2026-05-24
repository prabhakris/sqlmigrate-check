"""CLI helpers for severity-filter arguments."""
from __future__ import annotations

import argparse
from typing import Optional

from sqlmigrate_check.detector import Severity
from sqlmigrate_check.severity_filter import parse_severity

_DEFAULT_MIN_SEVERITY = "WARNING"


def add_severity_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach --min-severity argument to *parser*."""
    parser.add_argument(
        "--min-severity",
        dest="min_severity",
        default=_DEFAULT_MIN_SEVERITY,
        metavar="LEVEL",
        help=(
            "Minimum severity level to report. "
            "One of: WARNING, DANGER. Defaults to WARNING."
        ),
    )


def min_severity_from_args(args: argparse.Namespace) -> Optional[Severity]:
    """Extract and validate the --min-severity value from parsed *args*.

    Returns a Severity enum value, or None if the attribute is absent.
    Raises SystemExit with a helpful message on invalid input.
    """
    raw: str | None = getattr(args, "min_severity", None)
    if raw is None:
        return None
    try:
        return parse_severity(raw)
    except ValueError as exc:
        raise SystemExit(f"[sqlmigrate-check] {exc}") from exc
