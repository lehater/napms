from datetime import datetime, timezone
from uuid import UUID

import pytest

from napms.contexts.network_enforcement_placement.application.select import (
    SelectEnforcement,
)
from napms.contexts.network_enforcement_placement.domain.model import (
    EffectiveWindow,
    EnforcementAttachment,
    ForwardingPath,
    InputProvenance,
    LogicalFirewall,
    LogicalFirewallCorrespondence,
    NoForwardingPath,
    PathAttachmentReference,
    PlacementInvariantError,
    PlacementKnowledgeSnapshot,
    Provenance,
    ProviderRealizationReference,
    SelectionStatus,
    TrafficRelation,
    TraversalPoint,
)


NOW = datetime(
    2026,
    9,
    9,
    12,
    tzinfo=timezone.utc,
)
START = datetime(
    2026,
    1,
    1,
    tzinfo=timezone.utc,
)
END = datetime(
    2027,
    1,
    1,
    tzinfo=timezone.utc,
)


def window(
    start=START,
    end=END,
):
    return EffectiveWindow(start, end)


def provenance(value):
    return Provenance((value,))


def provider(value):
    return ProviderRealizationReference(
        "lab",
        value,
    )


def point_ref(value):
    return PathAttachmentReference(
        "lab",
        value,
    )


def firewall(
    value,
    *,
    validity=None,
):
    return LogicalFirewall(
        UUID(int=value),
        validity or window(),
        provenance(f"lf:{value}"),
    )


def correspondence(
    value,
    provider_value,
    *,
    validity=None,
):
    return LogicalFirewallCorrespondence(
        UUID(int=value),
        provider(provider_value),
        validity or window(),
        provenance(
            f"corr:{value}:{provider_value}"
        ),
    )


def attachment(
    value,
    firewall_value,
    provider_value,
    point_value,
    *,
    validity=None,
):
    return EnforcementAttachment(
        UUID(int=value),
        UUID(int=firewall_value),
        provider(provider_value),
        point_ref(point_value),
        validity or window(),
        provenance(
            f"attachment:{value}"
        ),
    )


def traversal(
    provider_value,
    point_value,
):
    return TraversalPoint(
        provider(provider_value),
        point_ref(point_value),
        provenance(
            f"path:{provider_value}:{point_value}"
        ),
    )


def path(
    *points,
    validity=None,
):
    return ForwardingPath(
        "path:1",
        tuple(points),
        validity or window(),
        provenance("path:capture:1"),
    )


class MemoryKnowledge:
    def __init__(
        self,
        snapshot,
    ):
        self.snapshot = snapshot
        self.calls = []

    def load_for(
        self,
        *,
        relation,
        as_of,
    ):
        self.calls.append(
            (relation, as_of)
        )
        return self.snapshot


def execute(
    snapshot,
    *,
    relation=None,
):
    relation = relation or TrafficRelation(
        "10.0.0.1",
        "10.0.0.2",
    )
    return SelectEnforcement(
        placement_knowledge=(
            MemoryKnowledge(snapshot)
        )
    ).execute(
        relation=relation,
        as_of=NOW,
        input_provenance=(
            InputProvenance(
                ("domain:interaction:1",)
            )
        ),
    )


def test_selects_all_enforcement_points_in_path_order():
    snapshot = PlacementKnowledgeSnapshot(
        path=path(
            traversal(
                "device-b",
                "edge-b",
            ),
            traversal(
                "device-a",
                "edge-a",
            ),
        ),
        logical_firewalls=(
            firewall(2),
            firewall(1),
        ),
        correspondences=(
            correspondence(
                2,
                "device-a",
            ),
            correspondence(
                1,
                "device-b",
            ),
        ),
        attachments=(
            attachment(
                20,
                2,
                "device-a",
                "edge-a",
            ),
            attachment(
                10,
                1,
                "device-b",
                "edge-b",
            ),
        ),
    )

    result = execute(snapshot)

    assert (
        result.status
        is SelectionStatus.PLACED
    )
    assert result.complete
    assert [
        value.logical_firewall_id
        for value in result.placements
    ] == [
        UUID(int=1),
        UUID(int=2),
    ]
    assert [
        value.traversal_position
        for value in result.placements
    ] == [0, 1]
    assert (
        result
        .input_provenance
        .references
        == ("domain:interaction:1",)
    )
    assert (
        result
        .placements[0]
        .provenance
        .path_references
        == (
            "path:capture:1",
            "path:device-b:edge-b",
        )
    )


def test_complete_path_without_attachments_is_no_enforcement():
    result = execute(
        PlacementKnowledgeSnapshot(
            path=path(
                traversal(
                    "device-a",
                    "edge-a",
                )
            ),
        )
    )

    assert (
        result.status
        is SelectionStatus.NO_ENFORCEMENT
    )
    assert result.complete
    assert result.placements == ()


def test_positive_no_route_is_distinct_from_no_enforcement():
    result = execute(
        PlacementKnowledgeSnapshot(
            no_forwarding_path=NoForwardingPath(
                window(),
                provenance("no-route:1"),
            ),
        )
    )

    assert (
        result.status
        is SelectionStatus.NO_FORWARDING_PATH
    )
    assert result.complete
    assert result.path_reference is None


def test_missing_path_knowledge_is_unknown_not_no_route():
    result = execute(
        PlacementKnowledgeSnapshot(
            complete_for_pair=False,
            complete_for_attachments=False,
        )
    )

    assert (
        result.status
        is SelectionStatus.UNKNOWN
    )
    assert not result.complete
    assert {
        gap.reason
        for gap in result.knowledge_gaps
    } == {
        "ForwardingKnowledgeIncomplete"
    }


def test_relevant_attachment_without_correspondence_fails_closed():
    snapshot = PlacementKnowledgeSnapshot(
        path=path(
            traversal(
                "device-a",
                "edge-a",
            )
        ),
        logical_firewalls=(
            firewall(1),
        ),
        attachments=(
            attachment(
                10,
                1,
                "device-a",
                "edge-a",
            ),
        ),
    )

    result = execute(snapshot)

    assert (
        result.status
        is SelectionStatus.UNKNOWN
    )
    assert result.placements == ()
    assert {
        gap.reason
        for gap in result.knowledge_gaps
    } == {
        "MissingLogicalFirewallCorrespondence"
    }


def test_same_path_point_with_distinct_logical_firewalls_is_ambiguous():
    snapshot = PlacementKnowledgeSnapshot(
        path=path(
            traversal(
                "device-a",
                "edge-a",
            )
        ),
        logical_firewalls=(
            firewall(1),
            firewall(2),
        ),
        correspondences=(
            correspondence(
                1,
                "device-a",
            ),
            correspondence(
                2,
                "device-a",
            ),
        ),
        attachments=(
            attachment(
                10,
                1,
                "device-a",
                "edge-a",
            ),
            attachment(
                20,
                2,
                "device-a",
                "edge-a",
            ),
        ),
    )

    result = execute(snapshot)

    assert (
        result.status
        is SelectionStatus.AMBIGUOUS
    )
    assert result.complete
    assert {
        value.logical_firewall_id
        for value in result.placements
    } == {
        UUID(int=1),
        UUID(int=2),
    }
    assert (
        result
        .ambiguities[0]
        .logical_firewall_ids
        == (
            UUID(int=1),
            UUID(int=2),
        )
    )


def test_provider_realization_does_not_select_unrelated_logical_firewall():
    snapshot = PlacementKnowledgeSnapshot(
        path=path(
            traversal(
                "shared-device",
                "tenant-a",
            )
        ),
        logical_firewalls=(
            firewall(1),
            firewall(2),
        ),
        correspondences=(
            correspondence(
                1,
                "shared-device",
            ),
            correspondence(
                2,
                "shared-device",
            ),
        ),
        attachments=(
            attachment(
                10,
                1,
                "shared-device",
                "tenant-a",
            ),
            attachment(
                20,
                2,
                "shared-device",
                "tenant-b",
            ),
        ),
    )

    result = execute(snapshot)

    assert (
        result.status
        is SelectionStatus.PLACED
    )
    assert [
        value.logical_firewall_id
        for value in result.placements
    ] == [
        UUID(int=1)
    ]


def test_non_effective_path_is_unknown():
    expired = EffectiveWindow(
        datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        datetime(
            2025,
            2,
            1,
            tzinfo=timezone.utc,
        ),
    )
    result = execute(
        PlacementKnowledgeSnapshot(
            path=path(
                traversal(
                    "device-a",
                    "edge-a",
                ),
                validity=expired,
            ),
        )
    )

    assert (
        result.status
        is SelectionStatus.UNKNOWN
    )
    assert {
        gap.reason
        for gap in result.knowledge_gaps
    } == {
        "ForwardingPathNotEffective"
    }


def test_input_iteration_order_does_not_change_selection():
    forward = PlacementKnowledgeSnapshot(
        path=path(
            traversal(
                "device-a",
                "edge-a",
            ),
            traversal(
                "device-b",
                "edge-b",
            ),
        ),
        logical_firewalls=(
            firewall(1),
            firewall(2),
        ),
        correspondences=(
            correspondence(
                1,
                "device-a",
            ),
            correspondence(
                2,
                "device-b",
            ),
        ),
        attachments=(
            attachment(
                10,
                1,
                "device-a",
                "edge-a",
            ),
            attachment(
                20,
                2,
                "device-b",
                "edge-b",
            ),
        ),
    )
    reversed_facts = (
        PlacementKnowledgeSnapshot(
            path=forward.path,
            logical_firewalls=tuple(
                reversed(
                    forward.logical_firewalls
                )
            ),
            correspondences=tuple(
                reversed(
                    forward.correspondences
                )
            ),
            attachments=tuple(
                reversed(
                    forward.attachments
                )
            ),
        )
    )

    assert (
        execute(forward)
        == execute(reversed_facts)
    )


def test_naive_as_of_is_rejected_before_knowledge_lookup():
    knowledge = MemoryKnowledge(
        PlacementKnowledgeSnapshot(
            no_forwarding_path=NoForwardingPath(
                window(),
                provenance("no-route:1"),
            ),
        )
    )
    use_case = SelectEnforcement(
        placement_knowledge=knowledge
    )

    with pytest.raises(
        PlacementInvariantError
    ):
        use_case.execute(
            relation=TrafficRelation(
                "10.0.0.1",
                "10.0.0.2",
            ),
            as_of=datetime(
                2026,
                9,
                9,
                12,
            ),
        )

    assert knowledge.calls == []


def test_invalid_endpoint_pair_is_rejected():
    with pytest.raises(
        PlacementInvariantError
    ):
        TrafficRelation(
            "not-an-ip",
            "10.0.0.2",
        )
