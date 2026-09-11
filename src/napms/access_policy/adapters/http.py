from contextlib import AbstractContextManager
from datetime import datetime
from typing import Any, Callable
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from napms.access_policy.application.materialize_rule import (
    MaterializationOutcome,
    MaterializeAllowedAccessRule,
    SubmitAccessRuleProposal,
)
from napms.access_policy.application.ports import ConnectivityDecisionPort
from napms.access_policy.application.proposal_options import (
    DiscoverProposalInteractions,
    DiscoverProposalScopes,
    ProposalInteractionDiscoveryOutcome,
)
from napms.access_policy.application.read_rules import (
    AccessRuleDetailOutcome,
    GetAuthorizedAccessRule,
    ListAuthorizedAccessRules,
)
from napms.access_policy.application.select_effective_policy import (
    DiscoverEffectivePolicyScopes,
    EffectivePolicySelectionOutcome,
    SelectAccessPolicyEffectiveDesiredPolicy,
    SelectEffectiveDesiredPolicy,
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
from napms.access_policy.domain.model import (
    AccessRule,
    EffectiveWindow,
    OperationalState,
    RuleSemanticIdentity,
)
from napms.application_catalogue.application.ports import CataloguePersistenceError
from napms.application_catalogue.domain.model import DirectedInteractionIdentity
from napms.policy_export.application.normalization_ports import DcsProjectionDecodeError
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.http_support import PublicApiError, authenticated_actor, set_outcome
from napms.policy_export.adapters.http_json import port_constraint_json


class SubmitProposalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    authority_scope: str = Field(alias="authorityScope", min_length=1, max_length=512)
    source_component_deployment_id: UUID = Field(alias="sourceComponentDeploymentId")
    destination_component_deployment_id: UUID = Field(
        alias="destinationComponentDeploymentId"
    )
    dcs_contract_revision_id: UUID = Field(alias="dcsContractRevisionId")


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


def create_access_policy_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager[Any]],
    decisions: ConnectivityDecisionPort,
    clock: Callable[[], datetime],
) -> APIRouter:
    router = APIRouter()

    def require_actor(request: Request) -> AuthenticatedActor:
        return authenticated_actor(sessions, request)

    @router.get("/api/v1/access-rule-proposals/scopes", name="DiscoverProposalScopes")
    def discover_proposal_scopes(
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverProposalScopes"
        effective_time = clock()
        with open_scope() as scope:
            result = DiscoverProposalScopes(
                authority=scope.proposal_scope_discovery
            ).execute(
                actor_id=actor.actor_id,
                effective_time=effective_time,
            )
        set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "scopes": [{"scope": value} for value in result.permitted_scopes],
            "ambiguousScopes": [
                {"scope": value} for value in result.ambiguous_scopes
            ],
        }

    @router.get(
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
        effective_time = clock()
        with open_scope() as runtime_scope:
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
            presentations = (
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
        set_outcome(request, "Available")
        return {
            "items": [
                {
                    "sourceComponentDeploymentId": str(
                        identity.source_component_deployment_id
                    ),
                    "destinationComponentDeploymentId": str(
                        identity.destination_component_deployment_id
                    ),
                    "dcsContractRevisionId": str(identity.dcs_contract_revision_id),
                    "catalogue": presentations.get(identity),
                }
                for identity in result.page.identities
            ],
            "page": result.page.page,
            "pageSize": result.page.page_size,
            "hasMore": result.page.has_more,
        }

    @router.post("/api/v1/access-rule-proposals", name="SubmitAccessRuleProposal")
    def submit_access_rule_proposal(
        payload: SubmitProposalRequest,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "SubmitAccessRuleProposal"
        effective_time = clock()
        command = SubmitAccessRuleProposal(
            actor_id=actor.actor_id,
            authority_scope=payload.authority_scope,
            effective_time=effective_time,
            source_component_deployment_id=payload.source_component_deployment_id,
            destination_component_deployment_id=payload.destination_component_deployment_id,
            dcs_contract_revision_id=payload.dcs_contract_revision_id,
        )
        with open_scope() as scope:
            result = MaterializeAllowedAccessRule(
                authority=scope.authority,
                catalogue=scope.proposal_catalogue,
                decisions=decisions,
                rules=scope.access_rules,
            ).execute(command)
            presentation = (
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
            set_outcome(request, result.outcome.value)
            return JSONResponse(
                status_code=(
                    201
                    if result.outcome is MaterializationOutcome.MATERIALIZED
                    else 200
                ),
                content={
                    "outcome": result.outcome.value,
                    "rule": _rule_dto(result.rule, presentation),
                },
            )

        if result.outcome is MaterializationOutcome.NOT_ALLOWED:
            set_outcome(request, result.outcome.value)
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
        raise PublicApiError(status_code=status_code, code=code, message=message)

    @router.get("/api/v1/access-rules", name="ListAccessRules")
    def list_access_rules(
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=100),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "ListAccessRules"
        effective_time = clock()
        with open_scope() as runtime_scope:
            result = ListAuthorizedAccessRules(
                read_authority=runtime_scope.rule_read_scope_discovery,
                rules=runtime_scope.access_rules,
            ).execute(
                actor_id=actor.actor_id,
                effective_time=effective_time,
                page=page,
                page_size=pageSize,
            )
            presentations = _describe_semantic_identities(
                runtime_scope,
                tuple(rule.semantic_identity for rule in result.rules),
            )

        set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "items": [
                _rule_dto(rule, presentations.get(rule.semantic_identity))
                for rule in result.rules
            ],
            "page": result.page,
            "pageSize": result.page_size,
            "hasMore": result.has_more,
            "ambiguousScopes": [
                {"scope": scope} for scope in result.ambiguous_scopes
            ],
        }

    @router.get("/api/v1/access-rules/{rule_id}", name="GetAccessRule")
    def get_access_rule(
        rule_id: UUID,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetAccessRule"
        effective_time = clock()
        with open_scope() as runtime_scope:
            result = GetAuthorizedAccessRule(
                authority=runtime_scope.authority,
                rules=runtime_scope.access_rules,
            ).execute(
                rule_id=rule_id,
                actor_id=actor.actor_id,
                effective_time=effective_time,
            )
            presentation = (
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
        set_outcome(request, "Found")
        return {
            "rule": _rule_detail_dto(result.rule, presentation),
            "capabilities": {
                "setOperationalState": result.state_mutation_admission.value,
                "setEffectiveWindow": result.effective_window_mutation_admission.value,
            },
        }

    @router.patch(
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
        effective_time = clock()
        with open_scope() as runtime_scope:
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
        set_outcome(request, result.outcome.value)
        return {
            "outcome": result.outcome.value,
            "rule": _rule_dto(result.rule),
        }

    @router.patch(
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
        effective_time = clock()
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

        with open_scope() as runtime_scope:
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
        set_outcome(request, result.outcome.value)
        return {
            "outcome": result.outcome.value,
            "rule": _rule_dto(result.rule),
        }

    @router.get("/api/v1/policy-views/scopes", name="DiscoverPolicyViewScopes")
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
        with open_scope() as runtime_scope:
            result = DiscoverEffectivePolicyScopes(
                authority=runtime_scope.effective_policy_scope_discovery,
            ).execute(
                actor_id=actor.actor_id,
                effective_time=as_of,
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

    @router.get("/api/v1/effective-desired-policy", name="GetEffectiveDesiredPolicy")
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
            presentations = (
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
        set_outcome(request, "Selected")
        return {
            "scope": selection.scope,
            "asOf": selection.as_of.isoformat(),
            "authorityReference": selection.authority_reference,
            "rules": [
                _rule_dto(rule, presentations.get(rule.semantic_identity))
                for rule in selection.rules
            ],
        }

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
            "dcsContractRevisionId": str(rule.semantic_identity.dcs_contract_revision_id),
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
