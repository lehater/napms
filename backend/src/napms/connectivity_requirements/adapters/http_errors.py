from fastapi import FastAPI, Request

from napms.connectivity_requirements.application.ports import (
    ActiveRequirementSemanticConflict,
    RequirementCommitOutcomeUnknown,
    RequirementPersistenceError,
    RequirementVersionConflict,
)
from napms.runtime.http_support import error_response


def register_connectivity_requirements_http_error_handlers(app: FastAPI) -> None:
    async def uncertain_commit_handler(
        request: Request, exc: RequirementCommitOutcomeUnknown
    ):
        return error_response(
            request,
            status_code=503,
            code="PersistenceOutcomeUnknown",
            message="The authoritative persistence outcome is currently unknown.",
            dependency="ConnectivityRequirementsPersistence",
        )

    async def version_conflict_handler(request: Request, exc: RequirementVersionConflict):
        return error_response(
            request,
            status_code=409,
            code="RequirementVersionConflict",
            message="The Connectivity Requirement changed concurrently.",
            dependency="ConnectivityRequirementsPersistence",
        )

    async def semantic_conflict_handler(
        request: Request, exc: ActiveRequirementSemanticConflict
    ):
        return error_response(
            request,
            status_code=409,
            code="RequirementSemanticConflict",
            message="An Active Connectivity Requirement already owns this semantic need.",
            dependency="ConnectivityRequirementsPersistence",
        )

    async def persistence_handler(request: Request, exc: RequirementPersistenceError):
        return error_response(
            request,
            status_code=503,
            code="PersistenceUnavailable",
            message="Connectivity Requirements persistence is unavailable.",
            dependency="ConnectivityRequirementsPersistence",
        )

    app.add_exception_handler(RequirementCommitOutcomeUnknown, uncertain_commit_handler)
    app.add_exception_handler(RequirementVersionConflict, version_conflict_handler)
    app.add_exception_handler(ActiveRequirementSemanticConflict, semantic_conflict_handler)
    app.add_exception_handler(RequirementPersistenceError, persistence_handler)
