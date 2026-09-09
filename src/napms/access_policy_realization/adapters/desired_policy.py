from itertools import product

from napms.access_policy.application.select_effective_policy import (
    EffectivePolicySelectionOutcome,
    SelectEffectiveDesiredPolicy,
)
from napms.access_policy_realization.application.ports import (
    DesiredPolicyRowProjection,
    DesiredPolicySnapshot,
)
from napms.access_policy_realization.domain.model import (
    AddressConstraint,
    AddressRange,
    DomainInteractionIdentity,
    InputProvenance,
    KnowledgeGap,
    PortConstraint,
    PortRange,
    ProtocolSelector,
    ResolutionInvariantError,
    TechnicalAccessPredicate,
)
from napms.policy_export.application.export_snapshot import (
    SnapshotAssemblyOutcome,
)
from napms.policy_export.application.normalization_types import (
    NormalizationInvariantError,
    PortConstraint as ExportPortConstraint,
    PortConstraintKind as ExportPortConstraintKind,
)


_PROTOCOL_NUMBERS = {
    "tcp": 6,
    "udp": 17,
}


def _gap(
    reason: str,
    *references: str,
) -> KnowledgeGap:
    return KnowledgeGap(
        owner="Access Policy Realization",
        reason=reason,
        references=tuple(
            value
            for value in references
            if value
        ),
    )


def _interaction(
    value,
) -> DomainInteractionIdentity:
    return DomainInteractionIdentity(
        value.source_component_deployment_id,
        value.destination_component_deployment_id,
        value.dcs_contract_revision_id,
    )


def _ports(
    value: ExportPortConstraint,
) -> tuple[PortConstraint, ...]:
    if (
        value.kind
        is ExportPortConstraintKind.NOT_APPLICABLE
    ):
        return (
            PortConstraint.not_applicable(),
        )
    if (
        value.kind
        is ExportPortConstraintKind.ANY
    ):
        return (
            PortConstraint.any(),
        )
    return tuple(
        PortConstraint.ranged(
            PortRange(
                item.first,
                item.last,
            )
        )
        for item in value.ranges
    )


def _row_provenance(
    row,
    *,
    authority_reference: str,
) -> InputProvenance:
    references = [
        "access-rule:" + str(row.rule_id),
        "access-policy-authority:"
        + authority_reference,
        "acc-fact:" + row.acc_fact_reference,
        "acc-validity:"
        + row.acc_validity_reference,
        "acc-provenance:"
        + row.acc_provenance_reference,
        "source-fact:"
        + row.source_fact_reference,
        "source-validity:"
        + row.source_validity_reference,
        "source-provenance:"
        + row.source_provenance_reference,
        "destination-fact:"
        + row.destination_fact_reference,
        "destination-validity:"
        + row.destination_validity_reference,
        "destination-provenance:"
        + row.destination_provenance_reference,
    ]
    if row.decision_reference:
        references.append(
            "connectivity-decision:"
            + row.decision_reference
        )
    if row.service_reference:
        references.append(
            "service-reference:"
            + row.service_reference
        )
    return InputProvenance(
        tuple(references)
    )


class EffectiveDesiredPolicyProjectionAdapter:
    def __init__(
        self,
        *,
        selector,
        snapshot_assembler,
        normalizer,
        actor_id: str,
    ) -> None:
        self._selector = selector
        self._snapshot_assembler = (
            snapshot_assembler
        )
        self._normalizer = normalizer
        self._actor_id = actor_id

    def load_effective(
        self,
        *,
        governance_scope: str,
        as_of,
    ) -> DesiredPolicySnapshot:
        selection = self._selector.execute(
            SelectEffectiveDesiredPolicy(
                scope=governance_scope,
                as_of=as_of,
                actor_id=self._actor_id,
            )
        )
        selection_reference = (
            "access-policy-selection:"
            + selection.outcome.value
        )
        if (
            selection.outcome
            is not EffectivePolicySelectionOutcome.SELECTED
        ):
            return DesiredPolicySnapshot(
                governance_scope=governance_scope,
                as_of=as_of,
                desired_interactions=(),
                rows=(),
                provenance_references=(
                    selection_reference,
                ),
                complete=False,
                knowledge_gaps=(
                    _gap(
                        (
                            "DesiredPolicyReadAuthorityDenied"
                            if selection.outcome
                            is EffectivePolicySelectionOutcome.AUTHORITY_DENIED
                            else "DesiredPolicyReadAuthorityUnknown"
                        ),
                        selection_reference,
                    ),
                ),
            )

        authority_reference = (
            selection.authority_reference
        )
        if not authority_reference:
            return DesiredPolicySnapshot(
                governance_scope=governance_scope,
                as_of=as_of,
                desired_interactions=(),
                rows=(),
                provenance_references=(
                    selection_reference,
                ),
                complete=False,
                knowledge_gaps=(
                    _gap(
                        "DesiredPolicyAuthorityReferenceMissing",
                        selection_reference,
                    ),
                ),
            )

        assembly = (
            self._snapshot_assembler.execute(
                selection
            )
        )
        if (
            assembly.outcome
            is not SnapshotAssemblyOutcome.SUCCESS
            or assembly.snapshot is None
        ):
            diagnostics = tuple(
                _gap(
                    (
                        "DesiredPolicySnapshot:"
                        + item.source.value
                        + ":"
                        + item.category.value
                    ),
                    (
                        str(item.rule_id)
                        if item.rule_id
                        is not None
                        else ""
                    ),
                    item.reference or "",
                )
                for item
                in assembly.diagnostics
            )
            if not diagnostics:
                diagnostics = (
                    _gap(
                        "DesiredPolicySnapshotUnavailable",
                    ),
                )
            return DesiredPolicySnapshot(
                governance_scope=governance_scope,
                as_of=as_of,
                desired_interactions=tuple(
                    _interaction(
                        rule.semantic_identity
                    )
                    for rule
                    in selection.rules
                ),
                rows=(),
                provenance_references=(
                    selection_reference,
                    "access-policy-authority:"
                    + authority_reference,
                ),
                complete=False,
                knowledge_gaps=diagnostics,
            )

        try:
            normalized = (
                self._normalizer.execute(
                    assembly.snapshot
                )
            )
        except NormalizationInvariantError:
            return DesiredPolicySnapshot(
                governance_scope=governance_scope,
                as_of=as_of,
                desired_interactions=tuple(
                    _interaction(
                        rule.semantic_identity
                    )
                    for rule
                    in selection.rules
                ),
                rows=(),
                provenance_references=(
                    selection_reference,
                    "access-policy-authority:"
                    + authority_reference,
                ),
                complete=False,
                knowledge_gaps=(
                    _gap(
                        "DesiredPolicyNormalizationFailed",
                    ),
                ),
            )

        gaps: list[KnowledgeGap] = []
        projected: list[
            DesiredPolicyRowProjection
        ] = []
        desired_interactions = tuple(
            sorted(
                {
                    _interaction(
                        rule.semantic_identity
                    )
                    for rule
                    in selection.rules
                },
                key=lambda item: (
                    str(
                        item.source_component_deployment_id
                    ),
                    str(
                        item.destination_component_deployment_id
                    ),
                    str(
                        item.dcs_contract_revision_id
                    ),
                ),
            )
        )

        if (
            normalized.scope
            != governance_scope
            or normalized.as_of != as_of
        ):
            gaps.append(
                _gap(
                    "DesiredPolicyNormalizationCorrelationMismatch",
                )
            )

        for row in normalized.rows:
            interaction = _interaction(
                row.rule_semantic_identity
            )
            protocol_number = (
                _PROTOCOL_NUMBERS.get(
                    row.protocol
                )
            )
            if protocol_number is None:
                gaps.append(
                    _gap(
                        (
                            "UnsupportedDesiredProtocol:"
                            + row.protocol
                        ),
                        "access-rule:"
                        + str(row.rule_id),
                    )
                )
                continue

            try:
                source_address = (
                    AddressConstraint.ranged(
                        AddressRange(
                            row.source_technical_address,
                            row.source_technical_address,
                        )
                    )
                )
                destination_address = (
                    AddressConstraint.ranged(
                        AddressRange(
                            row.destination_technical_address,
                            row.destination_technical_address,
                        )
                    )
                )
                source_ports = _ports(
                    row.source_ports
                )
                destination_ports = _ports(
                    row.destination_ports
                )
            except (
                ResolutionInvariantError,
                ValueError,
                TypeError,
            ):
                gaps.append(
                    _gap(
                        "InvalidDesiredTechnicalProjection",
                        "access-rule:"
                        + str(row.rule_id),
                    )
                )
                continue

            provenance = _row_provenance(
                row,
                authority_reference=(
                    authority_reference
                ),
            )
            for (
                source_port,
                destination_port,
            ) in product(
                source_ports,
                destination_ports,
            ):
                projected.append(
                    DesiredPolicyRowProjection(
                        rule_reference=(
                            "access-rule:"
                            + str(row.rule_id)
                        ),
                        interaction=interaction,
                        predicate=(
                            TechnicalAccessPredicate(
                                source_addresses=(
                                    source_address
                                ),
                                destination_addresses=(
                                    destination_address
                                ),
                                protocol=(
                                    ProtocolSelector.ip_protocol(
                                        protocol_number
                                    )
                                ),
                                source_ports=source_port,
                                destination_ports=(
                                    destination_port
                                ),
                            )
                        ),
                        input_provenance=(
                            provenance
                        ),
                    )
                )

        return DesiredPolicySnapshot(
            governance_scope=governance_scope,
            as_of=as_of,
            desired_interactions=(
                desired_interactions
            ),
            rows=tuple(projected),
            provenance_references=(
                selection_reference,
                "access-policy-authority:"
                + authority_reference,
            ),
            complete=not gaps,
            knowledge_gaps=tuple(gaps),
        )
