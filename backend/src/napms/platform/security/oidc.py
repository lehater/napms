from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Any, Protocol
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

import jwt

from napms.contexts.authority_management.domain.model import AuthorityGrant, Principal


KNOWN_INSTANCE_PERMISSIONS = frozenset(
    {
        "resource.read",
        "resource.write",
        "application.read",
        "application.write",
        "deployment.read",
        "deployment.write",
        "business.read",
        "business.write",
        "access.decide",
        "access.manage",
        "policy.read",
    }
)
KNOWN_SCOPED_ACTIONS = frozenset({"access.request", "policy.export"})


class AuthenticationRejected(Exception):
    pass


class IdentityDependencyUnavailable(Exception):
    pass


class JsonFetcher(Protocol):
    def fetch(self, url: str) -> dict[str, Any]: ...


class _HttpsRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _require_https(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class HttpsJsonFetcher:
    def fetch(self, url: str) -> dict[str, Any]:
        _require_https(url)
        opener = build_opener(_HttpsRedirectHandler())
        try:
            with opener.open(
                Request(url, headers={"Accept": "application/json"}), timeout=10
            ) as response:
                _require_https(response.geturl())
                payload = json.loads(response.read().decode("utf-8"))
        except IdentityDependencyUnavailable:
            raise
        except Exception as exc:
            raise IdentityDependencyUnavailable("OIDC metadata is unavailable") from exc
        if not isinstance(payload, dict):
            raise IdentityDependencyUnavailable("OIDC metadata is malformed")
        return payload


@dataclass(frozen=True)
class OidcConfig:
    issuer: str
    audience: str
    allowed_algorithms: tuple[str, ...]
    permissions_claim: str
    authority_claim: str

    def __post_init__(self) -> None:
        _require_https(self.issuer)
        if not self.audience.strip():
            raise ValueError("OIDC audience must be non-empty")
        if not self.allowed_algorithms:
            raise ValueError("at least one asymmetric JWT algorithm is required")
        for algorithm in self.allowed_algorithms:
            normalized = algorithm.upper()
            if normalized == "NONE" or normalized.startswith("HS"):
                raise ValueError("symmetric or unsigned JWT algorithms are forbidden")
        if not self.permissions_claim.strip() or not self.authority_claim.strip():
            raise ValueError("OIDC claim names must be non-empty")


class OidcIdentityValidator:
    def __init__(self, *, config: OidcConfig, fetcher: JsonFetcher | None = None) -> None:
        self._config = config
        self._fetcher = fetcher or HttpsJsonFetcher()

    def validate_bearer(self, token: str) -> Principal:
        if not token.strip():
            raise AuthenticationRejected("bearer token is missing")
        header = self._unverified_header(token)
        algorithm = header.get("alg")
        kid = header.get("kid")
        if not isinstance(algorithm, str) or algorithm not in self._config.allowed_algorithms:
            raise AuthenticationRejected("JWT algorithm is not allowed")
        if not isinstance(kid, str) or not kid.strip():
            raise AuthenticationRejected("JWT kid is required")

        discovery = self._fetch_discovery()
        jwks_uri = discovery.get("jwks_uri")
        if not isinstance(jwks_uri, str):
            raise IdentityDependencyUnavailable("OIDC jwks_uri is missing")
        _require_https(jwks_uri)
        jwks = self._fetcher.fetch(jwks_uri)
        keys = jwks.get("keys")
        if not isinstance(keys, list):
            raise IdentityDependencyUnavailable("OIDC JWKS is malformed")
        key_data = next(
            (
                candidate
                for candidate in keys
                if isinstance(candidate, dict) and candidate.get("kid") == kid
            ),
            None,
        )
        if key_data is None:
            raise AuthenticationRejected("JWT signing key is unknown")

        try:
            key = jwt.PyJWK.from_dict(key_data, algorithm=algorithm).key
            claims = jwt.decode(
                token,
                key=key,
                algorithms=[algorithm],
                audience=self._config.audience,
                issuer=self._config.issuer,
                options={"require": ["iss", "aud", "exp", "sub"]},
            )
        except jwt.PyJWTError as exc:
            raise AuthenticationRejected("JWT validation failed") from exc
        except Exception as exc:
            raise AuthenticationRejected("JWT key material is invalid") from exc
        return self._principal_from_claims(claims)

    def _fetch_discovery(self) -> dict[str, Any]:
        issuer = self._config.issuer.rstrip("/")
        discovery = self._fetcher.fetch(f"{issuer}/.well-known/openid-configuration")
        if discovery.get("issuer") != self._config.issuer:
            raise IdentityDependencyUnavailable("OIDC discovery issuer mismatch")
        return discovery

    @staticmethod
    def _unverified_header(token: str) -> dict[str, Any]:
        try:
            header = jwt.get_unverified_header(token)
        except jwt.PyJWTError as exc:
            raise AuthenticationRejected("JWT header is invalid") from exc
        if not isinstance(header, dict):
            raise AuthenticationRejected("JWT header is invalid")
        return header

    def _principal_from_claims(self, claims: dict[str, Any]) -> Principal:
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise AuthenticationRejected("JWT sub is invalid")

        permissions_raw = claims.get(self._config.permissions_claim, [])
        if not isinstance(permissions_raw, list) or not all(
            isinstance(value, str) for value in permissions_raw
        ):
            raise AuthenticationRejected("instance permissions claim is malformed")
        permissions = frozenset(
            value for value in permissions_raw if value in KNOWN_INSTANCE_PERMISSIONS
        )

        authority_raw = claims.get(self._config.authority_claim, [])
        if not isinstance(authority_raw, list):
            raise AuthenticationRejected("authority claim is malformed")
        grants: list[AuthorityGrant] = []
        for raw in authority_raw:
            if not isinstance(raw, dict):
                raise AuthenticationRejected("authority grant is malformed")
            action = raw.get("action")
            scope = raw.get("scope")
            if not isinstance(action, str) or not action.strip():
                raise AuthenticationRejected("authority action is malformed")
            if not isinstance(scope, str) or not scope.strip():
                raise AuthenticationRejected("authority scope is malformed")
            effective_from = _numeric_date(raw.get("effectiveFrom"), "effectiveFrom")
            effective_until = _numeric_date(raw.get("effectiveUntil"), "effectiveUntil")
            if (
                effective_from is not None
                and effective_until is not None
                and effective_until <= effective_from
            ):
                raise AuthenticationRejected("authority grant window is invalid")
            if action in KNOWN_SCOPED_ACTIONS:
                grants.append(
                    AuthorityGrant(
                        action=action,
                        scope=scope,
                        effective_from=effective_from,
                        effective_until=effective_until,
                    )
                )

        return Principal(
            subject=subject,
            instance_permissions=permissions,
            authority_grants=tuple(grants),
        )


def _require_https(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https" or not parsed.netloc:
        raise IdentityDependencyUnavailable("OIDC URL must be absolute HTTPS")


def _numeric_date(value: Any, field: str) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AuthenticationRejected(f"authority {field} must be NumericDate")
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc)
    except (OverflowError, OSError, ValueError) as exc:
        raise AuthenticationRejected(f"authority {field} is invalid") from exc
