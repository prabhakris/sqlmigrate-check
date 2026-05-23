"""Tests for sqlmigrate_check.watch_cli."""
from __future__ import annotations

import argparse
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sqlmigrate_check.watch_cli import (
    add_watch_arguments,
    build_watch_session,
    watch_callback_factory,
)
from sqlmigrate_check.watch import WatchSession


# ---------------------------------------------------------------------------
# add_watch_arguments
# ---------------------------------------------------------------------------


def test_add_watch_arguments_defaults() -> None:
    parser = argparse.ArgumentParser()
    add_watch_arguments(parser)
    args = parser.parse_args([])
    assert args.watch is False
    assert args.watch_interval == pytest.approx(1.0)


def test_add_watch_arguments_enabled() -> None:
    parser = argparse.ArgumentParser()
    add_watch_arguments(parser)
    args = parser.parse_args(["--watch", "--watch-interval", "2.5"])
    assert args.watch is True
    assert args.watch_interval == pytest.approx(2.5)


# ---------------------------------------------------------------------------
# build_watch_session
# ---------------------------------------------------------------------------


def test_build_watch_session_returns_session(tmp_path: Path) -> None:
    f = tmp_path / "m.sql"
    f.write_text("SELECT 1;")
    cb = MagicMock()
    session = build_watch_session([f], cb, interval=0.5)
    assert isinstance(session, WatchSession)


# ---------------------------------------------------------------------------
# watch_callback_factory
# ---------------------------------------------------------------------------


def test_callback_factory_calls_rescan(capsys: pytest.CaptureFixture) -> None:
    rescan = MagicMock()
    cb = watch_callback_factory(rescan)
    changed = [Path("migrations/0001.sql")]
    cb(changed)
    rescan.assert_called_once()


def test_callback_factory_prints_changed_files(
    capsys: pytest.CaptureFixture,
) -> None:
    rescan = MagicMock()
    cb = watch_callback_factory(rescan)
    cb([Path("a.sql"), Path("b.sql")])
    out = capsys.readouterr().out
    assert "a.sql" in out
    assert "b.sql" in out
