from datetime import datetime, timezone
from uuid import UUID

import pytest

from napms.network_enforcement_placement.application.network_context import (
    ReadNetworkContext,
)
from napms.network_enforcement_placement.domain.model import (
    KnowledgeGap,
    ProviderRealizationReference,
    TrafficRelation,
)
from napms.network_enforcement_placement.domain.network_context import (
    NetworkContextCandidate,
    NetworkContextSnapshot,
)


NOW = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)


class StubKnowledge:
    def __init__(self, snapshot: NetworkContextSnapshot) -> None:
        self.snapshot = snapshot

    def load_candidates_for(self, *, relation: TrafficRelation, as_of: datetime):
        assert relation == TrafficRelation("10.20.1.15", "10.50.8.12")
        assert as_of == NOW
        return self.snapshot


def _candidate(reference: str, relevance: str | None = None):
    return NetworkContextCandidate(
        provider_realization=ProviderRealizationReference("device", reference),
        logical_firewall_id=UUID("00000000-0000-0000-0000-000000000001"),
        provenance_references=(f"source:{reference}",),
        source_relevance=relevance,
    )


def test_candidate_set_is_canonical_but_not_path_ordered() -> None:
    snapshot = NetworkContextSnapshot(
        candidates=(
            _candidate("fw-z", "Possible"),
            _candidate("fw-a", "Strong"),
        ),
        complete_for_pair=False,
        knowledge_gaps=(
            KnowledgeGap(
                "Network Enforcement Placement",
                "CandidateSetMayContainFalsePositives",
            ),
        ),
    )

    result = ReadNetworkContext(knowledge=StubKnowledge(snapshot)).execute(
        TrafficRelation("10.20.1.15", "10.50.8.12"),
        as_of=NOW,
    )

    assert [item.provider_realization.reference for item in result.candidates] == [
        "fw-a",
        "fw-z",
    ]
    assert result.complete_for_pair is False
    assert result.candidates[0].source_relevance == "Strong"
    assert result.knowledge_gaps[0].reason == "CandidateSetMayContainFalsePositives"


def test_empty_incomplete_candidate_set_does_not_mean_no_enforcement() -> None:
    result = ReadNetworkContext(
        knowledge=StubKnowledge(
            NetworkContextSnapshot(
                candidates=(),
                complete_for_pair=False,
                knowledge_gaps=(
                    KnowledgeGap(
                        "Network Enforcement Placement",
                        "CandidateKnowledgeIncomplete",
                    ),
                ),
            )
        )
    ).execute(
        TrafficRelation("10.20.1.15", "10.50.8.12"),
        as_of=NOW,
    )

    assert result.candidates == ()
    assert result.complete_for_pair is False
    assert result.knowledge_gaps


def test_candidate_requires_attributable_provenance() -> None:
    with pytest.raises(ValueError, match="candidate provenance"):
        NetworkContextCandidate(
            provider_realization=ProviderRealizationReference("device", "fw-a"),
            provenance_references=(),
        )
