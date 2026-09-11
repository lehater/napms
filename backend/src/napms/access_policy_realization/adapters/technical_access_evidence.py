from dataclasses import dataclass
from uuid import UUID

from napms.access_policy_realization.domain.model import (
    AddressConstraint,
    AddressRange,
    InputProvenance,
    PortConstraint,
    PortRange,
    ProtocolSelector,
    TechnicalAccessPredicate,
)
from napms.technical_access_evidence.domain.model import (
    AddressConstraintKind as TaeAddressConstraintKind,
    EvidenceTimeKind,
    PortConstraintKind as TaePortConstraintKind,
    ProtocolSelectorKind as TaeProtocolSelectorKind,
    TechnicalAccessEvidenceSet,
)


@dataclass(frozen=True, slots=True)
class ProjectedTechnicalAccess:
    predicate: TechnicalAccessPredicate
    input_provenance: InputProvenance


class TechnicalAccessEvidenceProjectionAdapter:
    def project_entry(
        self,
        *,
        evidence_set: TechnicalAccessEvidenceSet,
        evidence_entry_id: UUID,
    ) -> ProjectedTechnicalAccess:
        matches = tuple(
            entry
            for entry in evidence_set.entries
            if (
                entry.evidence_entry_id
                == evidence_entry_id
            )
        )
        if len(matches) != 1:
            raise ValueError(
                "evidence entry must exist exactly once "
                "inside the supplied evidence set"
            )
        entry = matches[0]
        payload = entry.payload
        references = [
            (
                "tae-evidence-set:"
                + str(
                    evidence_set.evidence_set_id
                )
            ),
            (
                "tae-evidence-entry:"
                + str(
                    entry.evidence_entry_id
                )
            ),
            (
                "tae-source:"
                + evidence_set.source.namespace
                + ":"
                + evidence_set.source.reference
            ),
            (
                "tae-source-scope:"
                + evidence_set.source_scope.value
            ),
            (
                "tae-source-capture:"
                + evidence_set.source_capture_reference.value
            ),
            (
                "tae-kind:"
                + evidence_set.kind.value
            ),
            (
                "tae-recorded-at:"
                + evidence_set.recorded_at.isoformat()
            ),
        ]
        references.extend(
            _evidence_time_references(
                evidence_set
            )
        )
        if payload.action is not None:
            references.append(
                "tae-action:"
                + payload.action.value
            )
        if (
            payload.source_entry_reference
            is not None
        ):
            references.append(
                "tae-source-entry:"
                + payload.source_entry_reference
            )
        if payload.source_position is not None:
            references.append(
                "tae-source-position:"
                + str(payload.source_position)
            )

        return ProjectedTechnicalAccess(
            predicate=_predicate(
                payload.predicate
            ),
            input_provenance=InputProvenance(
                tuple(references)
            ),
        )


def _predicate(
    value,
) -> TechnicalAccessPredicate:
    if (
        value.source_addresses.kind
        is TaeAddressConstraintKind.ANY
    ):
        source_addresses = (
            AddressConstraint.any()
        )
    else:
        source_addresses = (
            AddressConstraint.ranged(
                *(
                    AddressRange(
                        region.first,
                        region.last,
                    )
                    for region
                    in value.source_addresses.ranges
                )
            )
        )

    if (
        value.destination_addresses.kind
        is TaeAddressConstraintKind.ANY
    ):
        destination_addresses = (
            AddressConstraint.any()
        )
    else:
        destination_addresses = (
            AddressConstraint.ranged(
                *(
                    AddressRange(
                        region.first,
                        region.last,
                    )
                    for region
                    in value.destination_addresses.ranges
                )
            )
        )

    if (
        value.protocol.kind
        is TaeProtocolSelectorKind.ANY
    ):
        protocol = ProtocolSelector.any()
    else:
        assert value.protocol.number is not None
        protocol = ProtocolSelector.ip_protocol(
            value.protocol.number
        )

    return TechnicalAccessPredicate(
        source_addresses=source_addresses,
        destination_addresses=destination_addresses,
        protocol=protocol,
        source_ports=_ports(
            value.source_ports
        ),
        destination_ports=_ports(
            value.destination_ports
        ),
    )


def _ports(
    value,
) -> PortConstraint:
    if (
        value.kind
        is TaePortConstraintKind.NOT_APPLICABLE
    ):
        return PortConstraint.not_applicable()
    if (
        value.kind
        is TaePortConstraintKind.ANY
    ):
        return PortConstraint.any()
    return PortConstraint.ranged(
        *(
            PortRange(
                region.first,
                region.last,
            )
            for region
            in value.ranges
        )
    )


def _evidence_time_references(
    evidence_set: TechnicalAccessEvidenceSet,
) -> tuple[str, ...]:
    value = evidence_set.evidence_time
    if value.kind is EvidenceTimeKind.UNKNOWN:
        return ("tae-evidence-time:Unknown",)
    if value.kind is EvidenceTimeKind.INSTANT:
        assert value.at is not None
        return (
            (
                "tae-evidence-time:Instant:"
                + value.at.isoformat()
            ),
        )
    assert value.start is not None
    assert value.end is not None
    return (
        (
            "tae-evidence-time:Window:"
            + value.start.isoformat()
            + "/"
            + value.end.isoformat()
        ),
    )
