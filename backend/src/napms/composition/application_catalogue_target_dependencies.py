from napms.access_policy.adapters.postgres.application_catalogue_dependency_query import (
    PostgresAccessRuleDependencyQuery,
)
from napms.access_policy.domain.model import RuleSemanticIdentity
from napms.application_catalogue.application.target_ports import (
    ActiveDependencyReference,
    ActiveDependencySummary,
)
from napms.application_catalogue.domain.model import DirectedInteractionIdentity
from napms.connectivity_decision.adapters.postgres.application_catalogue_dependency_query import (
    PostgresConnectivityDecisionDependencyQuery,
)
from napms.connectivity_decision.domain.model import DecisionSubject
from napms.contexts.connectivity_requirements.infrastructure.persistence.postgres.application_catalogue_dependency_query import (
    PostgresConnectivityRequirementDependencyQuery,
)
from napms.contexts.connectivity_requirements.domain.model import RequiredSemanticInteraction


class ConnectivityRequirementDependencyAdapter:
    def __init__(self, query: PostgresConnectivityRequirementDependencyQuery) -> None:
        self._query = query

    def summarize_active_references(self, *, subjects, as_of, preview_limit):
        return self.list_active_references(
            subjects=subjects,
            as_of=as_of,
            offset=0,
            limit=preview_limit,
        )

    def list_active_references(self, *, subjects, as_of, offset, limit):
        total, references = self._query.page(
            subjects=tuple(_requirement_subject(item) for item in _unique(subjects)),
            as_of=as_of,
            offset=offset,
            limit=limit,
        )
        return _summary(total, references)

    def find_active_references(self, *, subject, as_of):
        """Bounded compatibility recheck for the M1 retirement service.

        M3 product reads use the summary/page contract above. The M1 lifecycle service
        only needs to know whether at least one peer dependency appeared after preflight.
        """
        return self.list_active_references(
            subjects=(subject,),
            as_of=as_of,
            offset=0,
            limit=1,
        ).references


class ConnectivityDecisionDependencyAdapter:
    def __init__(self, query: PostgresConnectivityDecisionDependencyQuery) -> None:
        self._query = query

    def summarize_active_references(self, *, subjects, as_of, preview_limit):
        return self.list_active_references(
            subjects=subjects,
            as_of=as_of,
            offset=0,
            limit=preview_limit,
        )

    def list_active_references(self, *, subjects, as_of, offset, limit):
        total, references = self._query.page(
            subjects=tuple(_decision_subject(item) for item in _unique(subjects)),
            as_of=as_of,
            offset=offset,
            limit=limit,
        )
        return _summary(total, references)

    def find_active_references(self, *, subject, as_of):
        return self.list_active_references(
            subjects=(subject,),
            as_of=as_of,
            offset=0,
            limit=1,
        ).references


class AccessRuleDependencyAdapter:
    def __init__(self, query: PostgresAccessRuleDependencyQuery) -> None:
        self._query = query

    def summarize_active_references(self, *, subjects, as_of, preview_limit):
        return self.list_active_references(
            subjects=subjects,
            as_of=as_of,
            offset=0,
            limit=preview_limit,
        )

    def list_active_references(self, *, subjects, as_of, offset, limit):
        total, references = self._query.page(
            subjects=tuple(_rule_subject(item) for item in _unique(subjects)),
            as_of=as_of,
            offset=offset,
            limit=limit,
        )
        return _summary(total, references)

    def find_active_references(self, *, subject, as_of):
        return self.list_active_references(
            subjects=(subject,),
            as_of=as_of,
            offset=0,
            limit=1,
        ).references


def _unique(
    subjects: tuple[DirectedInteractionIdentity, ...],
) -> tuple[DirectedInteractionIdentity, ...]:
    return tuple(dict.fromkeys(subjects))


def _requirement_subject(value: DirectedInteractionIdentity) -> RequiredSemanticInteraction:
    return RequiredSemanticInteraction(
        source_component_deployment_id=value.source_component_deployment_id,
        destination_component_deployment_id=value.destination_component_deployment_id,
        dcs_contract_revision_id=value.dcs_contract_revision_id,
    )


def _decision_subject(value: DirectedInteractionIdentity) -> DecisionSubject:
    return DecisionSubject(
        source_component_deployment_id=value.source_component_deployment_id,
        destination_component_deployment_id=value.destination_component_deployment_id,
        dcs_contract_revision_id=value.dcs_contract_revision_id,
    )


def _rule_subject(value: DirectedInteractionIdentity) -> RuleSemanticIdentity:
    return RuleSemanticIdentity(
        source_component_deployment_id=value.source_component_deployment_id,
        destination_component_deployment_id=value.destination_component_deployment_id,
        dcs_contract_revision_id=value.dcs_contract_revision_id,
    )


def _summary(total: int, references: tuple[str, ...]) -> ActiveDependencySummary:
    return ActiveDependencySummary(
        total=total,
        references=tuple(ActiveDependencyReference(reference) for reference in references),
    )
