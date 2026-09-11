from fastapi import FastAPI, Request

from napms.connectivity_decision.application.ports import (
    DecisionCommitOutcomeUnknown,
    DecisionPersistenceError,
)
from napms.runtime.http_support import error_response


def register_connectivity_decision_http_error_handlers(app: FastAPI) -> None:
    async def uncertain_commit_handler(
        request: Request, exc: DecisionCommitOutcomeUnknown
    ):
        return error_response(
            request,
            status_code=503,
            code="DecisionPersistenceOutcomeUnknown",
            message="The Connectivity Decision persistence outcome is currently unknown.",
            dependency="ConnectivityDecisionPersistence",
        )

    async def persistence_handler(request: Request, exc: DecisionPersistenceError):
        return error_response(
            request,
            status_code=503,
            code="DecisionPersistenceUnavailable",
            message="Connectivity Decision persistence is unavailable.",
            dependency="ConnectivityDecisionPersistence",
        )

    app.add_exception_handler(DecisionCommitOutcomeUnknown, uncertain_commit_handler)
    app.add_exception_handler(DecisionPersistenceError, persistence_handler)
