from napms.contexts.access_policy.application.active_dependency_references import (
    AccessRuleDependencySubject,
    ReadActiveAccessRuleReferences,
)
from napms.contexts.application_catalogue.application.target.ports import (
    ActiveDependencyReference,
    ActiveDependencySummary,
)
from napms.contexts.application_catalogue.domain.model import DirectedInteractionIdentity
from napms.contexts.connectivity_decision.application.active_dependency_references import (
    ConnectivityDecisionDependencySubject,
    ReadActiveConnectivityDecisionReferences,
)
from napms.contexts.connectivity_requirements.application.active_dependency_references import (
    ConnectivityRequirementDependencySubject,
    ReadActiveConnectivityRequirementReferences,
)


class ConnectivityRequirementDependencyAdapter:
    def __init__(self, query: ReadActiveConnectivityRequirementReferences) -> None:
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

class ConnectivityDecisionDependencyAdapter:
    def __init__(self, query: ReadActiveConnectivityDecisionReferences) -> None:
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

class AccessRuleDependencyAdapter:
    def __init__(self, query: ReadActiveAccessRuleReferences) -> None:
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

def _unique(
    subjects: tuple[DirectedInteractionIdentity, ...],
) -> tuple[DirectedInteractionIdentity, ...]:
    return tuple(dict.fromkeys(subjects))


def _requirement_subject(value: DirectedInteractionIdentity) -> ConnectivityRequirementDependencySubject:
    return ConnectivityRequirementDependencySubject(
        source_component_deployment_id=value.source_component_deployment_id,
        destination_component_deployment_id=value.destination_component_deployment_id,
        dcs_contract_revision_id=value.dcs_contract_revision_id,
    )


def _decision_subject(value: DirectedInteractionIdentity) -> ConnectivityDecisionDependencySubject:
    return ConnectivityDecisionDependencySubject(
        source_component_deployment_id=value.source_component_deployment_id,
        destination_component_deployment_id=value.destination_component_deployment_id,
        dcs_contract_revision_id=value.dcs_contract_revision_id,
    )


def _rule_subject(value: DirectedInteractionIdentity) -> AccessRuleDependencySubject:
    return AccessRuleDependencySubject(
        source_component_deployment_id=value.source_component_deployment_id,
        destination_component_deployment_id=value.destination_component_deployment_id,
        dcs_contract_revision_id=value.dcs_contract_revision_id,
    )


def _summary(total: int, references: tuple[str, ...]) -> ActiveDependencySummary:
    return ActiveDependencySummary(
        total=total,
        references=tuple(ActiveDependencyReference(reference) for reference in references),
    )
