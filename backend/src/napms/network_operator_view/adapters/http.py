from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from fastapi import APIRouter, HTTPException, Query, Request

from napms.network_operator_view.application import ReadOutcome
from napms.runtime.auth import InMemorySessionStore
from napms.runtime.http_support import SESSION_COOKIE_NAME


def create_network_operator_view_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[str], AbstractContextManager],
) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/api/v1/network-operator-realization",
        name="ReadNetworkOperatorRealization",
    )
    def read_network_operator_realization(
        request: Request,
        scope: str = Query(min_length=1, max_length=512),
        as_of: datetime = Query(alias="asOf"),
    ):
        actor = sessions.get(request.cookies.get(SESSION_COOKIE_NAME))
        if actor is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise HTTPException(status_code=422, detail="asOf must include timezone")

        with open_scope(actor.actor_id) as operator_scope:
            result = operator_scope.read.execute(
                actor_id=actor.actor_id,
                scope=scope,
                as_of=as_of,
            )

        if result.outcome is ReadOutcome.AUTHORITY_DENIED:
            raise HTTPException(status_code=403, detail="Authority denied")
        if result.outcome is ReadOutcome.AUTHORITY_UNKNOWN:
            raise HTTPException(status_code=409, detail="Authority unknown")

        assert result.view is not None
        view = result.view
        desired_value = view.desired.value
        rendering_values = view.rendering.value or ()
        reconciliation_value = view.reconciliation.value
        operation_value = view.operation.value

        return {
            "scope": view.scope,
            "asOf": view.as_of.isoformat(),
            "authorityReference": view.authority_reference,
            "desired": {
                "availability": view.desired.availability.value,
                "status": getattr(getattr(desired_value, "status", None), "value", None),
                "ruleReferences": sorted(
                    {
                        reference
                        for intent in getattr(desired_value, "intents", ())
                        for reference in intent.rule_references
                    }
                ),
                "targets": [
                    {
                        "logicalFirewallId": str(intent.target.logical_firewall_id),
                        "enforcementAttachmentId": str(
                            intent.target.enforcement_attachment_id
                        ),
                        "placementProvenanceReferences": list(
                            intent.placement_provenance_references
                        ),
                    }
                    for intent in getattr(desired_value, "intents", ())
                ],
                "reason": view.desired.reason,
            },
            "reconciliation": {
                "availability": view.reconciliation.availability.value,
                "status": getattr(
                    getattr(reconciliation_value, "status", None), "value", None
                ),
                "requiredChange": getattr(
                    getattr(reconciliation_value, "required_change", None),
                    "value",
                    None,
                ),
                "reason": view.reconciliation.reason,
            },
            "rendering": {
                "availability": view.rendering.availability.value,
                "artifacts": [
                    {
                        "status": item.status.value,
                        "logicalFirewallId": str(item.target.logical_firewall_id),
                        "enforcementAttachmentId": str(
                            item.target.enforcement_attachment_id
                        ),
                        "rendererName": item.renderer_name,
                        "rendererContractVersion": item.renderer_contract_version,
                        "content": item.content,
                        "reason": item.reason,
                    }
                    for item in rendering_values
                ],
                "reason": view.rendering.reason,
            },
            "operation": {
                "availability": view.operation.availability.value,
                "operationId": getattr(operation_value, "operation_id", None),
                "outcome": getattr(
                    getattr(operation_value, "outcome", None), "value", None
                ),
                "provenanceReferences": list(
                    getattr(operation_value, "provenance_references", ())
                ),
                "reason": view.operation.reason,
            },
        }

    return router
