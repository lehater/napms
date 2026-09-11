from collections import defaultdict

from napms.contexts.connectivity_requirements.application.ports import (
    ConnectivityRequirementRepository,
    RequirementPersistenceError,
)
from napms.contexts.connectivity_requirements.domain.model import (
    RequiredSemanticInteraction,
    RequirementLifecycleState,
)
from napms.workflows.scoped_connectivity_inventory.application.model import (
    CoverageSummary,
    InteractionIdentity,
    RequirementCurrent,
    RequirementSummary,
)
from napms.workflows.scoped_connectivity_inventory.application.ports import (
    DependencyAvailability,
    RequirementSummaryReadResult,
)


def _to_required(identity: InteractionIdentity) -> RequiredSemanticInteraction:
    return RequiredSemanticInteraction(
        source_component_deployment_id=identity.source_component_deployment_id,
        destination_component_deployment_id=identity.destination_component_deployment_id,
        dcs_contract_revision_id=identity.dcs_contract_revision_id,
    )


def _to_inventory(identity: RequiredSemanticInteraction) -> InteractionIdentity:
    return InteractionIdentity(
        identity.source_component_deployment_id,
        identity.destination_component_deployment_id,
        identity.dcs_contract_revision_id,
    )


class ConnectivityRequirementsScopedConnectivityAdapter:
    def __init__(self, *, requirements: ConnectivityRequirementRepository) -> None:
        self._requirements = requirements

    def summarize_requirements(
        self,
        *,
        responsibility_scope,
        identities,
        as_of,
    ) -> RequirementSummaryReadResult:
        unique = tuple(dict.fromkeys(identities))
        if not unique:
            return RequirementSummaryReadResult(
                DependencyAvailability.AVAILABLE,
                (),
            )

        requested = set(unique)
        try:
            rows = self._requirements.list_inventory_summaries(
                governance_scope=responsibility_scope,
                interactions=tuple(_to_required(identity) for identity in unique),
            )
        except RequirementPersistenceError:
            return RequirementSummaryReadResult(
                DependencyAvailability.UNAVAILABLE
            )

        grouped: dict[InteractionIdentity, list] = defaultdict(list)
        for row in rows:
            identity = _to_inventory(row.required_interaction)
            if row.governance_scope != responsibility_scope or identity not in requested:
                return RequirementSummaryReadResult(
                    DependencyAvailability.UNAVAILABLE
                )
            grouped[identity].append(row)

        items = []
        for identity in unique:
            matches = grouped.get(identity, [])
            current = [
                requirement
                for requirement in matches
                if (
                    requirement.lifecycle_state is RequirementLifecycleState.ACTIVE
                    and requirement.applicability.applies_at(as_of)
                )
            ]
            if current:
                items.append(
                    RequirementSummary(
                        identity=identity,
                        current=RequirementCurrent.REQUIRED,
                        historical_only=False,
                        coverage=CoverageSummary.UNKNOWN,
                    )
                )
            elif matches:
                items.append(
                    RequirementSummary(
                        identity=identity,
                        current=RequirementCurrent.NONE,
                        historical_only=True,
                        coverage=CoverageSummary.NOT_CURRENT,
                    )
                )
            else:
                items.append(
                    RequirementSummary(
                        identity=identity,
                        current=RequirementCurrent.NONE,
                        historical_only=False,
                        coverage=CoverageSummary.NOT_APPLICABLE,
                    )
                )

        return RequirementSummaryReadResult(
            DependencyAvailability.AVAILABLE,
            tuple(items),
        )
