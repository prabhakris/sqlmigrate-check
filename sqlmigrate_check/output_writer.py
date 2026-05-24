"""Output writer — abstracts writing formatted results to file or stdout."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, TextIO

from sqlmigrate_check.formatter import OutputFormat, format_result
from sqlmigrate_check.pipeline import ScanSummary
from sqlmigrate_check.reporter import Report


def _open_output(path: Optional[Path]) -> TextIO:
    """Return an open writable stream; caller is responsible for closing it."""
    if path is None:
        return sys.stdout
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.open("w", encoding="utf-8")


def write_report(
    report: Report,
    summary: ScanSummary,
    fmt: OutputFormat = OutputFormat.TEXT,
    output_path: Optional[Path] = None,
) -> None:
    """Format *report* / *summary* and write to *output_path* (or stdout)."""
    lines: list[str] = []
    for file_path, detection_result in summary.results.items():
        lines.append(format_result(detection_result, fmt, file_path=str(file_path)))

    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"

    stream = _open_output(output_path)
    try:
        stream.write(text)
    finally:
        if stream is not sys.stdout:
            stream.close()


def write_text(
    content: str,
    output_path: Optional[Path] = None,
) -> None:
    """Write arbitrary *content* to *output_path* (or stdout)."""
    stream = _open_output(output_path)
    try:
        stream.write(content)
        if not content.endswith("\n"):
            stream.write("\n")
    finally:
        if stream is not sys.stdout:
            stream.close()
