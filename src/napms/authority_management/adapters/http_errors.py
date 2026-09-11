from fastapi import FastAPI, Request

from napms.authority_management.application.ports import AuthorityPersistenceError
from napms.runtime.http_support import error_response


def register_authority_management_http_error_handlers(app: FastAPI) -> None:
    async def persistence_handler(request: Request, exc: AuthorityPersistenceError):
        return error_response(
            request,
            status_code=503,
            code="AuthorityUnavailable",
            message="Authority information is unavailable.",
            dependency="AuthorityManagement",
        )

    app.add_exception_handler(AuthorityPersistenceError, persistence_handler)
