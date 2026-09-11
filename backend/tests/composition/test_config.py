import pytest

from napms.composition.config import (
    ApplicationConfig,
    ConfigurationError,
    PostgresConfig,
    load_application_config,
)


def test_loader_builds_one_typed_local_dev_config():
    config = load_application_config(
        {
            "NAPMS_ENVIRONMENT": "local-dev",
            "NAPMS_DATABASE_DSN": "postgresql://napms:secret@localhost:5432/napms",
        }
    )

    assert config.environment == "local-dev"
    assert config.postgres.dsn.endswith("/napms")
    assert "secret" not in repr(config.postgres)


@pytest.mark.parametrize(
    "environ",
    [
        {},
        {"NAPMS_ENVIRONMENT": "local-dev"},
        {"NAPMS_DATABASE_DSN": "postgresql://localhost/napms"},
    ],
)
def test_missing_required_configuration_fails_startup(environ):
    with pytest.raises(ConfigurationError):
        load_application_config(environ)


@pytest.mark.parametrize(
    "dsn",
    [
        "mssql://localhost/napms",
        "sqlite:///napms.db",
        "postgresql:///napms",
        "postgresql://localhost",
    ],
)
def test_non_postgres_or_incomplete_dsn_is_rejected(dsn):
    with pytest.raises(ConfigurationError):
        PostgresConfig(dsn=dsn)


def test_i7_composition_does_not_silently_expand_beyond_local_dev():
    with pytest.raises(ConfigurationError):
        ApplicationConfig(
            environment="production",
            postgres=PostgresConfig("postgresql://localhost/napms"),
        )
