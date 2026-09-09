from datetime import datetime

from napms.network_enforcement_placement.application.ports import (
    PlacementKnowledgePort,
)
from napms.network_enforcement_placement.domain.model import (
    EnforcementSelection,
    InputProvenance,
    TrafficRelation,
    require_aware,
)
from napms.network_enforcement_placement.domain.selection import (
    select_enforcement,
)


class SelectEnforcement:
    def __init__(
        self,
        *,
        placement_knowledge: PlacementKnowledgePort,
    ) -> None:
        self._placement_knowledge = (
            placement_knowledge
        )

    def execute(
        self,
        *,
        relation: TrafficRelation,
        as_of: datetime,
        input_provenance: InputProvenance = (
            InputProvenance()
        ),
    ) -> EnforcementSelection:
        require_aware(as_of)
        knowledge = (
            self._placement_knowledge.load_for(
                relation=relation,
                as_of=as_of,
            )
        )
        return select_enforcement(
            relation,
            as_of=as_of,
            knowledge=knowledge,
            input_provenance=(
                input_provenance
            ),
        )
