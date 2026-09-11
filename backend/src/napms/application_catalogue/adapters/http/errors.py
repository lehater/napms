from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse

from napms.application_catalogue.application.ports import CataloguePersistenceError
from napms.application_catalogue.domain.model import CatalogueInvariantError
from napms.runtime.http_support import error_response


async def catalogue_invariant_error_handler(
    request: Request,
    exc: CatalogueInvariantError,
) -> JSONResponse:
    """Transport safety net for catalogue validation that escapes route mapping."""

    correlation_id = getattr(request.state, "correlation_id", str(uuid4()))
    request.state.semantic_outcome = "CatalogueValidationError"
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "CatalogueValidationError",
                "message": str(exc) or "The catalogue request violates domain constraints.",
                "correlationId": correlation_id,
            }
        },
    )


def register_application_catalogue_http_error_handlers(app) -> None:
    async def catalogue_persistence_handler(
        request: Request, exc: CataloguePersistenceError
    ):
        return error_response(
            request,
            status_code=503,
            code="CatalogueUnavailable",
            message="Catalogue information is unavailable.",
            dependency="ApplicationCommunicationCatalogue",
        )

    app.add_exception_handler(CatalogueInvariantError, catalogue_invariant_error_handler)
    app.add_exception_handler(CataloguePersistenceError, catalogue_persistence_handler)
