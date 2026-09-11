from datetime import datetime, timedelta, timezone

import pytest

from napms.runtime.auth import (
    AuthenticatedActor,
    InMemorySessionStore,
    LocalAuthenticationConfigurationError,
    LocalCredential,
    LocalPasswordAuthenticator,
    hash_local_password,
    verify_local_password,
)


def _credential(password="secret"):
    return LocalCredential(
        login="alexey",
        actor_id="actor-1",
        password_hash=hash_local_password(password, salt=b"0123456789abcdef"),
    )


def test_password_hash_round_trip_and_repr_does_not_expose_hash():
    encoded = hash_local_password("secret", salt=b"0123456789abcdef")
    assert verify_local_password("secret", encoded)
    assert not verify_local_password("wrong", encoded)
    assert "secret" not in encoded

    credential = _credential()
    assert credential.password_hash not in repr(credential)
    assert "<redacted>" in repr(credential)


def test_invalid_local_hash_is_rejected_at_configuration_boundary():
    with pytest.raises(LocalAuthenticationConfigurationError):
        LocalCredential(login="alexey", actor_id="actor-1", password_hash="plaintext")


def test_authenticator_returns_configured_actor_only_for_exact_credentials():
    authenticator = LocalPasswordAuthenticator(_credential())

    assert authenticator.authenticate(login="alexey", password="secret") == AuthenticatedActor(
        actor_id="actor-1", login="alexey"
    )
    assert authenticator.authenticate(login="alexey", password="wrong") is None
    assert authenticator.authenticate(login="other", password="secret") is None


def test_session_store_uses_opaque_server_side_identity_and_expires():
    now = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
    current = [now]
    store = InMemorySessionStore(
        ttl=timedelta(minutes=30),
        clock=lambda: current[0],
        new_session_id=lambda: "opaque-session",
    )
    actor = AuthenticatedActor(actor_id="actor-1", login="alexey")

    session_id = store.create(actor)
    assert session_id == "opaque-session"
    assert store.get(session_id) == actor
    assert store.get("actor-1") is None

    current[0] = now + timedelta(minutes=30)
    assert store.get(session_id) is None


def test_logout_invalidates_session():
    store = InMemorySessionStore(new_session_id=lambda: "opaque-session")
    actor = AuthenticatedActor(actor_id="actor-1", login="alexey")
    session_id = store.create(actor)

    store.delete(session_id)

    assert store.get(session_id) is None
