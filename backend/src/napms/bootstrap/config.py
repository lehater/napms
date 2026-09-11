import os
from dataclasses import dataclass, field
from typing import Mapping

from napms.composition.config import (
    ApplicationConfig,
    ConfigurationError,
    load_application_config,
)
from napms.runtime.auth import LocalCredential


@dataclass(frozen=True, slots=True)
class HttpServerConfig:
    host: str = "127.0.0.1"
    port: int = 8000

    def __post_init__(self) -> None:
        if not self.host:
            raise ConfigurationError("NAPMS_HTTP_HOST must be non-empty")
        if not 1 <= self.port <= 65535:
            raise ConfigurationError("NAPMS_HTTP_PORT must be between 1 and 65535")


@dataclass(frozen=True, slots=True)
class LocalSeedConfig:
    application: ApplicationConfig
    actor_id: str


@dataclass(frozen=True, slots=True)
class HttpRuntimeConfig:
    application: ApplicationConfig
    local_credential: LocalCredential = field(repr=False)
    server: HttpServerConfig = HttpServerConfig()


def load_http_runtime_config(
    environ: Mapping[str, str] | None = None,
) -> HttpRuntimeConfig:
    source = os.environ if environ is None else environ
    application = load_application_config(source)

    login = source.get("NAPMS_LOCAL_AUTH_LOGIN")
    actor_id = source.get("NAPMS_LOCAL_AUTH_ACTOR_ID")
    password_hash = source.get("NAPMS_LOCAL_AUTH_PASSWORD_HASH")
    if not login:
        raise ConfigurationError("NAPMS_LOCAL_AUTH_LOGIN is required")
    if not actor_id:
        raise ConfigurationError("NAPMS_LOCAL_AUTH_ACTOR_ID is required")
    if not password_hash:
        raise ConfigurationError("NAPMS_LOCAL_AUTH_PASSWORD_HASH is required")

    raw_port = source.get("NAPMS_HTTP_PORT", "8000")
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ConfigurationError("NAPMS_HTTP_PORT must be an integer") from exc

    try:
        credential = LocalCredential(
            login=login,
            actor_id=actor_id,
            password_hash=password_hash,
        )
    except ValueError as exc:
        raise ConfigurationError("invalid local authentication configuration") from exc

    return HttpRuntimeConfig(
        application=application,
        local_credential=credential,
        server=HttpServerConfig(
            host=source.get("NAPMS_HTTP_HOST", "127.0.0.1"),
            port=port,
        ),
    )


def load_local_seed_config(
    environ: Mapping[str, str] | None = None,
) -> LocalSeedConfig:
    source = os.environ if environ is None else environ
    application = load_application_config(source)
    actor_id = source.get("NAPMS_LOCAL_AUTH_ACTOR_ID")
    if not actor_id:
        raise ConfigurationError("NAPMS_LOCAL_AUTH_ACTOR_ID is required")
    return LocalSeedConfig(
        application=application,
        actor_id=actor_id,
    )
