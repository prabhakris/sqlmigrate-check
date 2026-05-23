"""Central registry that maps rule IDs to their check functions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from sqlmigrate_check.detector import Issue

# Type alias for a rule check function: (sql: str, filepath: str) -> List[Issue]
RuleFunc = Callable[[str, str], List[Issue]]


@dataclass
class RuleEntry:
    rule_id: str
    description: str
    func: RuleFunc
    severity_default: str = "danger"


_REGISTRY: Dict[str, RuleEntry] = {}


def register(rule_id: str, description: str, severity_default: str = "danger") -> Callable[[RuleFunc], RuleFunc]:
    """Decorator to register a rule function under *rule_id*."""
    def decorator(func: RuleFunc) -> RuleFunc:
        _REGISTRY[rule_id] = RuleEntry(
            rule_id=rule_id,
            description=description,
            func=func,
            severity_default=severity_default,
        )
        return func
    return decorator


def get(rule_id: str) -> Optional[RuleEntry]:
    """Return the RuleEntry for *rule_id*, or None if not found."""
    return _REGISTRY.get(rule_id)


def all_rules() -> List[RuleEntry]:
    """Return all registered rules in insertion order."""
    return list(_REGISTRY.values())


def all_rule_ids() -> List[str]:
    """Return all registered rule IDs."""
    return list(_REGISTRY.keys())


def is_registered(rule_id: str) -> bool:
    """Return True if *rule_id* is present in the registry."""
    return rule_id in _REGISTRY


def clear() -> None:  # pragma: no cover – only used in tests
    """Remove all entries (useful for isolated unit tests)."""
    _REGISTRY.clear()
