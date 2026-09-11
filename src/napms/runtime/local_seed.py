"""Compatibility facade; local seed entrypoint lives in napms.bootstrap.local_seed."""

from napms.bootstrap.local_seed import run, seed_local_demo

__all__ = ["run", "seed_local_demo"]
