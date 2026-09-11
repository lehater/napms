from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Sequence

from napms.runtime.auth import AuthenticatedActor


@dataclass(frozen=True, slots=True)
class VerifiedExternalIdentity:
    """Protocol-neutral result of a trusted outer authentication adapter."""

    provider_id: str
    subject_id: str
    login_hint: str | None = None

    def __post_init__(self) -> None:
        if not self.provider_id:
            raise ValueError("provider_id must be non-empty")
        if not self.subject_id:
            raise ValueError("subject_id must be non-empty")


@dataclass(frozen=True, slots=True)
class ActorIdentityMapping:
    provider_id: str
    subject_id: str
    actor_id: str
    login: str
    active: bool = True

    def __post_init__(self) -> None:
        if not self.provider_id:
            raise ValueError("provider_id must be non-empty")
        if not self.subject_id:
            raise ValueError("subject_id must be non-empty")
        if not self.actor_id:
            raise ValueError("actor_id must be non-empty")
        if not self.login:
            raise ValueError("login must be non-empty")


class ActorIdentityResolutionKind(str, Enum):
    MAPPED = "Mapped"
    UNMAPPED = "Unmapped"
    AMBIGUOUS = "Ambiguous"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class ActorIdentityResolution:
    kind: ActorIdentityResolutionKind
    actor: AuthenticatedActor | None = None
    diagnostic: str | None = None

    def __post_init__(self) -> None:
        if self.kind is ActorIdentityResolutionKind.MAPPED:
            if self.actor is None:
                raise ValueError("Mapped resolution requires actor")
        elif self.actor is not None:
            raise ValueError(f"{self.kind.value} resolution must not expose actor")


class ActorIdentityResolver(Protocol):
    def resolve(self, identity: VerifiedExternalIdentity) -> ActorIdentityResolution: ...


class DeterministicActorIdentityResolver:
    """In-process I23 proof adapter; it does not represent a real enterprise directory."""

    def __init__(self, mappings: Sequence[ActorIdentityMapping]) -> None:
        self._mappings = tuple(mappings)

    def resolve(self, identity: VerifiedExternalIdentity) -> ActorIdentityResolution:
        matches = [
            mapping
            for mapping in self._mappings
            if mapping.active
            and mapping.provider_id == identity.provider_id
            and mapping.subject_id == identity.subject_id
        ]
        if not matches:
            return ActorIdentityResolution(ActorIdentityResolutionKind.UNMAPPED)

        actors = {(mapping.actor_id, mapping.login) for mapping in matches}
        if len(actors) != 1:
            return ActorIdentityResolution(
                ActorIdentityResolutionKind.AMBIGUOUS,
                diagnostic="multiple effective NAPMS actors match external subject",
            )

        actor_id, login = next(iter(actors))
        return ActorIdentityResolution(
            ActorIdentityResolutionKind.MAPPED,
            actor=AuthenticatedActor(actor_id=actor_id, login=login),
        )


class UnknownActorIdentityResolver:
    """Deterministic proof adapter for unavailable/indeterminate mapping evidence."""

    def resolve(self, identity: VerifiedExternalIdentity) -> ActorIdentityResolution:
        return ActorIdentityResolution(
            ActorIdentityResolutionKind.UNKNOWN,
            diagnostic="actor identity mapping evidence is unavailable",
        )
