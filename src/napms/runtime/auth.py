import base64
import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hmac import compare_digest
from typing import Callable


_SCRYPT_PREFIX = "scrypt-v1"
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_DKLEN = 32


class LocalAuthenticationConfigurationError(ValueError):
    """Local/test authentication configuration is invalid."""


def _require_text(value: str, *, field_name: str) -> None:
    if not value:
        raise LocalAuthenticationConfigurationError(f"{field_name} must be non-empty")


def _decode_password_hash(encoded: str) -> tuple[bytes, bytes]:
    parts = encoded.split("$")
    if len(parts) != 3 or parts[0] != _SCRYPT_PREFIX:
        raise LocalAuthenticationConfigurationError("unsupported local password hash format")
    try:
        salt = base64.urlsafe_b64decode(parts[1].encode("ascii"))
        expected = base64.urlsafe_b64decode(parts[2].encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise LocalAuthenticationConfigurationError("invalid local password hash encoding") from exc
    if len(salt) < 16 or len(expected) != _SCRYPT_DKLEN:
        raise LocalAuthenticationConfigurationError("invalid local password hash payload")
    return salt, expected


def hash_local_password(password: str, *, salt: bytes | None = None) -> str:
    """Create the supported local/test password hash; plaintext is never retained."""
    if not password:
        raise ValueError("password must be non-empty")
    actual_salt = secrets.token_bytes(16) if salt is None else salt
    if len(actual_salt) < 16:
        raise ValueError("salt must contain at least 16 bytes")
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=actual_salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_SCRYPT_DKLEN,
    )
    return "$".join(
        (
            _SCRYPT_PREFIX,
            base64.urlsafe_b64encode(actual_salt).decode("ascii"),
            base64.urlsafe_b64encode(digest).decode("ascii"),
        )
    )


def verify_local_password(password: str, encoded_hash: str) -> bool:
    salt, expected = _decode_password_hash(encoded_hash)
    actual = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_SCRYPT_DKLEN,
    )
    return compare_digest(actual, expected)


@dataclass(frozen=True, slots=True)
class LocalCredential:
    login: str
    actor_id: str
    password_hash: str

    def __post_init__(self) -> None:
        _require_text(self.login, field_name="login")
        _require_text(self.actor_id, field_name="actor_id")
        _decode_password_hash(self.password_hash)

    def __repr__(self) -> str:
        return (
            f"LocalCredential(login={self.login!r}, actor_id={self.actor_id!r}, "
            "password_hash=<redacted>)"
        )


@dataclass(frozen=True, slots=True)
class AuthenticatedActor:
    actor_id: str
    login: str


class LocalPasswordAuthenticator:
    """Replaceable controlled/test authenticator for one configured local actor."""

    def __init__(self, credential: LocalCredential) -> None:
        self._credential = credential

    def authenticate(self, *, login: str, password: str) -> AuthenticatedActor | None:
        # Verify the password even for a wrong login so login existence is not exposed
        # by a cheap-vs-expensive branch at this boundary.
        password_matches = verify_local_password(password, self._credential.password_hash)
        login_matches = compare_digest(login, self._credential.login)
        if not (login_matches and password_matches):
            return None
        return AuthenticatedActor(
            actor_id=self._credential.actor_id,
            login=self._credential.login,
        )


@dataclass(frozen=True, slots=True)
class SessionRecord:
    actor: AuthenticatedActor
    expires_at: datetime


class InMemorySessionStore:
    """Opaque server-side sessions for the bounded local/test runtime."""

    def __init__(
        self,
        *,
        ttl: timedelta = timedelta(hours=8),
        clock: Callable[[], datetime] | None = None,
        new_session_id: Callable[[], str] | None = None,
    ) -> None:
        if ttl <= timedelta(0):
            raise ValueError("session ttl must be positive")
        self._ttl = ttl
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._new_session_id = new_session_id or (lambda: secrets.token_urlsafe(32))
        self._sessions: dict[str, SessionRecord] = {}

    def create(self, actor: AuthenticatedActor) -> str:
        now = self._now()
        session_id = self._new_session_id()
        if not session_id:
            raise RuntimeError("session id generator returned an empty value")
        self._sessions[session_id] = SessionRecord(actor=actor, expires_at=now + self._ttl)
        return session_id

    def get(self, session_id: str | None) -> AuthenticatedActor | None:
        if not session_id:
            return None
        record = self._sessions.get(session_id)
        if record is None:
            return None
        if self._now() >= record.expires_at:
            self._sessions.pop(session_id, None)
            return None
        return record.actor

    def delete(self, session_id: str | None) -> None:
        if session_id:
            self._sessions.pop(session_id, None)

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise RuntimeError("session clock must return an offset-aware datetime")
        return value
