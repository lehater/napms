from contextlib import AbstractContextManager
from datetime import datetime
from typing import Any, Callable
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from napms.application_catalogue.application.ports import CataloguePersistenceError
from napms.application_catalogue.domain.model import DirectedInteractionIdentity
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
from napms.policy_export.application.normalization_ports import DcsProjectionDecodeError
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.http_support import (
    PublicApiError,
    authenticated_actor,
    set_outcome,
)
from napms.runtime.normalized_policy_json import port_constraint_json


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


def create_connectivity_requirements_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager[Any]],
    clock: Callable[[], datetime],
) -> APIRouter:
    router = APIRouter()

    def require_actor(request: Request) -> AuthenticatedActor:
        return authenticated_actor(sessions, request)

    @router.get(
        "/api/v1/connectivity-requirements/scopes",
        name="DiscoverConnectivityRequirementScopes",
    )
    def discover_connectivity_requirement_scopes(
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverConnectivityRequirementScopes"
        effective_time = clock()
        with open_scope() as runtime_scope:
            result = DiscoverRequirementScopes(
                discovery=runtime_scope.requirement_declaration_scopes,
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
        effective_time = clock()
        with open_scope() as runtime_scope:
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

        if result.outcome is RequiredInteractionDiscoveryOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is RequiredInteractionDiscoveryOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.page is not None
        set_outcome(request, result.outcome.value)
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

    @router.post(
        "/api/v1/connectivity-requirements",
        name="DeclareConnectivityRequirement",
    )
    def declare_connectivity_requirement(
        payload: DeclareConnectivityRequirementRequest,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DeclareConnectivityRequirement"
        effective_time = clock()
        applicability = _requirement_applicability_from_request(payload.applicability)
        interaction = RequiredSemanticInteraction(
            source_component_deployment_id=payload.source_component_deployment_id,
            destination_component_deployment_id=payload.destination_component_deployment_id,
            dcs_contract_revision_id=payload.dcs_contract_revision_id,
        )
        with open_scope() as runtime_scope:
            result = DeclareConnectivityRequirement(
                authority=runtime_scope.requirement_authority,
                catalogue=runtime_scope.requirement_catalogue,
                requirements=runtime_scope.connectivity_requirements,
            ).execute(
                DeclareRequirement(
                    governance_scope=payload.authority_scope,
                    dependent_component_deployment_id=payload.dependent_component_deployment_id,
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

        if result.outcome in {DeclarationOutcome.DECLARED, DeclarationOutcome.RESOLVED}:
            assert result.requirement is not None
            request.state.requirement_id = str(result.requirement.requirement_id)
            if result.outcome is DeclarationOutcome.DECLARED:
                request.state.authority_reference = (
                    result.requirement.declaration_provenance.authority_reference
                )
            set_outcome(request, result.outcome.value)
            return JSONResponse(
                status_code=(201 if result.outcome is DeclarationOutcome.DECLARED else 200),
                content={
                    "outcome": result.outcome.value,
                    "requirement": _requirement_dto(result.requirement, presentation),
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
        raise PublicApiError(status_code=status_code, code=code, message=message)

    @router.get(
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
        effective_time = clock()
        with open_scope() as runtime_scope:
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
                tuple(value.required_interaction for value in result.requirements),
            )

        set_outcome(
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

    @router.get(
        "/api/v1/connectivity-requirements/{requirement_id}",
        name="GetConnectivityRequirement",
    )
    def get_connectivity_requirement(
        requirement_id: UUID,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetConnectivityRequirement"
        effective_time = clock()
        with open_scope() as runtime_scope:
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
        set_outcome(request, "Found")
        return {
            "requirement": _requirement_dto(result.requirement, presentation),
            "capabilities": {
                "setApplicability": result.applicability_mutation_admission.value,
                "setJustification": result.justification_mutation_admission.value,
                "retire": result.retirement_admission.value,
            },
        }

    @router.patch(
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
        effective_time = clock()
        applicability = _requirement_applicability_from_request(payload.applicability)
        with open_scope() as runtime_scope:
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

        if result.outcome is ApplicabilityMutationOutcome.REQUIREMENT_NOT_FOUND:
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
        set_outcome(request, result.outcome.value)
        return {
            "outcome": result.outcome.value,
            "requirement": _requirement_dto(result.requirement, presentation),
        }

    @router.patch(
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
        effective_time = clock()
        with open_scope() as runtime_scope:
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

        if result.outcome is JustificationMutationOutcome.REQUIREMENT_NOT_FOUND:
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
        set_outcome(request, result.outcome.value)
        return {
            "outcome": result.outcome.value,
            "requirement": _requirement_dto(result.requirement, presentation),
        }

    @router.post(
        "/api/v1/connectivity-requirements/{requirement_id}/retirement",
        name="RetireConnectivityRequirement",
    )
    def retire_connectivity_requirement(
        requirement_id: UUID,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "RetireConnectivityRequirement"
        effective_time = clock()
        with open_scope() as runtime_scope:
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
        if result.outcome is RetirementOutcome.RETIRED and result.requirement.lifecycle_history:
            request.state.authority_reference = (
                result.requirement.lifecycle_history[-1].authority_reference
            )
        set_outcome(request, result.outcome.value)
        return {
            "outcome": result.outcome.value,
            "requirement": _requirement_dto(result.requirement, presentation),
        }

    return router


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
    return RequirementApplicability.absolute_window(start=value.start, end=value.end)


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
        "applicability": _requirement_applicability_dto(requirement.applicability),
        "justification": requirement.justification,
        "lifecycleState": requirement.lifecycle_state.value,
        "version": requirement.version,
        "declarationProvenance": {
            "actorId": requirement.declaration_provenance.actor_id,
            "effectiveTime": requirement.declaration_provenance.effective_time.isoformat(),
            "authorityReference": requirement.declaration_provenance.authority_reference,
            "catalogueReference": requirement.declaration_provenance.catalogue_reference,
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
