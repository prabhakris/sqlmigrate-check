"""Wire up the built-in rules from rules.py into the central registry.

Importing this module has the side-effect of populating the registry.
The CLI and pipeline should import this module before running checks.
"""
from __future__ import annotations

from sqlmigrate_check import rule_registry
from sqlmigrate_check.rules import (
    check_add_not_null_without_default,
    check_drop_column,
    check_drop_table,
    check_rename_table,
    check_truncate,
)

# ---------------------------------------------------------------------------
# Register every built-in rule exactly once.
# ---------------------------------------------------------------------------

rule_registry.register(
    rule_id="drop-table",
    description="DROP TABLE destroys data permanently.",
    severity_default="danger",
)(check_drop_table)

rule_registry.register(
    rule_id="drop-column",
    description="DROP COLUMN removes a column and its data.",
    severity_default="danger",
)(check_drop_column)

rule_registry.register(
    rule_id="truncate",
    description="TRUNCATE removes all rows from a table.",
    severity_default="danger",
)(check_truncate)

rule_registry.register(
    rule_id="add-not-null-without-default",
    description="Adding a NOT NULL column without a DEFAULT blocks writes on large tables.",
    severity_default="danger",
)(check_add_not_null_without_default)

rule_registry.register(
    rule_id="rename-table",
    description="RENAME TABLE may break application queries that reference the old name.",
    severity_default="warning",
)(check_rename_table)
