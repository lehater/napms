from datetime import datetime

from fastapi import Request
from fastapi.responses import JSONResponse

from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.http_api import PublicApiError, SESSION_COOKIE_NAME


SUCCESS_OUTCOMES = {"Created", "Updated", "Resolved"}


def authenticated_actor(
    sessions: InMemorySessionStore,
    request: Request,
) -> AuthenticatedActor:
    actor = sessions.get(request.cookies.get(SESSION_COOKIE_NAME))
    if actor is None:
        raise PublicApiError(
            status_code=401,
            code="AuthenticationRequired",
            message="Authentication is required.",
        )
    request.state.actor_id = actor.actor_id
    return actor


def require_actor(sessions: InMemorySessionStore, request: Request) -> str:
    return authenticated_actor(sessions, request).actor_id


def set_outcome(request: Request, outcome: str) -> None:
    request.state.semantic_outcome = outcome


def set_dependency(request: Request, dependency: str) -> None:
    request.state.dependency = dependency


def require_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise PublicApiError(
            status_code=422,
            code="InvalidCatalogueTime",
            message=f"{field_name} must include an explicit timezone offset.",
        )


def require_interval(valid_from: datetime, valid_to: datetime | None) -> None:
    require_aware(valid_from, "validFrom")
    if valid_to is not None:
        require_aware(valid_to, "validTo")
        if valid_from >= valid_to:
            raise PublicApiError(
                status_code=422,
                code="InvalidCatalogueInterval",
                message="validFrom must be before validTo.",
            )


def require_mutation_success(outcome) -> None:
    value = getattr(outcome, "value", str(outcome))
    if value in SUCCESS_OUTCOMES:
        return
    mapping = {
        "AuthorityDenied": (403, "CatalogueAuthorityDenied", "Catalogue curation is not permitted."),
        "AuthorityUnknown": (409, "CatalogueAuthorityUnknown", "Catalogue curation authority is unknown."),
        "NotFound": (404, "CatalogueSubjectNotFound", "The catalogue subject was not found."),
        "ParentInactive": (409, "CatalogueParentInactive", "The parent catalogue entity is not Active."),
        "ResourceInactive": (409, "CatalogueResourceInactive", "The Resource is not Active."),
        "RetirementBlocked": (409, "CatalogueRetirementBlocked", "Catalogue retirement is blocked by active dependants."),
        "InputInvalid": (422, "CatalogueInputInvalid", "The catalogue mutation input is invalid."),
        "OverlapConflict": (409, "CatalogueOverlapConflict", "The catalogue temporal fact overlaps authoritative state."),
        "ConcurrencyConflict": (409, "CatalogueConcurrencyConflict", "The catalogue entity changed concurrently."),
        "IdempotencyConflict": (409, "CatalogueIdempotencyConflict", "The Idempotency-Key was already used for a different command."),
        "PersistenceUnknown": (503, "CataloguePersistenceOutcomeUnknown", "The catalogue persistence outcome is unknown."),
    }
    status_code, code, message = mapping.get(
        value,
        (500, "CatalogueMutationFailed", "The catalogue mutation could not be completed."),
    )
    raise PublicApiError(status_code=status_code, code=code, message=message)


def mutation_response(outcome, content: dict) -> JSONResponse:
    status_code = 201 if getattr(outcome, "value", str(outcome)) == "Created" else 200
    return JSONResponse(status_code=status_code, content=content)


# Temporary aliases for staged I32 migration. Owner-local HTTP adapters should use
# the public names above; legacy facades may re-export these while callers migrate.
_require_actor = require_actor
_require_aware = require_aware
_require_interval = require_interval
_require_success = require_mutation_success
_mutation_response = mutation_response
