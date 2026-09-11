from uuid import UUID

from napms.contexts.network_enforcement_placement.domain.model import (
    KnowledgeGap,
    ProviderRealizationReference,
    TrafficRelation,
)
from napms.contexts.network_enforcement_placement.domain.network_context import (
    NetworkContextCandidate,
    NetworkContextSnapshot,
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
