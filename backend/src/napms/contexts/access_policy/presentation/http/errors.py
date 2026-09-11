from fastapi import FastAPI, Request

from napms.contexts.access_policy.application.ports import (
    AccessRuleCommitOutcomeUnknown,
    AccessRulePersistenceError,
)
from napms.runtime.http_support import error_response


def register_access_policy_http_error_handlers(app: FastAPI) -> None:
    async def uncertain_commit_handler(
        request: Request, exc: AccessRuleCommitOutcomeUnknown
    ):
        return error_response(
            request,
            status_code=503,
            code="PersistenceOutcomeUnknown",
            message="The authoritative persistence outcome is currently unknown.",
            dependency="AccessPolicyPersistence",
        )

    async def persistence_handler(request: Request, exc: AccessRulePersistenceError):
        return error_response(
            request,
            status_code=503,
            code="PersistenceUnavailable",
            message="The authoritative persistence service is unavailable.",
            dependency="AccessPolicyPersistence",
        )

    app.add_exception_handler(AccessRuleCommitOutcomeUnknown, uncertain_commit_handler)
    app.add_exception_handler(AccessRulePersistenceError, persistence_handler)
