"""Compatibility facade; executable composition lives in napms.bootstrap.composition."""

from napms.bootstrap.composition import build_http_api, build_local_dev_http_api

__all__ = ["build_http_api", "build_local_dev_http_api"]
