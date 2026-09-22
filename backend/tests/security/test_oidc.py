from datetime import datetime, timedelta, timezone

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from napms.platform.security.oidc import (
    AuthenticationRejected,
    IdentityDependencyUnavailable,
    OidcConfig,
    OidcIdentityValidator,
)


NOW = datetime.now(timezone.utc)


class Fetcher:
    def __init__(self, *, issuer: str, jwk: dict) -> None:
        self.issuer = issuer
        self.jwk = jwk

    def fetch(self, url: str) -> dict:
        if url.endswith("/.well-known/openid-configuration"):
            return {"issuer": self.issuer, "jwks_uri": "https://id.example.test/jwks"}
        if url == "https://id.example.test/jwks":
            return {"keys": [self.jwk]}
        raise AssertionError(url)


def material():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_jwk = jwt.algorithms.RSAAlgorithm.to_jwk(private_key.public_key(), as_dict=True)
    public_jwk["kid"] = "key-1"
    return private_key, public_jwk


def config() -> OidcConfig:
    return OidcConfig(
        issuer="https://id.example.test",
        audience="napms",
        allowed_algorithms=("RS256",),
        permissions_claim="permissions",
        authority_claim="authority",
    )


def token(private_key, **claims):
    payload = {
        "iss": "https://id.example.test",
        "aud": "napms",
        "sub": "subject:alice",
        "exp": NOW + timedelta(minutes=5),
        **claims,
    }
    return jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "key-1"})


def test_valid_token_builds_principal_and_filters_unknown_grants() -> None:
    private_key, jwk = material()
    validator = OidcIdentityValidator(
        config=config(), fetcher=Fetcher(issuer="https://id.example.test", jwk=jwk)
    )
    value = validator.validate_bearer(
        token(
            private_key,
            permissions=["resource.read", "unknown.permission"],
            authority=[
                {"action": "access.request", "scope": "scope:a"},
                {"action": "unknown.action", "scope": "scope:b"},
            ],
        )
    )
    assert value.instance_permissions == frozenset({"resource.read"})
    assert [(item.action, item.scope) for item in value.authority_grants] == [
        ("access.request", "scope:a")
    ]


def test_invalid_signature_is_authentication_rejection() -> None:
    _, jwk = material()
    other_key, _ = material()
    validator = OidcIdentityValidator(
        config=config(), fetcher=Fetcher(issuer="https://id.example.test", jwk=jwk)
    )
    with pytest.raises(AuthenticationRejected):
        validator.validate_bearer(token(other_key))


def test_discovery_issuer_mismatch_is_dependency_failure() -> None:
    private_key, jwk = material()
    validator = OidcIdentityValidator(
        config=config(), fetcher=Fetcher(issuer="https://other.example.test", jwk=jwk)
    )
    with pytest.raises(IdentityDependencyUnavailable):
        validator.validate_bearer(token(private_key))


def test_malformed_identity_claims_fail_closed() -> None:
    private_key, jwk = material()
    validator = OidcIdentityValidator(
        config=config(), fetcher=Fetcher(issuer="https://id.example.test", jwk=jwk)
    )
    with pytest.raises(AuthenticationRejected):
        validator.validate_bearer(token(private_key, permissions="resource.read"))
    with pytest.raises(AuthenticationRejected):
        validator.validate_bearer(
            token(private_key, authority=[{"action": "access.request", "scope": ""}])
        )


def test_config_rejects_non_https_and_symmetric_algorithms() -> None:
    with pytest.raises(IdentityDependencyUnavailable):
        OidcConfig(
            issuer="http://id.example.test",
            audience="napms",
            allowed_algorithms=("RS256",),
            permissions_claim="permissions",
            authority_claim="authority",
        )
    with pytest.raises(ValueError):
        OidcConfig(
            issuer="https://id.example.test",
            audience="napms",
            allowed_algorithms=("HS256",),
            permissions_claim="permissions",
            authority_claim="authority",
        )
