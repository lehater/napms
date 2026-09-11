"""Compatibility facade; process configuration lives in napms.bootstrap.config."""

from napms.bootstrap.config import (
    HttpRuntimeConfig,
    HttpServerConfig,
    LocalSeedConfig,
    load_http_runtime_config,
    load_local_seed_config,
)

__all__ = [
    "HttpRuntimeConfig",
    "HttpServerConfig",
    "LocalSeedConfig",
    "load_http_runtime_config",
    "load_local_seed_config",
]
