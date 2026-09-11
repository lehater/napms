from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from napms.contexts.network_enforcement_placement.domain.model import (
    InputProvenance,
    KnowledgeGap,
    PathAttachmentReference,
    ProviderRealizationReference,
    TrafficRelation,
    require_aware,
)


def _non_empty_optional(value: str | None, *, field_name: str) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty when provided")
    return normalized


@dataclass(frozen=True, slots=True)
class NetworkContextCandidate:
    """One source-supported network/enforcement candidate for a traffic pair.

    Candidate membership means only that the provider realization is relevant to
    the queried traffic according to the contributing Network Context source. It
    does not assert traversal, ordering, authorization, or configured state.
    """

    provider_realization: ProviderRealizationReference
    provenance_references: tuple[str, ...]
    logical_firewall_id: UUID | None = None
    enforcement_attachment_id: UUID | None = None
    path_attachment: PathAttachmentReference | None = None
    source_relevance: str | None = None

    def __post_init__(self) -> None:
        provenance = tuple(
            sorted(
                {
                    item.strip()
                    for item in self.provenance_references
                    if item.strip()
                }
            )
        )
        if not provenance:
            raise ValueError("candidate provenance must contain at least one reference")
        object.__setattr__(self, "provenance_references", provenance)
        object.__setattr__(
            self,
            "source_relevance",
            _non_empty_optional(
                self.source_relevance,
                field_name="source_relevance",
            ),
        )


@dataclass(frozen=True, slots=True)
class NetworkContextSnapshot:
    """Unordered candidate-set knowledge for one traffic pair at one time.

    `complete_for_pair` says only whether the source claims the candidate list is
    complete for the represented pair/time. It does not turn candidates into a
    proven path and does not imply that every candidate is a true positive.
    """

    candidates: tuple[NetworkContextCandidate, ...] = ()
    complete_for_pair: bool = False
    knowledge_gaps: tuple[KnowledgeGap, ...] = ()

    def __post_init__(self) -> None:
        candidates = tuple(self.candidates)
        keys = [
            (
                item.provider_realization,
                item.logical_firewall_id,
                item.enforcement_attachment_id,
                item.path_attachment,
            )
            for item in candidates
        ]
        if len(keys) != len(set(keys)):
            raise ValueError("Network Context candidates must be unique")
        object.__setattr__(
            self,
            "candidates",
            tuple(
                sorted(
                    candidates,
                    key=lambda item: (
                        item.provider_realization.namespace,
                        item.provider_realization.reference,
                        str(item.logical_firewall_id or ""),
                        str(item.enforcement_attachment_id or ""),
                        (
                            item.path_attachment.namespace
                            if item.path_attachment is not None
                            else ""
                        ),
                        (
                            item.path_attachment.reference
                            if item.path_attachment is not None
                            else ""
                        ),
                    ),
                )
            ),
        )
        object.__setattr__(self, "knowledge_gaps", tuple(self.knowledge_gaps))


@dataclass(frozen=True, slots=True)
class NetworkContextResult:
    relation: TrafficRelation
    as_of: datetime
    candidates: tuple[NetworkContextCandidate, ...]
    complete_for_pair: bool
    knowledge_gaps: tuple[KnowledgeGap, ...]
    input_provenance: InputProvenance = InputProvenance()

    def __post_init__(self) -> None:
        require_aware(self.as_of)
        object.__setattr__(self, "candidates", tuple(self.candidates))
        object.__setattr__(self, "knowledge_gaps", tuple(self.knowledge_gaps))
