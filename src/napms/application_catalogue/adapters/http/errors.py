from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse

from napms.application_catalogue.domain.model import CatalogueInvariantError


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
