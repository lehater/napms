from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from napms.access_policy_realization.domain.algebra import (
    expand_predicate,
    fragment_sort_key,
    intersect_fragments,
    subtract_many,
)
from napms.access_policy_realization.domain.model import (
    DomainAccessResolution,
    DomainInteractionIdentity,
    KnowledgeGap,
    ResolutionInvariantError,
    ResolutionStatus,
    TechnicalRegionFragment,
    require_aware,
)


class RealizationInvariantError(ResolutionInvariantError):
    """Raised when I20 realization state is structurally invalid."""


def _non_empty(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise RealizationInvariantError(
            f"{field_name} must be non-empty"
        )
    return normalized


def _references(
    values: tuple[str, ...],
    *,
    field_name: str,
    required: bool = False,
) -> tuple[str, ...]:
    normalized = tuple(
        sorted(
            {
                _non_empty(
                    value,
                    field_name=field_name,
                )
                for value in values
            }
        )
    )
    if required and not normalized:
        raise RealizationInvariantError(
            f"{field_name} must not be empty"
        )
    return normalized


@dataclass(frozen=True, slots=True)
class EnforcementTarget:
    logical_firewall_id: UUID
    enforcement_attachment_id: UUID


@dataclass(frozen=True, slots=True)
class EnforcementPlacementProjection:
    target: EnforcementTarget
    provenance_references: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provenance_references",
            _references(
                self.provenance_references,
                field_name="placement provenance reference",
                required=True,
            ),
        )


class PlacementStatus(str, Enum):
    PLACED = "Placed"
    NO_ENFORCEMENT = "NoEnforcement"
    NO_FORWARDING_PATH = "NoForwardingPath"
    AMBIGUOUS = "Ambiguous"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class DesiredPolicyContribution:
    rule_reference: str
    interaction: DomainInteractionIdentity
    fragment: TechnicalRegionFragment
    resolution: DomainAccessResolution
    placement_status: PlacementStatus
    placements: tuple[EnforcementPlacementProjection, ...] = ()
    placement_provenance_references: tuple[str, ...] = ()
    knowledge_gaps: tuple[KnowledgeGap, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "rule_reference",
            _non_empty(
                self.rule_reference,
                field_name="rule reference",
            ),
        )
        object.__setattr__(
            self,
            "placements",
            tuple(self.placements),
        )
        object.__setattr__(
            self,
            "placement_provenance_references",
            _references(
                self.placement_provenance_references,
                field_name="placement provenance reference",
            ),
        )
        object.__setattr__(
            self,
            "knowledge_gaps",
            tuple(self.knowledge_gaps),
        )
        if (
            self.placement_status is PlacementStatus.PLACED
            and not self.placements
        ):
            raise RealizationInvariantError(
                "Placed contribution requires at least one placement"
            )
        if self.placement_status in (
            PlacementStatus.NO_ENFORCEMENT,
            PlacementStatus.NO_FORWARDING_PATH,
        ) and self.placements:
            raise RealizationInvariantError(
                "terminal no-placement contribution cannot carry placements"
            )
        if self.placement_status is PlacementStatus.AMBIGUOUS:
            targets = {
                item.target
                for item in self.placements
            }
            if len(targets) < 2:
                raise RealizationInvariantError(
                    "Ambiguous placement requires at least two targets"
                )


@dataclass(frozen=True, slots=True)
class DesiredEnforcementIntent:
    target: EnforcementTarget
    fragment: TechnicalRegionFragment
    rule_references: tuple[str, ...]
    interactions: tuple[DomainInteractionIdentity, ...]
    placement_provenance_references: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "rule_references",
            _references(
                self.rule_references,
                field_name="rule reference",
                required=True,
            ),
        )
        interactions = tuple(
            sorted(
                set(self.interactions),
                key=lambda item: (
                    str(item.source_component_deployment_id),
                    str(item.destination_component_deployment_id),
                    str(item.dcs_contract_revision_id),
                ),
            )
        )
        if not interactions:
            raise RealizationInvariantError(
                "desired intent requires interaction provenance"
            )
        object.__setattr__(
            self,
            "interactions",
            interactions,
        )
        object.__setattr__(
            self,
            "placement_provenance_references",
            _references(
                self.placement_provenance_references,
                field_name="placement provenance reference",
                required=True,
            ),
        )


class DesiredDerivationStatus(str, Enum):
    DERIVED = "Derived"
    AMBIGUOUS = "Ambiguous"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class DesiredEnforcementPolicy:
    governance_scope: str
    as_of: datetime
    desired_interactions: tuple[DomainInteractionIdentity, ...]
    status: DesiredDerivationStatus
    intents: tuple[DesiredEnforcementIntent, ...]
    no_enforcement_rule_references: tuple[str, ...] = ()
    no_forwarding_path_rule_references: tuple[str, ...] = ()
    ambiguous_rule_references: tuple[str, ...] = ()
    unknown_rule_references: tuple[str, ...] = ()
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
                        str(item.source_component_deployment_id),
                        str(item.destination_component_deployment_id),
                        str(item.dcs_contract_revision_id),
                    ),
                )
            ),
        )
        object.__setattr__(
            self,
            "intents",
            tuple(self.intents),
        )
        for field_name in (
            "no_enforcement_rule_references",
            "no_forwarding_path_rule_references",
            "ambiguous_rule_references",
            "unknown_rule_references",
        ):
            object.__setattr__(
                self,
                field_name,
                _references(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )
        object.__setattr__(
            self,
            "knowledge_gaps",
            tuple(self.knowledge_gaps),
        )
        if (
            self.status is DesiredDerivationStatus.DERIVED
            and (
                self.ambiguous_rule_references
                or self.unknown_rule_references
                or self.knowledge_gaps
            )
        ):
            raise RealizationInvariantError(
                "Derived policy cannot carry ambiguity/unknown diagnostics"
            )

    def regions_for(
        self,
        target: EnforcementTarget,
    ) -> tuple[TechnicalRegionFragment, ...]:
        return canonical_union(
            tuple(
                item.fragment
                for item in self.intents
                if item.target == target
            )
        )

    def interactions_for(
        self,
        target: EnforcementTarget,
    ) -> tuple[DomainInteractionIdentity, ...]:
        return tuple(
            sorted(
                {
                    interaction
                    for item in self.intents
                    if item.target == target
                    for interaction in item.interactions
                },
                key=lambda item: (
                    str(item.source_component_deployment_id),
                    str(item.destination_component_deployment_id),
                    str(item.dcs_contract_revision_id),
                ),
            )
        )


@dataclass(frozen=True, slots=True)
class ManagedReconciliationScope:
    policy_governance_scope: str
    target: EnforcementTarget
    source_contract_reference: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "policy_governance_scope",
            _non_empty(
                self.policy_governance_scope,
                field_name="policy governance scope",
            ),
        )
        object.__setattr__(
            self,
            "source_contract_reference",
            _non_empty(
                self.source_contract_reference,
                field_name="source contract reference",
            ),
        )


@dataclass(frozen=True, slots=True)
class ConfiguredEnforcementSnapshot:
    managed_scope: ManagedReconciliationScope
    as_of: datetime
    permit_regions: tuple[TechnicalRegionFragment, ...]
    domain_resolutions: tuple[DomainAccessResolution, ...]
    evidence_references: tuple[str, ...]
    complete_for_managed_scope: bool
    knowledge_gaps: tuple[KnowledgeGap, ...] = ()

    def __post_init__(self) -> None:
        require_aware(self.as_of)
        object.__setattr__(
            self,
            "permit_regions",
            canonical_union(
                tuple(self.permit_regions)
            ),
        )
        object.__setattr__(
            self,
            "domain_resolutions",
            tuple(self.domain_resolutions),
        )
        object.__setattr__(
            self,
            "evidence_references",
            _references(
                self.evidence_references,
                field_name="evidence reference",
                required=True,
            ),
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
            raise RealizationInvariantError(
                "complete configured snapshot cannot carry knowledge gaps"
            )
        if self.complete_for_managed_scope:
            attributed_regions: list[
                TechnicalRegionFragment
            ] = []
            for resolution in self.domain_resolutions:
                attributed_regions.extend(
                    expand_predicate(
                        resolution.predicate
                    )
                )
            if canonical_union(
                tuple(attributed_regions)
            ) != self.permit_regions:
                raise RealizationInvariantError(
                    "complete configured snapshot requires "
                    "I18 attribution for every permit region"
                )


class ReconciliationStatus(str, Enum):
    SATISFIED = "Satisfied"
    DRIFT = "Drift"
    AMBIGUOUS = "Ambiguous"
    UNKNOWN = "Unknown"


class RequiredSemanticChange(str, Enum):
    NO_OP = "No-op"
    ADD = "Add"
    REMOVE = "Remove"
    REPLACE = "Replace"


@dataclass(frozen=True, slots=True)
class PolicyReconciliation:
    managed_scope: ManagedReconciliationScope
    as_of: datetime
    status: ReconciliationStatus
    common: tuple[TechnicalRegionFragment, ...]
    missing: tuple[TechnicalRegionFragment, ...]
    extra: tuple[TechnicalRegionFragment, ...]
    required_change: RequiredSemanticChange | None
    complete: bool
    knowledge_gaps: tuple[KnowledgeGap, ...] = ()

    def __post_init__(self) -> None:
        require_aware(self.as_of)
        for field_name in ("common", "missing", "extra"):
            object.__setattr__(
                self,
                field_name,
                canonical_union(
                    tuple(getattr(self, field_name))
                ),
            )
        object.__setattr__(
            self,
            "knowledge_gaps",
            tuple(self.knowledge_gaps),
        )
        if self.complete != (
            self.status
            in (
                ReconciliationStatus.SATISFIED,
                ReconciliationStatus.DRIFT,
            )
        ):
            raise RealizationInvariantError(
                "complete flag must match confident reconciliation status"
            )
        if self.complete and self.required_change is None:
            raise RealizationInvariantError(
                "complete reconciliation requires semantic change"
            )
        if not self.complete and self.required_change is not None:
            raise RealizationInvariantError(
                "degraded reconciliation cannot claim semantic change"
            )


def canonical_union(
    fragments: tuple[TechnicalRegionFragment, ...],
) -> tuple[TechnicalRegionFragment, ...]:
    result: list[TechnicalRegionFragment] = []
    for fragment in tuple(
        sorted(
            set(fragments),
            key=fragment_sort_key,
        )
    ):
        uncovered = (fragment,)
        if result:
            uncovered = subtract_many(
                uncovered,
                tuple(result),
            )
        result.extend(uncovered)
    return tuple(
        sorted(
            set(result),
            key=fragment_sort_key,
        )
    )


def intersect_many(
    left: tuple[TechnicalRegionFragment, ...],
    right: tuple[TechnicalRegionFragment, ...],
) -> tuple[TechnicalRegionFragment, ...]:
    intersections = []
    for left_fragment in canonical_union(left):
        for right_fragment in canonical_union(right):
            overlap = intersect_fragments(
                left_fragment,
                right_fragment,
            )
            if overlap is not None:
                intersections.append(overlap)
    return canonical_union(
        tuple(intersections)
    )


def _gap(
    reason: str,
    *references: str,
) -> KnowledgeGap:
    return KnowledgeGap(
        owner="Access Policy Realization",
        reason=reason,
        references=tuple(references),
    )


def _merge_intents(
    intents: list[DesiredEnforcementIntent],
) -> tuple[DesiredEnforcementIntent, ...]:
    merged: dict[
        tuple[EnforcementTarget, TechnicalRegionFragment],
        DesiredEnforcementIntent,
    ] = {}
    for intent in intents:
        key = (
            intent.target,
            intent.fragment,
        )
        existing = merged.get(key)
        if existing is None:
            merged[key] = intent
            continue
        merged[key] = DesiredEnforcementIntent(
            target=intent.target,
            fragment=intent.fragment,
            rule_references=(
                existing.rule_references
                + intent.rule_references
            ),
            interactions=(
                existing.interactions
                + intent.interactions
            ),
            placement_provenance_references=(
                existing.placement_provenance_references
                + intent.placement_provenance_references
            ),
        )
    return tuple(
        sorted(
            merged.values(),
            key=lambda item: (
                str(item.target.logical_firewall_id),
                str(item.target.enforcement_attachment_id),
                fragment_sort_key(item.fragment),
            ),
        )
    )


def _desired_resolution_disposition(
    contribution: DesiredPolicyContribution,
    desired_interactions: set[DomainInteractionIdentity],
) -> DesiredDerivationStatus:
    resolution = contribution.resolution
    if resolution.status is ResolutionStatus.UNKNOWN:
        return DesiredDerivationStatus.UNKNOWN
    if (
        not resolution.remainder.complete
        or resolution.remainder.fragments
        or resolution.status
        in (
            ResolutionStatus.PARTIAL,
            ResolutionStatus.UNRESOLVED,
        )
    ):
        return DesiredDerivationStatus.UNKNOWN

    resolved_interactions = {
        item.interaction
        for item in resolution.correspondences
    }
    if contribution.interaction not in resolved_interactions:
        return DesiredDerivationStatus.UNKNOWN
    if (
        resolved_interactions
        - desired_interactions
    ):
        return DesiredDerivationStatus.AMBIGUOUS
    return DesiredDerivationStatus.DERIVED


def derive_desired_enforcement_policy(
    *,
    governance_scope: str,
    as_of: datetime,
    desired_interactions: tuple[DomainInteractionIdentity, ...],
    contributions: tuple[DesiredPolicyContribution, ...],
) -> DesiredEnforcementPolicy:
    require_aware(as_of)
    governance_scope = _non_empty(
        governance_scope,
        field_name="governance scope",
    )
    desired_set = set(desired_interactions)
    intents: list[DesiredEnforcementIntent] = []
    no_enforcement: list[str] = []
    no_forwarding_path: list[str] = []
    ambiguous: list[str] = []
    unknown: list[str] = []
    gaps: list[KnowledgeGap] = []

    for contribution in contributions:
        if contribution.resolution.as_of != as_of:
            unknown.append(
                contribution.rule_reference
            )
            gaps.append(
                _gap(
                    "DesiredResolutionTimeMismatch",
                    contribution.rule_reference,
                )
            )
            continue
        if contribution.interaction not in desired_set:
            unknown.append(
                contribution.rule_reference
            )
            gaps.append(
                _gap(
                    "DesiredInteractionNotInEffectivePolicy",
                    contribution.rule_reference,
                )
            )
            continue
        if expand_predicate(
            contribution.resolution.predicate
        ) != (contribution.fragment,):
            raise RealizationInvariantError(
                "first-slice desired contribution requires "
                "one exact resolution fragment"
            )

        disposition = _desired_resolution_disposition(
            contribution,
            desired_set,
        )
        if disposition is DesiredDerivationStatus.UNKNOWN:
            unknown.append(
                contribution.rule_reference
            )
            gaps.extend(
                contribution.resolution.knowledge_gaps
            )
            if not contribution.resolution.knowledge_gaps:
                gaps.append(
                    _gap(
                        "DesiredDomainMeaningIncomplete",
                        contribution.rule_reference,
                    )
                )
            continue
        if disposition is DesiredDerivationStatus.AMBIGUOUS:
            ambiguous.append(
                contribution.rule_reference
            )
            continue

        if contribution.placement_status is PlacementStatus.UNKNOWN:
            unknown.append(
                contribution.rule_reference
            )
            gaps.extend(
                contribution.knowledge_gaps
            )
            if not contribution.knowledge_gaps:
                gaps.append(
                    _gap(
                        "PlacementKnowledgeIncomplete",
                        contribution.rule_reference,
                    )
                )
            continue
        if contribution.placement_status is PlacementStatus.AMBIGUOUS:
            ambiguous.append(
                contribution.rule_reference
            )
            continue
        if (
            contribution.placement_status
            is PlacementStatus.NO_ENFORCEMENT
        ):
            no_enforcement.append(
                contribution.rule_reference
            )
            continue
        if (
            contribution.placement_status
            is PlacementStatus.NO_FORWARDING_PATH
        ):
            no_forwarding_path.append(
                contribution.rule_reference
            )
            continue

        for placement in contribution.placements:
            intents.append(
                DesiredEnforcementIntent(
                    target=placement.target,
                    fragment=contribution.fragment,
                    rule_references=(
                        contribution.rule_reference,
                    ),
                    interactions=(
                        contribution.interaction,
                    ),
                    placement_provenance_references=(
                        placement.provenance_references
                        + contribution.placement_provenance_references
                    ),
                )
            )

    if unknown:
        status = DesiredDerivationStatus.UNKNOWN
    elif ambiguous:
        status = DesiredDerivationStatus.AMBIGUOUS
    else:
        status = DesiredDerivationStatus.DERIVED

    return DesiredEnforcementPolicy(
        governance_scope=governance_scope,
        as_of=as_of,
        desired_interactions=desired_interactions,
        status=status,
        intents=_merge_intents(intents),
        no_enforcement_rule_references=tuple(no_enforcement),
        no_forwarding_path_rule_references=tuple(no_forwarding_path),
        ambiguous_rule_references=tuple(ambiguous),
        unknown_rule_references=tuple(unknown),
        knowledge_gaps=tuple(gaps),
    )


def _configured_ambiguity_is_material(
    resolution: DomainAccessResolution,
    desired_interactions: set[DomainInteractionIdentity],
) -> bool:
    return any(
        any(
            interaction not in desired_interactions
            for interaction in witness.interactions
        )
        for witness in resolution.ambiguities
    )


def _degraded_reconciliation(
    *,
    managed_scope: ManagedReconciliationScope,
    as_of: datetime,
    status: ReconciliationStatus,
    gaps: tuple[KnowledgeGap, ...] = (),
) -> PolicyReconciliation:
    return PolicyReconciliation(
        managed_scope=managed_scope,
        as_of=as_of,
        status=status,
        common=(),
        missing=(),
        extra=(),
        required_change=None,
        complete=False,
        knowledge_gaps=gaps,
    )


def reconcile_enforcement_policy(
    *,
    desired: DesiredEnforcementPolicy,
    configured: ConfiguredEnforcementSnapshot,
) -> PolicyReconciliation:
    scope = configured.managed_scope
    if (
        scope.policy_governance_scope
        != desired.governance_scope
        or configured.as_of != desired.as_of
    ):
        return _degraded_reconciliation(
            managed_scope=scope,
            as_of=configured.as_of,
            status=ReconciliationStatus.UNKNOWN,
            gaps=(
                _gap(
                    "ManagedScopeOrTimeMismatch",
                    scope.source_contract_reference,
                ),
            ),
        )

    if desired.status is DesiredDerivationStatus.UNKNOWN:
        return _degraded_reconciliation(
            managed_scope=scope,
            as_of=desired.as_of,
            status=ReconciliationStatus.UNKNOWN,
            gaps=desired.knowledge_gaps,
        )
    if desired.status is DesiredDerivationStatus.AMBIGUOUS:
        return _degraded_reconciliation(
            managed_scope=scope,
            as_of=desired.as_of,
            status=ReconciliationStatus.AMBIGUOUS,
        )
    if (
        not configured.complete_for_managed_scope
        or configured.knowledge_gaps
    ):
        gaps = configured.knowledge_gaps or (
            _gap(
                "ConfiguredManagedScopeIncomplete",
                scope.source_contract_reference,
            ),
        )
        return _degraded_reconciliation(
            managed_scope=scope,
            as_of=desired.as_of,
            status=ReconciliationStatus.UNKNOWN,
            gaps=tuple(gaps),
        )

    desired_interactions = set(
        desired.interactions_for(
            scope.target
        )
    )
    for resolution in configured.domain_resolutions:
        if resolution.as_of != desired.as_of:
            return _degraded_reconciliation(
                managed_scope=scope,
                as_of=desired.as_of,
                status=ReconciliationStatus.UNKNOWN,
                gaps=(
                    _gap(
                        "ConfiguredResolutionTimeMismatch",
                    ),
                ),
            )
        if resolution.status is ResolutionStatus.UNKNOWN:
            return _degraded_reconciliation(
                managed_scope=scope,
                as_of=desired.as_of,
                status=ReconciliationStatus.UNKNOWN,
                gaps=resolution.knowledge_gaps or (
                    _gap(
                        "ConfiguredDomainMeaningIncomplete",
                    ),
                ),
            )
        if _configured_ambiguity_is_material(
            resolution,
            desired_interactions,
        ):
            return _degraded_reconciliation(
                managed_scope=scope,
                as_of=desired.as_of,
                status=ReconciliationStatus.AMBIGUOUS,
            )

    desired_regions = desired.regions_for(
        scope.target
    )
    configured_regions = configured.permit_regions
    common = intersect_many(
        desired_regions,
        configured_regions,
    )
    missing = canonical_union(
        subtract_many(
            desired_regions,
            configured_regions,
        )
    )
    extra = canonical_union(
        subtract_many(
            configured_regions,
            desired_regions,
        )
    )

    if not missing and not extra:
        status = ReconciliationStatus.SATISFIED
        change = RequiredSemanticChange.NO_OP
    elif missing and not extra:
        status = ReconciliationStatus.DRIFT
        change = RequiredSemanticChange.ADD
    elif not missing and extra:
        status = ReconciliationStatus.DRIFT
        change = RequiredSemanticChange.REMOVE
    else:
        status = ReconciliationStatus.DRIFT
        change = RequiredSemanticChange.REPLACE

    return PolicyReconciliation(
        managed_scope=scope,
        as_of=desired.as_of,
        status=status,
        common=common,
        missing=missing,
        extra=extra,
        required_change=change,
        complete=True,
    )
