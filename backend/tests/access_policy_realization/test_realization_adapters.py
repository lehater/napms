from dataclasses import replace
from datetime import datetime, timedelta, timezone
from uuid import UUID

from napms.access_policy.application.select_effective_policy import (
    EffectivePolicySelectionOutcome,
    EffectivePolicySelectionResult,
)
from napms.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    OperationalState,
    ProposalProvenance,
    RuleSemanticIdentity,
)
from napms.access_policy_realization.adapters.configured_evidence import (
    ConfiguredEvidenceProjectionAdapter,
)
from napms.access_policy_realization.adapters.desired_policy import (
    EffectiveDesiredPolicyProjectionAdapter,
)
from napms.access_policy_realization.adapters.placement import (
    NetworkEnforcementPlacementProjectionAdapter,
)
from napms.access_policy_realization.application.ports import (
    ConfiguredPolicySemantics,
    ManagedReconciliationScopeContract,
)
from napms.access_policy_realization.domain.model import (
    InputProvenance,
)
from napms.access_policy_realization.domain.realization import (
    EnforcementTarget,
    ManagedReconciliationScope,
    PlacementStatus,
)
from napms.network_enforcement_placement.domain.model import (
    EnforcementPlacement,
    EnforcementSelection,
    InputProvenance as NepInputProvenance,
    PathAttachmentReference,
    PlacementProvenance,
    ProviderRealizationReference,
    SelectionStatus,
    TrafficRelation,
)
from napms.policy_export.application.export_snapshot import (
    ExportSnapshotAssemblyResult,
    SnapshotAssemblyOutcome,
)
from napms.policy_export.application.normalization_types import (
    NormalizedPolicyRow,
    PortConstraint,
    PortRange,
    SuccessfulNormalizedPolicyExport,
)
from napms.policy_export.application.ports import (
    ResourceReference,
)
from napms.technical_access_evidence.application.read import (
    EvidenceSetDetailOutcome,
    EvidenceSetDetailResult,
)
from napms.technical_access_evidence.domain.model import (
    AddressConstraint as TaeAddressConstraint,
    AddressRange as TaeAddressRange,
    EvidenceAction,
    EvidenceKind,
    EvidenceSourceReference,
    EvidenceTime,
    PortConstraint as TaePortConstraint,
    PortRange as TaePortRange,
    ProtocolSelector as TaeProtocolSelector,
    SourceCaptureReference,
    SourceScopeReference,
    TechnicalAccessEntry,
    TechnicalAccessEntryPayload,
    TechnicalAccessEvidenceSet,
    TechnicalAccessPredicate as TaePredicate,
)


NOW = datetime(
    2026,
    9,
    9,
    12,
    tzinfo=timezone.utc,
)
IDENTITY = RuleSemanticIdentity(
    UUID(int=1),
    UUID(int=2),
    UUID(int=3),
)
TARGET = EnforcementTarget(
    UUID(int=10),
    UUID(int=20),
)


def rule():
    return AccessRule(
        rule_id=UUID(int=4),
        semantic_identity=IDENTITY,
        operational_state=(
            OperationalState.ACTIVE
        ),
        decision=DecisionReference(
            subject=IDENTITY,
            result=(
                ConnectivityDecisionResult.ALLOWED
            ),
            decision_id="decision:1",
        ),
        proposal_provenance=(
            ProposalProvenance(
                actor_id="actor:1",
                authority_scope="scope:a",
                effective_time=NOW,
                authority_reference=(
                    "write-authority:1"
                ),
                catalogue_reference=(
                    "catalogue:1"
                ),
            )
        ),
    )


class Selector:
    def execute(self, command):
        return EffectivePolicySelectionResult(
            EffectivePolicySelectionOutcome.SELECTED,
            command.scope,
            command.as_of,
            (rule(),),
            "read-authority:1",
        )


class Assembler:
    def execute(self, selection):
        return ExportSnapshotAssemblyResult(
            SnapshotAssemblyOutcome.SUCCESS,
            snapshot=object(),
        )


class Normalizer:
    def __init__(
        self,
        protocol="tcp",
    ):
        self.protocol = protocol

    def execute(self, snapshot):
        return SuccessfulNormalizedPolicyExport(
            scope="scope:a",
            as_of=NOW,
            authority_reference=(
                "read-authority:1"
            ),
            rows=(
                NormalizedPolicyRow(
                    rule_id=UUID(int=4),
                    rule_semantic_identity=(
                        IDENTITY
                    ),
                    decision_reference=(
                        "decision:1"
                    ),
                    rule_governance_scope=(
                        "scope:a"
                    ),
                    rule_operational_state=(
                        OperationalState.ACTIVE
                    ),
                    rule_effective_window=None,
                    snapshot_as_of=NOW,
                    read_authority_reference=(
                        "read-authority:1"
                    ),
                    source_resource_reference=(
                        ResourceReference(
                            "resource:a"
                        )
                    ),
                    source_endpoint_reference=(
                        "endpoint:a"
                    ),
                    source_technical_address=(
                        "10.0.0.1"
                    ),
                    source_fact_reference=(
                        "source-fact:1"
                    ),
                    source_validity_reference=(
                        "source-validity:1"
                    ),
                    source_provenance_reference=(
                        "source-provenance:1"
                    ),
                    destination_resource_reference=(
                        ResourceReference(
                            "resource:b"
                        )
                    ),
                    destination_endpoint_reference=(
                        "endpoint:b"
                    ),
                    destination_technical_address=(
                        "10.0.0.2"
                    ),
                    destination_fact_reference=(
                        "destination-fact:1"
                    ),
                    destination_validity_reference=(
                        "destination-validity:1"
                    ),
                    destination_provenance_reference=(
                        "destination-provenance:1"
                    ),
                    protocol=self.protocol,
                    source_ports=(
                        PortConstraint.any()
                    ),
                    destination_ports=(
                        PortConstraint.ranged(
                            PortRange(
                                443,
                                443,
                            )
                        )
                    ),
                    service_reference=None,
                    acc_fact_reference=(
                        "acc-fact:1"
                    ),
                    acc_validity_reference=(
                        "acc-validity:1"
                    ),
                    acc_provenance_reference=(
                        "acc-provenance:1"
                    ),
                ),
            ),
        )


def desired_adapter(
    protocol="tcp",
):
    return EffectiveDesiredPolicyProjectionAdapter(
        selector=Selector(),
        snapshot_assembler=Assembler(),
        normalizer=Normalizer(
            protocol
        ),
        actor_id="actor:1",
    )


def test_desired_adapter_projects_owner_snapshot_to_apr_types():
    result = desired_adapter().load_effective(
        governance_scope="scope:a",
        as_of=NOW,
    )

    assert result.complete
    assert len(result.rows) == 1
    row = result.rows[0]
    assert (
        row.predicate.protocol.number
        == 6
    )
    assert (
        row.predicate.destination_ports.ranges[
            0
        ].first
        == 443
    )
    assert (
        row.interaction.dcs_contract_revision_id
        == UUID(int=3)
    )


def test_desired_adapter_rejects_mis_correlated_normalized_row():
    class BadNormalizer(Normalizer):
        def execute(self, snapshot):
            normalized = super().execute(
                snapshot
            )
            row = replace(
                normalized.rows[0],
                rule_governance_scope=(
                    "scope:other"
                ),
            )
            return replace(
                normalized,
                rows=(row,),
            )

    result = (
        EffectiveDesiredPolicyProjectionAdapter(
            selector=Selector(),
            snapshot_assembler=Assembler(),
            normalizer=BadNormalizer(),
            actor_id="actor:1",
        ).load_effective(
            governance_scope="scope:a",
            as_of=NOW,
        )
    )

    assert not result.complete
    assert result.rows == ()
    assert {
        gap.reason
        for gap in result.knowledge_gaps
    } == {
        "DesiredPolicyRowCorrelationMismatch"
    }


def test_desired_adapter_fails_closed_for_unsupported_protocol():
    result = desired_adapter(
        "vendor-proto"
    ).load_effective(
        governance_scope="scope:a",
        as_of=NOW,
    )

    assert not result.complete
    assert result.rows == ()
    assert {
        gap.reason
        for gap in result.knowledge_gaps
    } == {
        "UnsupportedDesiredProtocol:vendor-proto"
    }


class NepSelector:
    def execute(
        self,
        *,
        relation,
        as_of,
        input_provenance,
    ):
        provider = (
            ProviderRealizationReference(
                "controller",
                "device-a",
            )
        )
        path_attachment = (
            PathAttachmentReference(
                "controller",
                "edge-a",
            )
        )
        return EnforcementSelection(
            relation=relation,
            as_of=as_of,
            status=SelectionStatus.PLACED,
            path_reference="path:1",
            placements=(
                EnforcementPlacement(
                    logical_firewall_id=(
                        TARGET.logical_firewall_id
                    ),
                    enforcement_attachment_id=(
                        TARGET.enforcement_attachment_id
                    ),
                    provider_realization=(
                        provider
                    ),
                    path_attachment=(
                        path_attachment
                    ),
                    traversal_position=0,
                    provenance=(
                        PlacementProvenance(
                            ("path-prov:1",),
                            ("fw-prov:1",),
                            ("corr-prov:1",),
                            ("attach-prov:1",),
                        )
                    ),
                ),
            ),
            ambiguities=(),
            knowledge_gaps=(),
            input_provenance=(
                NepInputProvenance(
                    input_provenance.references
                )
            ),
            complete=True,
        )


def test_nep_adapter_rejects_mis_correlated_selection():
    class BadNepSelector(NepSelector):
        def execute(
            self,
            *,
            relation,
            as_of,
            input_provenance,
        ):
            value = super().execute(
                relation=relation,
                as_of=as_of,
                input_provenance=(
                    input_provenance
                ),
            )
            return replace(
                value,
                as_of=as_of
                - timedelta(minutes=1),
            )

    result = (
        NetworkEnforcementPlacementProjectionAdapter(
            select_enforcement=(
                BadNepSelector()
            )
        ).select_for(
            source_ip="10.0.0.1",
            destination_ip="10.0.0.2",
            as_of=NOW,
            input_provenance=(
                InputProvenance(
                    ("desired:1",)
                )
            ),
        )
    )

    assert (
        result.status
        is PlacementStatus.UNKNOWN
    )
    assert result.placements == ()
    assert {
        gap.reason
        for gap in result.knowledge_gaps
    } == {
        "PlacementSelectionCorrelationMismatch"
    }


def test_nep_adapter_preserves_attachment_target_and_provenance():
    result = (
        NetworkEnforcementPlacementProjectionAdapter(
            select_enforcement=(
                NepSelector()
            )
        ).select_for(
            source_ip="10.0.0.1",
            destination_ip="10.0.0.2",
            as_of=NOW,
            input_provenance=(
                InputProvenance(
                    ("desired:1",)
                )
            ),
        )
    )

    assert (
        result.status
        is PlacementStatus.PLACED
    )
    assert (
        result.placements[0].target
        == TARGET
    )
    assert any(
        value.startswith(
            "nep-enforcement-attachment:"
        )
        for value
        in result.placements[
            0
        ].provenance_references
    )


def tae_predicate():
    return TaePredicate(
        source_addresses=(
            TaeAddressConstraint.ranged(
                TaeAddressRange(
                    "10.0.0.1",
                    "10.0.0.1",
                )
            )
        ),
        destination_addresses=(
            TaeAddressConstraint.ranged(
                TaeAddressRange(
                    "10.0.0.2",
                    "10.0.0.2",
                )
            )
        ),
        protocol=(
            TaeProtocolSelector.ip_protocol(
                6
            )
        ),
        source_ports=(
            TaePortConstraint.any()
        ),
        destination_ports=(
            TaePortConstraint.ranged(
                TaePortRange(
                    443,
                    443,
                )
            )
        ),
    )


def evidence_set(
    *,
    action=EvidenceAction.PERMIT,
    source_scope="policy-a",
):
    return TechnicalAccessEvidenceSet(
        evidence_set_id=UUID(int=100),
        kind=EvidenceKind.CONFIGURED,
        source=EvidenceSourceReference(
            "controller",
            "fw-a",
        ),
        source_scope=SourceScopeReference(
            source_scope
        ),
        source_capture_reference=(
            SourceCaptureReference(
                "capture:1"
            )
        ),
        evidence_time=(
            EvidenceTime.instant(
                NOW
            )
        ),
        recorded_at=NOW,
        entries=(
            TechnicalAccessEntry(
                UUID(int=101),
                TechnicalAccessEntryPayload(
                    predicate=tae_predicate(),
                    action=action,
                    source_entry_reference=(
                        "rule:1"
                    ),
                    source_position=0,
                ),
            ),
        ),
    )


class GetEvidence:
    def __init__(
        self,
        value,
    ):
        self.value = value

    def execute(self, evidence_set_id):
        return EvidenceSetDetailResult(
            EvidenceSetDetailOutcome.FOUND,
            self.value,
        )


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


def test_configured_adapter_requires_exact_source_scope_time_and_permit_semantics():
    result = ConfiguredEvidenceProjectionAdapter(
        get_evidence_set=(
            GetEvidence(
                evidence_set()
            )
        )
    ).load_configured(
        evidence_set_id=UUID(int=100),
        contract=contract(),
        as_of=NOW,
    )

    assert result.complete_for_managed_scope
    assert len(result.permits) == 1
    assert (
        result.permits[
            0
        ].predicate.protocol.number
        == 6
    )


def test_configured_adapter_rejects_mis_correlated_evidence_id():
    wrong = replace(
        evidence_set(),
        evidence_set_id=UUID(int=999),
    )
    result = ConfiguredEvidenceProjectionAdapter(
        get_evidence_set=(
            GetEvidence(wrong)
        )
    ).load_configured(
        evidence_set_id=UUID(int=100),
        contract=contract(),
        as_of=NOW,
    )

    assert (
        not result.complete_for_managed_scope
    )
    assert {
        gap.reason
        for gap in result.knowledge_gaps
    } == {
        "ConfiguredEvidenceSetIdMismatch"
    }


def test_configured_adapter_block_entry_fails_closed():
    result = ConfiguredEvidenceProjectionAdapter(
        get_evidence_set=(
            GetEvidence(
                evidence_set(
                    action=EvidenceAction.BLOCK
                )
            )
        )
    ).load_configured(
        evidence_set_id=UUID(int=100),
        contract=contract(),
        as_of=NOW,
    )

    assert (
        not result.complete_for_managed_scope
    )
    assert result.permits == ()
    assert {
        gap.reason
        for gap in result.knowledge_gaps
    } == {
        "ConfiguredSourceNotEffectivePermitSet"
    }


def test_configured_adapter_scope_mismatch_fails_closed():
    result = ConfiguredEvidenceProjectionAdapter(
        get_evidence_set=(
            GetEvidence(
                evidence_set(
                    source_scope=(
                        "other-policy"
                    )
                )
            )
        )
    ).load_configured(
        evidence_set_id=UUID(int=100),
        contract=contract(),
        as_of=NOW,
    )

    assert (
        not result.complete_for_managed_scope
    )
    assert {
        gap.reason
        for gap in result.knowledge_gaps
    } == {
        "ConfiguredEvidenceScopeMismatch"
    }
