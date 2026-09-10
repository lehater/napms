from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json
from uuid import UUID

from napms.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityOutcome,
    ApplicationCatalogueCommandReceipt,
    ApplicationCatalogueCurationAuthorityPort,
    CatalogueConcurrencyConflict,
    CatalogueIdempotencyConflict,
    CataloguePersistenceOutcomeUnknown,
    DcsProjectionAuthoringEncoder,
)
from napms.application_catalogue.application.target_ports import (
    AccessRuleDependencyPort,
    ActiveDependencyReference,
    ActiveDependencySummary,
    ConnectivityDecisionDependencyPort,
    ConnectivityRequirementDependencyPort,
    TargetApplicationCatalogueIdentityFactory,
    TargetApplicationCatalogueProvenanceFactory,
    TargetApplicationCatalogueRepository,
)
from napms.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    canonical_dcs_alternatives,
)
from napms.application_catalogue.domain.model import (
    CatalogueInvariantError,
    CatalogueLifecycleState,
    ComponentDeployment,
    DcsRevision,
    DirectedInteractionIdentity,
)
from napms.application_catalogue.domain.target_model import (
    ApplicationDeployment,
    DeploymentInteraction,
    DeploymentInteractionCompatibility,
    DeploymentInteractionSide,
    InteractionDefinition,
)


_DEPENDENCY_PREVIEW_LIMIT = 20


class TargetMutationOutcome(str, Enum):
    CREATED = "Created"
    UPDATED = "Updated"
    RESOLVED = "Resolved"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    NOT_FOUND = "NotFound"
    PARENT_INACTIVE = "ParentInactive"
    ALREADY_EXISTS = "AlreadyExists"
    DEPENDENCY_BLOCKED = "DependencyBlocked"
    INPUT_INVALID = "InputInvalid"
    CONCURRENCY_CONFLICT = "ConcurrencyConflict"
    IDEMPOTENCY_CONFLICT = "IdempotencyConflict"
    PERSISTENCE_UNKNOWN = "PersistenceUnknown"


class TargetDependencyKind(str, Enum):
    DEPLOYMENT_INTERACTIONS = "DeploymentInteractions"
    CONNECTIVITY_REQUIREMENTS = "ConnectivityRequirements"
    CONNECTIVITY_DECISIONS = "ConnectivityDecisions"
    ACCESS_RULES = "AccessRules"


@dataclass(frozen=True, slots=True)
class TargetDependencyGroup:
    kind: TargetDependencyKind
    references: tuple[ActiveDependencyReference, ...] = ()
    total: int | None = None

    @property
    def count(self) -> int:
        return len(self.references) if self.total is None else self.total


@dataclass(frozen=True, slots=True)
class CreateInteractionDefinitionCommand:
    application_id: UUID
    source_component_id: UUID
    destination_component_id: UUID
    traffic_alternatives: tuple[AuthoredDcsTrafficAlternative, ...]
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class CreateApplicationDeploymentCommand:
    application_id: UUID
    company_reference: str
    environment: str
    scope_reference: str
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class SelectDeploymentInteractionCommand:
    application_deployment_id: UUID
    interaction_definition_id: UUID
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class UpdateInteractionDefinitionEndpointsCommand:
    interaction_definition_id: UUID
    source_component_id: UUID
    destination_component_id: UUID
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class UpdateInteractionDefinitionTrafficCommand:
    interaction_definition_id: UUID
    traffic_alternatives: tuple[AuthoredDcsTrafficAlternative, ...]
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class InteractionDefinitionMutationResult:
    outcome: TargetMutationOutcome
    interaction_definition: InteractionDefinition | None = None
    dependencies: tuple[TargetDependencyGroup, ...] = ()
    generated_revisions: tuple[DcsRevision, ...] = ()


@dataclass(frozen=True, slots=True)
class ApplicationDeploymentMutationResult:
    outcome: TargetMutationOutcome
    application_deployment: ApplicationDeployment | None = None


@dataclass(frozen=True, slots=True)
class DeploymentInteractionMutationResult:
    outcome: TargetMutationOutcome
    deployment_interaction: DeploymentInteraction | None = None
    compatibility: DeploymentInteractionCompatibility | None = None
    dcs_revision: DcsRevision | None = None


def _required(value: str) -> str | None:
    normalized = value.strip() if value else ""
    return normalized or None


def _constraint_payload(value: DcsPortConstraint) -> dict[str, object]:
    return {
        "kind": value.kind.value,
        "ranges": [[item.first, item.last] for item in value.ranges],
    }


def _alternative_payload(value: AuthoredDcsTrafficAlternative) -> dict[str, object]:
    return {
        "protocol": value.protocol,
        "sourcePorts": _constraint_payload(value.source_ports),
        "destinationPorts": _constraint_payload(value.destination_ports),
        "serviceReference": value.service_reference,
    }


def _fingerprint(payload: dict[str, object]) -> str:
    return sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _authority_reference(
    *,
    authority: ApplicationCatalogueCurationAuthorityPort,
    actor_id: str,
    effective_time: datetime,
) -> tuple[TargetMutationOutcome | None, str | None]:
    check = authority.check_curation(actor_id=actor_id, effective_time=effective_time)
    if check.outcome is ApplicationCatalogueAuthorityOutcome.DENIED:
        return TargetMutationOutcome.AUTHORITY_DENIED, None
    if (
        check.outcome is not ApplicationCatalogueAuthorityOutcome.PERMITTED
        or check.authority_reference is None
    ):
        return TargetMutationOutcome.AUTHORITY_UNKNOWN, None
    return None, check.authority_reference


def _commit(repository: TargetApplicationCatalogueRepository) -> TargetMutationOutcome | None:
    try:
        repository.commit()
    except CatalogueConcurrencyConflict:
        return TargetMutationOutcome.CONCURRENCY_CONFLICT
    except CatalogueIdempotencyConflict:
        return TargetMutationOutcome.IDEMPOTENCY_CONFLICT
    except CataloguePersistenceOutcomeUnknown:
        return TargetMutationOutcome.PERSISTENCE_UNKNOWN
    return None


def _dependency_group(
    kind: TargetDependencyKind,
    references: tuple[ActiveDependencyReference, ...],
    *,
    total: int | None = None,
) -> TargetDependencyGroup | None:
    by_reference = {item.reference: item for item in references}
    ordered = tuple(by_reference[key] for key in sorted(by_reference))
    count = len(ordered) if total is None else total
    if count <= 0:
        return None
    return TargetDependencyGroup(kind=kind, references=ordered, total=count)


def _compatibility_subject(value: DeploymentInteractionCompatibility) -> DirectedInteractionIdentity:
    return DirectedInteractionIdentity(
        source_component_deployment_id=value.source_component_deployment_id,
        destination_component_deployment_id=value.destination_component_deployment_id,
        dcs_contract_revision_id=value.current_dcs_revision_id,
    )


def _dependency_summary(
    port,
    *,
    subjects: tuple[DirectedInteractionIdentity, ...],
    as_of: datetime,
) -> ActiveDependencySummary:
    summarize = getattr(port, "summarize_active_references", None)
    if summarize is not None:
        return summarize(
            subjects=subjects,
            as_of=as_of,
            preview_limit=_DEPENDENCY_PREVIEW_LIMIT,
        )

    # Transitional compatibility for M1 in-memory adapters. Production M3 adapters
    # implement the bounded batch contract above.
    references: dict[str, ActiveDependencyReference] = {}
    for subject in subjects:
        for item in port.find_active_references(subject=subject, as_of=as_of):
            references[item.reference] = item
    ordered = tuple(references[key] for key in sorted(references))
    return ActiveDependencySummary(
        total=len(ordered),
        references=ordered[:_DEPENDENCY_PREVIEW_LIMIT],
    )


class CreateInteractionDefinition:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: TargetApplicationCatalogueRepository,
        identities: TargetApplicationCatalogueIdentityFactory,
        provenance: TargetApplicationCatalogueProvenanceFactory,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._identities = identities
        self._provenance = provenance

    def execute(
        self,
        command: CreateInteractionDefinitionCommand,
    ) -> InteractionDefinitionMutationResult:
        authority_outcome, authority_reference = _authority_reference(
            authority=self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority_outcome is not None:
            return InteractionDefinitionMutationResult(authority_outcome)
        idempotency_key = _required(command.idempotency_key)
        if idempotency_key is None:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.INPUT_INVALID)
        try:
            alternatives = canonical_dcs_alternatives(command.traffic_alternatives)
        except CatalogueInvariantError:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.INPUT_INVALID)
        fingerprint = _fingerprint(
            {
                "applicationId": str(command.application_id),
                "sourceComponentId": str(command.source_component_id),
                "destinationComponentId": str(command.destination_component_id),
                "trafficAlternatives": [_alternative_payload(item) for item in alternatives],
            }
        )
        receipt = self._catalogue.find_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is not None:
            if (
                receipt.command_kind != "CreateInteractionDefinition"
                or receipt.request_fingerprint != fingerprint
            ):
                return InteractionDefinitionMutationResult(
                    TargetMutationOutcome.IDEMPOTENCY_CONFLICT
                )
            existing = self._catalogue.get_interaction_definition(receipt.result_id)
            if existing is None:
                return InteractionDefinitionMutationResult(
                    TargetMutationOutcome.PERSISTENCE_UNKNOWN
                )
            return InteractionDefinitionMutationResult(
                TargetMutationOutcome.RESOLVED,
                interaction_definition=existing,
            )

        application = self._catalogue.get_application(command.application_id)
        source = self._catalogue.get_component(command.source_component_id)
        destination = self._catalogue.get_component(command.destination_component_id)
        if application is None or source is None or destination is None:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.NOT_FOUND)
        if (
            application.lifecycle_state is not CatalogueLifecycleState.ACTIVE
            or source.lifecycle_state is not CatalogueLifecycleState.ACTIVE
            or destination.lifecycle_state is not CatalogueLifecycleState.ACTIVE
        ):
            return InteractionDefinitionMutationResult(TargetMutationOutcome.PARENT_INACTIVE)
        if (
            source.application_id != application.application_id
            or destination.application_id != application.application_id
        ):
            return InteractionDefinitionMutationResult(TargetMutationOutcome.INPUT_INVALID)

        interaction_definition_id = self._identities.new_interaction_definition_id()
        try:
            value = InteractionDefinition(
                interaction_definition_id=interaction_definition_id,
                application_id=application.application_id,
                source_component_id=source.component_id,
                destination_component_id=destination.component_id,
                traffic_alternatives=alternatives,
                provenance_reference=self._provenance.for_interaction_definition(
                    interaction_definition_id=interaction_definition_id,
                    actor_id=command.actor_id,
                    authority_reference=authority_reference,
                    effective_time=command.effective_time,
                ),
            )
        except CatalogueInvariantError:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.INPUT_INVALID)
        self._catalogue.add_interaction_definition(value)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind="CreateInteractionDefinition",
                request_fingerprint=fingerprint,
                result_id=value.interaction_definition_id,
                result_version=value.version,
            ),
        )
        commit_outcome = _commit(self._catalogue)
        return InteractionDefinitionMutationResult(
            commit_outcome or TargetMutationOutcome.CREATED,
            interaction_definition=None if commit_outcome else value,
        )


class CreateApplicationDeployment:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: TargetApplicationCatalogueRepository,
        identities: TargetApplicationCatalogueIdentityFactory,
        provenance: TargetApplicationCatalogueProvenanceFactory,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._identities = identities
        self._provenance = provenance

    def execute(
        self,
        command: CreateApplicationDeploymentCommand,
    ) -> ApplicationDeploymentMutationResult:
        authority_outcome, authority_reference = _authority_reference(
            authority=self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority_outcome is not None:
            return ApplicationDeploymentMutationResult(authority_outcome)
        idempotency_key = _required(command.idempotency_key)
        company = _required(command.company_reference)
        environment = _required(command.environment)
        scope = _required(command.scope_reference)
        if None in (idempotency_key, company, environment, scope):
            return ApplicationDeploymentMutationResult(TargetMutationOutcome.INPUT_INVALID)
        fingerprint = _fingerprint(
            {
                "applicationId": str(command.application_id),
                "companyReference": company,
                "environment": environment,
                "scopeReference": scope,
            }
        )
        receipt = self._catalogue.find_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is not None:
            if (
                receipt.command_kind != "CreateApplicationDeployment"
                or receipt.request_fingerprint != fingerprint
            ):
                return ApplicationDeploymentMutationResult(
                    TargetMutationOutcome.IDEMPOTENCY_CONFLICT
                )
            existing = self._catalogue.get_application_deployment(receipt.result_id)
            if existing is None:
                return ApplicationDeploymentMutationResult(
                    TargetMutationOutcome.PERSISTENCE_UNKNOWN
                )
            return ApplicationDeploymentMutationResult(
                TargetMutationOutcome.RESOLVED,
                application_deployment=existing,
            )
        application = self._catalogue.get_application(command.application_id)
        if application is None:
            return ApplicationDeploymentMutationResult(TargetMutationOutcome.NOT_FOUND)
        if application.lifecycle_state is not CatalogueLifecycleState.ACTIVE:
            return ApplicationDeploymentMutationResult(TargetMutationOutcome.PARENT_INACTIVE)

        application_deployment_id = self._identities.new_application_deployment_id()
        try:
            value = ApplicationDeployment(
                application_deployment_id=application_deployment_id,
                application_id=application.application_id,
                company_reference=company,
                environment=environment,
                scope_reference=scope,
                provenance_reference=self._provenance.for_application_deployment(
                    application_deployment_id=application_deployment_id,
                    actor_id=command.actor_id,
                    authority_reference=authority_reference,
                    effective_time=command.effective_time,
                ),
            )
        except CatalogueInvariantError:
            return ApplicationDeploymentMutationResult(TargetMutationOutcome.INPUT_INVALID)
        self._catalogue.add_application_deployment(value)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind="CreateApplicationDeployment",
                request_fingerprint=fingerprint,
                result_id=value.application_deployment_id,
                result_version=value.version,
            ),
        )
        commit_outcome = _commit(self._catalogue)
        return ApplicationDeploymentMutationResult(
            commit_outcome or TargetMutationOutcome.CREATED,
            application_deployment=None if commit_outcome else value,
        )


class SelectDeploymentInteraction:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: TargetApplicationCatalogueRepository,
        identities: TargetApplicationCatalogueIdentityFactory,
        provenance: TargetApplicationCatalogueProvenanceFactory,
        encoder: DcsProjectionAuthoringEncoder,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._identities = identities
        self._provenance = provenance
        self._encoder = encoder

    def execute(
        self,
        command: SelectDeploymentInteractionCommand,
    ) -> DeploymentInteractionMutationResult:
        authority_outcome, authority_reference = _authority_reference(
            authority=self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority_outcome is not None:
            return DeploymentInteractionMutationResult(authority_outcome)
        idempotency_key = _required(command.idempotency_key)
        if idempotency_key is None:
            return DeploymentInteractionMutationResult(TargetMutationOutcome.INPUT_INVALID)
        fingerprint = _fingerprint(
            {
                "applicationDeploymentId": str(command.application_deployment_id),
                "interactionDefinitionId": str(command.interaction_definition_id),
            }
        )
        receipt = self._catalogue.find_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is not None:
            if (
                receipt.command_kind != "SelectDeploymentInteraction"
                or receipt.request_fingerprint != fingerprint
            ):
                return DeploymentInteractionMutationResult(
                    TargetMutationOutcome.IDEMPOTENCY_CONFLICT
                )
            existing = self._catalogue.get_deployment_interaction(receipt.result_id)
            if existing is None:
                return DeploymentInteractionMutationResult(
                    TargetMutationOutcome.PERSISTENCE_UNKNOWN
                )
            compatibility = self._catalogue.get_compatibility_projection(
                existing.deployment_interaction_id
            )
            revision = (
                self._catalogue.get_dcs_revision(compatibility.current_dcs_revision_id)
                if compatibility is not None
                else None
            )
            if compatibility is None or revision is None:
                return DeploymentInteractionMutationResult(
                    TargetMutationOutcome.PERSISTENCE_UNKNOWN
                )
            return DeploymentInteractionMutationResult(
                TargetMutationOutcome.RESOLVED,
                existing,
                compatibility,
                revision,
            )

        deployment = self._catalogue.get_application_deployment(
            command.application_deployment_id
        )
        definition = self._catalogue.get_interaction_definition(
            command.interaction_definition_id
        )
        if deployment is None or definition is None:
            return DeploymentInteractionMutationResult(TargetMutationOutcome.NOT_FOUND)
        if (
            deployment.lifecycle_state is not CatalogueLifecycleState.ACTIVE
            or definition.lifecycle_state is not CatalogueLifecycleState.ACTIVE
        ):
            return DeploymentInteractionMutationResult(TargetMutationOutcome.PARENT_INACTIVE)
        if deployment.application_id != definition.application_id:
            return DeploymentInteractionMutationResult(TargetMutationOutcome.INPUT_INVALID)
        if self._catalogue.find_active_deployment_interaction(
            application_deployment_id=deployment.application_deployment_id,
            interaction_definition_id=definition.interaction_definition_id,
        ) is not None:
            return DeploymentInteractionMutationResult(TargetMutationOutcome.ALREADY_EXISTS)

        source_component = self._catalogue.get_component(definition.source_component_id)
        destination_component = self._catalogue.get_component(
            definition.destination_component_id
        )
        if source_component is None or destination_component is None:
            return DeploymentInteractionMutationResult(
                TargetMutationOutcome.PERSISTENCE_UNKNOWN
            )
        if (
            source_component.lifecycle_state is not CatalogueLifecycleState.ACTIVE
            or destination_component.lifecycle_state is not CatalogueLifecycleState.ACTIVE
        ):
            return DeploymentInteractionMutationResult(TargetMutationOutcome.PARENT_INACTIVE)

        deployment_interaction_id = self._identities.new_deployment_interaction_id()
        source_compatibility_id = self._identities.new_component_deployment_id()
        destination_compatibility_id = self._identities.new_component_deployment_id()
        revision_id = self._identities.new_dcs_revision_id()
        interaction = DeploymentInteraction(
            deployment_interaction_id=deployment_interaction_id,
            application_deployment_id=deployment.application_deployment_id,
            interaction_definition_id=definition.interaction_definition_id,
            provenance_reference=self._provenance.for_deployment_interaction(
                deployment_interaction_id=deployment_interaction_id,
                actor_id=command.actor_id,
                authority_reference=authority_reference,
                effective_time=command.effective_time,
            ),
        )
        source_compatibility = ComponentDeployment(
            deployment_id=source_compatibility_id,
            component_id=source_component.component_id,
            provenance_reference=self._provenance.for_compatibility_component_deployment(
                component_deployment_id=source_compatibility_id,
                deployment_interaction_id=deployment_interaction_id,
                side=DeploymentInteractionSide.SOURCE,
                actor_id=command.actor_id,
                authority_reference=authority_reference,
                effective_time=command.effective_time,
            ),
        )
        destination_compatibility = ComponentDeployment(
            deployment_id=destination_compatibility_id,
            component_id=destination_component.component_id,
            provenance_reference=self._provenance.for_compatibility_component_deployment(
                component_deployment_id=destination_compatibility_id,
                deployment_interaction_id=deployment_interaction_id,
                side=DeploymentInteractionSide.DESTINATION,
                actor_id=command.actor_id,
                authority_reference=authority_reference,
                effective_time=command.effective_time,
            ),
        )
        revision = DcsRevision(
            revision_id=revision_id,
            source_component_deployment_id=source_compatibility.deployment_id,
            destination_component_deployment_id=destination_compatibility.deployment_id,
            projection_payload=self._encoder.encode(definition.traffic_alternatives),
            provenance_reference=self._provenance.for_dcs_revision(
                revision_id=revision_id,
                actor_id=command.actor_id,
                authority_reference=authority_reference,
                effective_time=command.effective_time,
            ),
        )
        compatibility = DeploymentInteractionCompatibility(
            deployment_interaction_id=deployment_interaction_id,
            source_component_deployment_id=source_compatibility.deployment_id,
            destination_component_deployment_id=destination_compatibility.deployment_id,
            current_dcs_revision_id=revision.revision_id,
        )
        try:
            self._catalogue.add_deployment_interaction(interaction)
            self._catalogue.add_component_deployment(source_compatibility)
            self._catalogue.add_component_deployment(destination_compatibility)
            self._catalogue.add_dcs_revision(revision)
            self._catalogue.add_compatibility_projection(compatibility)
        except CatalogueConcurrencyConflict:
            return DeploymentInteractionMutationResult(
                TargetMutationOutcome.CONCURRENCY_CONFLICT
            )
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind="SelectDeploymentInteraction",
                request_fingerprint=fingerprint,
                result_id=interaction.deployment_interaction_id,
                result_version=interaction.version,
            ),
        )
        commit_outcome = _commit(self._catalogue)
        if commit_outcome is not None:
            return DeploymentInteractionMutationResult(commit_outcome)
        return DeploymentInteractionMutationResult(
            TargetMutationOutcome.CREATED,
            interaction,
            compatibility,
            revision,
        )


class UpdateInteractionDefinitionEndpoints:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: TargetApplicationCatalogueRepository,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue

    def execute(
        self,
        command: UpdateInteractionDefinitionEndpointsCommand,
    ) -> InteractionDefinitionMutationResult:
        authority_outcome, _ = _authority_reference(
            authority=self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority_outcome is not None:
            return InteractionDefinitionMutationResult(authority_outcome)
        idempotency_key = _required(command.idempotency_key)
        if idempotency_key is None or command.expected_version < 1:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.INPUT_INVALID)
        fingerprint = _fingerprint(
            {
                "interactionDefinitionId": str(command.interaction_definition_id),
                "sourceComponentId": str(command.source_component_id),
                "destinationComponentId": str(command.destination_component_id),
                "expectedVersion": command.expected_version,
            }
        )
        receipt = self._catalogue.find_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is not None:
            if (
                receipt.command_kind != "UpdateInteractionDefinitionEndpoints"
                or receipt.request_fingerprint != fingerprint
            ):
                return InteractionDefinitionMutationResult(
                    TargetMutationOutcome.IDEMPOTENCY_CONFLICT
                )
            existing = self._catalogue.get_interaction_definition(receipt.result_id)
            if existing is None:
                return InteractionDefinitionMutationResult(
                    TargetMutationOutcome.PERSISTENCE_UNKNOWN
                )
            return InteractionDefinitionMutationResult(
                TargetMutationOutcome.RESOLVED,
                interaction_definition=existing,
            )
        current = self._catalogue.get_interaction_definition(
            command.interaction_definition_id
        )
        if current is None:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.NOT_FOUND)
        if current.lifecycle_state is not CatalogueLifecycleState.ACTIVE:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.PARENT_INACTIVE)
        if current.version != command.expected_version:
            return InteractionDefinitionMutationResult(
                TargetMutationOutcome.CONCURRENCY_CONFLICT
            )

        active_selections = self._catalogue.list_active_deployment_interactions_for_definition(
            interaction_definition_id=current.interaction_definition_id
        )
        if active_selections:
            references = tuple(
                ActiveDependencyReference(str(item.deployment_interaction_id))
                for item in active_selections[:_DEPENDENCY_PREVIEW_LIMIT]
            )
            return InteractionDefinitionMutationResult(
                TargetMutationOutcome.DEPENDENCY_BLOCKED,
                interaction_definition=current,
                dependencies=(
                    TargetDependencyGroup(
                        TargetDependencyKind.DEPLOYMENT_INTERACTIONS,
                        references,
                        total=len(active_selections),
                    ),
                ),
            )

        source = self._catalogue.get_component(command.source_component_id)
        destination = self._catalogue.get_component(command.destination_component_id)
        if source is None or destination is None:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.NOT_FOUND)
        if (
            source.lifecycle_state is not CatalogueLifecycleState.ACTIVE
            or destination.lifecycle_state is not CatalogueLifecycleState.ACTIVE
        ):
            return InteractionDefinitionMutationResult(TargetMutationOutcome.PARENT_INACTIVE)
        if (
            source.application_id != current.application_id
            or destination.application_id != current.application_id
        ):
            return InteractionDefinitionMutationResult(TargetMutationOutcome.INPUT_INVALID)
        try:
            updated = current.changed_endpoints(
                source_component_id=source.component_id,
                destination_component_id=destination.component_id,
            )
            self._catalogue.save_interaction_definition(
                updated,
                expected_version=command.expected_version,
            )
        except CatalogueInvariantError:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.INPUT_INVALID)
        except CatalogueConcurrencyConflict:
            return InteractionDefinitionMutationResult(
                TargetMutationOutcome.CONCURRENCY_CONFLICT
            )
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind="UpdateInteractionDefinitionEndpoints",
                request_fingerprint=fingerprint,
                result_id=updated.interaction_definition_id,
                result_version=updated.version,
            ),
        )
        commit_outcome = _commit(self._catalogue)
        if commit_outcome is not None:
            return InteractionDefinitionMutationResult(commit_outcome)
        return InteractionDefinitionMutationResult(
            TargetMutationOutcome.UPDATED,
            interaction_definition=updated,
        )


class UpdateInteractionDefinitionTraffic:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: TargetApplicationCatalogueRepository,
        identities: TargetApplicationCatalogueIdentityFactory,
        provenance: TargetApplicationCatalogueProvenanceFactory,
        encoder: DcsProjectionAuthoringEncoder,
        requirements: ConnectivityRequirementDependencyPort,
        decisions: ConnectivityDecisionDependencyPort,
        access_rules: AccessRuleDependencyPort,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._identities = identities
        self._provenance = provenance
        self._encoder = encoder
        self._requirements = requirements
        self._decisions = decisions
        self._access_rules = access_rules

    def execute(
        self,
        command: UpdateInteractionDefinitionTrafficCommand,
    ) -> InteractionDefinitionMutationResult:
        authority_outcome, authority_reference = _authority_reference(
            authority=self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority_outcome is not None:
            return InteractionDefinitionMutationResult(authority_outcome)
        idempotency_key = _required(command.idempotency_key)
        if idempotency_key is None or command.expected_version < 1:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.INPUT_INVALID)
        try:
            alternatives = canonical_dcs_alternatives(command.traffic_alternatives)
        except CatalogueInvariantError:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.INPUT_INVALID)
        fingerprint = _fingerprint(
            {
                "interactionDefinitionId": str(command.interaction_definition_id),
                "trafficAlternatives": [_alternative_payload(item) for item in alternatives],
                "expectedVersion": command.expected_version,
            }
        )
        receipt = self._catalogue.find_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is not None:
            if (
                receipt.command_kind != "UpdateInteractionDefinitionTraffic"
                or receipt.request_fingerprint != fingerprint
            ):
                return InteractionDefinitionMutationResult(
                    TargetMutationOutcome.IDEMPOTENCY_CONFLICT
                )
            existing = self._catalogue.get_interaction_definition(receipt.result_id)
            if existing is None:
                return InteractionDefinitionMutationResult(
                    TargetMutationOutcome.PERSISTENCE_UNKNOWN
                )
            return InteractionDefinitionMutationResult(
                TargetMutationOutcome.RESOLVED,
                interaction_definition=existing,
            )
        current = self._catalogue.get_interaction_definition(
            command.interaction_definition_id
        )
        if current is None:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.NOT_FOUND)
        if current.lifecycle_state is not CatalogueLifecycleState.ACTIVE:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.PARENT_INACTIVE)
        if current.version != command.expected_version:
            return InteractionDefinitionMutationResult(
                TargetMutationOutcome.CONCURRENCY_CONFLICT
            )
        if alternatives == current.traffic_alternatives:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.INPUT_INVALID)

        selections = self._catalogue.list_active_deployment_interactions_for_definition(
            interaction_definition_id=current.interaction_definition_id
        )
        projections: list[DeploymentInteractionCompatibility] = []
        for selection in selections:
            projection = self._catalogue.get_compatibility_projection(
                selection.deployment_interaction_id
            )
            if projection is None:
                return InteractionDefinitionMutationResult(
                    TargetMutationOutcome.PERSISTENCE_UNKNOWN
                )
            projections.append(projection)
        subjects = tuple(_compatibility_subject(item) for item in projections)

        summaries = (
            (
                TargetDependencyKind.CONNECTIVITY_REQUIREMENTS,
                _dependency_summary(
                    self._requirements,
                    subjects=subjects,
                    as_of=command.effective_time,
                ),
            ),
            (
                TargetDependencyKind.CONNECTIVITY_DECISIONS,
                _dependency_summary(
                    self._decisions,
                    subjects=subjects,
                    as_of=command.effective_time,
                ),
            ),
            (
                TargetDependencyKind.ACCESS_RULES,
                _dependency_summary(
                    self._access_rules,
                    subjects=subjects,
                    as_of=command.effective_time,
                ),
            ),
        )
        groups = tuple(
            group
            for kind, summary in summaries
            if (
                group := _dependency_group(
                    kind,
                    summary.references,
                    total=summary.total,
                )
            )
            is not None
        )
        if groups:
            return InteractionDefinitionMutationResult(
                TargetMutationOutcome.DEPENDENCY_BLOCKED,
                interaction_definition=current,
                dependencies=groups,
            )

        try:
            updated = current.changed_traffic(alternatives)
        except CatalogueInvariantError:
            return InteractionDefinitionMutationResult(TargetMutationOutcome.INPUT_INVALID)
        encoded = self._encoder.encode(updated.traffic_alternatives)
        generated: list[DcsRevision] = []
        try:
            for projection in projections:
                revision_id = self._identities.new_dcs_revision_id()
                revision = DcsRevision(
                    revision_id=revision_id,
                    source_component_deployment_id=projection.source_component_deployment_id,
                    destination_component_deployment_id=projection.destination_component_deployment_id,
                    projection_payload=encoded,
                    provenance_reference=self._provenance.for_dcs_revision(
                        revision_id=revision_id,
                        actor_id=command.actor_id,
                        authority_reference=authority_reference,
                        effective_time=command.effective_time,
                    ),
                )
                advanced = projection.advanced_to(revision.revision_id)
                self._catalogue.add_dcs_revision(revision)
                self._catalogue.save_compatibility_projection(
                    advanced,
                    expected_version=projection.version,
                )
                generated.append(revision)
            self._catalogue.save_interaction_definition(
                updated,
                expected_version=command.expected_version,
            )
        except CatalogueConcurrencyConflict:
            return InteractionDefinitionMutationResult(
                TargetMutationOutcome.CONCURRENCY_CONFLICT
            )
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind="UpdateInteractionDefinitionTraffic",
                request_fingerprint=fingerprint,
                result_id=updated.interaction_definition_id,
                result_version=updated.version,
            ),
        )
        commit_outcome = _commit(self._catalogue)
        if commit_outcome is not None:
            return InteractionDefinitionMutationResult(commit_outcome)
        return InteractionDefinitionMutationResult(
            TargetMutationOutcome.UPDATED,
            interaction_definition=updated,
            generated_revisions=tuple(generated),
        )
