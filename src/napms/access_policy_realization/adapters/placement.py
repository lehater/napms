from napms.access_policy_realization.application.ports import (
    PlacementSelectionProjection,
)
from napms.access_policy_realization.domain.model import (
    InputProvenance,
    KnowledgeGap,
)
from napms.access_policy_realization.domain.realization import (
    EnforcementPlacementProjection,
    EnforcementTarget,
    PlacementStatus,
)
from napms.network_enforcement_placement.domain.model import (
    InputProvenance as NepInputProvenance,
    SelectionStatus,
    TrafficRelation,
)


_STATUS = {
    SelectionStatus.PLACED: (
        PlacementStatus.PLACED
    ),
    SelectionStatus.NO_ENFORCEMENT: (
        PlacementStatus.NO_ENFORCEMENT
    ),
    SelectionStatus.NO_FORWARDING_PATH: (
        PlacementStatus.NO_FORWARDING_PATH
    ),
    SelectionStatus.AMBIGUOUS: (
        PlacementStatus.AMBIGUOUS
    ),
    SelectionStatus.UNKNOWN: (
        PlacementStatus.UNKNOWN
    ),
}


def _placement_references(
    selection,
    placement,
) -> tuple[str, ...]:
    references = [
        (
            "nep-logical-firewall:"
            + str(
                placement.logical_firewall_id
            )
        ),
        (
            "nep-enforcement-attachment:"
            + str(
                placement.enforcement_attachment_id
            )
        ),
        (
            "nep-provider-realization:"
            + placement.provider_realization.namespace
            + ":"
            + placement.provider_realization.reference
        ),
        (
            "nep-path-attachment:"
            + placement.path_attachment.namespace
            + ":"
            + placement.path_attachment.reference
        ),
        (
            "nep-traversal-position:"
            + str(
                placement.traversal_position
            )
        ),
    ]
    if selection.path_reference:
        references.append(
            "nep-path:"
            + selection.path_reference
        )
    provenance = placement.provenance
    references.extend(
        "nep-path-provenance:" + item
        for item in provenance.path_references
    )
    references.extend(
        "nep-firewall-provenance:" + item
        for item
        in provenance.logical_firewall_references
    )
    references.extend(
        "nep-correspondence-provenance:"
        + item
        for item
        in provenance.correspondence_references
    )
    references.extend(
        "nep-attachment-provenance:" + item
        for item
        in provenance.attachment_references
    )
    return tuple(references)


class NetworkEnforcementPlacementProjectionAdapter:
    def __init__(
        self,
        *,
        select_enforcement,
    ) -> None:
        self._select_enforcement = (
            select_enforcement
        )

    def select_for(
        self,
        *,
        source_ip: str,
        destination_ip: str,
        as_of,
        input_provenance: InputProvenance,
    ) -> PlacementSelectionProjection:
        selection = (
            self._select_enforcement.execute(
                relation=TrafficRelation(
                    source_ip,
                    destination_ip,
                ),
                as_of=as_of,
                input_provenance=(
                    NepInputProvenance(
                        input_provenance.references
                    )
                ),
            )
        )
        placements = tuple(
            EnforcementPlacementProjection(
                target=EnforcementTarget(
                    placement.logical_firewall_id,
                    placement.enforcement_attachment_id,
                ),
                provenance_references=(
                    _placement_references(
                        selection,
                        placement,
                    )
                ),
            )
            for placement
            in selection.placements
        )
        references = list(
            (
                "nep-input:" + item
                for item
                in selection.input_provenance.references
            )
        )
        if selection.path_reference:
            references.append(
                "nep-path:"
                + selection.path_reference
            )
        for ambiguity in (
            selection.ambiguities
        ):
            references.extend(
                (
                    "nep-ambiguity-position:"
                    + str(
                        ambiguity.traversal_position
                    ),
                    (
                        "nep-ambiguity-provider:"
                        + ambiguity.provider_realization.namespace
                        + ":"
                        + ambiguity.provider_realization.reference
                    ),
                    (
                        "nep-ambiguity-path-attachment:"
                        + ambiguity.path_attachment.namespace
                        + ":"
                        + ambiguity.path_attachment.reference
                    ),
                )
            )
            references.extend(
                "nep-ambiguity-firewall:"
                + str(value)
                for value
                in ambiguity.logical_firewall_ids
            )

        return PlacementSelectionProjection(
            status=_STATUS[
                selection.status
            ],
            placements=placements,
            provenance_references=tuple(
                references
            ),
            knowledge_gaps=tuple(
                KnowledgeGap(
                    owner=item.owner,
                    reason=item.reason,
                    references=item.references,
                )
                for item
                in selection.knowledge_gaps
            ),
        )
