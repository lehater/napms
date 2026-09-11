from contextlib import AbstractContextManager
from datetime import datetime
from typing import Any, Callable
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from napms.requirement_policy_alignment.application.align import (
    AlignConnectivityRequirementToPolicy,
    AlignmentQueryOutcome,
    AlignVisibleConnectivityRequirementsToPolicy,
)
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.http_support import PublicApiError, authenticated_actor, set_outcome


def create_requirement_policy_alignment_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager[Any]],
) -> APIRouter:
    router = APIRouter()

    def require_actor(request: Request) -> AuthenticatedActor:
        return authenticated_actor(sessions, request)

    @router.get(
        "/api/v1/connectivity-requirements/alignment",
        name="ListConnectivityRequirementAlignment",
    )
    def list_connectivity_requirement_alignment(
        request: Request,
        as_of: datetime = Query(alias="asOf"),
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=100),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "ListConnectivityRequirementAlignment"
        _require_as_of(as_of)
        with open_scope() as runtime_scope:
            result = AlignVisibleConnectivityRequirementsToPolicy(
                requirements=runtime_scope.requirement_alignment,
                policy=runtime_scope.policy_alignment,
            ).execute(
                actor_id=actor.actor_id,
                as_of=as_of,
                page=page,
                page_size=pageSize,
            )

        if result.outcome is AlignmentQueryOutcome.UNAVAILABLE:
            raise PublicApiError(
                status_code=503,
                code="AlignmentUnavailable", dependency="RequirementPolicyAlignment",
                message="Requirement-to-policy alignment is unavailable.",
            )

        set_outcome(request, "Aligned")
        return {
            "asOf": as_of.isoformat(),
            "items": [
                {
                    "requirementId": str(item.requirement_id),
                    "status": item.status.value,
                    "semanticIdentity": {
                        "sourceComponentDeploymentId": str(
                            item.semantic_identity.source_component_deployment_id
                        ),
                        "destinationComponentDeploymentId": str(
                            item.semantic_identity.destination_component_deployment_id
                        ),
                        "dcsContractRevisionId": str(
                            item.semantic_identity.dcs_contract_revision_id
                        ),
                    },
                }
                for item in result.items
            ],
            "page": result.page,
            "pageSize": result.page_size,
            "hasMore": result.has_more,
            "ambiguousScopes": [
                {"scope": scope} for scope in result.ambiguous_scopes
            ],
        }

    @router.get(
        "/api/v1/connectivity-requirements/{requirement_id}/alignment",
        name="GetConnectivityRequirementAlignment",
    )
    def get_connectivity_requirement_alignment(
        requirement_id: UUID,
        request: Request,
        as_of: datetime = Query(alias="asOf"),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetConnectivityRequirementAlignment"
        _require_as_of(as_of)
        with open_scope() as runtime_scope:
            result = AlignConnectivityRequirementToPolicy(
                requirements=runtime_scope.requirement_alignment,
                policy=runtime_scope.policy_alignment,
            ).execute(
                requirement_id=requirement_id,
                actor_id=actor.actor_id,
                as_of=as_of,
            )

        mapping = {
            AlignmentQueryOutcome.REQUIREMENT_NOT_FOUND: (
                404,
                "RequirementNotFound",
                "The Connectivity Requirement was not found.",
            ),
            AlignmentQueryOutcome.AUTHORITY_DENIED: (
                403,
                "AuthorityDenied",
                "The requested operation is not permitted.",
            ),
            AlignmentQueryOutcome.AUTHORITY_UNKNOWN: (
                409,
                "AuthorityUnknown",
                "Authority for the requested operation is ambiguous or unavailable.",
            ),
            AlignmentQueryOutcome.UNAVAILABLE: (
                503,
                "AlignmentUnavailable",
                "Requirement-to-policy alignment is unavailable.",
            ),
        }
        if result.outcome is not AlignmentQueryOutcome.ALIGNED:
            status_code, code, message = mapping[result.outcome]
            raise PublicApiError(
                status_code=status_code,
                code=code,
                message=message,
                dependency=(
                    "AuthorityManagement"
                    if code in {"AuthorityDenied", "AuthorityUnknown"}
                    else "RequirementPolicyAlignment"
                ),
            )

        assert result.status is not None
        assert result.semantic_identity is not None
        request.state.requirement_id = str(requirement_id)
        request.state.authority_reference = result.requirement_read_authority_reference
        set_outcome(request, result.status.value)
        return {
            "requirementId": str(requirement_id),
            "asOf": as_of.isoformat(),
            "status": result.status.value,
            "semanticIdentity": {
                "sourceComponentDeploymentId": str(
                    result.semantic_identity.source_component_deployment_id
                ),
                "destinationComponentDeploymentId": str(
                    result.semantic_identity.destination_component_deployment_id
                ),
                "dcsContractRevisionId": str(
                    result.semantic_identity.dcs_contract_revision_id
                ),
            },
            "requirementReadAuthorityReference": (
                result.requirement_read_authority_reference
            ),
        }

    return router


def _require_as_of(as_of: datetime) -> None:
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise PublicApiError(
            status_code=422,
            code="InvalidAsOf",
            message="asOf must include an explicit timezone offset.",
        )
