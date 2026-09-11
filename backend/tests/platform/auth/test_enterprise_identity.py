import pytest

from napms.platform.auth.enterprise_identity import (
    ActorIdentityMapping,
    ActorIdentityResolution,
    ActorIdentityResolutionKind,
    DeterministicActorIdentityResolver,
    UnknownActorIdentityResolver,
    VerifiedExternalIdentity,
)


def test_verified_external_identity_requires_qualified_subject() -> None:
    with pytest.raises(ValueError, match="provider_id"):
        VerifiedExternalIdentity(provider_id="", subject_id="subject-1")
    with pytest.raises(ValueError, match="subject_id"):
        VerifiedExternalIdentity(provider_id="issuer-a", subject_id="")


def test_exact_mapping_establishes_one_napms_actor() -> None:
    resolver = DeterministicActorIdentityResolver(
        [
            ActorIdentityMapping(
                provider_id="issuer-a",
                subject_id="subject-17",
                actor_id="alice",
                login="alice@example.test",
            )
        ]
    )

    outcome = resolver.resolve(
        VerifiedExternalIdentity(
            provider_id="issuer-a",
            subject_id="subject-17",
            login_hint="untrusted-display@example.test",
        )
    )

    assert outcome.kind is ActorIdentityResolutionKind.MAPPED
    assert outcome.actor is not None
    assert outcome.actor.actor_id == "alice"
    assert outcome.actor.login == "alice@example.test"


def test_login_hint_does_not_create_or_change_actor_mapping() -> None:
    resolver = DeterministicActorIdentityResolver([])

    outcome = resolver.resolve(
        VerifiedExternalIdentity(
            provider_id="issuer-a",
            subject_id="subject-17",
            login_hint="alice@example.test",
        )
    )

    assert outcome.kind is ActorIdentityResolutionKind.UNMAPPED
    assert outcome.actor is None


def test_provider_identity_qualifies_external_subject() -> None:
    resolver = DeterministicActorIdentityResolver(
        [
            ActorIdentityMapping(
                provider_id="issuer-a",
                subject_id="subject-17",
                actor_id="alice",
                login="alice",
            ),
            ActorIdentityMapping(
                provider_id="issuer-b",
                subject_id="subject-17",
                actor_id="bob",
                login="bob",
            ),
        ]
    )

    outcome = resolver.resolve(
        VerifiedExternalIdentity(provider_id="issuer-b", subject_id="subject-17")
    )

    assert outcome.kind is ActorIdentityResolutionKind.MAPPED
    assert outcome.actor is not None
    assert outcome.actor.actor_id == "bob"


def test_ambiguous_effective_mapping_fails_closed() -> None:
    resolver = DeterministicActorIdentityResolver(
        [
            ActorIdentityMapping(
                provider_id="issuer-a",
                subject_id="subject-17",
                actor_id="alice",
                login="alice",
            ),
            ActorIdentityMapping(
                provider_id="issuer-a",
                subject_id="subject-17",
                actor_id="bob",
                login="bob",
            ),
        ]
    )

    outcome = resolver.resolve(
        VerifiedExternalIdentity(provider_id="issuer-a", subject_id="subject-17")
    )

    assert outcome.kind is ActorIdentityResolutionKind.AMBIGUOUS
    assert outcome.actor is None


def test_inactive_mapping_does_not_establish_actor() -> None:
    resolver = DeterministicActorIdentityResolver(
        [
            ActorIdentityMapping(
                provider_id="issuer-a",
                subject_id="subject-17",
                actor_id="alice",
                login="alice",
                active=False,
            )
        ]
    )

    outcome = resolver.resolve(
        VerifiedExternalIdentity(provider_id="issuer-a", subject_id="subject-17")
    )

    assert outcome.kind is ActorIdentityResolutionKind.UNMAPPED
    assert outcome.actor is None


def test_unknown_mapping_evidence_never_exposes_actor() -> None:
    outcome = UnknownActorIdentityResolver().resolve(
        VerifiedExternalIdentity(provider_id="issuer-a", subject_id="subject-17")
    )

    assert outcome.kind is ActorIdentityResolutionKind.UNKNOWN
    assert outcome.actor is None


def test_resolution_invariant_rejects_actor_on_non_mapped_outcome() -> None:
    from napms.platform.auth.local import AuthenticatedActor

    with pytest.raises(ValueError, match="must not expose actor"):
        ActorIdentityResolution(
            ActorIdentityResolutionKind.AMBIGUOUS,
            actor=AuthenticatedActor(actor_id="alice", login="alice"),
        )
