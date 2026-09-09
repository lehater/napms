from datetime import datetime
from typing import Protocol

from napms.network_enforcement_placement.domain.model import (
    PlacementKnowledgeSnapshot,
    TrafficRelation,
)


class PlacementKnowledgePort(Protocol):
    def load_for(
        self,
        *,
        relation: TrafficRelation,
        as_of: datetime,
    ) -> PlacementKnowledgeSnapshot: ...
