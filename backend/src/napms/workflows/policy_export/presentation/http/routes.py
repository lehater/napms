from contextlib import AbstractContextManager
from datetime import datetime
from typing import Any, Callable

from fastapi import APIRouter, Depends, Query, Request

from napms.contexts.access_policy.application.select_effective_policy import (
    EffectivePolicySelectionOutcome,
    SelectAccessPolicyEffectiveDesiredPolicy,
    SelectEffectiveDesiredPolicy,
)
from napms.contexts.access_policy.domain.model import RuleSemanticIdentity
from napms.contexts.application_catalogue.application.ports import CataloguePersistenceError
from napms.contexts.application_catalogue.domain.model import DirectedInteractionIdentity
from napms.workflows.policy_export.application.export_snapshot import (
    AssembleExportSnapshot,
    SnapshotAssemblyOutcome,
)
from napms.workflows.policy_export.application.normalize_snapshot import NormalizeExportSnapshot
from napms.workflows.policy_export.application.normalization_ports import DcsProjectionDecodeError
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.http_support import PublicApiError, authenticated_actor, set_outcome
from napms.workflows.policy_export.presentation.http.json import (
    normalized_policy_export_json,
    port_constraint_json,
    snapshot_diagnostic_json,
)


def create_policy_export_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager[Any]],
) -> APIRouter:
    router = APIRouter()

    def require_actor(request: Request) -> AuthenticatedActor:
        return authenticated_actor(sessions, request)

    @router.get("/api/v1/normalized-policy", name="GetNormalizedPolicy")
    def get_normalized_policy(
        request: Request,
        scope: str,
        as_of: datetime = Query(alias="asOf"),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetNormalizedPolicy"
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise PublicApiError(
                status_code=422,
                code="InvalidAsOf",
                message="asOf must include an explicit timezone offset.",
            )

        with open_scope() as runtime_scope:
            selection = SelectAccessPolicyEffectiveDesiredPolicy(
                authority=runtime_scope.authority,
                rules=runtime_scope.access_rules,
            ).execute(
                SelectEffectiveDesiredPolicy(
                    scope=scope,
                    as_of=as_of,
                    actor_id=actor.actor_id,
                )
            )

            if selection.outcome is EffectivePolicySelectionOutcome.AUTHORITY_DENIED:
                raise PublicApiError(
                    status_code=403,
                    code="AuthorityDenied", dependency="AuthorityManagement",
                    message="The requested operation is not permitted.",
                )
            if selection.outcome is EffectivePolicySelectionOutcome.AUTHORITY_UNKNOWN:
                raise PublicApiError(
                    status_code=409,
                    code="AuthorityUnknown", dependency="AuthorityManagement",
                    message="Authority for the requested operation is ambiguous or unavailable.",
                )

            assembly = AssembleExportSnapshot(
                application_catalogue=runtime_scope.application_projection,
                resource_catalogue=runtime_scope.resource_projection,
            ).execute(selection)

            if assembly.outcome is not SnapshotAssemblyOutcome.SUCCESS:
                raise PublicApiError(
                    status_code=409,
                    code="SnapshotIncomplete", dependency="PolicyExportSnapshot",
                    message="A coherent normalized-policy snapshot cannot currently be produced.",
                    details={
                        "diagnostics": [
                            snapshot_diagnostic_json(value)
                            for value in assembly.diagnostics
                        ]
                    },
                )

            assert assembly.snapshot is not None
            normalized = NormalizeExportSnapshot(
                decoder=runtime_scope.dcs_decoder
            ).execute(assembly.snapshot)
            presentations = _describe_semantic_identities(
                runtime_scope,
                tuple(row.rule_semantic_identity for row in normalized.rows),
            )

        request.state.authority_reference = normalized.authority_reference
        set_outcome(request, "NormalizedPolicyExported")
        payload = normalized_policy_export_json(normalized)
        for encoded, row in zip(payload["rows"], normalized.rows):
            encoded["catalogue"] = presentations.get(row.rule_semantic_identity)
        return payload

    return router


def _interaction_identity(identity: RuleSemanticIdentity) -> DirectedInteractionIdentity:
    return DirectedInteractionIdentity(
        source_component_deployment_id=identity.source_component_deployment_id,
        destination_component_deployment_id=identity.destination_component_deployment_id,
        dcs_contract_revision_id=identity.dcs_contract_revision_id,
    )


def _describe_semantic_identities(
    runtime_scope,
    identities,
) -> dict[RuleSemanticIdentity, dict[str, Any]]:
    values = tuple(dict.fromkeys(identities))
    if not values:
        return {}
    try:
        descriptions = runtime_scope.catalogue_describer.execute(
            tuple(_interaction_identity(identity) for identity in values)
        )
    except CataloguePersistenceError:
        return {}
    return {
        identity: _catalogue_presentation_dto(
            description,
            decoder=runtime_scope.dcs_decoder,
        )
        for identity, description in zip(values, descriptions)
    }


def _catalogue_presentation_dto(description, *, decoder) -> dict[str, Any]:
    traffic_alternatives: list[dict[str, Any]] = []
    if description.dcs_projection_payload is not None:
        try:
            alternatives = decoder.decode(description.dcs_projection_payload)
        except DcsProjectionDecodeError:
            alternatives = ()
        traffic_alternatives = [
            {
                "protocol": alternative.protocol,
                "sourcePorts": port_constraint_json(alternative.source_ports),
                "destinationPorts": port_constraint_json(alternative.destination_ports),
                "serviceReference": alternative.service_reference,
            }
            for alternative in alternatives
        ]
    return {
        "sourceDisplayName": description.source_display_name,
        "destinationDisplayName": description.destination_display_name,
        "dcsDisplayName": description.dcs_display_name,
        "trafficAlternatives": traffic_alternatives,
        "dcsProvenanceReference": description.dcs_provenance_reference,
    }
