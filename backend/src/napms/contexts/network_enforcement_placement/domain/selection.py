from datetime import datetime

from napms.contexts.network_enforcement_placement.domain.model import (
    EnforcementPlacement,
    EnforcementSelection,
    InputProvenance,
    KnowledgeGap,
    PlacementAmbiguity,
    PlacementKnowledgeSnapshot,
    PlacementProvenance,
    SelectionStatus,
    TrafficRelation,
    require_aware,
)


OWNER = "Network Enforcement Placement"


def _gap(
    reason: str,
    *references: str,
) -> KnowledgeGap:
    return KnowledgeGap(
        OWNER,
        reason,
        tuple(references),
    )


def _gap_key(
    value: KnowledgeGap,
) -> tuple[str, str, tuple[str, ...]]:
    return (
        value.owner,
        value.reason,
        value.references,
    )


def _placement_key(
    value: EnforcementPlacement,
) -> tuple[int, str, str]:
    return (
        value.traversal_position,
        str(value.logical_firewall_id),
        str(value.enforcement_attachment_id),
    )


def select_enforcement(
    relation: TrafficRelation,
    *,
    as_of: datetime,
    knowledge: PlacementKnowledgeSnapshot,
    input_provenance: InputProvenance = (
        InputProvenance()
    ),
) -> EnforcementSelection:
    require_aware(as_of)

    gaps = list(knowledge.knowledge_gaps)

    if knowledge.no_forwarding_path is not None:
        no_path = knowledge.no_forwarding_path
        if not knowledge.complete_for_pair:
            gaps.append(
                _gap(
                    "ForwardingKnowledgeIncomplete"
                )
            )
        if not no_path.validity.contains(as_of):
            gaps.append(
                _gap(
                    "NoForwardingPathNotEffective",
                    *no_path.provenance.references,
                )
            )
        if gaps:
            return EnforcementSelection(
                relation=relation,
                as_of=as_of,
                status=SelectionStatus.UNKNOWN,
                path_reference=None,
                placements=(),
                ambiguities=(),
                knowledge_gaps=tuple(
                    sorted(
                        set(gaps),
                        key=_gap_key,
                    )
                ),
                input_provenance=input_provenance,
                complete=False,
            )
        return EnforcementSelection(
            relation=relation,
            as_of=as_of,
            status=(
                SelectionStatus.NO_FORWARDING_PATH
            ),
            path_reference=None,
            placements=(),
            ambiguities=(),
            knowledge_gaps=(),
            input_provenance=input_provenance,
            complete=True,
        )

    path = knowledge.path
    if path is None:
        gaps.append(
            _gap(
                "ForwardingKnowledgeIncomplete"
            )
        )
        return EnforcementSelection(
            relation=relation,
            as_of=as_of,
            status=SelectionStatus.UNKNOWN,
            path_reference=None,
            placements=(),
            ambiguities=(),
            knowledge_gaps=tuple(
                sorted(
                    set(gaps),
                    key=_gap_key,
                )
            ),
            input_provenance=input_provenance,
            complete=False,
        )

    if not knowledge.complete_for_pair:
        gaps.append(
            _gap(
                "ForwardingKnowledgeIncomplete",
                path.path_reference,
            )
        )
    if not path.validity.contains(as_of):
        gaps.append(
            _gap(
                "ForwardingPathNotEffective",
                path.path_reference,
            )
        )
    if not knowledge.complete_for_attachments:
        gaps.append(
            _gap(
                "AttachmentKnowledgeIncomplete",
                path.path_reference,
            )
        )

    firewalls = {
        item.logical_firewall_id: item
        for item in knowledge.logical_firewalls
    }
    correspondences = {
        (
            item.logical_firewall_id,
            item.provider_realization,
        ): item
        for item in knowledge.correspondences
    }

    placements: list[
        EnforcementPlacement
    ] = []
    ambiguities: list[
        PlacementAmbiguity
    ] = []

    for position, point in enumerate(
        path.traversal_points
    ):
        point_placements: list[
            EnforcementPlacement
        ] = []
        candidates = [
            item
            for item in knowledge.attachments
            if (
                item.provider_realization
                == point.provider_realization
                and item.path_attachment
                == point.path_attachment
                and item.validity.contains(
                    as_of
                )
            )
        ]
        candidates.sort(
            key=lambda item: str(
                item.enforcement_attachment_id
            )
        )

        for attachment in candidates:
            firewall = firewalls.get(
                attachment.logical_firewall_id
            )
            if firewall is None:
                gaps.append(
                    _gap(
                        "MissingLogicalFirewall",
                        str(
                            attachment.logical_firewall_id
                        ),
                        str(
                            attachment.enforcement_attachment_id
                        ),
                    )
                )
                continue
            if not firewall.validity.contains(
                as_of
            ):
                gaps.append(
                    _gap(
                        "LogicalFirewallNotEffective",
                        str(
                            firewall.logical_firewall_id
                        ),
                        str(
                            attachment.enforcement_attachment_id
                        ),
                    )
                )
                continue

            correspondence = (
                correspondences.get(
                    (
                        attachment.logical_firewall_id,
                        attachment.provider_realization,
                    )
                )
            )
            if correspondence is None:
                gaps.append(
                    _gap(
                        "MissingLogicalFirewallCorrespondence",
                        str(
                            attachment.logical_firewall_id
                        ),
                        (
                            attachment
                            .provider_realization
                            .namespace
                        ),
                        (
                            attachment
                            .provider_realization
                            .reference
                        ),
                    )
                )
                continue
            if not (
                correspondence.validity.contains(
                    as_of
                )
            ):
                gaps.append(
                    _gap(
                        "LogicalFirewallCorrespondenceNotEffective",
                        str(
                            attachment.logical_firewall_id
                        ),
                        (
                            attachment
                            .provider_realization
                            .namespace
                        ),
                        (
                            attachment
                            .provider_realization
                            .reference
                        ),
                    )
                )
                continue

            placement = (
                EnforcementPlacement(
                    logical_firewall_id=(
                        attachment.logical_firewall_id
                    ),
                    enforcement_attachment_id=(
                        attachment
                        .enforcement_attachment_id
                    ),
                    provider_realization=(
                        point.provider_realization
                    ),
                    path_attachment=(
                        point.path_attachment
                    ),
                    traversal_position=position,
                    provenance=(
                        PlacementProvenance(
                            path_references=(
                                path
                                .provenance
                                .references
                                + point
                                .provenance
                                .references
                            ),
                            logical_firewall_references=(
                                firewall
                                .provenance
                                .references
                            ),
                            correspondence_references=(
                                correspondence
                                .provenance
                                .references
                            ),
                            attachment_references=(
                                attachment
                                .provenance
                                .references
                            ),
                        )
                    ),
                )
            )
            point_placements.append(
                placement
            )
            placements.append(placement)

        distinct_firewalls = tuple(
            sorted(
                {
                    item.logical_firewall_id
                    for item
                    in point_placements
                },
                key=str,
            )
        )
        if len(distinct_firewalls) > 1:
            ambiguities.append(
                PlacementAmbiguity(
                    traversal_position=(
                        position
                    ),
                    provider_realization=(
                        point
                        .provider_realization
                    ),
                    path_attachment=(
                        point.path_attachment
                    ),
                    logical_firewall_ids=(
                        distinct_firewalls
                    ),
                )
            )

    placements = sorted(
        placements,
        key=_placement_key,
    )
    ambiguities = sorted(
        ambiguities,
        key=lambda value: (
            value.traversal_position,
            value.provider_realization,
            value.path_attachment,
        ),
    )
    unique_gaps = tuple(
        sorted(
            set(gaps),
            key=_gap_key,
        )
    )

    if unique_gaps:
        status = SelectionStatus.UNKNOWN
        complete = False
    elif ambiguities:
        status = SelectionStatus.AMBIGUOUS
        complete = True
    elif placements:
        status = SelectionStatus.PLACED
        complete = True
    else:
        status = (
            SelectionStatus.NO_ENFORCEMENT
        )
        complete = True

    return EnforcementSelection(
        relation=relation,
        as_of=as_of,
        status=status,
        path_reference=(
            path.path_reference
        ),
        placements=tuple(placements),
        ambiguities=tuple(ambiguities),
        knowledge_gaps=unique_gaps,
        input_provenance=input_provenance,
        complete=complete,
    )
