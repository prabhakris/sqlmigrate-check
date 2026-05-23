"""Tests for sqlmigrate_check.exit_codes."""
import pytest

from sqlmigrate_check.exit_codes import ExitCode, exit_code_for_report


# ---------------------------------------------------------------------------
# ExitCode enum sanity checks
# ---------------------------------------------------------------------------

def test_exit_code_ok_is_zero():
    assert ExitCode.OK == 0


def test_exit_code_warnings_is_one():
    assert ExitCode.WARNINGS == 1


def test_exit_code_danger_is_two():
    assert ExitCode.DANGER == 2


def test_exit_code_config_error_is_three():
    assert ExitCode.CONFIG_ERROR == 3


def test_exit_code_io_error_is_four():
    assert ExitCode.IO_ERROR == 4


# ---------------------------------------------------------------------------
# exit_code_for_report
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fail_on", ["danger", "warning"])
def test_no_issues_returns_ok(fail_on):
    code = exit_code_for_report(has_danger=False, has_warnings=False, fail_on=fail_on)
    assert code == ExitCode.OK


@pytest.mark.parametrize("fail_on", ["danger", "warning"])
def test_danger_always_returns_danger_code(fail_on):
    code = exit_code_for_report(has_danger=True, has_warnings=False, fail_on=fail_on)
    assert code == ExitCode.DANGER


def test_warning_with_fail_on_warning_returns_warnings_code():
    code = exit_code_for_report(has_danger=False, has_warnings=True, fail_on="warning")
    assert code == ExitCode.WARNINGS


def test_warning_with_fail_on_danger_returns_ok():
    code = exit_code_for_report(has_danger=False, has_warnings=True, fail_on="danger")
    assert code == ExitCode.OK


def test_danger_takes_precedence_over_warning():
    code = exit_code_for_report(has_danger=True, has_warnings=True, fail_on="warning")
    assert code == ExitCode.DANGER


def test_exit_code_is_int_subclass():
    """ExitCode values can be used directly where an int is expected."""
    assert int(ExitCode.OK) == 0
    assert int(ExitCode.DANGER) == 2
