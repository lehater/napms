from datetime import datetime
from uuid import UUID

from napms.contexts.access_policy_realization.application.ports import (
    ConfiguredEvidencePort,
    DesiredPolicyPort,
    DomainKnowledgePort,
    EnforcementPlacementPort,
    ManagedReconciliationScopeContract,
)
from napms.contexts.access_policy_realization.application.resolve import (
    ResolveTechnicalAccess,
)
from napms.contexts.access_policy_realization.domain.algebra import (
    expand_predicate,
)
from napms.contexts.access_policy_realization.domain.model import (
    KnowledgeGap,
)
from napms.contexts.access_policy_realization.domain.realization import (
    ConfiguredEnforcementSnapshot,
    DesiredEnforcementPolicy,
    DesiredPolicyContribution,
    derive_desired_enforcement_policy,
)


def _gap(
    reason: str,
    *references: str,
) -> KnowledgeGap:
    return KnowledgeGap(
        owner="Access Policy Realization",
        reason=reason,
        references=tuple(references),
    )


class DeriveDesiredEnforcementFromOwners:
    def __init__(
        self,
        *,
        desired_policy: DesiredPolicyPort,
        domain_knowledge: DomainKnowledgePort,
        placement: EnforcementPlacementPort,
    ) -> None:
        self._desired_policy = desired_policy
        self._resolver = ResolveTechnicalAccess(
            domain_knowledge=domain_knowledge
        )
        self._placement = placement

    def execute(
        self,
        *,
        governance_scope: str,
        as_of: datetime,
    ) -> DesiredEnforcementPolicy:
        snapshot = (
            self._desired_policy.load_effective(
                governance_scope=governance_scope,
                as_of=as_of,
            )
        )
        gaps = list(
            snapshot.knowledge_gaps
        )
        correlated = (
            snapshot.governance_scope
            == governance_scope
            and snapshot.as_of == as_of
        )
        if not correlated:
            gaps.append(
                _gap(
                    "DesiredPolicySnapshotCorrelationMismatch",
                    *snapshot.provenance_references,
                )
            )

        contributions: list[
            DesiredPolicyContribution
        ] = []
        for row in (
            snapshot.rows
            if correlated
            else ()
        ):
            fragments = expand_predicate(
                row.predicate
            )
            if len(fragments) != 1:
                gaps.append(
                    _gap(
                        "DesiredProjectionNotSingleFragment",
                        row.rule_reference,
                    )
                )
                continue
            fragment = fragments[0]
            if (
                fragment.source_address.first
                != fragment.source_address.last
                or fragment.destination_address.first
                != fragment.destination_address.last
            ):
                gaps.append(
                    _gap(
                        "PlacementRequiresExactEndpoints",
                        row.rule_reference,
                    )
                )
                continue

            resolution = self._resolver.execute(
                predicate=row.predicate,
                as_of=as_of,
                input_provenance=(
                    row.input_provenance
                ),
            )
            placement = self._placement.select_for(
                source_ip=(
                    fragment.source_address.first
                ),
                destination_ip=(
                    fragment.destination_address.first
                ),
                as_of=as_of,
                input_provenance=(
                    row.input_provenance
                ),
            )
            contributions.append(
                DesiredPolicyContribution(
                    rule_reference=(
                        row.rule_reference
                    ),
                    interaction=row.interaction,
                    fragment=fragment,
                    resolution=resolution,
                    placement_status=(
                        placement.status
                    ),
                    placements=(
                        placement.placements
                    ),
                    placement_provenance_references=(
                        placement.provenance_references
                    ),
                    knowledge_gaps=(
                        placement.knowledge_gaps
                    ),
                )
            )

        return derive_desired_enforcement_policy(
            governance_scope=governance_scope,
            as_of=as_of,
            desired_interactions=(
                snapshot.desired_interactions
            ),
            contributions=tuple(
                contributions
            ),
            knowledge_gaps=tuple(gaps),
        )


class BuildConfiguredEnforcementSnapshot:
    def __init__(
        self,
        *,
        configured_evidence: ConfiguredEvidencePort,
        domain_knowledge: DomainKnowledgePort,
    ) -> None:
        self._configured_evidence = (
            configured_evidence
        )
        self._resolver = ResolveTechnicalAccess(
            domain_knowledge=domain_knowledge
        )

    def execute(
        self,
        *,
        evidence_set_id: UUID,
        contract: ManagedReconciliationScopeContract,
        as_of: datetime,
    ) -> ConfiguredEnforcementSnapshot:
        projection = (
            self._configured_evidence.load_configured(
                evidence_set_id=evidence_set_id,
                contract=contract,
                as_of=as_of,
            )
        )
        gaps = list(
            projection.knowledge_gaps
        )
        complete = (
            projection.complete_for_managed_scope
        )
        if (
            projection.managed_scope
            != contract.managed_scope
            or projection.as_of != as_of
        ):
            gaps.append(
                _gap(
                    "ConfiguredProjectionCorrelationMismatch",
                    contract.managed_scope.source_contract_reference,
                )
            )
            complete = False

        regions = []
        resolutions = []
        for permit in projection.permits:
            regions.extend(
                expand_predicate(
                    permit.predicate
                )
            )
            resolutions.append(
                self._resolver.execute(
                    predicate=permit.predicate,
                    as_of=as_of,
                    input_provenance=(
                        permit.input_provenance
                    ),
                )
            )

        return ConfiguredEnforcementSnapshot(
            managed_scope=(
                contract.managed_scope
            ),
            as_of=as_of,
            permit_regions=tuple(regions),
            domain_resolutions=tuple(
                resolutions
            ),
            evidence_references=(
                projection.evidence_references
            ),
            complete_for_managed_scope=(
                complete
            ),
            knowledge_gaps=tuple(
                gaps
            ),
        )
