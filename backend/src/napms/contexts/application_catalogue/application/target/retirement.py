from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID

from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityOutcome,
    ApplicationCatalogueCurationAuthorityPort,
    CataloguePersistenceError,
)
from napms.contexts.application_catalogue.application.target.curation import TargetMutationOutcome
from napms.contexts.application_catalogue.application.target.lifecycle import (
    RetirementDependencyKind,
    RetirementMutationResult,
)
from napms.contexts.application_catalogue.application.target.ports import (
    AccessRuleDependencyPort,
    ActiveDependencyReference,
    ActiveDependencySummary,
    ConnectivityDecisionDependencyPort,
    ConnectivityRequirementDependencyPort,
    TargetApplicationCatalogueRepository,
)
from napms.contexts.application_catalogue.domain.model import CatalogueInvariantError, DirectedInteractionIdentity


_DEFAULT_PREVIEW_LIMIT = 20


class RetirementSubjectKind(str, Enum):
    APPLICATION_DEFINITION = "ApplicationDefinition"
    COMPONENT = "Component"
    INTERACTION_DEFINITION = "InteractionDefinition"
    APPLICATION_DEPLOYMENT = "ApplicationDeployment"
    DEPLOYMENT_INTERACTION = "DeploymentInteraction"


@dataclass(frozen=True, slots=True)
class TargetRetirementDependencyGroup:
    kind: RetirementDependencyKind
    total: int
    references: tuple[ActiveDependencyReference, ...] = ()

    def __post_init__(self) -> None:
        if self.total < 0:
            raise CatalogueInvariantError("retirement dependency total must be >= 0")
        if len(self.references) > self.total:
            raise CatalogueInvariantError("retirement dependency preview cannot exceed total")

    @property
    def count(self) -> int:
        return self.total


@dataclass(frozen=True, slots=True)
class TargetRetirementMutationResult:
    outcome: TargetMutationOutcome
    subject: object | None = None
    dependencies: tuple[TargetRetirementDependencyGroup, ...] = ()


class LocalRetirementDependencyReadPort(Protocol):
    def page(
        self,
        *,
        subject_kind: RetirementSubjectKind,
        subject_id: UUID,
        dependency_kind: RetirementDependencyKind,
        as_of: datetime,
        offset: int,
        limit: int,
    ) -> ActiveDependencySummary: ...


_LOCAL_KINDS = {
    RetirementSubjectKind.APPLICATION_DEFINITION: (
        RetirementDependencyKind.COMPONENTS,
        RetirementDependencyKind.INTERACTIONS,
        RetirementDependencyKind.APPLICATION_DEPLOYMENTS,
    ),
    RetirementSubjectKind.COMPONENT: (
        RetirementDependencyKind.INTERACTIONS,
        RetirementDependencyKind.LEGACY_COMPONENT_DEPLOYMENTS,
    ),
    RetirementSubjectKind.INTERACTION_DEFINITION: (
        RetirementDependencyKind.DEPLOYMENT_INTERACTIONS,
    ),
    RetirementSubjectKind.APPLICATION_DEPLOYMENT: (
        RetirementDependencyKind.DEPLOYMENT_INTERACTIONS,
    ),
    RetirementSubjectKind.DEPLOYMENT_INTERACTION: (
        RetirementDependencyKind.RESOURCE_BINDINGS,
    ),
}

_PEER_KINDS = (
    RetirementDependencyKind.CONNECTIVITY_REQUIREMENTS,
    RetirementDependencyKind.CONNECTIVITY_DECISIONS,
    RetirementDependencyKind.ACCESS_RULES,
)


class TargetRetirementDependencyReader:
    """Bounded, exact dependency projection for retirement UX and admission preflight."""

    def __init__(
        self,
        *,
        catalogue: TargetApplicationCatalogueRepository,
        local: LocalRetirementDependencyReadPort,
        requirements: ConnectivityRequirementDependencyPort,
        decisions: ConnectivityDecisionDependencyPort,
        access_rules: AccessRuleDependencyPort,
    ) -> None:
        self._catalogue = catalogue
        self._local = local
        self._requirements = requirements
        self._decisions = decisions
        self._access_rules = access_rules

    def subject_exists(
        self,
        *,
        subject_kind: RetirementSubjectKind,
        subject_id: UUID,
    ) -> bool:
        loaders = {
            RetirementSubjectKind.APPLICATION_DEFINITION: self._catalogue.get_application,
            RetirementSubjectKind.COMPONENT: self._catalogue.get_component,
            RetirementSubjectKind.INTERACTION_DEFINITION: self._catalogue.get_interaction_definition,
            RetirementSubjectKind.APPLICATION_DEPLOYMENT: self._catalogue.get_application_deployment,
            RetirementSubjectKind.DEPLOYMENT_INTERACTION: self._catalogue.get_deployment_interaction,
        }
        return loaders[subject_kind](subject_id) is not None

    def summarize(
        self,
        *,
        subject_kind: RetirementSubjectKind,
        subject_id: UUID,
        as_of: datetime,
        preview_limit: int = _DEFAULT_PREVIEW_LIMIT,
    ) -> tuple[TargetRetirementDependencyGroup, ...] | None:
        _validate_page(as_of=as_of, offset=0, limit=preview_limit)
        if not self.subject_exists(subject_kind=subject_kind, subject_id=subject_id):
            return None

        kinds = list(_LOCAL_KINDS[subject_kind])
        if subject_kind is RetirementSubjectKind.DEPLOYMENT_INTERACTION:
            kinds.extend(_PEER_KINDS)
        groups = []
        for kind in kinds:
            group = self.page(
                subject_kind=subject_kind,
                subject_id=subject_id,
                dependency_kind=kind,
                as_of=as_of,
                offset=0,
                limit=preview_limit,
                require_subject=False,
            )
            if group.total:
                groups.append(group)
        return tuple(groups)

    def page(
        self,
        *,
        subject_kind: RetirementSubjectKind,
        subject_id: UUID,
        dependency_kind: RetirementDependencyKind,
        as_of: datetime,
        offset: int,
        limit: int,
        require_subject: bool = True,
    ) -> TargetRetirementDependencyGroup:
        _validate_page(as_of=as_of, offset=offset, limit=limit)
        allowed = set(_LOCAL_KINDS[subject_kind])
        if subject_kind is RetirementSubjectKind.DEPLOYMENT_INTERACTION:
            allowed.update(_PEER_KINDS)
        if dependency_kind not in allowed:
            raise CatalogueInvariantError("dependency kind is not valid for retirement subject")
        if require_subject and not self.subject_exists(
            subject_kind=subject_kind,
            subject_id=subject_id,
        ):
            raise LookupError("retirement subject not found")

        if dependency_kind in _LOCAL_KINDS[subject_kind]:
            summary = self._local.page(
                subject_kind=subject_kind,
                subject_id=subject_id,
                dependency_kind=dependency_kind,
                as_of=as_of,
                offset=offset,
                limit=limit,
            )
        else:
            subject = self._compatibility_subject(subject_id)
            port = {
                RetirementDependencyKind.CONNECTIVITY_REQUIREMENTS: self._requirements,
                RetirementDependencyKind.CONNECTIVITY_DECISIONS: self._decisions,
                RetirementDependencyKind.ACCESS_RULES: self._access_rules,
            }[dependency_kind]
            summary = port.list_active_references(
                subjects=(subject,),
                as_of=as_of,
                offset=offset,
                limit=limit,
            )
        return TargetRetirementDependencyGroup(
            kind=dependency_kind,
            total=summary.total,
            references=summary.references,
        )

    def _compatibility_subject(self, deployment_interaction_id: UUID) -> DirectedInteractionIdentity:
        compatibility = self._catalogue.get_compatibility_projection(deployment_interaction_id)
        if compatibility is None:
            raise CataloguePersistenceError(
                "Deployment Interaction compatibility projection is unavailable"
            )
        return DirectedInteractionIdentity(
            source_component_deployment_id=compatibility.source_component_deployment_id,
            destination_component_deployment_id=compatibility.destination_component_deployment_id,
            dcs_contract_revision_id=compatibility.current_dcs_revision_id,
        )


class BoundedRetirementService:
    """Authorize, preflight exact bounded dependencies, then delegate lifecycle mutation."""

    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        subject_kind: RetirementSubjectKind,
        subject_id_attribute: str,
        dependencies: TargetRetirementDependencyReader,
        delegate,
    ) -> None:
        self._authority = authority
        self._subject_kind = subject_kind
        self._subject_id_attribute = subject_id_attribute
        self._dependencies = dependencies
        self._delegate = delegate

    def execute(self, command) -> TargetRetirementMutationResult:
        authority = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority.outcome is ApplicationCatalogueAuthorityOutcome.DENIED:
            return TargetRetirementMutationResult(TargetMutationOutcome.AUTHORITY_DENIED)
        if (
            authority.outcome is not ApplicationCatalogueAuthorityOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return TargetRetirementMutationResult(TargetMutationOutcome.AUTHORITY_UNKNOWN)

        subject_id = getattr(command, self._subject_id_attribute)
        groups = self._dependencies.summarize(
            subject_kind=self._subject_kind,
            subject_id=subject_id,
            as_of=command.effective_time,
        )
        if groups:
            return TargetRetirementMutationResult(
                TargetMutationOutcome.DEPENDENCY_BLOCKED,
                dependencies=groups,
            )

        # The M1 delegate repeats authority/version/dependency checks and owns the
        # actual transaction. That second check closes the preflight-to-write race.
        result: RetirementMutationResult = self._delegate.execute(command)
        if result.outcome is TargetMutationOutcome.DEPENDENCY_BLOCKED:
            current = self._dependencies.summarize(
                subject_kind=self._subject_kind,
                subject_id=subject_id,
                as_of=command.effective_time,
            )
            if current:
                return TargetRetirementMutationResult(
                    result.outcome,
                    subject=result.subject,
                    dependencies=current,
                )
        return TargetRetirementMutationResult(
            result.outcome,
            subject=result.subject,
            dependencies=tuple(
                TargetRetirementDependencyGroup(
                    kind=group.kind,
                    total=group.count,
                    references=group.references,
                )
                for group in result.dependencies
            ),
        )


def _validate_page(*, as_of: datetime, offset: int, limit: int) -> None:
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise CatalogueInvariantError("as_of must be offset-aware")
    if offset < 0 or not 1 <= limit <= 200:
        raise CatalogueInvariantError(
            "retirement dependency page requires offset >= 0 and limit within 1..200"
        )
