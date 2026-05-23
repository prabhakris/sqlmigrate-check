"""CLI helpers for emitting scan metrics alongside normal output."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from sqlmigrate_check.metrics import ScanMetrics
from sqlmigrate_check.metrics_formatter import format_metrics_json, format_metrics_text


def emit_metrics(
    metrics: ScanMetrics,
    *,
    fmt: str = "text",
    output_file: Optional[str] = None,
) -> None:
    """Write metrics to *output_file* (or stdout) in *fmt* format.

    Parameters
    ----------
    metrics:
        The populated :class:`ScanMetrics` instance.
    fmt:
        ``"text"`` (default) or ``"json"``.
    output_file:
        File path to write to.  ``None`` means *stdout*.
    """
    if fmt == "json":
        rendered = format_metrics_json(metrics)
    else:
        rendered = format_metrics_text(metrics)

    if output_file is None:
        print(rendered, file=sys.stdout)
    else:
        Path(output_file).write_text(rendered, encoding="utf-8")


def add_metrics_arguments(parser: object) -> None:  # pragma: no cover
    """Attach ``--metrics`` / ``--metrics-file`` flags to an argparse parser."""
    import argparse

    p: argparse.ArgumentParser = parser  # type: ignore[assignment]
    p.add_argument(
        "--metrics",
        choices=["text", "json"],
        default=None,
        metavar="FORMAT",
        help="Emit scan metrics in the given format (text or json).",
    )
    p.add_argument(
        "--metrics-file",
        default=None,
        metavar="PATH",
        help="Write metrics to PATH instead of stdout.",
    )
