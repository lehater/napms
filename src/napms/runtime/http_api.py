import json
import logging
import re
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable, ContextManager
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from napms.access_policy.application.materialize_rule import (
    MaterializationOutcome,
    MaterializeAllowedAccessRule,
    SubmitAccessRuleProposal,
)
from napms.access_policy.application.ports import (
    AccessRuleCommitOutcomeUnknown,
    AccessRulePersistenceError,
    ConnectivityDecisionPort,
)
from napms.access_policy.application.read_rules import (
    AccessRuleDetailOutcome,
    GetAuthorizedAccessRule,
    ListAuthorizedAccessRules,
)
from napms.access_policy.application.proposal_options import (
    DiscoverProposalInteractions,
    DiscoverProposalScopes,
    ProposalInteractionDiscoveryOutcome,
)
from napms.access_policy.application.set_effective_window import (
    EffectiveWindowMutationOutcome,
    SetAccessRuleEffectiveWindow,
    SetRuleEffectiveWindow,
)
from napms.access_policy.application.set_operational_state import (
    OperationalStateMutationOutcome,
    SetAccessRuleOperationalState,
    SetRuleOperationalState,
)
from napms.access_policy.application.select_effective_policy import (
    DiscoverEffectivePolicyScopes,
    EffectivePolicySelectionOutcome,
    SelectAccessPolicyEffectiveDesiredPolicy,
    SelectEffectiveDesiredPolicy,
)
from napms.access_policy.domain.model import (
    AccessRule,
    EffectiveWindow,
    OperationalState,
    RuleSemanticIdentity,
)
from napms.application_catalogue.application.describe_interactions import (
    DirectedInteractionDescription,
)
from napms.application_catalogue.application.ports import CataloguePersistenceError
from napms.application_catalogue.domain.model import DirectedInteractionIdentity
from napms.authority_management.application.ports import AuthorityPersistenceError
from napms.connectivity_decision.application.options import (
    DecisionInteractionDiscoveryOutcome,
    DiscoverDecisionInteractions,
    DiscoverDecisionScopes,
)
from napms.connectivity_decision.application.ports import (
    DecisionCommitOutcomeUnknown,
    DecisionPersistenceError,
)
from napms.connectivity_decision.application.read import (
    DecisionDetailOutcome,
    GetConnectivityDecision as GetConnectivityDecisionRecord,
    ListConnectivityDecisions,
)
from napms.connectivity_decision.application.record import (
    RecordConnectivityDecision,
    RecordDecision,
    RecordDecisionOutcome,
)
from napms.connectivity_decision.domain.model import (
    ConnectivityDecision as DurableConnectivityDecision,
    DecisionEvidenceReference,
    DecisionInvariantError,
    DecisionOutcome as DurableDecisionOutcome,
    DecisionSubject,
    DecisionValidity,
)
from napms.connectivity_requirements.application.declare import (
    DeclarationOutcome,
    DeclareConnectivityRequirement,
    DeclareRequirement,
)
from napms.connectivity_requirements.application.options import (
    DiscoverRequiredInteractions,
    DiscoverRequirementScopes,
    RequiredInteractionDiscoveryOutcome,
)
from napms.connectivity_requirements.application.ports import (
    ActiveRequirementSemanticConflict,
    RequirementCommitOutcomeUnknown,
    RequirementPersistenceError,
    RequirementVersionConflict,
)
from napms.connectivity_requirements.application.read import (
    GetConnectivityRequirement,
    ListConnectivityRequirements,
    RequirementDetailOutcome,
)
from napms.connectivity_requirements.application.retire import (
    RetireConnectivityRequirement,
    RetireRequirement,
    RetirementOutcome,
)
from napms.connectivity_requirements.application.set_applicability import (
    ApplicabilityMutationOutcome,
    SetConnectivityRequirementApplicability,
    SetRequirementApplicability,
)
from napms.connectivity_requirements.application.set_justification import (
    JustificationMutationOutcome,
    SetConnectivityRequirementJustification,
    SetRequirementJustification,
)
from napms.connectivity_requirements.domain.model import (
    ConnectivityRequirement,
    RequiredSemanticInteraction,
    RequirementApplicability,
    RequirementApplicabilityKind,
)
from napms.requirement_policy_alignment.application.align import (
    AlignConnectivityRequirementToPolicy,
    AlignmentQueryOutcome,
    AlignVisibleConnectivityRequirementsToPolicy,
)
from napms.policy_export.application.export_snapshot import (
    AssembleExportSnapshot,
    SnapshotAssemblyOutcome,
)
from napms.policy_export.application.normalize_snapshot import NormalizeExportSnapshot
from napms.policy_export.application.normalization_ports import DcsProjectionDecodeError
from napms.policy_export.application.normalization_types import (
    NormalizationInvariantError,
)
from napms.runtime.auth import (
    AuthenticatedActor,
    InMemorySessionStore,
    LocalPasswordAuthenticator,
)
from napms.runtime.normalized_policy_json import (
    normalized_policy_export_json,
    port_constraint_json,
    snapshot_diagnostic_json,
)


SESSION_COOKIE_NAME = "napms_session"
CORRELATION_HEADER = "X-Correlation-ID"
_CORRELATION_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_LOGGER = logging.getLogger("napms.runtime.http")
_ERROR_DEPENDENCIES = {
    "AuthorityDenied": "AuthorityManagement",
    "AuthorityUnknown": "AuthorityManagement",
    "AuthorityUnavailable": "AuthorityManagement",
    "InteractionInvalid": "ApplicationCommunicationCatalogue",
    "InteractionUnknown": "ApplicationCommunicationCatalogue",
    "CatalogueUnavailable": "ApplicationCommunicationCatalogue",
    "DecisionUnknown": "ConnectivityDecision",
    "DecisionSubjectMismatch": "ConnectivityDecision",
    "DecisionPersistenceUnavailable": "ConnectivityDecisionPersistence",
    "DecisionPersistenceOutcomeUnknown": "ConnectivityDecisionPersistence",
    "PersistenceUnavailable": "AccessPolicyPersistence",
    "PersistenceOutcomeUnknown": "AccessPolicyPersistence",
    "SnapshotIncomplete": "PolicyExportSnapshot",
    "NormalizationFailed": "PolicyExportNormalization",
    "AlignmentUnavailable": "RequirementPolicyAlignment",
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class HttpApiDependencies:
    authenticator: LocalPasswordAuthenticator
    sessions: InMemorySessionStore
    open_scope: Callable[[], ContextManager[Any]]
    decisions: ConnectivityDecisionPort
    readiness: Callable[[], bool]
    clock: Callable[[], datetime] = _utc_now
    secure_cookie: bool = False


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    login: str = Field(min_length=1, max_length=256)
    password: str = Field(min_length=1, max_length=4096)


class SubmitProposalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    authority_scope: str = Field(alias="authorityScope", min_length=1, max_length=512)
    source_component_deployment_id: UUID = Field(alias="sourceComponentDeploymentId")
    destination_component_deployment_id: UUID = Field(
        alias="destinationComponentDeploymentId"
    )
    dcs_contract_revision_id: UUID = Field(alias="dcsContractRevisionId")


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
    outcome: DurableDecisionOutcome
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


class SetOperationalStateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    target_state: OperationalState = Field(alias="targetState")


class EffectiveWindowValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: datetime
    end: datetime


class SetEffectiveWindowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    window: EffectiveWindowValue | None


class RequirementApplicabilityValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: RequirementApplicabilityKind
    start: datetime | None = None
    end: datetime | None = None


class DeclareConnectivityRequirementRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    authority_scope: str = Field(alias="authorityScope", min_length=1, max_length=512)
    dependent_component_deployment_id: UUID = Field(
        alias="dependentComponentDeploymentId"
    )
    source_component_deployment_id: UUID = Field(alias="sourceComponentDeploymentId")
    destination_component_deployment_id: UUID = Field(
        alias="destinationComponentDeploymentId"
    )
    dcs_contract_revision_id: UUID = Field(alias="dcsContractRevisionId")
    applicability: RequirementApplicabilityValue
    justification: str = Field(min_length=1, max_length=4096)


class SetRequirementApplicabilityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    applicability: RequirementApplicabilityValue


class SetRequirementJustificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    justification: str = Field(min_length=1, max_length=4096)


class PublicApiError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def configure_json_logging(*, level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    _LOGGER.handlers.clear()
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(level)
    _LOGGER.propagate = False


def _safe_correlation_id(raw: str | None) -> str:
    if raw and _CORRELATION_PATTERN.fullmatch(raw):
        return raw
    return str(uuid4())


def _correlation_id(request: Request) -> str:
    return getattr(request.state, "correlation_id", str(uuid4()))


def _set_outcome(request: Request, outcome: str) -> None:
    request.state.semantic_outcome = outcome


def _set_dependency(request: Request, dependency: str) -> None:
    request.state.dependency = dependency


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    _set_outcome(request, code)
    dependency = _ERROR_DEPENDENCIES.get(code)
    if dependency is not None and not getattr(request.state, "dependency", None):
        _set_dependency(request, dependency)
    error = {
        "code": code,
        "message": message,
        "correlationId": _correlation_id(request),
    }
    if details is not None:
        error["details"] = details
    return JSONResponse(
        status_code=status_code,
        content={"error": error},
    )


def _actor_dto(actor: AuthenticatedActor) -> dict[str, str]:
    return {"actorId": actor.actor_id, "login": actor.login}


def _interaction_identity(
    identity: RuleSemanticIdentity,
) -> DirectedInteractionIdentity:
    return DirectedInteractionIdentity(
        source_component_deployment_id=identity.source_component_deployment_id,
        destination_component_deployment_id=identity.destination_component_deployment_id,
        dcs_contract_revision_id=identity.dcs_contract_revision_id,
    )


def _catalogue_presentation_dto(
    description: DirectedInteractionDescription,
    *,
    decoder,
) -> dict[str, Any]:
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
                "destinationPorts": port_constraint_json(
                    alternative.destination_ports
                ),
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


def _describe_semantic_identities(
    runtime_scope,
    identities,
) -> dict[RuleSemanticIdentity, dict[str, Any]]:
    semantic_identities = tuple(dict.fromkeys(identities))
    if not semantic_identities:
        return {}
    try:
        descriptions = runtime_scope.catalogue_describer.execute(
            tuple(
                _interaction_identity(identity)
                for identity in semantic_identities
            )
        )
    except CataloguePersistenceError:
        return {}

    return {
        semantic_identity: _catalogue_presentation_dto(
            description,
            decoder=runtime_scope.dcs_decoder,
        )
        for semantic_identity, description in zip(
            semantic_identities,
            descriptions,
        )
    }


def _decision_subject_to_rule_identity(
    subject: DecisionSubject,
) -> RuleSemanticIdentity:
    return RuleSemanticIdentity(
        source_component_deployment_id=subject.source_component_deployment_id,
        destination_component_deployment_id=subject.destination_component_deployment_id,
        dcs_contract_revision_id=subject.dcs_contract_revision_id,
    )


def _describe_decision_subjects(
    runtime_scope,
    subjects,
) -> dict[DecisionSubject, dict[str, Any]]:
    values = tuple(dict.fromkeys(subjects))
    identities = tuple(_decision_subject_to_rule_identity(value) for value in values)
    presentations = _describe_semantic_identities(runtime_scope, identities)
    return {
        subject: presentations.get(identity)
        for subject, identity in zip(values, identities)
    }


def _decision_dto(
    decision: DurableConnectivityDecision,
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


def _requirement_applicability_from_request(
    value: RequirementApplicabilityValue,
) -> RequirementApplicability:
    if value.kind is RequirementApplicabilityKind.ONGOING:
        if value.start is not None or value.end is not None:
            raise PublicApiError(
                status_code=422,
                code="InvalidRequirementApplicability",
                message="Ongoing applicability cannot include start/end.",
            )
        return RequirementApplicability.ongoing()

    if value.start is None or value.end is None:
        raise PublicApiError(
            status_code=422,
            code="InvalidRequirementApplicability",
            message="AbsoluteWindow requires start and end.",
        )
    if (
        value.start.tzinfo is None
        or value.start.utcoffset() is None
        or value.end.tzinfo is None
        or value.end.utcoffset() is None
        or value.start >= value.end
    ):
        raise PublicApiError(
            status_code=422,
            code="InvalidRequirementApplicability",
            message="AbsoluteWindow requires offset-aware start < end.",
        )
    return RequirementApplicability.absolute_window(
        start=value.start,
        end=value.end,
    )


def _requirement_applicability_dto(
    value: RequirementApplicability,
) -> dict[str, Any]:
    if value.kind is RequirementApplicabilityKind.ONGOING:
        return {"kind": "Ongoing"}
    assert value.start is not None
    assert value.end is not None
    return {
        "kind": "AbsoluteWindow",
        "start": value.start.isoformat(),
        "end": value.end.isoformat(),
    }


def _required_interaction_to_acc(
    identity: RequiredSemanticInteraction,
) -> DirectedInteractionIdentity:
    return DirectedInteractionIdentity(
        source_component_deployment_id=identity.source_component_deployment_id,
        destination_component_deployment_id=identity.destination_component_deployment_id,
        dcs_contract_revision_id=identity.dcs_contract_revision_id,
    )


def _describe_required_interactions(
    runtime_scope,
    identities,
) -> dict[RequiredSemanticInteraction, dict[str, Any]]:
    values = tuple(dict.fromkeys(identities))
    if not values:
        return {}
    try:
        descriptions = runtime_scope.catalogue_describer.execute(
            tuple(_required_interaction_to_acc(value) for value in values)
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


def _requirement_dto(
    requirement: ConnectivityRequirement,
    catalogue: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "requirementId": str(requirement.requirement_id),
        "governanceScope": requirement.governance_scope,
        "dependentComponentDeploymentId": str(
            requirement.dependent_component_deployment_id
        ),
        "requiredInteraction": {
            "sourceComponentDeploymentId": str(
                requirement.required_interaction.source_component_deployment_id
            ),
            "destinationComponentDeploymentId": str(
                requirement.required_interaction.destination_component_deployment_id
            ),
            "dcsContractRevisionId": str(
                requirement.required_interaction.dcs_contract_revision_id
            ),
        },
        "applicability": _requirement_applicability_dto(
            requirement.applicability
        ),
        "justification": requirement.justification,
        "lifecycleState": requirement.lifecycle_state.value,
        "version": requirement.version,
        "declarationProvenance": {
            "actorId": requirement.declaration_provenance.actor_id,
            "effectiveTime": (
                requirement.declaration_provenance.effective_time.isoformat()
            ),
            "authorityReference": (
                requirement.declaration_provenance.authority_reference
            ),
            "catalogueReference": (
                requirement.declaration_provenance.catalogue_reference
            ),
        },
        "applicabilityHistory": [
            {
                "previousApplicability": _requirement_applicability_dto(
                    change.previous_applicability
                ),
                "newApplicability": _requirement_applicability_dto(
                    change.new_applicability
                ),
                "actorId": change.actor_id,
                "effectiveTime": change.effective_time.isoformat(),
                "governanceScope": change.governance_scope,
                "authorityReference": change.authority_reference,
            }
            for change in requirement.applicability_history
        ],
        "justificationHistory": [
            {
                "previousJustification": change.previous_justification,
                "newJustification": change.new_justification,
                "actorId": change.actor_id,
                "effectiveTime": change.effective_time.isoformat(),
                "governanceScope": change.governance_scope,
                "authorityReference": change.authority_reference,
            }
            for change in requirement.justification_history
        ],
        "lifecycleHistory": [
            {
                "fromState": change.from_state.value,
                "toState": change.to_state.value,
                "actorId": change.actor_id,
                "effectiveTime": change.effective_time.isoformat(),
                "governanceScope": change.governance_scope,
                "authorityReference": change.authority_reference,
            }
            for change in requirement.lifecycle_history
        ],
        "catalogue": catalogue,
    }


def _rule_dto(
    rule: AccessRule,
    catalogue: dict[str, Any] | None = None,
) -> dict[str, Any]:
    window = None
    if rule.effective_window is not None:
        window = {
            "start": rule.effective_window.start.isoformat(),
            "end": rule.effective_window.end.isoformat(),
        }
    return {
        "ruleId": str(rule.rule_id),
        "semanticIdentity": {
            "sourceComponentDeploymentId": str(
                rule.semantic_identity.source_component_deployment_id
            ),
            "destinationComponentDeploymentId": str(
                rule.semantic_identity.destination_component_deployment_id
            ),
            "dcsContractRevisionId": str(
                rule.semantic_identity.dcs_contract_revision_id
            ),
        },
        "governanceScope": rule.governance_scope,
        "operationalState": rule.operational_state.value,
        "effectiveWindow": window,
        "decisionReference": rule.decision.decision_id,
        "catalogue": catalogue,
    }


def _rule_detail_dto(
    rule: AccessRule,
    catalogue: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = _rule_dto(rule, catalogue)
    payload["proposalProvenance"] = {
        "actorId": rule.proposal_provenance.actor_id,
        "effectiveTime": rule.proposal_provenance.effective_time.isoformat(),
        "authorityReference": rule.proposal_provenance.authority_reference,
        "catalogueReference": rule.proposal_provenance.catalogue_reference,
    }
    payload["stateHistory"] = [
        {
            "fromState": transition.from_state.value,
            "toState": transition.to_state.value,
            "actorId": transition.actor_id,
            "effectiveTime": transition.effective_time.isoformat(),
            "governanceScope": transition.governance_scope,
            "authorityReference": transition.authority_reference,
        }
        for transition in rule.operational_state_history
    ]
    payload["effectiveWindowHistory"] = [
        {
            "previousWindow": (
                {
                    "start": change.previous_window.start.isoformat(),
                    "end": change.previous_window.end.isoformat(),
                }
                if change.previous_window is not None
                else None
            ),
            "newWindow": (
                {
                    "start": change.new_window.start.isoformat(),
                    "end": change.new_window.end.isoformat(),
                }
                if change.new_window is not None
                else None
            ),
            "actorId": change.actor_id,
            "effectiveTime": change.effective_time.isoformat(),
            "governanceScope": change.governance_scope,
            "authorityReference": change.authority_reference,
        }
        for change in rule.effective_window_history
    ]
    return payload


def create_http_api(dependencies: HttpApiDependencies) -> FastAPI:
    app = FastAPI(title="NAPMS API", version="1")

    @app.middleware("http")
    async def runtime_boundary(request: Request, call_next):
        request.state.correlation_id = _safe_correlation_id(
            request.headers.get(CORRELATION_HEADER)
        )
        request.state.operation = request.url.path
        request.state.semantic_outcome = "HttpCompleted"
        started = perf_counter()
        error: Exception | None = None
        try:
            response = await call_next(request)
        except Exception as exc:  # boundary owns generic failure/logging
            error = exc
            request.state.semantic_outcome = "InternalError"
            response = _error_response(
                request,
                status_code=500,
                code="InternalError",
                message="The operation could not be completed.",
            )

        response.headers[CORRELATION_HEADER] = request.state.correlation_id
        duration_ms = round((perf_counter() - started) * 1000, 3)
        event = {
            "event": "operation_completed",
            "operation": request.state.operation,
            "correlationId": request.state.correlation_id,
            "outcome": request.state.semantic_outcome,
            "httpStatus": response.status_code,
            "durationMs": duration_ms,
        }
        actor_id = getattr(request.state, "actor_id", None)
        if actor_id:
            event["actorId"] = actor_id
        for state_name, event_name in (
            ("rule_id", "ruleId"),
            ("requirement_id", "requirementId"),
            ("authority_reference", "authorityReference"),
            ("decision_reference", "decisionReference"),
            ("dependency", "dependency"),
        ):
            value = getattr(request.state, state_name, None)
            if value:
                event[event_name] = value

        if error is not None:
            event["exception"] = {
                "class": type(error).__name__,
                "stack": [
                    frame.rstrip()
                    for frame in traceback.format_list(
                        traceback.extract_tb(error.__traceback__)
                    )
                ],
            }

        level = logging.INFO
        if response.status_code >= 500:
            level = logging.ERROR if error is not None else logging.WARNING
        elif response.status_code >= 400:
            level = logging.WARNING
        _LOGGER.log(
            level,
            json.dumps(event, separators=(",", ":"), sort_keys=True),
        )
        return response

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_error_handler(
        request: Request,
        exc: StarletteHTTPException,
    ):
        if exc.status_code == 404:
            return _error_response(
                request,
                status_code=404,
                code="NotFound",
                message="The requested resource was not found.",
            )
        if exc.status_code == 405:
            return _error_response(
                request,
                status_code=405,
                code="MethodNotAllowed",
                message="The requested method is not allowed.",
            )
        return _error_response(
            request,
            status_code=exc.status_code,
            code="HttpError",
            message="The request could not be completed.",
        )

    @app.exception_handler(PublicApiError)
    async def public_api_error_handler(request: Request, exc: PublicApiError):
        return _error_response(
            request,
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        return _error_response(
            request,
            status_code=422,
            code="ValidationError",
            message="The request is invalid.",
        )

    @app.exception_handler(AccessRuleCommitOutcomeUnknown)
    async def uncertain_commit_handler(
        request: Request,
        exc: AccessRuleCommitOutcomeUnknown,
    ):
        return _error_response(
            request,
            status_code=503,
            code="PersistenceOutcomeUnknown",
            message="The authoritative persistence outcome is currently unknown.",
        )

    @app.exception_handler(AccessRulePersistenceError)
    async def access_rule_persistence_handler(
        request: Request,
        exc: AccessRulePersistenceError,
    ):
        return _error_response(
            request,
            status_code=503,
            code="PersistenceUnavailable",
            message="The authoritative persistence service is unavailable.",
        )

    @app.exception_handler(DecisionCommitOutcomeUnknown)
    async def decision_uncertain_commit_handler(
        request: Request,
        exc: DecisionCommitOutcomeUnknown,
    ):
        _set_dependency(request, "ConnectivityDecisionPersistence")
        return _error_response(
            request,
            status_code=503,
            code="DecisionPersistenceOutcomeUnknown",
            message="The Connectivity Decision persistence outcome is currently unknown.",
        )

    @app.exception_handler(DecisionPersistenceError)
    async def decision_persistence_handler(
        request: Request,
        exc: DecisionPersistenceError,
    ):
        _set_dependency(request, "ConnectivityDecisionPersistence")
        return _error_response(
            request,
            status_code=503,
            code="DecisionPersistenceUnavailable",
            message="Connectivity Decision persistence is unavailable.",
        )

    @app.exception_handler(RequirementCommitOutcomeUnknown)
    async def requirement_uncertain_commit_handler(
        request: Request,
        exc: RequirementCommitOutcomeUnknown,
    ):
        _set_dependency(request, "ConnectivityRequirementsPersistence")
        return _error_response(
            request,
            status_code=503,
            code="PersistenceOutcomeUnknown",
            message="The authoritative persistence outcome is currently unknown.",
        )

    @app.exception_handler(RequirementVersionConflict)
    async def requirement_version_conflict_handler(
        request: Request,
        exc: RequirementVersionConflict,
    ):
        _set_dependency(request, "ConnectivityRequirementsPersistence")
        return _error_response(
            request,
            status_code=409,
            code="RequirementVersionConflict",
            message="The Connectivity Requirement changed concurrently.",
        )

    @app.exception_handler(ActiveRequirementSemanticConflict)
    async def requirement_semantic_conflict_handler(
        request: Request,
        exc: ActiveRequirementSemanticConflict,
    ):
        _set_dependency(request, "ConnectivityRequirementsPersistence")
        return _error_response(
            request,
            status_code=409,
            code="RequirementSemanticConflict",
            message="An Active Connectivity Requirement already owns this semantic need.",
        )

    @app.exception_handler(RequirementPersistenceError)
    async def requirement_persistence_handler(
        request: Request,
        exc: RequirementPersistenceError,
    ):
        _set_dependency(request, "ConnectivityRequirementsPersistence")
        return _error_response(
            request,
            status_code=503,
            code="PersistenceUnavailable",
            message="Connectivity Requirements persistence is unavailable.",
        )

    @app.exception_handler(AuthorityPersistenceError)
    async def authority_persistence_handler(
        request: Request,
        exc: AuthorityPersistenceError,
    ):
        return _error_response(
            request,
            status_code=503,
            code="AuthorityUnavailable",
            message="Authority information is unavailable.",
        )

    @app.exception_handler(NormalizationInvariantError)
    async def normalization_error_handler(
        request: Request,
        exc: NormalizationInvariantError,
    ):
        return _error_response(
            request,
            status_code=500,
            code="NormalizationFailed",
            message="The normalized policy could not be produced safely.",
        )

    @app.exception_handler(CataloguePersistenceError)
    async def catalogue_persistence_handler(
        request: Request,
        exc: CataloguePersistenceError,
    ):
        return _error_response(
            request,
            status_code=503,
            code="CatalogueUnavailable",
            message="Catalogue information is unavailable.",
        )

    def require_actor(request: Request) -> AuthenticatedActor:
        actor = dependencies.sessions.get(request.cookies.get(SESSION_COOKIE_NAME))
        if actor is None:
            raise PublicApiError(
                status_code=401,
                code="AuthenticationRequired",
                message="Authentication is required.",
            )
        request.state.actor_id = actor.actor_id
        return actor

    @app.post("/api/v1/session", name="CreateSession")
    def create_session(payload: LoginRequest, request: Request):
        request.state.operation = "CreateSession"
        actor = dependencies.authenticator.authenticate(
            login=payload.login,
            password=payload.password,
        )
        if actor is None:
            raise PublicApiError(
                status_code=401,
                code="AuthenticationFailed",
                message="Authentication failed.",
            )

        session_id = dependencies.sessions.create(actor)
        request.state.actor_id = actor.actor_id
        _set_outcome(request, "Authenticated")
        response = JSONResponse(status_code=200, content={"actor": _actor_dto(actor)})
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_id,
            httponly=True,
            secure=dependencies.secure_cookie,
            samesite="strict",
            path="/",
        )
        return response

    @app.get("/api/v1/session", name="GetSession")
    def get_session(
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetSession"
        _set_outcome(request, "Authenticated")
        return {"actor": _actor_dto(actor)}

    @app.delete("/api/v1/session", status_code=204, name="DeleteSession")
    def delete_session(
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DeleteSession"
        dependencies.sessions.delete(request.cookies.get(SESSION_COOKIE_NAME))
        _set_outcome(request, "LoggedOut")
        response = Response(status_code=204)
        response.delete_cookie(
            key=SESSION_COOKIE_NAME,
            path="/",
            secure=dependencies.secure_cookie,
            httponly=True,
            samesite="strict",
        )
        return response

    @app.get(
        "/api/v1/connectivity-decisions/scopes",
        name="DiscoverConnectivityDecisionScopes",
    )
    def discover_connectivity_decision_scopes(
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverConnectivityDecisionScopes"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = DiscoverDecisionScopes(
                discovery=runtime_scope.decision_scopes,
            ).execute(
                actor_id=actor.actor_id,
                effective_time=effective_time,
            )
        _set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "scopes": [{"scope": scope} for scope in result.permitted_scopes],
            "ambiguousScopes": [
                {"scope": scope} for scope in result.ambiguous_scopes
            ],
        }

    @app.get(
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
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
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
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is DecisionInteractionDiscoveryOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.page is not None
        _set_outcome(request, result.outcome.value)
        return {
            "items": [
                {
                    "sourceComponentDeploymentId": str(
                        subject.source_component_deployment_id
                    ),
                    "destinationComponentDeploymentId": str(
                        subject.destination_component_deployment_id
                    ),
                    "dcsContractRevisionId": str(
                        subject.dcs_contract_revision_id
                    ),
                    "catalogue": presentations.get(subject),
                }
                for subject in result.page.subjects
            ],
            "page": result.page.page,
            "pageSize": result.page.page_size,
            "hasMore": result.page.has_more,
        }

    @app.post(
        "/api/v1/connectivity-decisions",
        name="RecordConnectivityDecision",
    )
    def record_connectivity_decision(
        payload: RecordConnectivityDecisionRequest,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "RecordConnectivityDecision"
        effective_time = dependencies.clock()
        validity = _decision_validity_from_request(payload)
        if not payload.reason_code.strip() or not payload.reason_text.strip():
            raise PublicApiError(
                status_code=422,
                code="ValidationError",
                message="Decision reason code and reason text must be non-empty.",
            )
        evidence = tuple(
            DecisionEvidenceReference(
                kind=value.kind,
                reference=value.reference,
            )
            for value in payload.evidence_references
        )
        subject = DecisionSubject(
            source_component_deployment_id=payload.source_component_deployment_id,
            destination_component_deployment_id=(
                payload.destination_component_deployment_id
            ),
            dcs_contract_revision_id=payload.dcs_contract_revision_id,
        )
        with dependencies.open_scope() as runtime_scope:
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
            _set_outcome(request, result.outcome.value)
            return JSONResponse(
                status_code=(
                    201
                    if result.outcome is RecordDecisionOutcome.RECORDED
                    else 200
                ),
                content={
                    "outcome": result.outcome.value,
                    "decision": _decision_dto(
                        result.decision,
                        presentation,
                    ),
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
        )

    @app.get(
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
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
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

        _set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "items": [
                _decision_dto(
                    value,
                    presentations.get(value.subject),
                )
                for value in result.decisions
            ],
            "page": result.page,
            "pageSize": result.page_size,
            "hasMore": result.has_more,
            "ambiguousScopes": [
                {"scope": scope} for scope in result.ambiguous_scopes
            ],
        }

    @app.get(
        "/api/v1/connectivity-decisions/{decision_id}",
        name="GetConnectivityDecision",
    )
    def get_connectivity_decision(
        decision_id: UUID,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetConnectivityDecision"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = GetConnectivityDecisionRecord(
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
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is DecisionDetailOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.decision is not None
        request.state.decision_reference = str(result.decision.decision_id)
        request.state.authority_reference = result.read_authority_reference
        _set_outcome(request, "Found")
        return {
            "decision": _decision_dto(
                result.decision,
                presentation,
            ),
            "readAuthorityReference": result.read_authority_reference,
        }

    @app.get(
        "/api/v1/connectivity-requirements/scopes",
        name="DiscoverConnectivityRequirementScopes",
    )
    def discover_connectivity_requirement_scopes(
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverConnectivityRequirementScopes"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = DiscoverRequirementScopes(
                discovery=runtime_scope.requirement_declaration_scopes,
            ).execute(
                actor_id=actor.actor_id,
                effective_time=effective_time,
            )
        _set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "scopes": [{"scope": scope} for scope in result.permitted_scopes],
            "ambiguousScopes": [
                {"scope": scope} for scope in result.ambiguous_scopes
            ],
        }

    @app.get(
        "/api/v1/connectivity-requirements/interactions",
        name="DiscoverConnectivityRequirementInteractions",
    )
    def discover_connectivity_requirement_interactions(
        request: Request,
        scope: str,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=100),
        search: str | None = Query(None, max_length=256),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverConnectivityRequirementInteractions"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = DiscoverRequiredInteractions(
                authority=runtime_scope.requirement_authority,
                catalogue=runtime_scope.requirement_interaction_catalogue,
            ).execute(
                actor_id=actor.actor_id,
                scope=scope,
                effective_time=effective_time,
                page=page,
                page_size=pageSize,
                search=search,
            )
            presentations = (
                _describe_required_interactions(
                    runtime_scope,
                    result.page.interactions,
                )
                if result.page is not None
                else {}
            )

        if (
            result.outcome
            is RequiredInteractionDiscoveryOutcome.AUTHORITY_DENIED
        ):
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if (
            result.outcome
            is RequiredInteractionDiscoveryOutcome.AUTHORITY_UNKNOWN
        ):
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.page is not None
        _set_outcome(request, result.outcome.value)
        return {
            "items": [
                {
                    "sourceComponentDeploymentId": str(
                        identity.source_component_deployment_id
                    ),
                    "destinationComponentDeploymentId": str(
                        identity.destination_component_deployment_id
                    ),
                    "dcsContractRevisionId": str(
                        identity.dcs_contract_revision_id
                    ),
                    "catalogue": presentations.get(identity),
                }
                for identity in result.page.interactions
            ],
            "page": result.page.page,
            "pageSize": result.page.page_size,
            "hasMore": result.page.has_more,
        }

    @app.post(
        "/api/v1/connectivity-requirements",
        name="DeclareConnectivityRequirement",
    )
    def declare_connectivity_requirement(
        payload: DeclareConnectivityRequirementRequest,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DeclareConnectivityRequirement"
        effective_time = dependencies.clock()
        applicability = _requirement_applicability_from_request(
            payload.applicability
        )
        interaction = RequiredSemanticInteraction(
            source_component_deployment_id=(
                payload.source_component_deployment_id
            ),
            destination_component_deployment_id=(
                payload.destination_component_deployment_id
            ),
            dcs_contract_revision_id=payload.dcs_contract_revision_id,
        )
        with dependencies.open_scope() as runtime_scope:
            result = DeclareConnectivityRequirement(
                authority=runtime_scope.requirement_authority,
                catalogue=runtime_scope.requirement_catalogue,
                requirements=runtime_scope.connectivity_requirements,
            ).execute(
                DeclareRequirement(
                    governance_scope=payload.authority_scope,
                    dependent_component_deployment_id=(
                        payload.dependent_component_deployment_id
                    ),
                    required_interaction=interaction,
                    applicability=applicability,
                    justification=payload.justification,
                    actor_id=actor.actor_id,
                    effective_time=effective_time,
                )
            )
            presentation = (
                _describe_required_interactions(
                    runtime_scope,
                    (result.requirement.required_interaction,),
                ).get(result.requirement.required_interaction)
                if result.requirement is not None
                else None
            )

        if result.outcome in {
            DeclarationOutcome.DECLARED,
            DeclarationOutcome.RESOLVED,
        }:
            assert result.requirement is not None
            request.state.requirement_id = str(
                result.requirement.requirement_id
            )
            if result.outcome is DeclarationOutcome.DECLARED:
                request.state.authority_reference = (
                    result.requirement.declaration_provenance.authority_reference
                )
            _set_outcome(request, result.outcome.value)
            return JSONResponse(
                status_code=(
                    201
                    if result.outcome is DeclarationOutcome.DECLARED
                    else 200
                ),
                content={
                    "outcome": result.outcome.value,
                    "requirement": _requirement_dto(
                        result.requirement,
                        presentation,
                    ),
                },
            )

        mapping = {
            DeclarationOutcome.AUTHORITY_DENIED: (
                403,
                "AuthorityDenied",
                "The requested operation is not permitted.",
            ),
            DeclarationOutcome.AUTHORITY_UNKNOWN: (
                409,
                "AuthorityUnknown",
                "Authority for the requested operation is ambiguous or unavailable.",
            ),
            DeclarationOutcome.INTERACTION_INVALID: (
                422,
                "InteractionInvalid",
                "The selected interaction is invalid.",
            ),
            DeclarationOutcome.INTERACTION_UNKNOWN: (
                409,
                "InteractionUnknown",
                "The selected interaction cannot currently be established.",
            ),
            DeclarationOutcome.DEPENDENT_INVALID: (
                422,
                "DependentInvalid",
                "The dependent Component Deployment must participate in the interaction.",
            ),
            DeclarationOutcome.INPUT_INVALID: (
                422,
                "ValidationError",
                "The Connectivity Requirement is invalid.",
            ),
        }
        status_code, code, message = mapping[result.outcome]
        raise PublicApiError(
            status_code=status_code,
            code=code,
            message=message,
        )

    @app.get(
        "/api/v1/connectivity-requirements",
        name="ListConnectivityRequirements",
    )
    def list_connectivity_requirements(
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=100),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "ListConnectivityRequirements"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = ListConnectivityRequirements(
                read_scopes=runtime_scope.requirement_read_scopes,
                requirements=runtime_scope.connectivity_requirements,
            ).execute(
                actor_id=actor.actor_id,
                effective_time=effective_time,
                page=page,
                page_size=pageSize,
            )
            presentations = _describe_required_interactions(
                runtime_scope,
                tuple(
                    value.required_interaction
                    for value in result.requirements
                ),
            )

        _set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "items": [
                _requirement_dto(
                    value,
                    presentations.get(value.required_interaction),
                )
                for value in result.requirements
            ],
            "page": result.page,
            "pageSize": result.page_size,
            "hasMore": result.has_more,
            "ambiguousScopes": [
                {"scope": scope} for scope in result.ambiguous_scopes
            ],
        }

    @app.get(
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
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise PublicApiError(
                status_code=422,
                code="InvalidAsOf",
                message="asOf must include an explicit timezone offset.",
            )
        with dependencies.open_scope() as runtime_scope:
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
                code="AlignmentUnavailable",
                message="Requirement-to-policy alignment is unavailable.",
            )

        _set_outcome(request, "Aligned")
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

    @app.get(
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
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise PublicApiError(
                status_code=422,
                code="InvalidAsOf",
                message="asOf must include an explicit timezone offset.",
            )
        with dependencies.open_scope() as runtime_scope:
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
            )

        assert result.status is not None
        assert result.semantic_identity is not None
        request.state.requirement_id = str(requirement_id)
        request.state.authority_reference = (
            result.requirement_read_authority_reference
        )
        _set_outcome(request, result.status.value)
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

    @app.get(
        "/api/v1/connectivity-requirements/{requirement_id}",
        name="GetConnectivityRequirement",
    )
    def get_connectivity_requirement(
        requirement_id: UUID,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetConnectivityRequirement"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = GetConnectivityRequirement(
                authority=runtime_scope.requirement_authority,
                requirements=runtime_scope.connectivity_requirements,
            ).execute(
                requirement_id=requirement_id,
                actor_id=actor.actor_id,
                effective_time=effective_time,
            )
            presentation = (
                _describe_required_interactions(
                    runtime_scope,
                    (result.requirement.required_interaction,),
                ).get(result.requirement.required_interaction)
                if result.requirement is not None
                else None
            )

        if result.outcome is RequirementDetailOutcome.REQUIREMENT_NOT_FOUND:
            raise PublicApiError(
                status_code=404,
                code="RequirementNotFound",
                message="The Connectivity Requirement was not found.",
            )
        if result.outcome is RequirementDetailOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is RequirementDetailOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.requirement is not None
        assert result.applicability_mutation_admission is not None
        assert result.justification_mutation_admission is not None
        assert result.retirement_admission is not None
        request.state.requirement_id = str(result.requirement.requirement_id)
        request.state.authority_reference = result.read_authority_reference
        _set_outcome(request, "Found")
        return {
            "requirement": _requirement_dto(
                result.requirement,
                presentation,
            ),
            "capabilities": {
                "setApplicability": (
                    result.applicability_mutation_admission.value
                ),
                "setJustification": (
                    result.justification_mutation_admission.value
                ),
                "retire": result.retirement_admission.value,
            },
        }

    @app.patch(
        "/api/v1/connectivity-requirements/{requirement_id}/applicability",
        name="SetConnectivityRequirementApplicability",
    )
    def set_connectivity_requirement_applicability(
        requirement_id: UUID,
        payload: SetRequirementApplicabilityRequest,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "SetConnectivityRequirementApplicability"
        effective_time = dependencies.clock()
        applicability = _requirement_applicability_from_request(
            payload.applicability
        )
        with dependencies.open_scope() as runtime_scope:
            result = SetConnectivityRequirementApplicability(
                authority=runtime_scope.requirement_authority,
                requirements=runtime_scope.connectivity_requirements,
            ).execute(
                SetRequirementApplicability(
                    requirement_id=requirement_id,
                    applicability=applicability,
                    actor_id=actor.actor_id,
                    effective_time=effective_time,
                )
            )
            presentation = (
                _describe_required_interactions(
                    runtime_scope,
                    (result.requirement.required_interaction,),
                ).get(result.requirement.required_interaction)
                if result.requirement is not None
                else None
            )

        if (
            result.outcome
            is ApplicabilityMutationOutcome.REQUIREMENT_NOT_FOUND
        ):
            raise PublicApiError(
                status_code=404,
                code="RequirementNotFound",
                message="The Connectivity Requirement was not found.",
            )
        if result.outcome is ApplicabilityMutationOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is ApplicabilityMutationOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )
        if result.outcome is ApplicabilityMutationOutcome.REQUIREMENT_RETIRED:
            raise PublicApiError(
                status_code=409,
                code="RequirementRetired",
                message="A Retired Connectivity Requirement is immutable.",
            )

        assert result.requirement is not None
        request.state.requirement_id = str(result.requirement.requirement_id)
        if (
            result.outcome is ApplicabilityMutationOutcome.UPDATED
            and result.requirement.applicability_history
        ):
            request.state.authority_reference = (
                result.requirement.applicability_history[-1].authority_reference
            )
        _set_outcome(request, result.outcome.value)
        return {
            "outcome": result.outcome.value,
            "requirement": _requirement_dto(
                result.requirement,
                presentation,
            ),
        }

    @app.patch(
        "/api/v1/connectivity-requirements/{requirement_id}/justification",
        name="SetConnectivityRequirementJustification",
    )
    def set_connectivity_requirement_justification(
        requirement_id: UUID,
        payload: SetRequirementJustificationRequest,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "SetConnectivityRequirementJustification"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = SetConnectivityRequirementJustification(
                authority=runtime_scope.requirement_authority,
                requirements=runtime_scope.connectivity_requirements,
            ).execute(
                SetRequirementJustification(
                    requirement_id=requirement_id,
                    justification=payload.justification,
                    actor_id=actor.actor_id,
                    effective_time=effective_time,
                )
            )
            presentation = (
                _describe_required_interactions(
                    runtime_scope,
                    (result.requirement.required_interaction,),
                ).get(result.requirement.required_interaction)
                if result.requirement is not None
                else None
            )

        if (
            result.outcome
            is JustificationMutationOutcome.REQUIREMENT_NOT_FOUND
        ):
            raise PublicApiError(
                status_code=404,
                code="RequirementNotFound",
                message="The Connectivity Requirement was not found.",
            )
        if result.outcome is JustificationMutationOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is JustificationMutationOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )
        if result.outcome is JustificationMutationOutcome.REQUIREMENT_RETIRED:
            raise PublicApiError(
                status_code=409,
                code="RequirementRetired",
                message="A Retired Connectivity Requirement is immutable.",
            )
        if result.outcome is JustificationMutationOutcome.INPUT_INVALID:
            raise PublicApiError(
                status_code=422,
                code="ValidationError",
                message="Requirement justification must be non-empty.",
            )

        assert result.requirement is not None
        request.state.requirement_id = str(result.requirement.requirement_id)
        if (
            result.outcome is JustificationMutationOutcome.UPDATED
            and result.requirement.justification_history
        ):
            request.state.authority_reference = (
                result.requirement.justification_history[-1].authority_reference
            )
        _set_outcome(request, result.outcome.value)
        return {
            "outcome": result.outcome.value,
            "requirement": _requirement_dto(
                result.requirement,
                presentation,
            ),
        }

    @app.post(
        "/api/v1/connectivity-requirements/{requirement_id}/retirement",
        name="RetireConnectivityRequirement",
    )
    def retire_connectivity_requirement(
        requirement_id: UUID,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "RetireConnectivityRequirement"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = RetireConnectivityRequirement(
                authority=runtime_scope.requirement_authority,
                requirements=runtime_scope.connectivity_requirements,
            ).execute(
                RetireRequirement(
                    requirement_id=requirement_id,
                    actor_id=actor.actor_id,
                    effective_time=effective_time,
                )
            )
            presentation = (
                _describe_required_interactions(
                    runtime_scope,
                    (result.requirement.required_interaction,),
                ).get(result.requirement.required_interaction)
                if result.requirement is not None
                else None
            )

        if result.outcome is RetirementOutcome.REQUIREMENT_NOT_FOUND:
            raise PublicApiError(
                status_code=404,
                code="RequirementNotFound",
                message="The Connectivity Requirement was not found.",
            )
        if result.outcome is RetirementOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is RetirementOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.requirement is not None
        request.state.requirement_id = str(result.requirement.requirement_id)
        if (
            result.outcome is RetirementOutcome.RETIRED
            and result.requirement.lifecycle_history
        ):
            request.state.authority_reference = (
                result.requirement.lifecycle_history[-1].authority_reference
            )
        _set_outcome(request, result.outcome.value)
        return {
            "outcome": result.outcome.value,
            "requirement": _requirement_dto(
                result.requirement,
                presentation,
            ),
        }

    @app.get("/api/v1/access-rule-proposals/scopes", name="DiscoverProposalScopes")
    def discover_proposal_scopes(
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverProposalScopes"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as scope:
            result = DiscoverProposalScopes(
                authority=scope.proposal_scope_discovery
            ).execute(
                actor_id=actor.actor_id,
                effective_time=effective_time,
            )
        _set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "scopes": [{"scope": value} for value in result.permitted_scopes],
            "ambiguousScopes": [
                {"scope": value} for value in result.ambiguous_scopes
            ],
        }

    @app.get(
        "/api/v1/access-rule-proposals/interactions",
        name="DiscoverProposalInteractions",
    )
    def discover_proposal_interactions(
        request: Request,
        scope: str,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=100),
        search: str | None = Query(None, max_length=256),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverProposalInteractions"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = DiscoverProposalInteractions(
                authority=runtime_scope.authority,
                catalogue=runtime_scope.proposal_interaction_catalogue,
            ).execute(
                actor_id=actor.actor_id,
                scope=scope,
                effective_time=effective_time,
                page=page,
                page_size=pageSize,
                search=search,
            )
            proposal_presentations = (
                _describe_semantic_identities(
                    runtime_scope,
                    result.page.identities,
                )
                if result.page is not None
                else {}
            )

        if result.outcome is ProposalInteractionDiscoveryOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is ProposalInteractionDiscoveryOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )
        assert result.page is not None
        _set_outcome(request, "Available")
        return {
            "items": [
                {
                    "sourceComponentDeploymentId": str(
                        identity.source_component_deployment_id
                    ),
                    "destinationComponentDeploymentId": str(
                        identity.destination_component_deployment_id
                    ),
                    "dcsContractRevisionId": str(
                        identity.dcs_contract_revision_id
                    ),
                    "catalogue": proposal_presentations.get(identity),
                }
                for identity in result.page.identities
            ],
            "page": result.page.page,
            "pageSize": result.page.page_size,
            "hasMore": result.page.has_more,
        }

    @app.post("/api/v1/access-rule-proposals", name="SubmitAccessRuleProposal")
    def submit_access_rule_proposal(
        payload: SubmitProposalRequest,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "SubmitAccessRuleProposal"
        effective_time = dependencies.clock()
        command = SubmitAccessRuleProposal(
            actor_id=actor.actor_id,
            authority_scope=payload.authority_scope,
            effective_time=effective_time,
            source_component_deployment_id=payload.source_component_deployment_id,
            destination_component_deployment_id=payload.destination_component_deployment_id,
            dcs_contract_revision_id=payload.dcs_contract_revision_id,
        )
        with dependencies.open_scope() as scope:
            result = MaterializeAllowedAccessRule(
                authority=scope.authority,
                catalogue=scope.proposal_catalogue,
                decisions=dependencies.decisions,
                rules=scope.access_rules,
            ).execute(command)
            proposal_rule_presentation = (
                _describe_semantic_identities(
                    scope,
                    (result.rule.semantic_identity,),
                ).get(result.rule.semantic_identity)
                if result.rule is not None
                else None
            )

        if result.outcome in {
            MaterializationOutcome.MATERIALIZED,
            MaterializationOutcome.RESOLVED,
        }:
            assert result.rule is not None
            request.state.rule_id = str(result.rule.rule_id)
            request.state.authority_reference = (
                result.rule.proposal_provenance.authority_reference
            )
            if result.rule.decision.decision_id:
                request.state.decision_reference = result.rule.decision.decision_id
            _set_outcome(request, result.outcome.value)
            return JSONResponse(
                status_code=(
                    201
                    if result.outcome is MaterializationOutcome.MATERIALIZED
                    else 200
                ),
                content={
                    "outcome": result.outcome.value,
                    "rule": _rule_dto(
                        result.rule,
                        proposal_rule_presentation,
                    ),
                },
            )

        if result.outcome is MaterializationOutcome.NOT_ALLOWED:
            _set_outcome(request, result.outcome.value)
            return {"outcome": "NotAllowed", "rule": None}

        mapping = {
            MaterializationOutcome.AUTHORITY_DENIED: (
                403,
                "AuthorityDenied",
                "The requested operation is not permitted.",
            ),
            MaterializationOutcome.AUTHORITY_UNKNOWN: (
                409,
                "AuthorityUnknown",
                "Authority for the requested operation is ambiguous or unavailable.",
            ),
            MaterializationOutcome.INTERACTION_INVALID: (
                422,
                "InteractionInvalid",
                "The selected interaction is invalid.",
            ),
            MaterializationOutcome.INTERACTION_UNKNOWN: (
                409,
                "InteractionUnknown",
                "The selected interaction cannot currently be established.",
            ),
            MaterializationOutcome.DECISION_UNKNOWN: (
                503,
                "DecisionUnknown",
                "The connectivity decision is currently unavailable.",
            ),
            MaterializationOutcome.DECISION_SUBJECT_MISMATCH: (
                502,
                "DecisionSubjectMismatch",
                "The connectivity decision could not be correlated safely.",
            ),
        }
        status_code, code, message = mapping[result.outcome]
        raise PublicApiError(
            status_code=status_code,
            code=code,
            message=message,
        )

    @app.get("/api/v1/access-rules", name="ListAccessRules")
    def list_access_rules(
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=100),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "ListAccessRules"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = ListAuthorizedAccessRules(
                read_authority=runtime_scope.rule_read_scope_discovery,
                rules=runtime_scope.access_rules,
            ).execute(
                actor_id=actor.actor_id,
                effective_time=effective_time,
                page=page,
                page_size=pageSize,
            )
            rule_presentations = _describe_semantic_identities(
                runtime_scope,
                tuple(rule.semantic_identity for rule in result.rules),
            )

        _set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "items": [
                _rule_dto(
                    rule,
                    rule_presentations.get(rule.semantic_identity),
                )
                for rule in result.rules
            ],
            "page": result.page,
            "pageSize": result.page_size,
            "hasMore": result.has_more,
            "ambiguousScopes": [
                {"scope": scope} for scope in result.ambiguous_scopes
            ],
        }

    @app.get("/api/v1/access-rules/{rule_id}", name="GetAccessRule")
    def get_access_rule(
        rule_id: UUID,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetAccessRule"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = GetAuthorizedAccessRule(
                authority=runtime_scope.authority,
                rules=runtime_scope.access_rules,
            ).execute(
                rule_id=rule_id,
                actor_id=actor.actor_id,
                effective_time=effective_time,
            )
            rule_detail_presentation = (
                _describe_semantic_identities(
                    runtime_scope,
                    (result.rule.semantic_identity,),
                ).get(result.rule.semantic_identity)
                if result.rule is not None
                else None
            )

        if result.outcome is AccessRuleDetailOutcome.RULE_NOT_FOUND:
            raise PublicApiError(
                status_code=404,
                code="RuleNotFound",
                message="The Access Rule was not found.",
            )
        if result.outcome is AccessRuleDetailOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is AccessRuleDetailOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.rule is not None
        assert result.state_mutation_admission is not None
        assert result.effective_window_mutation_admission is not None
        request.state.rule_id = str(result.rule.rule_id)
        request.state.authority_reference = result.read_authority_reference
        _set_outcome(request, "Found")
        return {
            "rule": _rule_detail_dto(
                result.rule,
                rule_detail_presentation,
            ),
            "capabilities": {
                "setOperationalState": result.state_mutation_admission.value,
                "setEffectiveWindow": result.effective_window_mutation_admission.value,
            },
        }

    @app.patch(
        "/api/v1/access-rules/{rule_id}/operational-state",
        name="SetAccessRuleOperationalState",
    )
    def set_access_rule_operational_state(
        rule_id: UUID,
        payload: SetOperationalStateRequest,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "SetAccessRuleOperationalState"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = SetAccessRuleOperationalState(
                authority=runtime_scope.authority,
                rules=runtime_scope.access_rules,
            ).execute(
                SetRuleOperationalState(
                    rule_id=rule_id,
                    target_state=payload.target_state,
                    actor_id=actor.actor_id,
                    effective_time=effective_time,
                )
            )

        if result.outcome is OperationalStateMutationOutcome.RULE_NOT_FOUND:
            raise PublicApiError(
                status_code=404,
                code="RuleNotFound",
                message="The Access Rule was not found.",
            )
        if result.outcome is OperationalStateMutationOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is OperationalStateMutationOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.rule is not None
        request.state.rule_id = str(result.rule.rule_id)
        if (
            result.outcome is OperationalStateMutationOutcome.UPDATED
            and result.rule.operational_state_history
        ):
            request.state.authority_reference = (
                result.rule.operational_state_history[-1].authority_reference
            )
        _set_outcome(request, result.outcome.value)
        return {
            "outcome": result.outcome.value,
            "rule": _rule_dto(result.rule),
        }

    @app.patch(
        "/api/v1/access-rules/{rule_id}/effective-window",
        name="SetAccessRuleEffectiveWindow",
    )
    def set_access_rule_effective_window(
        rule_id: UUID,
        payload: SetEffectiveWindowRequest,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "SetAccessRuleEffectiveWindow"
        effective_time = dependencies.clock()

        window = None
        if payload.window is not None:
            start = payload.window.start
            end = payload.window.end
            if (
                start.tzinfo is None
                or start.utcoffset() is None
                or end.tzinfo is None
                or end.utcoffset() is None
                or start >= end
            ):
                raise PublicApiError(
                    status_code=422,
                    code="InvalidEffectiveWindow",
                    message="EffectiveWindow requires offset-aware start < end.",
                )
            window = EffectiveWindow(start=start, end=end)

        with dependencies.open_scope() as runtime_scope:
            result = SetAccessRuleEffectiveWindow(
                authority=runtime_scope.authority,
                rules=runtime_scope.access_rules,
            ).execute(
                SetRuleEffectiveWindow(
                    rule_id=rule_id,
                    window=window,
                    actor_id=actor.actor_id,
                    effective_time=effective_time,
                )
            )

        if result.outcome is EffectiveWindowMutationOutcome.RULE_NOT_FOUND:
            raise PublicApiError(
                status_code=404,
                code="RuleNotFound",
                message="The Access Rule was not found.",
            )
        if result.outcome is EffectiveWindowMutationOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is EffectiveWindowMutationOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.rule is not None
        request.state.rule_id = str(result.rule.rule_id)
        if (
            result.outcome is EffectiveWindowMutationOutcome.UPDATED
            and result.rule.effective_window_history
        ):
            request.state.authority_reference = (
                result.rule.effective_window_history[-1].authority_reference
            )
        _set_outcome(request, result.outcome.value)
        return {
            "outcome": result.outcome.value,
            "rule": _rule_dto(result.rule),
        }

    @app.get("/api/v1/policy-views/scopes", name="DiscoverPolicyViewScopes")
    def discover_policy_view_scopes(
        request: Request,
        as_of: datetime = Query(alias="asOf"),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverPolicyViewScopes"
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise PublicApiError(
                status_code=422,
                code="InvalidAsOf",
                message="asOf must include an explicit timezone offset.",
            )
        with dependencies.open_scope() as runtime_scope:
            result = DiscoverEffectivePolicyScopes(
                authority=runtime_scope.effective_policy_scope_discovery,
            ).execute(
                actor_id=actor.actor_id,
                effective_time=as_of,
            )
        _set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "scopes": [{"scope": scope} for scope in result.permitted_scopes],
            "ambiguousScopes": [
                {"scope": scope} for scope in result.ambiguous_scopes
            ],
        }

    @app.get("/api/v1/effective-desired-policy", name="GetEffectiveDesiredPolicy")
    def get_effective_desired_policy(
        request: Request,
        scope: str,
        as_of: datetime = Query(alias="asOf"),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetEffectiveDesiredPolicy"
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise PublicApiError(
                status_code=422,
                code="InvalidAsOf",
                message="asOf must include an explicit timezone offset.",
            )

        with dependencies.open_scope() as runtime_scope:
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
            effective_policy_presentations = (
                _describe_semantic_identities(
                    runtime_scope,
                    tuple(rule.semantic_identity for rule in selection.rules),
                )
                if selection.outcome is EffectivePolicySelectionOutcome.SELECTED
                else {}
            )

        if selection.outcome is EffectivePolicySelectionOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if selection.outcome is EffectivePolicySelectionOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        request.state.authority_reference = selection.authority_reference
        _set_outcome(request, "Selected")
        return {
            "scope": selection.scope,
            "asOf": selection.as_of.isoformat(),
            "authorityReference": selection.authority_reference,
            "rules": [
                _rule_dto(
                    rule,
                    effective_policy_presentations.get(rule.semantic_identity),
                )
                for rule in selection.rules
            ],
        }

    @app.get("/api/v1/normalized-policy", name="GetNormalizedPolicy")
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

        with dependencies.open_scope() as runtime_scope:
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
                    code="AuthorityDenied",
                    message="The requested operation is not permitted.",
                )
            if selection.outcome is EffectivePolicySelectionOutcome.AUTHORITY_UNKNOWN:
                raise PublicApiError(
                    status_code=409,
                    code="AuthorityUnknown",
                    message="Authority for the requested operation is ambiguous or unavailable.",
                )

            assembly = AssembleExportSnapshot(
                application_catalogue=runtime_scope.application_projection,
                resource_catalogue=runtime_scope.resource_projection,
            ).execute(selection)

            if assembly.outcome is not SnapshotAssemblyOutcome.SUCCESS:
                raise PublicApiError(
                    status_code=409,
                    code="SnapshotIncomplete",
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
            normalized_presentations = _describe_semantic_identities(
                runtime_scope,
                tuple(
                    row.rule_semantic_identity
                    for row in normalized.rows
                ),
            )

        request.state.authority_reference = normalized.authority_reference
        _set_outcome(request, "NormalizedPolicyExported")
        payload = normalized_policy_export_json(normalized)
        for encoded, row in zip(payload["rows"], normalized.rows):
            encoded["catalogue"] = normalized_presentations.get(
                row.rule_semantic_identity
            )
        return payload

    @app.get("/health/live", name="Liveness")
    def liveness(request: Request):
        request.state.operation = "Liveness"
        _set_outcome(request, "Alive")
        return {"status": "alive"}

    @app.get("/health/ready", name="Readiness")
    def readiness(request: Request):
        request.state.operation = "Readiness"
        try:
            ready = dependencies.readiness()
        except Exception:
            ready = False
        if not ready:
            _set_dependency(request, "PostgreSQL")
            _set_outcome(request, "NotReady")
            return JSONResponse(status_code=503, content={"status": "not-ready"})
        _set_outcome(request, "Ready")
        return {"status": "ready"}

    return app
