from uuid import UUID

from napms.contexts.network_enforcement_placement.application.network_context import ReadNetworkContext
from napms.contexts.network_enforcement_placement.domain.model import (
    KnowledgeGap,
    ProviderRealizationReference,
    TrafficRelation,
)
from napms.contexts.network_enforcement_placement.domain.network_context import (
    NetworkContextCandidate,
    NetworkContextSnapshot,
)
from napms.traffic_analysis.application.model import (
    NetworkCandidateView,
    NetworkContextView,
    TrafficAnalysisQuery,
)


class LocalDemoNetworkContextKnowledgeAdapter:
    """Local fixture source; returns candidates only and never a synthetic path."""

    def load_candidates_for(self, *, relation: TrafficRelation, as_of):
        if relation != TrafficRelation("10.10.10.10", "10.20.20.20"):
            return NetworkContextSnapshot(
                complete_for_pair=False,
                knowledge_gaps=(
                    KnowledgeGap(
                        owner="local-demo-network-context",
                        reason="NoFixtureForPair",
                    ),
                ),
            )
        return NetworkContextSnapshot(
            candidates=(
                NetworkContextCandidate(
                    provider_realization=ProviderRealizationReference(
                        "local-demo-firewall", "fw-demo-edge"
                    ),
                    logical_firewall_id=UUID("00000000-0000-0000-0000-000000000201"),
                    enforcement_attachment_id=UUID("00000000-0000-0000-0000-000000000211"),
                    provenance_references=("local-demo:network-context:edge",),
                    source_relevance="Strong",
                ),
                NetworkContextCandidate(
                    provider_realization=ProviderRealizationReference(
                        "local-demo-firewall", "fw-demo-core"
                    ),
                    logical_firewall_id=UUID("00000000-0000-0000-0000-000000000202"),
                    provenance_references=("local-demo:network-context:core",),
                    source_relevance="Possible",
                ),
                NetworkContextCandidate(
                    provider_realization=ProviderRealizationReference(
                        "local-demo-firewall", "fw-demo-legacy"
                    ),
                    provenance_references=("local-demo:network-context:legacy",),
                    source_relevance="Possible",
                ),
            ),
            complete_for_pair=False,
            knowledge_gaps=(
                KnowledgeGap(
                    owner="local-demo-network-context",
                    reason="CandidateSetMayContainFalsePositives",
                ),
            ),
        )


class NetworkEnforcementPlacementTrafficAnalysisAdapter:
    def __init__(self, *, reader: ReadNetworkContext) -> None:
        self._reader = reader

    def read(self, *, query: TrafficAnalysisQuery) -> NetworkContextView:
        result = self._reader.execute(
            TrafficRelation(query.source_address, query.destination_address),
            as_of=query.as_of,
        )
        return NetworkContextView(
            candidates=tuple(
                NetworkCandidateView(
                    provider_namespace=item.provider_realization.namespace,
                    device_reference=item.provider_realization.reference,
                    logical_firewall_reference=(
                        str(item.logical_firewall_id)
                        if item.logical_firewall_id is not None
                        else None
                    ),
                    enforcement_attachment_reference=(
                        str(item.enforcement_attachment_id)
                        if item.enforcement_attachment_id is not None
                        else None
                    ),
                    path_attachment_reference=(
                        f"{item.path_attachment.namespace}:{item.path_attachment.reference}"
                        if item.path_attachment is not None
                        else None
                    ),
                    source_relevance=item.source_relevance,
                    provenance_references=item.provenance_references,
                )
                for item in result.candidates
            ),
            complete_for_pair=result.complete_for_pair,
            knowledge_gaps=tuple(
                f"{item.owner}: {item.reason}" for item in result.knowledge_gaps
            ),
        )
