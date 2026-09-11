from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable
from uuid import UUID, uuid4

from napms.contexts.connectivity_requirements.application.ports import (
    ActiveRequirementSemanticConflict,
    ConnectivityRequirementRepository,
    InteractionOutcome,
    RequirementAuthorityAction,
    RequirementAuthorityPort,
    RequirementInteractionCataloguePort,
    TernaryOutcome,
)
from napms.contexts.connectivity_requirements.domain.model import (
    ConnectivityRequirement,
    RequiredSemanticInteraction,
    RequirementApplicability,
    RequirementDeclarationProvenance,
    RequirementInvariantError,
    RequirementSemanticKey,
)


class DeclarationOutcome(str, Enum):
    DECLARED = "Declared"
    RESOLVED = "Resolved"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    INTERACTION_INVALID = "InteractionInvalid"
    INTERACTION_UNKNOWN = "InteractionUnknown"
    DEPENDENT_INVALID = "DependentInvalid"
    INPUT_INVALID = "InputInvalid"


@dataclass(frozen=True, slots=True)
class DeclareRequirement:
    governance_scope: str
    dependent_component_deployment_id: UUID
    required_interaction: RequiredSemanticInteraction
    applicability: RequirementApplicability
    justification: str
    actor_id: str
    effective_time: datetime


@dataclass(frozen=True, slots=True)
class DeclarationResult:
    outcome: DeclarationOutcome
    requirement: ConnectivityRequirement | None = None


class DeclareConnectivityRequirement:
    def __init__(
        self,
        *,
        authority: RequirementAuthorityPort,
        catalogue: RequirementInteractionCataloguePort,
        requirements: ConnectivityRequirementRepository,
        id_factory: Callable[[], UUID] = uuid4,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._requirements = requirements
        self._id_factory = id_factory

    def execute(self, command: DeclareRequirement) -> DeclarationResult:
        authority = self._authority.check(
            actor_id=command.actor_id,
            action=RequirementAuthorityAction.DECLARE,
            scope=command.governance_scope,
            effective_time=command.effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return DeclarationResult(DeclarationOutcome.AUTHORITY_DENIED)
        if (
            authority.outcome is not TernaryOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return DeclarationResult(DeclarationOutcome.AUTHORITY_UNKNOWN)

        interaction = self._catalogue.validate_required_interaction(
            identity=command.required_interaction,
            effective_time=command.effective_time,
        )
        if interaction.outcome is InteractionOutcome.INVALID:
            return DeclarationResult(DeclarationOutcome.INTERACTION_INVALID)
        if (
            interaction.outcome is not InteractionOutcome.VALID
            or interaction.identity != command.required_interaction
        ):
            return DeclarationResult(DeclarationOutcome.INTERACTION_UNKNOWN)

        try:
            semantic_key = RequirementSemanticKey(
                governance_scope=command.governance_scope,
                dependent_component_deployment_id=(
                    command.dependent_component_deployment_id
                ),
                required_interaction=command.required_interaction,
            )
        except RequirementInvariantError:
            return DeclarationResult(DeclarationOutcome.DEPENDENT_INVALID)

        existing = self._requirements.find_active_by_semantic_key(semantic_key)
        if existing is not None:
            return DeclarationResult(
                DeclarationOutcome.RESOLVED,
                requirement=existing,
            )

        try:
            requirement = ConnectivityRequirement.declared(
                requirement_id=self._id_factory(),
                semantic_key=semantic_key,
                applicability=command.applicability,
                justification=command.justification,
                provenance=RequirementDeclarationProvenance(
                    actor_id=command.actor_id,
                    effective_time=command.effective_time,
                    governance_scope=command.governance_scope,
                    authority_reference=authority.authority_reference,
                    catalogue_reference=interaction.provenance_reference,
                ),
            )
        except RequirementInvariantError:
            return DeclarationResult(DeclarationOutcome.INPUT_INVALID)

        try:
            self._requirements.add(requirement)
            self._requirements.commit()
        except ActiveRequirementSemanticConflict:
            winner = self._requirements.find_active_by_semantic_key(semantic_key)
            if winner is None:
                raise
            return DeclarationResult(
                DeclarationOutcome.RESOLVED,
                requirement=winner,
            )

        return DeclarationResult(
            DeclarationOutcome.DECLARED,
            requirement=requirement,
        )
