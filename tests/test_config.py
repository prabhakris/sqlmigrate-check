"""Tests for sqlmigrate_check.config."""
from __future__ import annotations

import pytest

from sqlmigrate_check.config import Config, _config_from_dict, load_config


# ---------------------------------------------------------------------------
# Unit tests for Config dataclass
# ---------------------------------------------------------------------------

def test_default_config_values():
    cfg = Config()
    assert cfg.fail_on == "danger"
    assert cfg.exclude == []
    assert cfg.baseline_file is None
    assert cfg.recursive is True


def test_config_invalid_fail_on_raises():
    with pytest.raises(ValueError, match="Invalid fail_on"):
        Config(fail_on="critical")


def test_config_from_dict_full():
    cfg = _config_from_dict({
        "fail_on": "warning",
        "exclude": ["**/seed_*.sql"],
        "baseline_file": ".baseline.json",
        "recursive": False,
    })
    assert cfg.fail_on == "warning"
    assert cfg.exclude == ["**/seed_*.sql"]
    assert cfg.baseline_file == ".baseline.json"
    assert cfg.recursive is False


def test_config_from_dict_empty_uses_defaults():
    cfg = _config_from_dict({})
    assert cfg.fail_on == "danger"
    assert cfg.exclude == []
    assert cfg.baseline_file is None
    assert cfg.recursive is True


# ---------------------------------------------------------------------------
# Integration tests using tmp_path
# ---------------------------------------------------------------------------

def test_load_config_returns_defaults_when_no_file(tmp_path):
    cfg = load_config(start_dir=tmp_path)
    assert cfg == Config()


def test_load_config_from_dedicated_toml(tmp_path):
    toml_file = tmp_path / ".sqlmigrate-check.toml"
    toml_file.write_text(
        'fail_on = "warning"\nexclude = ["**/seed_*.sql"]\n',
        encoding="utf-8",
    )
    cfg = load_config(start_dir=tmp_path)
    assert cfg.fail_on == "warning"
    assert cfg.exclude == ["**/seed_*.sql"]


def test_load_config_from_pyproject_toml(tmp_path):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(
        "[tool.sqlmigrate-check]\nfail_on = \"warning\"\nrecursive = false\n",
        encoding="utf-8",
    )
    cfg = load_config(start_dir=tmp_path)
    assert cfg.fail_on == "warning"
    assert cfg.recursive is False


def test_load_config_pyproject_without_section_returns_defaults(tmp_path):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text("[tool.black]\nline-length = 88\n", encoding="utf-8")
    cfg = load_config(start_dir=tmp_path)
    assert cfg == Config()


def test_load_config_searches_parent_directories(tmp_path):
    (tmp_path / ".sqlmigrate-check.toml").write_text(
        'fail_on = "warning"\n', encoding="utf-8"
    )
    nested = tmp_path / "migrations" / "v2"
    nested.mkdir(parents=True)
    cfg = load_config(start_dir=nested)
    assert cfg.fail_on == "warning"
