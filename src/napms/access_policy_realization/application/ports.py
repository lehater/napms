from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID

from napms.access_policy_realization.domain.model import (
    DomainInteractionIdentity,
    DomainKnowledgeSnapshot,
    InputProvenance,
    KnowledgeGap,
    TechnicalAccessPredicate,
    require_aware,
)
from napms.access_policy_realization.domain.realization import (
    EnforcementPlacementProjection,
    ManagedReconciliationScope,
    PlacementStatus,
)


def _non_empty(
    value: str,
    *,
    field_name: str,
) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(
            f"{field_name} must be non-empty"
        )
    return normalized


@dataclass(frozen=True, slots=True)
class DesiredPolicyRowProjection:
    rule_reference: str
    interaction: DomainInteractionIdentity
    predicate: TechnicalAccessPredicate
    input_provenance: InputProvenance

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "rule_reference",
            _non_empty(
                self.rule_reference,
                field_name="rule reference",
            ),
        )


@dataclass(frozen=True, slots=True)
class DesiredPolicySnapshot:
    governance_scope: str
    as_of: datetime
    desired_interactions: tuple[
        DomainInteractionIdentity,
        ...,
    ]
    rows: tuple[DesiredPolicyRowProjection, ...]
    provenance_references: tuple[str, ...]
    complete: bool
    knowledge_gaps: tuple[KnowledgeGap, ...] = ()

    def __post_init__(self) -> None:
        require_aware(self.as_of)
        object.__setattr__(
            self,
            "governance_scope",
            _non_empty(
                self.governance_scope,
                field_name="governance scope",
            ),
        )
        object.__setattr__(
            self,
            "desired_interactions",
            tuple(
                sorted(
                    set(self.desired_interactions),
                    key=lambda item: (
                        str(
                            item.source_component_deployment_id
                        ),
                        str(
                            item.destination_component_deployment_id
                        ),
                        str(
                            item.dcs_contract_revision_id
                        ),
                    ),
                )
            ),
        )
        object.__setattr__(
            self,
            "rows",
            tuple(self.rows),
        )
        references = tuple(
            sorted(
                {
                    _non_empty(
                        item,
                        field_name=(
                            "desired policy provenance reference"
                        ),
                    )
                    for item
                    in self.provenance_references
                }
            )
        )
        if not references:
            raise ValueError(
                "desired policy snapshot requires provenance"
            )
        object.__setattr__(
            self,
            "provenance_references",
            references,
        )
        object.__setattr__(
            self,
            "knowledge_gaps",
            tuple(self.knowledge_gaps),
        )
        if self.complete and self.knowledge_gaps:
            raise ValueError(
                "complete desired snapshot cannot carry gaps"
            )
        if (
            not self.complete
            and not self.knowledge_gaps
        ):
            raise ValueError(
                "incomplete desired snapshot requires gaps"
            )


class DesiredPolicyPort(Protocol):
    def load_effective(
        self,
        *,
        governance_scope: str,
        as_of: datetime,
    ) -> DesiredPolicySnapshot: ...


@dataclass(frozen=True, slots=True)
class PlacementSelectionProjection:
    status: PlacementStatus
    placements: tuple[
        EnforcementPlacementProjection,
        ...,
    ] = ()
    provenance_references: tuple[str, ...] = ()
    knowledge_gaps: tuple[KnowledgeGap, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "placements",
            tuple(self.placements),
        )
        object.__setattr__(
            self,
            "provenance_references",
            tuple(
                sorted(
                    {
                        _non_empty(
                            item,
                            field_name=(
                                "placement provenance reference"
                            ),
                        )
                        for item
                        in self.provenance_references
                    }
                )
            ),
        )
        object.__setattr__(
            self,
            "knowledge_gaps",
            tuple(self.knowledge_gaps),
        )


class EnforcementPlacementPort(Protocol):
    def select_for(
        self,
        *,
        source_ip: str,
        destination_ip: str,
        as_of: datetime,
        input_provenance: InputProvenance,
    ) -> PlacementSelectionProjection: ...


class ConfiguredPolicySemantics(
    str,
    Enum,
):
    EFFECTIVE_PERMIT_SET = "EffectivePermitSet"


@dataclass(frozen=True, slots=True)
class ManagedReconciliationScopeContract:
    managed_scope: ManagedReconciliationScope
    evidence_source_namespace: str
    evidence_source_reference: str
    evidence_source_scope_reference: str
    semantics: ConfiguredPolicySemantics
    complete_for_managed_scope: bool
    provenance_reference: str

    def __post_init__(self) -> None:
        for field_name in (
            "evidence_source_namespace",
            "evidence_source_reference",
            "evidence_source_scope_reference",
            "provenance_reference",
        ):
            object.__setattr__(
                self,
                field_name,
                _non_empty(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )


@dataclass(frozen=True, slots=True)
class ConfiguredPermitProjection:
    predicate: TechnicalAccessPredicate
    input_provenance: InputProvenance


@dataclass(frozen=True, slots=True)
class ConfiguredEvidenceProjection:
    managed_scope: ManagedReconciliationScope
    as_of: datetime
    permits: tuple[
        ConfiguredPermitProjection,
        ...,
    ]
    evidence_references: tuple[str, ...]
    complete_for_managed_scope: bool
    knowledge_gaps: tuple[KnowledgeGap, ...] = ()

    def __post_init__(self) -> None:
        require_aware(self.as_of)
        object.__setattr__(
            self,
            "permits",
            tuple(self.permits),
        )
        references = tuple(
            sorted(
                {
                    _non_empty(
                        item,
                        field_name="evidence reference",
                    )
                    for item
                    in self.evidence_references
                }
            )
        )
        if not references:
            raise ValueError(
                "configured evidence projection requires references"
            )
        object.__setattr__(
            self,
            "evidence_references",
            references,
        )
        object.__setattr__(
            self,
            "knowledge_gaps",
            tuple(self.knowledge_gaps),
        )
        if (
            self.complete_for_managed_scope
            and self.knowledge_gaps
        ):
            raise ValueError(
                "complete configured projection cannot carry gaps"
            )


class ConfiguredEvidencePort(Protocol):
    def load_configured(
        self,
        *,
        evidence_set_id: UUID,
        contract: ManagedReconciliationScopeContract,
        as_of: datetime,
    ) -> ConfiguredEvidenceProjection: ...


class DomainKnowledgePort(Protocol):
    def load_for(
        self,
        *,
        predicate: TechnicalAccessPredicate,
        as_of: datetime,
    ) -> DomainKnowledgeSnapshot: ...
