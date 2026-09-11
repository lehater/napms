from datetime import datetime, timedelta, timezone
from uuid import UUID

from napms.contexts.access_policy_realization.application.ports import (
    ConfiguredEvidenceProjection,
    ConfiguredPermitProjection,
    ConfiguredPolicySemantics,
    DesiredPolicyRowProjection,
    DesiredPolicySnapshot,
    ManagedReconciliationScopeContract,
    PlacementSelectionProjection,
)
from napms.contexts.access_policy_realization.application.realize import (
    BuildConfiguredEnforcementSnapshot,
    DeriveDesiredEnforcementFromOwners,
)
from napms.contexts.access_policy_realization.domain.model import (
    AddressConstraint,
    AddressRange,
    DomainInteractionIdentity,
    DomainInteractionRegion,
    DomainKnowledgeSnapshot,
    DomainRegionProvenance,
    InputProvenance,
    KnowledgeGap,
    PortConstraint,
    PortRange,
    PortRegion,
    ProtocolSelector,
    ResolutionStatus,
    TechnicalAccessPredicate,
    TechnicalRegionFragment,
)
from napms.contexts.access_policy_realization.domain.realization import (
    DesiredDerivationStatus,
    EnforcementPlacementProjection,
    EnforcementTarget,
    ManagedReconciliationScope,
    PlacementStatus,
)


NOW = datetime(
    2026,
    9,
    9,
    12,
    tzinfo=timezone.utc,
)
INTERACTION = DomainInteractionIdentity(
    UUID(int=1),
    UUID(int=2),
    UUID(int=3),
)
TARGET = EnforcementTarget(
    UUID(int=10),
    UUID(int=20),
)


def predicate():
    return TechnicalAccessPredicate(
        AddressConstraint.ranged(
            AddressRange(
                "10.0.0.1",
                "10.0.0.1",
            )
        ),
        AddressConstraint.ranged(
            AddressRange(
                "10.0.0.2",
                "10.0.0.2",
            )
        ),
        ProtocolSelector.ip_protocol(6),
        PortConstraint.any(),
        PortConstraint.ranged(
            PortRange(443, 443)
        ),
    )


def fragment():
    return TechnicalRegionFragment(
        AddressRange(
            "10.0.0.1",
            "10.0.0.1",
        ),
        AddressRange(
            "10.0.0.2",
            "10.0.0.2",
        ),
        6,
        PortRegion.numeric(
            0,
            65535,
        ),
        PortRegion.numeric(
            443,
            443,
        ),
    )


class Knowledge:
    def load_for(
        self,
        *,
        predicate,
        as_of,
    ):
        assert as_of == NOW
        return DomainKnowledgeSnapshot(
            (
                DomainInteractionRegion(
                    INTERACTION,
                    fragment(),
                    DomainRegionProvenance(
                        ("acc:1",),
                        ("src:1",),
                        ("dst:1",),
                    ),
                ),
            )
        )


class Desired:
    def __init__(
        self,
        snapshot,
    ):
        self.snapshot = snapshot

    def load_effective(
        self,
        *,
        governance_scope,
        as_of,
    ):
        return self.snapshot


class Placement:
    def __init__(self):
        self.calls = []

    def select_for(
        self,
        *,
        source_ip,
        destination_ip,
        as_of,
        input_provenance,
    ):
        self.calls.append(
            (
                source_ip,
                destination_ip,
                as_of,
            )
        )
        return PlacementSelectionProjection(
            status=PlacementStatus.PLACED,
            placements=(
                EnforcementPlacementProjection(
                    TARGET,
                    ("placement:1",),
                ),
            ),
            provenance_references=(
                "path:1",
            ),
        )


def desired_snapshot(
    *,
    as_of=NOW,
    scope="scope:a",
):
    return DesiredPolicySnapshot(
        governance_scope=scope,
        as_of=as_of,
        desired_interactions=(
            INTERACTION,
        ),
        rows=(
            DesiredPolicyRowProjection(
                rule_reference="rule:1",
                interaction=INTERACTION,
                predicate=predicate(),
                input_provenance=(
                    InputProvenance(
                        ("desired:1",)
                    )
                ),
            ),
        ),
        provenance_references=(
            "desired-snapshot:1",
        ),
        complete=True,
    )


def test_owner_orchestration_derives_desired_intent():
    placement = Placement()
    result = (
        DeriveDesiredEnforcementFromOwners(
            desired_policy=Desired(
                desired_snapshot()
            ),
            domain_knowledge=Knowledge(),
            placement=placement,
        ).execute(
            governance_scope="scope:a",
            as_of=NOW,
        )
    )

    assert (
        result.status
        is DesiredDerivationStatus.DERIVED
    )
    assert result.regions_for(
        TARGET
    ) == (
        fragment(),
    )
    assert placement.calls == [
        (
            "10.0.0.1",
            "10.0.0.2",
            NOW,
        )
    ]


def test_desired_snapshot_correlation_mismatch_fails_closed_before_placement():
    placement = Placement()
    result = (
        DeriveDesiredEnforcementFromOwners(
            desired_policy=Desired(
                desired_snapshot(
                    as_of=NOW
                    - timedelta(minutes=1)
                )
            ),
            domain_knowledge=Knowledge(),
            placement=placement,
        ).execute(
            governance_scope="scope:a",
            as_of=NOW,
        )
    )

    assert (
        result.status
        is DesiredDerivationStatus.UNKNOWN
    )
    assert placement.calls == []
    assert {
        value.reason
        for value in result.knowledge_gaps
    } == {
        "DesiredPolicySnapshotCorrelationMismatch"
    }


class Configured:
    def __init__(
        self,
        projection,
    ):
        self.projection = projection

    def load_configured(
        self,
        *,
        evidence_set_id,
        contract,
        as_of,
    ):
        return self.projection


def contract():
    return ManagedReconciliationScopeContract(
        managed_scope=(
            ManagedReconciliationScope(
                "scope:a",
                TARGET,
                "contract:1",
            )
        ),
        evidence_source_namespace=(
            "controller"
        ),
        evidence_source_reference="fw-a",
        evidence_source_scope_reference=(
            "policy-a"
        ),
        semantics=(
            ConfiguredPolicySemantics.EFFECTIVE_PERMIT_SET
        ),
        complete_for_managed_scope=True,
        provenance_reference=(
            "contract-provenance:1"
        ),
    )


def configured_projection(
    *,
    as_of=NOW,
    managed_scope=None,
):
    return ConfiguredEvidenceProjection(
        managed_scope=(
            managed_scope
            or contract().managed_scope
        ),
        as_of=as_of,
        permits=(
            ConfiguredPermitProjection(
                predicate(),
                InputProvenance(
                    ("evidence:1",)
                ),
            ),
        ),
        evidence_references=(
            "evidence-set:1",
        ),
        complete_for_managed_scope=True,
    )


def test_configured_builder_reuses_i18_resolution():
    result = (
        BuildConfiguredEnforcementSnapshot(
            configured_evidence=Configured(
                configured_projection()
            ),
            domain_knowledge=Knowledge(),
        ).execute(
            evidence_set_id=UUID(int=100),
            contract=contract(),
            as_of=NOW,
        )
    )

    assert result.complete_for_managed_scope
    assert result.permit_regions == (
        fragment(),
    )
    assert (
        result.domain_resolutions[0].status
        is ResolutionStatus.EXACT
    )


def test_configured_projection_correlation_mismatch_fails_closed():
    result = (
        BuildConfiguredEnforcementSnapshot(
            configured_evidence=Configured(
                configured_projection(
                    as_of=NOW
                    - timedelta(minutes=1)
                )
            ),
            domain_knowledge=Knowledge(),
        ).execute(
            evidence_set_id=UUID(int=100),
            contract=contract(),
            as_of=NOW,
        )
    )

    assert (
        not result.complete_for_managed_scope
    )
    assert {
        value.reason
        for value in result.knowledge_gaps
    } == {
        "ConfiguredProjectionCorrelationMismatch"
    }
