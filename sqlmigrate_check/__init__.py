"""sqlmigrate-check: detect unsafe SQL migrations before deployment."""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sqlmigrate-check")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
