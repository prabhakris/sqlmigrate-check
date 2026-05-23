"""Exit codes for sqlmigrate-check CLI."""
from enum import IntEnum


class ExitCode(IntEnum):
    """Standard exit codes returned by the CLI."""

    OK = 0
    """No issues found; migration is safe."""

    WARNINGS = 1
    """One or more warning-level issues found."""

    DANGER = 2
    """One or more danger-level issues found."""

    CONFIG_ERROR = 3
    """Invalid configuration or bad CLI arguments."""

    IO_ERROR = 4
    """Could not read one or more migration files."""


def exit_code_for_report(has_danger: bool, has_warnings: bool, fail_on: str) -> ExitCode:
    """Determine the appropriate exit code given report state and *fail_on* policy.

    Parameters
    ----------
    has_danger:
        Whether the report contains at least one DANGER-level issue.
    has_warnings:
        Whether the report contains at least one WARNING-level issue.
    fail_on:
        Policy string – one of ``"danger"`` or ``"warning"``.
        When ``"warning"``, both warnings and dangers cause a non-zero exit.
        When ``"danger"``, only dangers cause a non-zero exit.

    Returns
    -------
    ExitCode
        The resolved exit code.
    """
    if has_danger:
        return ExitCode.DANGER
    if has_warnings and fail_on == "warning":
        return ExitCode.WARNINGS
    return ExitCode.OK
