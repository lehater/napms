from datetime import datetime
from typing import Protocol

from napms.network_enforcement_placement.domain.model import (
    InputProvenance,
    TrafficRelation,
    require_aware,
)
from napms.network_enforcement_placement.domain.network_context import (
    NetworkContextResult,
    NetworkContextSnapshot,
)


class NetworkContextKnowledgePort(Protocol):
    def load_candidates_for(
        self,
        *,
        relation: TrafficRelation,
        as_of: datetime,
    ) -> NetworkContextSnapshot: ...


class ReadNetworkContext:
    """Read unordered Network Context candidates without inventing a path."""

    def __init__(self, *, knowledge: NetworkContextKnowledgePort) -> None:
        self._knowledge = knowledge

    def execute(
        self,
        relation: TrafficRelation,
        *,
        as_of: datetime,
        input_provenance: InputProvenance = InputProvenance(),
    ) -> NetworkContextResult:
        require_aware(as_of)
        snapshot = self._knowledge.load_candidates_for(
            relation=relation,
            as_of=as_of,
        )
        return NetworkContextResult(
            relation=relation,
            as_of=as_of,
            candidates=snapshot.candidates,
            complete_for_pair=snapshot.complete_for_pair,
            knowledge_gaps=snapshot.knowledge_gaps,
            input_provenance=input_provenance,
        )
