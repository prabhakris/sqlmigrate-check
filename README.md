# sqlmigrate-check

> Pre-commit hook and CI utility to detect unsafe SQL migrations before deployment

---

## Installation

```bash
pip install sqlmigrate-check
```

Or with [pre-commit](https://pre-commit.com/):

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/your-org/sqlmigrate-check
    rev: v1.0.0
    hooks:
      - id: sqlmigrate-check
```

---

## Usage

Run against a directory of migration files:

```bash
sqlmigrate-check migrations/
```

Or check a single file:

```bash
sqlmigrate-check migrations/0042_add_users_index.sql
```

Example output:

```
✗ migrations/0042_add_users_index.sql
  [WARN] Line 3: DROP COLUMN detected — ensure column is no longer in use
  [ERROR] Line 7: Missing transaction block around schema change

1 file checked. 1 error, 1 warning found.
```

### CI Integration

Add to your pipeline to block unsafe migrations from reaching production:

```bash
sqlmigrate-check migrations/ --strict
```

The `--strict` flag causes the process to exit with a non-zero code on warnings as well as errors.

---

## Configuration

Place a `.sqlmigrate-check.toml` in your project root to customize rules:

```toml
[rules]
allow_drop_column = false
require_transactions = true
max_lock_timeout_ms = 5000
```

---

## License

MIT © [your-org](https://github.com/your-org)