import pytest

from napms.bootstrap.config import load_http_runtime_config, load_local_seed_config
from napms.platform.bootstrap.config import ConfigurationError
from napms.runtime.auth import hash_local_password


def _environment():
    return {
        "NAPMS_ENVIRONMENT": "local-dev",
        "NAPMS_DATABASE_DSN": "postgresql://napms:secret@localhost:5432/napms",
        "NAPMS_LOCAL_AUTH_LOGIN": "alexey",
        "NAPMS_LOCAL_AUTH_ACTOR_ID": "actor-1",
        "NAPMS_LOCAL_AUTH_PASSWORD_HASH": hash_local_password(
            "secret", salt=b"0123456789abcdef"
        ),
    }


def test_http_config_builds_on_existing_application_config_without_secret_repr():
    config = load_http_runtime_config(_environment())

    assert config.application.environment == "local-dev"
    assert config.local_credential.login == "alexey"
    assert config.server.host == "127.0.0.1"
    assert config.server.port == 8000
    assert config.local_credential.password_hash not in repr(config)


@pytest.mark.parametrize(
    "missing",
    (
        "NAPMS_LOCAL_AUTH_LOGIN",
        "NAPMS_LOCAL_AUTH_ACTOR_ID",
        "NAPMS_LOCAL_AUTH_PASSWORD_HASH",
    ),
)
def test_http_config_requires_local_authentication_material(missing):
    environ = _environment()
    environ.pop(missing)

    with pytest.raises(ConfigurationError):
        load_http_runtime_config(environ)


@pytest.mark.parametrize("port", ("0", "65536", "not-a-number"))
def test_http_config_rejects_invalid_port(port):
    environ = _environment()
    environ["NAPMS_HTTP_PORT"] = port

    with pytest.raises(ConfigurationError):
        load_http_runtime_config(environ)



def test_local_seed_config_uses_typed_application_and_actor_only():
    config = load_local_seed_config(_environment())

    assert config.application.environment == "local-dev"
    assert config.actor_id == "actor-1"


def test_local_seed_config_requires_actor_id():
    environ = _environment()
    environ.pop("NAPMS_LOCAL_AUTH_ACTOR_ID")

    with pytest.raises(ConfigurationError):
        load_local_seed_config(environ)
