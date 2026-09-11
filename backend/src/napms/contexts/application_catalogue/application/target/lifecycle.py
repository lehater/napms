from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Protocol
from uuid import UUID

from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityOutcome,
    ApplicationCatalogueCommandReceipt,
    ApplicationCatalogueCurationAuthorityPort,
    CatalogueConcurrencyConflict,
    CatalogueIdempotencyConflict,
    CataloguePersistenceOutcomeUnknown,
)
from napms.contexts.application_catalogue.application.target.curation import TargetMutationOutcome
from napms.contexts.application_catalogue.application.target.ports import (
    AccessRuleDependencyPort,
    ActiveDependencyReference,
    ConnectivityDecisionDependencyPort,
    ConnectivityRequirementDependencyPort,
    TargetApplicationCatalogueProvenanceFactory,
    TargetApplicationCatalogueRepository,
)
from napms.contexts.application_catalogue.domain.model import (
    Application,
    CatalogueInvariantError,
    Component,
    ComponentDeployment,
    DirectedInteractionIdentity,
)
from napms.contexts.application_catalogue.domain.target_model import (
    ApplicationDeployment,
    DeploymentInteraction,
    InteractionDefinition,
)


class RetirementDependencyKind(str, Enum):
    COMPONENTS = "Components"
    INTERACTIONS = "Interactions"
    APPLICATION_DEPLOYMENTS = "ApplicationDeployments"
    DEPLOYMENT_INTERACTIONS = "DeploymentInteractions"
    RESOURCE_BINDINGS = "ResourceBindings"
    CONNECTIVITY_REQUIREMENTS = "ConnectivityRequirements"
    CONNECTIVITY_DECISIONS = "ConnectivityDecisions"
    ACCESS_RULES = "AccessRules"
    LEGACY_COMPONENT_DEPLOYMENTS = "LegacyComponentDeployments"


@dataclass(frozen=True, slots=True)
class RetirementDependencyGroup:
    kind: RetirementDependencyKind
    references: tuple[ActiveDependencyReference, ...]

    @property
    def count(self) -> int:
        return len(self.references)


@dataclass(frozen=True, slots=True)
class RetirementMutationResult:
    outcome: TargetMutationOutcome
    subject: object | None = None
    dependencies: tuple[RetirementDependencyGroup, ...] = ()


@dataclass(frozen=True, slots=True)
class RetireApplicationDefinitionCommand:
    application_id: UUID
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RetireComponentTargetCommand:
    component_id: UUID
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RetireInteractionDefinitionCommand:
    interaction_definition_id: UUID
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RetireApplicationDeploymentCommand:
    application_deployment_id: UUID
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RetireDeploymentInteractionCommand:
    deployment_interaction_id: UUID
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


class TargetLifecycleRepository(TargetApplicationCatalogueRepository, Protocol):
    def list_active_components_for_application(
        self,
        *,
        application_id: UUID,
    ) -> tuple[Component, ...]: ...

    def list_active_interaction_definitions_for_application(
        self,
        *,
        application_id: UUID,
    ) -> tuple[InteractionDefinition, ...]: ...

    def list_active_application_deployments_for_application(
        self,
        *,
        application_id: UUID,
    ) -> tuple[ApplicationDeployment, ...]: ...

    def list_active_interaction_definitions_for_component(
        self,
        *,
        component_id: UUID,
    ) -> tuple[InteractionDefinition, ...]: ...

    def list_active_legacy_component_deployments(
        self,
        *,
        component_id: UUID,
    ) -> tuple[ComponentDeployment, ...]: ...

    def list_active_deployment_interactions_for_deployment(
        self,
        *,
        application_deployment_id: UUID,
    ) -> tuple[DeploymentInteraction, ...]: ...


class TargetRetirementDependencies:
    def __init__(
        self,
        *,
        catalogue: TargetLifecycleRepository,
        requirements: ConnectivityRequirementDependencyPort,
        decisions: ConnectivityDecisionDependencyPort,
        access_rules: AccessRuleDependencyPort,
    ) -> None:
        self._catalogue = catalogue
        self._requirements = requirements
        self._decisions = decisions
        self._access_rules = access_rules

    @staticmethod
    def _group(
        kind: RetirementDependencyKind,
        references: tuple[ActiveDependencyReference, ...],
    ) -> RetirementDependencyGroup | None:
        unique = {item.reference: item for item in references}
        if not unique:
            return None
        return RetirementDependencyGroup(
            kind,
            tuple(unique[key] for key in sorted(unique)),
        )

    @staticmethod
    def _ids(values, attribute: str) -> tuple[ActiveDependencyReference, ...]:
        return tuple(
            ActiveDependencyReference(str(getattr(item, attribute)))
            for item in values
        )

    def for_application(self, *, application_id: UUID) -> tuple[RetirementDependencyGroup, ...]:
        candidates = (
            self._group(
                RetirementDependencyKind.COMPONENTS,
                self._ids(
                    self._catalogue.list_active_components_for_application(
                        application_id=application_id
                    ),
                    "component_id",
                ),
            ),
            self._group(
                RetirementDependencyKind.INTERACTIONS,
                self._ids(
                    self._catalogue.list_active_interaction_definitions_for_application(
                        application_id=application_id
                    ),
                    "interaction_definition_id",
                ),
            ),
            self._group(
                RetirementDependencyKind.APPLICATION_DEPLOYMENTS,
                self._ids(
                    self._catalogue.list_active_application_deployments_for_application(
                        application_id=application_id
                    ),
                    "application_deployment_id",
                ),
            ),
        )
        return tuple(group for group in candidates if group is not None)

    def for_component(self, *, component_id: UUID) -> tuple[RetirementDependencyGroup, ...]:
        candidates = (
            self._group(
                RetirementDependencyKind.INTERACTIONS,
                self._ids(
                    self._catalogue.list_active_interaction_definitions_for_component(
                        component_id=component_id
                    ),
                    "interaction_definition_id",
                ),
            ),
            self._group(
                RetirementDependencyKind.LEGACY_COMPONENT_DEPLOYMENTS,
                self._ids(
                    self._catalogue.list_active_legacy_component_deployments(
                        component_id=component_id
                    ),
                    "deployment_id",
                ),
            ),
        )
        return tuple(group for group in candidates if group is not None)

    def for_interaction_definition(
        self,
        *,
        interaction_definition_id: UUID,
    ) -> tuple[RetirementDependencyGroup, ...]:
        return tuple(
            group
            for group in (
                self._group(
                    RetirementDependencyKind.DEPLOYMENT_INTERACTIONS,
                    self._ids(
                        self._catalogue.list_active_deployment_interactions_for_definition(
                            interaction_definition_id=interaction_definition_id
                        ),
                        "deployment_interaction_id",
                    ),
                ),
            )
            if group is not None
        )

    def for_application_deployment(
        self,
        *,
        application_deployment_id: UUID,
    ) -> tuple[RetirementDependencyGroup, ...]:
        return tuple(
            group
            for group in (
                self._group(
                    RetirementDependencyKind.DEPLOYMENT_INTERACTIONS,
                    self._ids(
                        self._catalogue.list_active_deployment_interactions_for_deployment(
                            application_deployment_id=application_deployment_id
                        ),
                        "deployment_interaction_id",
                    ),
                ),
            )
            if group is not None
        )

    def for_deployment_interaction(
        self,
        *,
        deployment_interaction_id: UUID,
        as_of: datetime,
    ) -> tuple[RetirementDependencyGroup, ...] | None:
        compatibility = self._catalogue.get_compatibility_projection(deployment_interaction_id)
        if compatibility is None:
            return None
        source_bindings = self._catalogue.find_effective_bindings(
            component_deployment_id=compatibility.source_component_deployment_id,
            as_of=as_of,
        )
        destination_bindings = self._catalogue.find_effective_bindings(
            component_deployment_id=compatibility.destination_component_deployment_id,
            as_of=as_of,
        )
        subject = DirectedInteractionIdentity(
            source_component_deployment_id=compatibility.source_component_deployment_id,
            destination_component_deployment_id=compatibility.destination_component_deployment_id,
            dcs_contract_revision_id=compatibility.current_dcs_revision_id,
        )
        candidates = (
            self._group(
                RetirementDependencyKind.RESOURCE_BINDINGS,
                tuple(
                    ActiveDependencyReference(binding.reference_id)
                    for binding in source_bindings + destination_bindings
                ),
            ),
            self._group(
                RetirementDependencyKind.CONNECTIVITY_REQUIREMENTS,
                self._requirements.find_active_references(subject=subject, as_of=as_of),
            ),
            self._group(
                RetirementDependencyKind.CONNECTIVITY_DECISIONS,
                self._decisions.find_active_references(subject=subject, as_of=as_of),
            ),
            self._group(
                RetirementDependencyKind.ACCESS_RULES,
                self._access_rules.find_active_references(subject=subject, as_of=as_of),
            ),
        )
        return tuple(group for group in candidates if group is not None)


class _RetireBase:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: TargetLifecycleRepository,
        provenance: TargetApplicationCatalogueProvenanceFactory,
        dependencies: TargetRetirementDependencies,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._provenance = provenance
        self._dependencies = dependencies

    def _authority_reference(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> tuple[TargetMutationOutcome | None, str | None]:
        check = self._authority.check_curation(
            actor_id=actor_id,
            effective_time=effective_time,
        )
        if check.outcome is ApplicationCatalogueAuthorityOutcome.DENIED:
            return TargetMutationOutcome.AUTHORITY_DENIED, None
        if (
            check.outcome is not ApplicationCatalogueAuthorityOutcome.PERMITTED
            or check.authority_reference is None
        ):
            return TargetMutationOutcome.AUTHORITY_UNKNOWN, None
        return None, check.authority_reference

    def _prepare(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
        idempotency_key: str,
        expected_version: int,
        command_kind: str,
        subject_id: UUID,
        load: Callable[[UUID], object | None],
    ) -> tuple[RetirementMutationResult | None, str | None, str | None]:
        authority_outcome, authority_reference = self._authority_reference(
            actor_id=actor_id,
            effective_time=effective_time,
        )
        if authority_outcome is not None:
            return RetirementMutationResult(authority_outcome), None, None
        key = idempotency_key.strip() if idempotency_key else ""
        if not key or expected_version < 1:
            return RetirementMutationResult(TargetMutationOutcome.INPUT_INVALID), None, None
        fingerprint = f"{command_kind}:{subject_id}:{expected_version}"
        receipt = self._catalogue.find_command_receipt(
            actor_id=actor_id,
            idempotency_key=key,
        )
        if receipt is not None:
            if (
                receipt.command_kind != command_kind
                or receipt.request_fingerprint != fingerprint
            ):
                return RetirementMutationResult(TargetMutationOutcome.IDEMPOTENCY_CONFLICT), None, None
            subject = load(UUID(str(receipt.result_id)))
            if subject is None:
                return RetirementMutationResult(TargetMutationOutcome.PERSISTENCE_UNKNOWN), None, None
            return RetirementMutationResult(TargetMutationOutcome.RESOLVED, subject), None, None
        return None, authority_reference, fingerprint

    def _finish(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
        command_kind: str,
        fingerprint: str,
        result_id: UUID,
        result_version: int,
    ) -> TargetMutationOutcome | None:
        self._catalogue.record_command_receipt(
            actor_id=actor_id,
            idempotency_key=idempotency_key.strip(),
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind=command_kind,
                request_fingerprint=fingerprint,
                result_id=result_id,
                result_version=result_version,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueConcurrencyConflict:
            return TargetMutationOutcome.CONCURRENCY_CONFLICT
        except CatalogueIdempotencyConflict:
            return TargetMutationOutcome.IDEMPOTENCY_CONFLICT
        except CataloguePersistenceOutcomeUnknown:
            return TargetMutationOutcome.PERSISTENCE_UNKNOWN
        return None


class RetireApplicationDefinition(_RetireBase):
    def execute(self, command: RetireApplicationDefinitionCommand) -> RetirementMutationResult:
        prepared, authority_reference, fingerprint = self._prepare(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
            idempotency_key=command.idempotency_key,
            expected_version=command.expected_version,
            command_kind="RetireApplicationDefinition",
            subject_id=command.application_id,
            load=self._catalogue.get_application,
        )
        if prepared is not None:
            return prepared
        current: Application | None = self._catalogue.get_application(command.application_id)
        if current is None:
            return RetirementMutationResult(TargetMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return RetirementMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        dependencies = self._dependencies.for_application(application_id=current.application_id)
        if dependencies:
            return RetirementMutationResult(TargetMutationOutcome.DEPENDENCY_BLOCKED, current, dependencies)
        try:
            retired = current.retired(
                retirement_provenance_reference=self._provenance.for_application_retirement(
                    application_id=current.application_id,
                    actor_id=command.actor_id,
                    authority_reference=authority_reference,
                    effective_time=command.effective_time,
                )
            )
            self._catalogue.save_application(retired, expected_version=command.expected_version)
        except CatalogueInvariantError:
            return RetirementMutationResult(TargetMutationOutcome.INPUT_INVALID)
        except CatalogueConcurrencyConflict:
            return RetirementMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        outcome = self._finish(
            actor_id=command.actor_id,
            idempotency_key=command.idempotency_key,
            command_kind="RetireApplicationDefinition",
            fingerprint=fingerprint,
            result_id=retired.application_id,
            result_version=retired.version,
        )
        return RetirementMutationResult(outcome or TargetMutationOutcome.UPDATED, retired)


class RetireComponentTarget(_RetireBase):
    def execute(self, command: RetireComponentTargetCommand) -> RetirementMutationResult:
        prepared, authority_reference, fingerprint = self._prepare(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
            idempotency_key=command.idempotency_key,
            expected_version=command.expected_version,
            command_kind="RetireComponentTarget",
            subject_id=command.component_id,
            load=self._catalogue.get_component,
        )
        if prepared is not None:
            return prepared
        current: Component | None = self._catalogue.get_component(command.component_id)
        if current is None:
            return RetirementMutationResult(TargetMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return RetirementMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        dependencies = self._dependencies.for_component(component_id=current.component_id)
        if dependencies:
            return RetirementMutationResult(TargetMutationOutcome.DEPENDENCY_BLOCKED, current, dependencies)
        try:
            retired = current.retired(
                retirement_provenance_reference=self._provenance.for_component_retirement(
                    component_id=current.component_id,
                    actor_id=command.actor_id,
                    authority_reference=authority_reference,
                    effective_time=command.effective_time,
                )
            )
            self._catalogue.save_component(retired, expected_version=command.expected_version)
        except CatalogueInvariantError:
            return RetirementMutationResult(TargetMutationOutcome.INPUT_INVALID)
        except CatalogueConcurrencyConflict:
            return RetirementMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        outcome = self._finish(
            actor_id=command.actor_id,
            idempotency_key=command.idempotency_key,
            command_kind="RetireComponentTarget",
            fingerprint=fingerprint,
            result_id=retired.component_id,
            result_version=retired.version,
        )
        return RetirementMutationResult(outcome or TargetMutationOutcome.UPDATED, retired)


class RetireInteractionDefinition(_RetireBase):
    def execute(self, command: RetireInteractionDefinitionCommand) -> RetirementMutationResult:
        prepared, authority_reference, fingerprint = self._prepare(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
            idempotency_key=command.idempotency_key,
            expected_version=command.expected_version,
            command_kind="RetireInteractionDefinition",
            subject_id=command.interaction_definition_id,
            load=self._catalogue.get_interaction_definition,
        )
        if prepared is not None:
            return prepared
        current = self._catalogue.get_interaction_definition(command.interaction_definition_id)
        if current is None:
            return RetirementMutationResult(TargetMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return RetirementMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        dependencies = self._dependencies.for_interaction_definition(
            interaction_definition_id=current.interaction_definition_id
        )
        if dependencies:
            return RetirementMutationResult(TargetMutationOutcome.DEPENDENCY_BLOCKED, current, dependencies)
        try:
            retired = current.retired(
                retirement_provenance_reference=self._provenance.for_interaction_definition_retirement(
                    interaction_definition_id=current.interaction_definition_id,
                    actor_id=command.actor_id,
                    authority_reference=authority_reference,
                    effective_time=command.effective_time,
                )
            )
            self._catalogue.save_interaction_definition(retired, expected_version=command.expected_version)
        except CatalogueInvariantError:
            return RetirementMutationResult(TargetMutationOutcome.INPUT_INVALID)
        except CatalogueConcurrencyConflict:
            return RetirementMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        outcome = self._finish(
            actor_id=command.actor_id,
            idempotency_key=command.idempotency_key,
            command_kind="RetireInteractionDefinition",
            fingerprint=fingerprint,
            result_id=retired.interaction_definition_id,
            result_version=retired.version,
        )
        return RetirementMutationResult(outcome or TargetMutationOutcome.UPDATED, retired)


class RetireApplicationDeployment(_RetireBase):
    def execute(self, command: RetireApplicationDeploymentCommand) -> RetirementMutationResult:
        prepared, authority_reference, fingerprint = self._prepare(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
            idempotency_key=command.idempotency_key,
            expected_version=command.expected_version,
            command_kind="RetireApplicationDeployment",
            subject_id=command.application_deployment_id,
            load=self._catalogue.get_application_deployment,
        )
        if prepared is not None:
            return prepared
        current = self._catalogue.get_application_deployment(command.application_deployment_id)
        if current is None:
            return RetirementMutationResult(TargetMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return RetirementMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        dependencies = self._dependencies.for_application_deployment(
            application_deployment_id=current.application_deployment_id
        )
        if dependencies:
            return RetirementMutationResult(TargetMutationOutcome.DEPENDENCY_BLOCKED, current, dependencies)
        try:
            retired = current.retired(
                retirement_provenance_reference=self._provenance.for_application_deployment_retirement(
                    application_deployment_id=current.application_deployment_id,
                    actor_id=command.actor_id,
                    authority_reference=authority_reference,
                    effective_time=command.effective_time,
                )
            )
            self._catalogue.save_application_deployment(retired, expected_version=command.expected_version)
        except CatalogueInvariantError:
            return RetirementMutationResult(TargetMutationOutcome.INPUT_INVALID)
        except CatalogueConcurrencyConflict:
            return RetirementMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        outcome = self._finish(
            actor_id=command.actor_id,
            idempotency_key=command.idempotency_key,
            command_kind="RetireApplicationDeployment",
            fingerprint=fingerprint,
            result_id=retired.application_deployment_id,
            result_version=retired.version,
        )
        return RetirementMutationResult(outcome or TargetMutationOutcome.UPDATED, retired)


class RetireDeploymentInteraction(_RetireBase):
    def execute(self, command: RetireDeploymentInteractionCommand) -> RetirementMutationResult:
        prepared, authority_reference, fingerprint = self._prepare(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
            idempotency_key=command.idempotency_key,
            expected_version=command.expected_version,
            command_kind="RetireDeploymentInteraction",
            subject_id=command.deployment_interaction_id,
            load=self._catalogue.get_deployment_interaction,
        )
        if prepared is not None:
            return prepared
        current = self._catalogue.get_deployment_interaction(command.deployment_interaction_id)
        if current is None:
            return RetirementMutationResult(TargetMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return RetirementMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        dependencies = self._dependencies.for_deployment_interaction(
            deployment_interaction_id=current.deployment_interaction_id,
            as_of=command.effective_time,
        )
        if dependencies is None:
            return RetirementMutationResult(TargetMutationOutcome.PERSISTENCE_UNKNOWN, current)
        if dependencies:
            return RetirementMutationResult(TargetMutationOutcome.DEPENDENCY_BLOCKED, current, dependencies)
        compatibility = self._catalogue.get_compatibility_projection(current.deployment_interaction_id)
        if compatibility is None:
            return RetirementMutationResult(TargetMutationOutcome.PERSISTENCE_UNKNOWN, current)
        source = self._catalogue.get_component_deployment(
            compatibility.source_component_deployment_id
        )
        destination = self._catalogue.get_component_deployment(
            compatibility.destination_component_deployment_id
        )
        if source is None or destination is None:
            return RetirementMutationResult(TargetMutationOutcome.PERSISTENCE_UNKNOWN, current)
        try:
            retired = current.retired(
                retirement_provenance_reference=self._provenance.for_deployment_interaction_retirement(
                    deployment_interaction_id=current.deployment_interaction_id,
                    actor_id=command.actor_id,
                    authority_reference=authority_reference,
                    effective_time=command.effective_time,
                )
            )
            retired_source = source.retired(
                retirement_provenance_reference=self._provenance.for_component_deployment_retirement(
                    deployment_id=source.deployment_id,
                    actor_id=command.actor_id,
                    authority_reference=authority_reference,
                    effective_time=command.effective_time,
                )
            )
            retired_destination = destination.retired(
                retirement_provenance_reference=self._provenance.for_component_deployment_retirement(
                    deployment_id=destination.deployment_id,
                    actor_id=command.actor_id,
                    authority_reference=authority_reference,
                    effective_time=command.effective_time,
                )
            )
            self._catalogue.save_deployment_interaction(retired, expected_version=command.expected_version)
            self._catalogue.save_component_deployment(retired_source, expected_version=source.version)
            self._catalogue.save_component_deployment(retired_destination, expected_version=destination.version)
        except CatalogueInvariantError:
            return RetirementMutationResult(TargetMutationOutcome.INPUT_INVALID)
        except CatalogueConcurrencyConflict:
            return RetirementMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        outcome = self._finish(
            actor_id=command.actor_id,
            idempotency_key=command.idempotency_key,
            command_kind="RetireDeploymentInteraction",
            fingerprint=fingerprint,
            result_id=retired.deployment_interaction_id,
            result_version=retired.version,
        )
        return RetirementMutationResult(outcome or TargetMutationOutcome.UPDATED, retired)
