"""Compatibility facade; executable HTTP entrypoint lives in napms.bootstrap.main."""

from napms.bootstrap.main import app, config, run

__all__ = ["app", "config", "run"]
