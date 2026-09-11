from fastapi import FastAPI, Request

from napms.policy_export.application.normalization_types import NormalizationInvariantError
from napms.runtime.http_support import error_response


def register_policy_export_http_error_handlers(app: FastAPI) -> None:
    async def normalization_error_handler(
        request: Request, exc: NormalizationInvariantError
    ):
        return error_response(
            request,
            status_code=500,
            code="NormalizationFailed",
            message="The normalized policy could not be produced safely.",
            dependency="PolicyExportNormalization",
        )

    app.add_exception_handler(NormalizationInvariantError, normalization_error_handler)
