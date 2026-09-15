from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from napms.contexts.access_policy_realization.domain.algebra import (
    fragment_sort_key,
    intersect_fragments,
    subtract_many,
)
from napms.contexts.access_policy_realization.domain.model import (
    TechnicalRegionFragment,
    require_aware,
)


class MvpPolicyInvariantError(ValueError):
    pass


def _non_empty(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise MvpPolicyInvariantError(f"{field_name} must be non-empty")
    return normalized


def _references(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted({_non_empty(value, field_name="reference") for value in values}))


@dataclass(frozen=True, slots=True, order=True)
class ComparisonScope:
    firewall_id: str
    access_list_name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "firewall_id", _non_empty(self.firewall_id, field_name="firewall_id"))
        object.__setattr__(
            self,
            "access_list_name",
            _non_empty(self.access_list_name, field_name="access_list_name"),
        )


@dataclass(frozen=True, slots=True)
class PermitSpace:
    fragments: tuple[TechnicalRegionFragment, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "fragments",
            tuple(sorted(set(self.fragments), key=fragment_sort_key)),
        )

    @property
    def is_empty(self) -> bool:
        return not self.fragments


@dataclass(frozen=True, slots=True)
class TargetRequiredPolicy:
    comparison_scope: ComparisonScope
    required_permit_space: PermitSpace
    contributing_policy_rule_refs: tuple[str, ...]
    logical_time: datetime
    provenance: tuple[str, ...]
    freshness: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_aware(self.logical_time, field_name="logical_time")
        rules = _references(self.contributing_policy_rule_refs)
        if not rules:
            raise MvpPolicyInvariantError("required policy needs at least one contributor")
        object.__setattr__(self, "contributing_policy_rule_refs", rules)
        object.__setattr__(self, "provenance", _references(self.provenance))
        object.__setattr__(self, "freshness", _references(self.freshness))


class ConfiguredCompleteness(str, Enum):
    COMPLETE = "Complete"
    INCOMPLETE = "Incomplete"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class ConfiguredEffectivePolicySnapshot:
    comparison_scope: ComparisonScope
    effective_permit_space: PermitSpace
    completeness: ConfiguredCompleteness
    base_correlation: str
    provenance: tuple[str, ...]
    unsupported_semantics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "base_correlation",
            _non_empty(self.base_correlation, field_name="base_correlation"),
        )
        object.__setattr__(self, "provenance", _references(self.provenance))
        object.__setattr__(
            self,
            "unsupported_semantics",
            _references(self.unsupported_semantics),
        )


class ComparisonStatus(str, Enum):
    REALIZED = "Realized"
    DRIFT = "Drift"


@dataclass(frozen=True, slots=True)
class ComparableAssessment:
    comparison_scope: ComparisonScope
    status: ComparisonStatus
    common: PermitSpace
    missing: PermitSpace
    excess: PermitSpace
    required_provenance: tuple[str, ...]
    configured_provenance: tuple[str, ...]
    base_configured_correlation: str

    def __post_init__(self) -> None:
        expected = (
            ComparisonStatus.REALIZED
            if self.missing.is_empty and self.excess.is_empty
            else ComparisonStatus.DRIFT
        )
        if self.status is not expected:
            raise MvpPolicyInvariantError("comparison status does not match semantic delta")


class UncomparableReason(str, Enum):
    COMPARISON_SCOPE_MISMATCH = "ComparisonScopeMismatch"
    CONFIGURED_INCOMPLETE = "ConfiguredIncomplete"
    CONFIGURED_UNKNOWN = "ConfiguredUnknown"
    UNSUPPORTED_CONFIGURED_SEMANTICS = "UnsupportedConfiguredSemantics"


@dataclass(frozen=True, slots=True)
class Uncomparable:
    reasons: tuple[UncomparableReason, ...]
    required_scope: ComparisonScope
    configured_scope: ComparisonScope
    required_provenance: tuple[str, ...]
    configured_provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        reasons = tuple(dict.fromkeys(self.reasons))
        if not reasons:
            raise MvpPolicyInvariantError("Uncomparable requires at least one reason")
        object.__setattr__(self, "reasons", reasons)


MvpComparisonResult = ComparableAssessment | Uncomparable


class ChangeOperation(str, Enum):
    ENSURE_PERMIT = "EnsurePermit"


@dataclass(frozen=True, slots=True)
class VerifiedChangeIntent:
    comparison_scope: ComparisonScope
    operation: ChangeOperation
    permit_space: PermitSpace
    base_configured_correlation: str
    required_policy_provenance: tuple[str, ...]
    delta_provenance: tuple[str, ...]
    verification_evidence: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.operation is not ChangeOperation.ENSURE_PERMIT:
            raise MvpPolicyInvariantError("MVP supports ENSURE_PERMIT only")
        if self.permit_space.is_empty:
            raise MvpPolicyInvariantError("ENSURE_PERMIT requires non-empty permit space")
        object.__setattr__(
            self,
            "base_configured_correlation",
            _non_empty(
                self.base_configured_correlation,
                field_name="base_configured_correlation",
            ),
        )
        object.__setattr__(
            self,
            "required_policy_provenance",
            _references(self.required_policy_provenance),
        )
        object.__setattr__(self, "delta_provenance", _references(self.delta_provenance))
        evidence = _references(self.verification_evidence)
        if not evidence:
            raise MvpPolicyInvariantError("verified intent requires verification evidence")
        object.__setattr__(self, "verification_evidence", evidence)


def _intersection(left: PermitSpace, right: PermitSpace) -> PermitSpace:
    overlaps = []
    for left_fragment in left.fragments:
        for right_fragment in right.fragments:
            overlap = intersect_fragments(left_fragment, right_fragment)
            if overlap is not None:
                overlaps.append(overlap)
    return PermitSpace(tuple(overlaps))


def compare_effective_policy(
    required: TargetRequiredPolicy,
    configured: ConfiguredEffectivePolicySnapshot,
) -> MvpComparisonResult:
    reasons: list[UncomparableReason] = []
    if required.comparison_scope != configured.comparison_scope:
        reasons.append(UncomparableReason.COMPARISON_SCOPE_MISMATCH)
    if configured.completeness is ConfiguredCompleteness.INCOMPLETE:
        reasons.append(UncomparableReason.CONFIGURED_INCOMPLETE)
    elif configured.completeness is ConfiguredCompleteness.UNKNOWN:
        reasons.append(UncomparableReason.CONFIGURED_UNKNOWN)
    if configured.unsupported_semantics:
        reasons.append(UncomparableReason.UNSUPPORTED_CONFIGURED_SEMANTICS)
    if reasons:
        return Uncomparable(
            reasons=tuple(reasons),
            required_scope=required.comparison_scope,
            configured_scope=configured.comparison_scope,
            required_provenance=required.provenance,
            configured_provenance=configured.provenance,
        )

    common = _intersection(required.required_permit_space, configured.effective_permit_space)
    missing = PermitSpace(
        subtract_many(
            required.required_permit_space.fragments,
            configured.effective_permit_space.fragments,
        )
    )
    excess = PermitSpace(
        subtract_many(
            configured.effective_permit_space.fragments,
            required.required_permit_space.fragments,
        )
    )
    status = (
        ComparisonStatus.REALIZED
        if missing.is_empty and excess.is_empty
        else ComparisonStatus.DRIFT
    )
    return ComparableAssessment(
        comparison_scope=required.comparison_scope,
        status=status,
        common=common,
        missing=missing,
        excess=excess,
        required_provenance=required.provenance,
        configured_provenance=configured.provenance,
        base_configured_correlation=configured.base_correlation,
    )


def plan_additive_change(result: MvpComparisonResult) -> VerifiedChangeIntent | None:
    if isinstance(result, Uncomparable) or result.missing.is_empty:
        return None
    return VerifiedChangeIntent(
        comparison_scope=result.comparison_scope,
        operation=ChangeOperation.ENSURE_PERMIT,
        permit_space=result.missing,
        base_configured_correlation=result.base_configured_correlation,
        required_policy_provenance=result.required_provenance,
        delta_provenance=result.required_provenance + result.configured_provenance,
        verification_evidence=(
            "AdditiveEnsurePermitCoversSelectedMissingSpace",
            "AdditiveEnsurePermitDoesNotNarrowConfiguredPermitSpace",
        ),
    )
