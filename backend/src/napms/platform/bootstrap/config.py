import os
from dataclasses import dataclass, field
from typing import Mapping
from urllib.parse import urlparse


class ConfigurationError(Exception):
    """Required runtime configuration is missing or invalid."""


@dataclass(frozen=True, slots=True)
class PostgresConfig:
    dsn: str = field(repr=False)

    def __post_init__(self) -> None:
        parsed = urlparse(self.dsn)
        if parsed.scheme not in {"postgres", "postgresql"}:
            raise ConfigurationError("PostgreSQL DSN must use postgres/postgresql scheme")
        if not parsed.hostname or not parsed.path or parsed.path == "/":
            raise ConfigurationError("PostgreSQL DSN requires host and database name")


@dataclass(frozen=True, slots=True)
class ApplicationConfig:
    environment: str
    postgres: PostgresConfig

    def __post_init__(self) -> None:
        if self.environment != "local-dev":
            raise ConfigurationError(
                "I7 greenfield composition is admitted only for local-dev"
            )


def load_application_config(
    environ: Mapping[str, str] | None = None,
) -> ApplicationConfig:
    source = os.environ if environ is None else environ
    environment = source.get("NAPMS_ENVIRONMENT")
    dsn = source.get("NAPMS_DATABASE_DSN")
    if not environment:
        raise ConfigurationError("NAPMS_ENVIRONMENT is required")
    if not dsn:
        raise ConfigurationError("NAPMS_DATABASE_DSN is required")
    return ApplicationConfig(
        environment=environment,
        postgres=PostgresConfig(dsn=dsn),
    )
