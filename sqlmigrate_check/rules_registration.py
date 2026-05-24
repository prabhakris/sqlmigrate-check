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
# Built-in rule definitions: (rule_id, description, severity_default, handler)
# ---------------------------------------------------------------------------

_BUILTIN_RULES = [
    (
        "drop-table",
        "DROP TABLE destroys data permanently.",
        "danger",
        check_drop_table,
    ),
    (
        "drop-column",
        "DROP COLUMN removes a column and its data.",
        "danger",
        check_drop_column,
    ),
    (
        "truncate",
        "TRUNCATE removes all rows from a table.",
        "danger",
        check_truncate,
    ),
    (
        "add-not-null-without-default",
        "Adding a NOT NULL column without a DEFAULT blocks writes on large tables.",
        "danger",
        check_add_not_null_without_default,
    ),
    (
        "rename-table",
        "RENAME TABLE may break application queries that reference the old name.",
        "warning",
        check_rename_table,
    ),
]

# ---------------------------------------------------------------------------
# Register every built-in rule exactly once.
# ---------------------------------------------------------------------------

for _rule_id, _description, _severity, _handler in _BUILTIN_RULES:
    rule_registry.register(
        rule_id=_rule_id,
        description=_description,
        severity_default=_severity,
    )(_handler)
