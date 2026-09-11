from napms.bootstrap.composition import build_local_dev_http_api
from napms.bootstrap.config import HttpRuntimeConfig
from napms.platform.bootstrap.config import ApplicationConfig, PostgresConfig
from napms.platform.auth.local import LocalCredential, hash_local_password


def _config(environment="local-dev"):
    return HttpRuntimeConfig(
        application=ApplicationConfig(
            environment=environment,
            postgres=PostgresConfig("postgresql://localhost/napms"),
        ),
        local_credential=LocalCredential(
            login="alexey",
            actor_id="actor-1",
            password_hash=hash_local_password(
                "secret",
                salt=b"0123456789abcdef",
            ),
        ),
    )


def test_local_dev_http_composition_builds_without_eager_postgres_access():
    app = build_local_dev_http_api(config=_config(), readiness_probe=lambda: True)

    assert app.title == "NAPMS API"
