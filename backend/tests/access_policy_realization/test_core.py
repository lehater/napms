from datetime import datetime, timezone
from uuid import UUID

import pytest

from napms.contexts.access_policy_realization.application.resolve import (
    ResolveTechnicalAccess,
)
from napms.contexts.access_policy_realization.domain.model import (
    AccessCorrespondence,
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
    ResolutionInvariantError,
    ResolutionStatus,
    TechnicalAccessPredicate,
    TechnicalRegionFragment,
)


NOW = datetime(
    2026,
    9,
    9,
    12,
    tzinfo=timezone.utc,
)


def identity(value):
    return DomainInteractionIdentity(
        UUID(int=value),
        UUID(int=value + 100),
        UUID(int=value + 200),
    )


def provenance(value):
    return DomainRegionProvenance(
        (f"acc:{value}",),
        (f"src:{value}",),
        (f"dst:{value}",),
    )


def predicate(
    *,
    src_first="10.0.0.1",
    src_last=None,
    dst="10.0.0.2",
    ports=((443, 443),),
    protocol=6,
):
    source = AddressConstraint.ranged(
        AddressRange(
            src_first,
            src_last or src_first,
        )
    )
    destination = AddressConstraint.ranged(
        AddressRange(
            dst,
            dst,
        )
    )
    destination_ports = PortConstraint.ranged(
        *(
            PortRange(first, last)
            for first, last in ports
        )
    )
    return TechnicalAccessPredicate(
        source,
        destination,
        ProtocolSelector.ip_protocol(
            protocol
        ),
        PortConstraint.any(),
        destination_ports,
    )


def fragment(
    *,
    src_first="10.0.0.1",
    src_last=None,
    dst="10.0.0.2",
    first=443,
    last=None,
    protocol=6,
):
    return TechnicalRegionFragment(
        AddressRange(
            src_first,
            src_last or src_first,
        ),
        AddressRange(dst, dst),
        protocol,
        PortRegion.numeric(0, 65535),
        PortRegion.numeric(
            first,
            last if last is not None else first,
        ),
    )


def region(value, **kwargs):
    return DomainInteractionRegion(
        identity(value),
        fragment(**kwargs),
        provenance(value),
    )


class MemoryKnowledge:
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.calls = []

    def load_for(
        self,
        *,
        predicate,
        as_of,
    ):
        self.calls.append(
            (predicate, as_of)
        )
        return self.snapshot


def resolve_predicate(
    value,
    snapshot,
):
    return ResolveTechnicalAccess(
        domain_knowledge=MemoryKnowledge(
            snapshot
        )
    ).execute(
        predicate=value,
        as_of=NOW,
        input_provenance=InputProvenance(
            ("evidence:1",)
        ),
    )


def test_exact_one_interaction_resolution():
    result = resolve_predicate(
        predicate(),
        DomainKnowledgeSnapshot(
            (region(1),)
        ),
    )

    assert (
        result.status
        is ResolutionStatus.EXACT
    )
    assert (
        result.correspondences[0].relation
        is AccessCorrespondence.EXACT
    )
    assert (
        result.remainder.fragments
        == ()
    )
    assert result.remainder.complete
    assert (
        result.input_provenance.references
        == ("evidence:1",)
    )


def test_predicate_covered_by_broader_domain_region():
    result = resolve_predicate(
        predicate(),
        DomainKnowledgeSnapshot(
            (
                region(
                    1,
                    first=440,
                    last=450,
                ),
            )
        ),
    )

    assert (
        result.status
        is ResolutionStatus.COVERED
    )
    assert (
        result.correspondences[0].relation
        is AccessCorrespondence.COVERED_BY
    )
    assert (
        result.remainder.fragments
        == ()
    )


def test_partial_port_overlap_preserves_exact_remainder():
    result = resolve_predicate(
        predicate(
            ports=((440, 450),)
        ),
        DomainKnowledgeSnapshot(
            (region(1, first=443),)
        ),
    )

    assert (
        result.status
        is ResolutionStatus.PARTIAL
    )
    assert (
        result.correspondences[0].relation
        is AccessCorrespondence.COVERS
    )
    assert [
        (
            value.destination_ports.first,
            value.destination_ports.last,
        )
        for value
        in result.remainder.fragments
    ] == [
        (440, 442),
        (444, 450),
    ]


def test_several_nonambiguous_interactions_cover_union():
    result = resolve_predicate(
        predicate(
            ports=(
                (443, 443),
                (8443, 8443),
            )
        ),
        DomainKnowledgeSnapshot(
            (
                region(
                    1,
                    first=443,
                ),
                region(
                    2,
                    first=8443,
                ),
            )
        ),
    )

    assert (
        result.status
        is ResolutionStatus.COVERED
    )
    assert {
        value.interaction
        for value
        in result.correspondences
    } == {
        identity(1),
        identity(2),
    }
    assert (
        result.remainder.fragments
        == ()
    )


def test_partial_address_overlap_preserves_exact_remainder():
    result = resolve_predicate(
        predicate(
            src_first="10.0.0.1",
            src_last="10.0.0.3",
        ),
        DomainKnowledgeSnapshot(
            (
                region(
                    1,
                    src_first="10.0.0.2",
                ),
            )
        ),
    )

    assert (
        result.status
        is ResolutionStatus.PARTIAL
    )
    assert [
        (
            value.source_address.first,
            value.source_address.last,
        )
        for value
        in result.remainder.fragments
    ] == [
        (
            "10.0.0.1",
            "10.0.0.1",
        ),
        (
            "10.0.0.3",
            "10.0.0.3",
        ),
    ]


def test_distinct_interactions_are_ambiguous_without_winner():
    result = resolve_predicate(
        predicate(),
        DomainKnowledgeSnapshot(
            (
                region(1),
                region(2),
            )
        ),
    )

    assert (
        result.status
        is ResolutionStatus.AMBIGUOUS
    )
    assert len(
        result.ambiguities
    ) == 1
    assert set(
        result.ambiguities[0].interactions
    ) == {
        identity(1),
        identity(2),
    }
    assert {
        value.interaction
        for value
        in result.correspondences
    } == {
        identity(1),
        identity(2),
    }


def test_duplicate_same_interaction_is_not_ambiguity():
    first = region(1)
    duplicate = DomainInteractionRegion(
        first.interaction,
        first.fragment,
        DomainRegionProvenance(
            ("acc:x",),
            ("src:x",),
            ("dst:x",),
        ),
    )

    result = resolve_predicate(
        predicate(),
        DomainKnowledgeSnapshot(
            (
                first,
                duplicate,
            )
        ),
    )

    assert (
        result.status
        is ResolutionStatus.EXACT
    )
    assert (
        result.ambiguities
        == ()
    )
    assert (
        result.correspondences[
            0
        ].provenance.acc_references
        == (
            "acc:1",
            "acc:x",
        )
    )


def test_no_overlap_with_complete_knowledge_is_unresolved():
    result = resolve_predicate(
        predicate(),
        DomainKnowledgeSnapshot(
            (region(1, first=80),)
        ),
    )

    assert (
        result.status
        is ResolutionStatus.UNRESOLVED
    )
    assert (
        result.correspondences
        == ()
    )
    assert (
        result.remainder.fragments
    )
    assert result.remainder.complete


def test_incomplete_snapshot_is_unknown_and_keeps_known_match():
    gap = KnowledgeGap(
        "Resource Catalogue",
        "MissingRealization",
        ("resource:x",),
    )
    result = resolve_predicate(
        predicate(),
        DomainKnowledgeSnapshot(
            (region(1),),
            (gap,),
            False,
        ),
    )

    assert (
        result.status
        is ResolutionStatus.UNKNOWN
    )
    assert result.correspondences
    assert (
        not result.remainder.complete
    )
    assert (
        result.knowledge_gaps
        == (gap,)
    )


def test_protocol_any_is_unknown_without_catalogue_lookup():
    value = TechnicalAccessPredicate(
        AddressConstraint.any(),
        AddressConstraint.any(),
        ProtocolSelector.any(),
        PortConstraint.any(),
        PortConstraint.any(),
    )
    knowledge = MemoryKnowledge(
        DomainKnowledgeSnapshot(())
    )

    result = ResolveTechnicalAccess(
        domain_knowledge=knowledge
    ).execute(
        predicate=value,
        as_of=NOW,
    )

    assert (
        result.status
        is ResolutionStatus.UNKNOWN
    )
    assert knowledge.calls == []
    assert (
        not result.remainder.complete
    )
    assert (
        result.knowledge_gaps[
            0
        ].reason
        == "ProtocolAnyAlgebraUnsupported"
    )


def test_not_applicable_ports_do_not_overlap_numeric_ports():
    value = TechnicalAccessPredicate(
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
        ProtocolSelector.ip_protocol(1),
        PortConstraint.not_applicable(),
        PortConstraint.not_applicable(),
    )
    numeric = DomainInteractionRegion(
        identity(1),
        TechnicalRegionFragment(
            AddressRange(
                "10.0.0.1",
                "10.0.0.1",
            ),
            AddressRange(
                "10.0.0.2",
                "10.0.0.2",
            ),
            1,
            PortRegion.numeric(
                0,
                65535,
            ),
            PortRegion.numeric(
                0,
                65535,
            ),
        ),
        provenance(1),
    )

    result = resolve_predicate(
        value,
        DomainKnowledgeSnapshot(
            (numeric,)
        ),
    )

    assert (
        result.status
        is ResolutionStatus.UNRESOLVED
    )


def test_naive_as_of_is_rejected_before_catalogue_lookup():
    knowledge = MemoryKnowledge(
        DomainKnowledgeSnapshot(())
    )

    with pytest.raises(
        ResolutionInvariantError
    ):
        ResolveTechnicalAccess(
            domain_knowledge=knowledge
        ).execute(
            predicate=predicate(),
            as_of=datetime(
                2026,
                9,
                9,
                12,
            ),
        )

    assert knowledge.calls == []
