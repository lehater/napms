from contextlib import AbstractContextManager
from datetime import datetime
from typing import Any, Callable
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from napms.application_catalogue.application.ports import CataloguePersistenceError
from napms.application_catalogue.domain.model import DirectedInteractionIdentity
from napms.connectivity_decision.application.options import (
    DecisionInteractionDiscoveryOutcome,
    DiscoverDecisionInteractions,
    DiscoverDecisionScopes,
)
from napms.connectivity_decision.application.read import (
    DecisionDetailOutcome,
    GetConnectivityDecision,
    ListConnectivityDecisions,
)
from napms.connectivity_decision.application.record import (
    RecordConnectivityDecision,
    RecordDecision,
    RecordDecisionOutcome,
)
from napms.connectivity_decision.domain.model import (
    ConnectivityDecision,
    DecisionEvidenceReference,
    DecisionInvariantError,
    DecisionOutcome,
    DecisionSubject,
    DecisionValidity,
)
from napms.policy_export.application.normalization_ports import DcsProjectionDecodeError
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.http_support import PublicApiError, authenticated_actor, set_outcome
from napms.policy_export.adapters.http_json import port_constraint_json


class DecisionEvidenceReferenceValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str = Field(min_length=1, max_length=256)
    reference: str = Field(min_length=1, max_length=2048)


class RecordConnectivityDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    authority_scope: str = Field(alias="authorityScope", min_length=1, max_length=512)
    source_component_deployment_id: UUID = Field(alias="sourceComponentDeploymentId")
    destination_component_deployment_id: UUID = Field(
        alias="destinationComponentDeploymentId"
    )
    dcs_contract_revision_id: UUID = Field(alias="dcsContractRevisionId")
    outcome: DecisionOutcome
    valid_from: datetime = Field(alias="validFrom")
    valid_until: datetime | None = Field(default=None, alias="validUntil")
    reason_code: str = Field(alias="reasonCode", min_length=1, max_length=256)
    reason_text: str = Field(alias="reasonText", min_length=1, max_length=4096)
    evidence_references: list[DecisionEvidenceReferenceValue] = Field(
        default_factory=list,
        alias="evidenceReferences",
    )
    supersedes_decision_id: UUID | None = Field(
        default=None,
        alias="supersedesDecisionId",
    )


def create_connectivity_decision_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager[Any]],
    clock: Callable[[], datetime],
) -> APIRouter:
    router = APIRouter()

    def require_actor(request: Request) -> AuthenticatedActor:
        return authenticated_actor(sessions, request)

    @router.get(
        "/api/v1/connectivity-decisions/scopes",
        name="DiscoverConnectivityDecisionScopes",
    )
    def discover_connectivity_decision_scopes(
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverConnectivityDecisionScopes"
        effective_time = clock()
        with open_scope() as runtime_scope:
            result = DiscoverDecisionScopes(
                discovery=runtime_scope.decision_scopes,
            ).execute(
                actor_id=actor.actor_id,
                effective_time=effective_time,
            )
        set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "scopes": [{"scope": scope} for scope in result.permitted_scopes],
            "ambiguousScopes": [
                {"scope": scope} for scope in result.ambiguous_scopes
            ],
        }

    @router.get(
        "/api/v1/connectivity-decisions/interactions",
        name="DiscoverConnectivityDecisionInteractions",
    )
    def discover_connectivity_decision_interactions(
        request: Request,
        scope: str,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=100),
        search: str | None = Query(None, max_length=256),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverConnectivityDecisionInteractions"
        effective_time = clock()
        with open_scope() as runtime_scope:
            result = DiscoverDecisionInteractions(
                authority=runtime_scope.decision_authority,
                catalogue=runtime_scope.decision_interaction_catalogue,
            ).execute(
                actor_id=actor.actor_id,
                scope=scope,
                effective_time=effective_time,
                page=page,
                page_size=pageSize,
                search=search,
            )
            presentations = (
                _describe_decision_subjects(
                    runtime_scope,
                    result.page.subjects,
                )
                if result.page is not None
                else {}
            )

        if result.outcome is DecisionInteractionDiscoveryOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied", dependency="AuthorityManagement",
                message="The requested operation is not permitted.",
            )
        if result.outcome is DecisionInteractionDiscoveryOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown", dependency="AuthorityManagement",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.page is not None
        set_outcome(request, result.outcome.value)
        return {
            "items": [
                {
                    "sourceComponentDeploymentId": str(
                        subject.source_component_deployment_id
                    ),
                    "destinationComponentDeploymentId": str(
                        subject.destination_component_deployment_id
                    ),
                    "dcsContractRevisionId": str(subject.dcs_contract_revision_id),
                    "catalogue": presentations.get(subject),
                }
                for subject in result.page.subjects
            ],
            "page": result.page.page,
            "pageSize": result.page.page_size,
            "hasMore": result.page.has_more,
        }

    @router.post(
        "/api/v1/connectivity-decisions",
        name="RecordConnectivityDecision",
    )
    def record_connectivity_decision(
        payload: RecordConnectivityDecisionRequest,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "RecordConnectivityDecision"
        effective_time = clock()
        validity = _decision_validity_from_request(payload)
        if not payload.reason_code.strip() or not payload.reason_text.strip():
            raise PublicApiError(
                status_code=422,
                code="ValidationError",
                message="Decision reason code and reason text must be non-empty.",
            )
        evidence = tuple(
            DecisionEvidenceReference(kind=value.kind, reference=value.reference)
            for value in payload.evidence_references
        )
        subject = DecisionSubject(
            source_component_deployment_id=payload.source_component_deployment_id,
            destination_component_deployment_id=payload.destination_component_deployment_id,
            dcs_contract_revision_id=payload.dcs_contract_revision_id,
        )
        with open_scope() as runtime_scope:
            result = RecordConnectivityDecision(
                authority=runtime_scope.decision_authority,
                catalogue=runtime_scope.decision_catalogue,
                decisions=runtime_scope.connectivity_decisions,
            ).execute(
                RecordDecision(
                    subject=subject,
                    governance_scope=payload.authority_scope,
                    outcome=payload.outcome,
                    validity=validity,
                    reason_code=payload.reason_code,
                    reason_text=payload.reason_text,
                    evidence_references=evidence,
                    actor_id=actor.actor_id,
                    effective_time=effective_time,
                    supersedes_decision_id=payload.supersedes_decision_id,
                )
            )
            presentation = (
                _describe_decision_subjects(
                    runtime_scope,
                    (result.decision.subject,),
                ).get(result.decision.subject)
                if result.decision is not None
                else None
            )

        if result.outcome in {
            RecordDecisionOutcome.RECORDED,
            RecordDecisionOutcome.RESOLVED,
        }:
            assert result.decision is not None
            request.state.decision_reference = str(result.decision.decision_id)
            if result.outcome is RecordDecisionOutcome.RECORDED:
                request.state.authority_reference = (
                    result.decision.provenance.authority_reference
                )
            set_outcome(request, result.outcome.value)
            return JSONResponse(
                status_code=(
                    201 if result.outcome is RecordDecisionOutcome.RECORDED else 200
                ),
                content={
                    "outcome": result.outcome.value,
                    "decision": _decision_dto(result.decision, presentation),
                },
            )

        mapping = {
            RecordDecisionOutcome.AUTHORITY_DENIED: (
                403,
                "AuthorityDenied",
                "The requested operation is not permitted.",
            ),
            RecordDecisionOutcome.AUTHORITY_UNKNOWN: (
                409,
                "AuthorityUnknown",
                "Authority for the requested operation is ambiguous or unavailable.",
            ),
            RecordDecisionOutcome.SUBJECT_INVALID: (
                422,
                "DecisionSubjectInvalid",
                "The selected Decision subject is not a valid directed interaction.",
            ),
            RecordDecisionOutcome.SUBJECT_UNKNOWN: (
                409,
                "DecisionSubjectUnknown",
                "The selected Decision subject cannot currently be established.",
            ),
            RecordDecisionOutcome.CURRENT_AMBIGUOUS: (
                409,
                "DecisionCurrentAmbiguous",
                "The current Connectivity Decision state is ambiguous.",
            ),
            RecordDecisionOutcome.SUPERSESSION_REQUIRED: (
                409,
                "DecisionSupersessionRequired",
                "A current Decision exists and must be explicitly superseded.",
            ),
            RecordDecisionOutcome.SUPERSESSION_INVALID: (
                409,
                "DecisionSupersessionInvalid",
                "The supplied supersession reference is not valid for this subject and scope.",
            ),
            RecordDecisionOutcome.CURRENT_CONFLICT: (
                409,
                "DecisionCurrentConflict",
                "The current Connectivity Decision changed concurrently.",
            ),
        }
        status_code, code, message = mapping[result.outcome]
        raise PublicApiError(
            status_code=status_code,
            code=code,
            message=message,
            dependency=(
                "AuthorityManagement"
                if code in {"AuthorityDenied", "AuthorityUnknown"}
                else None
            ),
        )

    @router.get(
        "/api/v1/connectivity-decisions",
        name="ListConnectivityDecisions",
    )
    def list_connectivity_decisions(
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=100),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "ListConnectivityDecisions"
        effective_time = clock()
        with open_scope() as runtime_scope:
            result = ListConnectivityDecisions(
                read_scopes=runtime_scope.decision_read_scopes,
                decisions=runtime_scope.connectivity_decisions,
            ).execute(
                actor_id=actor.actor_id,
                effective_time=effective_time,
                page=page,
                page_size=pageSize,
            )
            presentations = _describe_decision_subjects(
                runtime_scope,
                tuple(value.subject for value in result.decisions),
            )

        set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "items": [
                _decision_dto(value, presentations.get(value.subject))
                for value in result.decisions
            ],
            "page": result.page,
            "pageSize": result.page_size,
            "hasMore": result.has_more,
            "ambiguousScopes": [
                {"scope": scope} for scope in result.ambiguous_scopes
            ],
        }

    @router.get(
        "/api/v1/connectivity-decisions/{decision_id}",
        name="GetConnectivityDecision",
    )
    def get_connectivity_decision(
        decision_id: UUID,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetConnectivityDecision"
        effective_time = clock()
        with open_scope() as runtime_scope:
            result = GetConnectivityDecision(
                authority=runtime_scope.decision_authority,
                decisions=runtime_scope.connectivity_decisions,
            ).execute(
                decision_id=decision_id,
                actor_id=actor.actor_id,
                effective_time=effective_time,
            )
            presentation = (
                _describe_decision_subjects(
                    runtime_scope,
                    (result.decision.subject,),
                ).get(result.decision.subject)
                if result.decision is not None
                else None
            )

        if result.outcome is DecisionDetailOutcome.DECISION_NOT_FOUND:
            raise PublicApiError(
                status_code=404,
                code="DecisionNotFound",
                message="The Connectivity Decision was not found.",
            )
        if result.outcome is DecisionDetailOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied", dependency="AuthorityManagement",
                message="The requested operation is not permitted.",
            )
        if result.outcome is DecisionDetailOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown", dependency="AuthorityManagement",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.decision is not None
        request.state.decision_reference = str(result.decision.decision_id)
        request.state.authority_reference = result.read_authority_reference
        set_outcome(request, "Found")
        return {
            "decision": _decision_dto(result.decision, presentation),
            "readAuthorityReference": result.read_authority_reference,
        }

    return router


def _decision_subject_to_acc(subject: DecisionSubject) -> DirectedInteractionIdentity:
    return DirectedInteractionIdentity(
        source_component_deployment_id=subject.source_component_deployment_id,
        destination_component_deployment_id=subject.destination_component_deployment_id,
        dcs_contract_revision_id=subject.dcs_contract_revision_id,
    )


def _describe_decision_subjects(
    runtime_scope,
    subjects,
) -> dict[DecisionSubject, dict[str, Any] | None]:
    values = tuple(dict.fromkeys(subjects))
    if not values:
        return {}
    try:
        descriptions = runtime_scope.catalogue_describer.execute(
            tuple(_decision_subject_to_acc(value) for value in values)
        )
    except CataloguePersistenceError:
        return {value: None for value in values}
    return {
        subject: _catalogue_presentation_dto(
            description,
            decoder=runtime_scope.dcs_decoder,
        )
        for subject, description in zip(values, descriptions)
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


def _decision_dto(
    decision: ConnectivityDecision,
    catalogue: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "decisionId": str(decision.decision_id),
        "governanceScope": decision.governance_scope,
        "subject": {
            "sourceComponentDeploymentId": str(
                decision.subject.source_component_deployment_id
            ),
            "destinationComponentDeploymentId": str(
                decision.subject.destination_component_deployment_id
            ),
            "dcsContractRevisionId": str(
                decision.subject.dcs_contract_revision_id
            ),
        },
        "outcome": decision.outcome.value,
        "validity": {
            "validFrom": decision.validity.valid_from.isoformat(),
            "validUntil": (
                decision.validity.valid_until.isoformat()
                if decision.validity.valid_until is not None
                else None
            ),
        },
        "reason": {
            "code": decision.reason_code,
            "text": decision.reason_text,
        },
        "evidenceReferences": [
            {"kind": value.kind, "reference": value.reference}
            for value in decision.evidence_references
        ],
        "provenance": {
            "actorId": decision.provenance.actor_id,
            "decidedAt": decision.provenance.decided_at.isoformat(),
            "authorityReference": decision.provenance.authority_reference,
        },
        "supersedesDecisionId": (
            str(decision.supersedes_decision_id)
            if decision.supersedes_decision_id is not None
            else None
        ),
        "catalogue": catalogue,
    }


def _decision_validity_from_request(
    payload: RecordConnectivityDecisionRequest,
) -> DecisionValidity:
    if (
        payload.valid_from.tzinfo is None
        or payload.valid_from.utcoffset() is None
        or (
            payload.valid_until is not None
            and (
                payload.valid_until.tzinfo is None
                or payload.valid_until.utcoffset() is None
            )
        )
    ):
        raise PublicApiError(
            status_code=422,
            code="InvalidDecisionValidity",
            message="Decision validity timestamps must include an explicit timezone offset.",
        )
    try:
        return DecisionValidity(
            valid_from=payload.valid_from,
            valid_until=payload.valid_until,
        )
    except DecisionInvariantError as exc:
        raise PublicApiError(
            status_code=422,
            code="InvalidDecisionValidity",
            message="Decision validity requires validFrom < validUntil when an end is supplied.",
        ) from exc
