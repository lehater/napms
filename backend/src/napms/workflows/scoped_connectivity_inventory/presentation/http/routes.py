from contextlib import AbstractContextManager
from datetime import datetime
from typing import Any, Callable

from fastapi import APIRouter, Depends, Query, Request

from napms.platform.auth.local import AuthenticatedActor, InMemorySessionStore
from napms.platform.http.support import PublicApiError, authenticated_actor, set_outcome
from napms.workflows.scoped_connectivity_inventory.application.read import (
    InventoryQueryOutcome,
    ScopeDiscoveryQueryOutcome,
)


def create_scoped_connectivity_inventory_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager[Any]],
) -> APIRouter:
    router = APIRouter()

    def require_actor(request: Request) -> AuthenticatedActor:
        return authenticated_actor(sessions, request)

    @router.get(
        "/api/v1/connectivity/scopes",
        name="DiscoverScopedConnectivityScopes",
    )
    def discover_scoped_connectivity_scopes(
        request: Request,
        as_of: datetime = Query(alias="asOf"),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverScopedConnectivityScopes"
        _require_as_of(as_of)
        with open_scope() as runtime_scope:
            result = runtime_scope.scoped_connectivity_scopes.execute(
                actor_id=actor.actor_id,
                as_of=as_of,
            )

        if result.outcome is ScopeDiscoveryQueryOutcome.UNAVAILABLE:
            raise PublicApiError(
                status_code=503,
                code="ScopedConnectivityUnavailable", dependency="ScopedConnectivityInventory",
                message="Connectivity scope information is unavailable.",
            )

        set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "asOf": as_of.isoformat(),
            "scopes": [{"scope": scope} for scope in result.permitted_scopes],
            "ambiguousScopes": [
                {"scope": scope} for scope in result.ambiguous_scopes
            ],
        }

    @router.get(
        "/api/v1/connectivity",
        name="ReadScopedConnectivityInventory",
    )
    def read_scoped_connectivity_inventory(
        request: Request,
        scope: str = Query(min_length=1, max_length=512),
        as_of: datetime = Query(alias="asOf"),
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=100),
        search: str | None = Query(None, max_length=256),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "ReadScopedConnectivityInventory"
        _require_as_of(as_of)
        with open_scope() as runtime_scope:
            result = runtime_scope.scoped_connectivity_inventory.execute(
                actor_id=actor.actor_id,
                responsibility_scope=scope,
                as_of=as_of,
                page=page,
                page_size=pageSize,
                search=search,
            )

        mapping = {
            InventoryQueryOutcome.AUTHORITY_DENIED: (
                403,
                "AuthorityDenied",
                "The requested operation is not permitted.",
            ),
            InventoryQueryOutcome.AUTHORITY_UNKNOWN: (
                409,
                "AuthorityUnknown",
                "Authority for the requested operation is unavailable.",
            ),
            InventoryQueryOutcome.AUTHORITY_AMBIGUOUS: (
                409,
                "AuthorityUnknown",
                "Authority for the requested operation is ambiguous.",
            ),
            InventoryQueryOutcome.UNAVAILABLE: (
                503,
                "ScopedConnectivityUnavailable",
                "Connectivity inventory information is unavailable.",
            ),
        }
        if result.outcome is not InventoryQueryOutcome.AVAILABLE:
            status_code, code, message = mapping[result.outcome]
            raise PublicApiError(
                status_code=status_code,
                code=code,
                message=message,
                dependency=(
                    "AuthorityManagement"
                    if code in {"AuthorityDenied", "AuthorityUnknown"}
                    else "ScopedConnectivityInventory"
                ),
            )

        assert result.page is not None
        request.state.authority_reference = result.page.read_authority_reference
        set_outcome(
            request,
            "Partial" if result.page.partial else "Available",
        )
        return _scoped_connectivity_page_dto(result.page)

    return router


def _require_as_of(as_of: datetime) -> None:
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise PublicApiError(
            status_code=422,
            code="InvalidAsOf",
            message="asOf must include an explicit timezone offset.",
        )


def _scoped_resource_dto(resource) -> dict[str, Any]:
    return {
        "resourceReference": resource.resource_reference,
        "realizationState": resource.realization_state.value,
        "endpoints": [
            {
                "endpointReference": endpoint.endpoint_reference,
                "technicalAddress": endpoint.technical_address,
            }
            for endpoint in resource.endpoints
        ],
    }


def _scoped_relationship_dto(relationship) -> dict[str, Any]:
    return {
        "semanticIdentity": {
            "sourceComponentDeploymentId": str(
                relationship.identity.source_component_deployment_id
            ),
            "destinationComponentDeploymentId": str(
                relationship.identity.destination_component_deployment_id
            ),
            "dcsContractRevisionId": str(
                relationship.identity.dcs_contract_revision_id
            ),
        },
        "direction": relationship.direction.value,
        "remoteComponent": {
            "componentDeploymentId": str(
                relationship.remote_component_deployment_id
            ),
            "displayName": relationship.remote_component_display_name,
        },
        "dcsDisplayName": relationship.dcs_display_name,
        "accessSummary": relationship.access_summary,
        "remoteResourcesKnown": relationship.remote_resources_known,
        "remoteResources": [
            _scoped_resource_dto(resource)
            for resource in relationship.remote_resources
        ],
        "need": {
            "current": relationship.requirement.current.value,
            "historicalOnly": relationship.requirement.historical_only,
            "coverage": relationship.requirement.coverage.value,
        },
        "decision": {"state": relationship.decision.state.value},
        "policy": {
            "ruleExists": relationship.policy.rule_exists.value,
            "operationalState": relationship.policy.operational_state.value,
            "effectiveAtAsOf": relationship.policy.effective_at_as_of.value,
        },
    }


def _scoped_connectivity_page_dto(page) -> dict[str, Any]:
    return {
        "scope": page.scope,
        "asOf": page.as_of.isoformat(),
        "items": [
            {
                "resource": _scoped_resource_dto(item.resource),
                "componentsKnown": item.components_known,
                "components": [
                    {
                        "componentDeploymentId": str(
                            component.component_deployment_id
                        ),
                        "displayName": component.display_name,
                        "relationshipsKnown": component.relationships_known,
                        "relationships": [
                            _scoped_relationship_dto(relationship)
                            for relationship in component.relationships
                        ],
                    }
                    for component in item.components
                ],
            }
            for item in page.items
        ],
        "page": page.page,
        "pageSize": page.page_size,
        "hasMore": page.has_more,
        "partial": page.partial,
    }
