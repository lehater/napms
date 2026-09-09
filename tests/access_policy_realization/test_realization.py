from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from napms.access_policy_realization.application.derive import (
    DeriveDesiredEnforcementPolicy,
)
from napms.access_policy_realization.application.reconcile import (
    ReconcileEnforcementPolicy,
)
from napms.access_policy_realization.domain.algebra import (
    resolve_domain_access,
)
from napms.access_policy_realization.domain.model import (
    AddressConstraint,
    AddressRange,
    DomainInteractionIdentity,
    DomainInteractionRegion,
    DomainKnowledgeSnapshot,
    DomainRegionProvenance,
    InputProvenance,
    PortConstraint,
    PortRange,
    PortRegion,
    ProtocolSelector,
    TechnicalAccessPredicate,
    TechnicalRegionFragment,
)
from napms.access_policy_realization.domain.realization import (
    ConfiguredEnforcementSnapshot,
    DesiredDerivationStatus,
    DesiredPolicyContribution,
    EnforcementPlacementProjection,
    EnforcementTarget,
    ManagedReconciliationScope,
    PlacementStatus,
    RealizationInvariantError,
    ReconciliationStatus,
    RequiredSemanticChange,
)


NOW = datetime(
    2026,
    9,
    9,
    12,
    tzinfo=timezone.utc,
)


def identity(value: int) -> DomainInteractionIdentity:
    return DomainInteractionIdentity(
        UUID(int=value),
        UUID(int=value + 100),
        UUID(int=value + 200),
    )


def provenance(value: int) -> DomainRegionProvenance:
    return DomainRegionProvenance(
        (f"acc:{value}",),
        (f"src:{value}",),
        (f"dst:{value}",),
    )


def fragment(
    first: int = 443,
    last: int | None = None,
) -> TechnicalRegionFragment:
    return TechnicalRegionFragment(
        AddressRange(
            "10.0.0.1",
            "10.0.0.1",
        ),
        AddressRange(
            "10.0.0.2",
            "10.0.0.2",
        ),
        6,
        PortRegion.numeric(
            0,
            65535,
        ),
        PortRegion.numeric(
            first,
            last if last is not None else first,
        ),
    )


def predicate(
    first: int = 443,
    last: int | None = None,
) -> TechnicalAccessPredicate:
    return TechnicalAccessPredicate(
        AddressConstraint.ranged(
            AddressRange(
                "10.0.0.1",
                "10.0.0.1",
            )
        ),
        AddressConstraint.ranged(
            AddressRange(
                "10.0.0.2",
                "10.0.0.2",
            )
        ),
        ProtocolSelector.ip_protocol(6),
        PortConstraint.any(),
        PortConstraint.ranged(
            PortRange(
                first,
                last if last is not None else first,
            )
        ),
    )


def resolution(
    *interaction_values: int,
    first: int = 443,
    last: int | None = None,
):
    return resolve_domain_access(
        predicate(
            first,
            last,
        ),
        as_of=NOW,
        knowledge=DomainKnowledgeSnapshot(
            tuple(
                DomainInteractionRegion(
                    identity(value),
                    fragment(
                        first,
                        last,
                    ),
                    provenance(value),
                )
                for value in interaction_values
            )
        ),
        input_provenance=InputProvenance(
            ("desired:projection",)
        ),
    )


TARGET = EnforcementTarget(
    UUID(int=1000),
    UUID(int=2000),
)
OTHER_TARGET = EnforcementTarget(
    UUID(int=1000),
    UUID(int=2001),
)


def contribution(
    interaction_value: int = 1,
    *,
    resolved_values: tuple[int, ...] = (1,),
    region: TechnicalRegionFragment | None = None,
    placement_status: PlacementStatus = PlacementStatus.PLACED,
    targets: tuple[EnforcementTarget, ...] = (TARGET,),
) -> DesiredPolicyContribution:
    value = region or fragment()
    assert value.destination_ports.first is not None
    assert value.destination_ports.last is not None
    resolved = resolution(
        *resolved_values,
        first=value.destination_ports.first,
        last=value.destination_ports.last,
    )
    return DesiredPolicyContribution(
        rule_reference=f"rule:{interaction_value}",
        interaction=identity(
            interaction_value
        ),
        fragment=value,
        resolution=resolved,
        placement_status=placement_status,
        placements=tuple(
            EnforcementPlacementProjection(
                target,
                (
                    f"placement:{index}",
                ),
            )
            for index, target
            in enumerate(targets)
        ),
        placement_provenance_references=(
            "path:1",
        ),
    )


def desired_policy(
    *contributions: DesiredPolicyContribution,
    desired_values: tuple[int, ...] = (1,),
):
    return DeriveDesiredEnforcementPolicy().execute(
        governance_scope="scope:a",
        as_of=NOW,
        desired_interactions=tuple(
            identity(value)
            for value in desired_values
        ),
        contributions=tuple(contributions),
    )


def configured(
    regions: tuple[TechnicalRegionFragment, ...],
    *,
    complete: bool = True,
    target: EnforcementTarget = TARGET,
    governance_scope: str = "scope:a",
    resolutions=None,
    as_of: datetime = NOW,
):
    if resolutions is None:
        resolutions = tuple(
            resolution(
                first=value.destination_ports.first,
                last=value.destination_ports.last,
            )
            for value in regions
        )
    return ConfiguredEnforcementSnapshot(
        managed_scope=ManagedReconciliationScope(
            governance_scope,
            target,
            "contract:effective-permit:1",
        ),
        as_of=as_of,
        permit_regions=regions,
        domain_resolutions=tuple(
            resolutions
        ),
        evidence_references=(
            "evidence:set:1",
        ),
        complete_for_managed_scope=complete,
    )


def reconcile(desired, configured_snapshot):
    return ReconcileEnforcementPolicy().execute(
        desired=desired,
        configured=configured_snapshot,
    )


def test_exact_match_is_satisfied_no_op():
    desired = desired_policy(
        contribution()
    )

    result = reconcile(
        desired,
        configured(
            (fragment(),),
            resolutions=(resolution(1),),
        ),
    )

    assert (
        result.status
        is ReconciliationStatus.SATISFIED
    )
    assert (
        result.required_change
        is RequiredSemanticChange.NO_OP
    )
    assert result.common == (
        fragment(),
    )
    assert result.missing == ()
    assert result.extra == ()
    assert result.complete


@pytest.mark.parametrize(
    (
        "desired_regions",
        "configured_regions",
        "expected",
    ),
    (
        (
            (fragment(),),
            (),
            RequiredSemanticChange.ADD,
        ),
        (
            (),
            (fragment(22),),
            RequiredSemanticChange.REMOVE,
        ),
        (
            (fragment(),),
            (fragment(80),),
            RequiredSemanticChange.REPLACE,
        ),
    ),
)
def test_complete_delta_classification(
    desired_regions,
    configured_regions,
    expected,
):
    contributions = tuple(
        contribution(
            region=value,
        )
        for value in desired_regions
    )
    desired = desired_policy(
        *contributions
    )

    result = reconcile(
        desired,
        configured(
            configured_regions,
        ),
    )

    assert (
        result.status
        is ReconciliationStatus.DRIFT
    )
    assert result.required_change is expected
    assert result.complete


def test_partial_overlap_preserves_exact_common_missing_extra():
    desired = desired_policy(
        contribution(
            region=fragment(
                1000,
                2000,
            )
        )
    )

    result = reconcile(
        desired,
        configured(
            (
                fragment(
                    1500,
                    2500,
                ),
            )
        ),
    )

    assert [
        (
            value.destination_ports.first,
            value.destination_ports.last,
        )
        for value in result.common
    ] == [
        (
            1500,
            2000,
        )
    ]
    assert [
        (
            value.destination_ports.first,
            value.destination_ports.last,
        )
        for value in result.missing
    ] == [
        (
            1000,
            1499,
        )
    ]
    assert [
        (
            value.destination_ports.first,
            value.destination_ports.last,
        )
        for value in result.extra
    ] == [
        (
            2001,
            2500,
        )
    ]
    assert (
        result.required_change
        is RequiredSemanticChange.REPLACE
    )


def test_complete_configured_snapshot_requires_i18_attribution():
    with pytest.raises(
        RealizationInvariantError,
        match="I18 attribution",
    ):
        configured(
            (fragment(),),
            resolutions=(),
        )


def test_incomplete_configured_snapshot_cannot_infer_add():
    desired = desired_policy(
        contribution()
    )

    result = reconcile(
        desired,
        configured(
            (),
            complete=False,
        ),
    )

    assert (
        result.status
        is ReconciliationStatus.UNKNOWN
    )
    assert result.required_change is None
    assert not result.complete


def test_managed_scope_mismatch_is_unknown_not_remove():
    desired = desired_policy(
        contribution()
    )

    result = reconcile(
        desired,
        configured(
            (fragment(22),),
            governance_scope="scope:b",
        ),
    )

    assert (
        result.status
        is ReconciliationStatus.UNKNOWN
    )
    assert result.required_change is None


def test_configured_time_mismatch_is_unknown():
    desired = desired_policy(
        contribution()
    )

    result = reconcile(
        desired,
        configured(
            (fragment(),),
            as_of=NOW - timedelta(
                minutes=1
            ),
        ),
    )

    assert (
        result.status
        is ReconciliationStatus.UNKNOWN
    )


def test_non_desired_domain_collision_makes_desired_policy_ambiguous():
    desired = desired_policy(
        contribution(
            resolved_values=(
                1,
                2,
            )
        ),
        desired_values=(1,),
    )

    assert (
        desired.status
        is DesiredDerivationStatus.AMBIGUOUS
    )
    assert desired.intents == ()


def test_shared_region_is_accepted_when_all_interactions_are_desired():
    desired = desired_policy(
        contribution(
            1,
            resolved_values=(
                1,
                2,
            ),
        ),
        contribution(
            2,
            resolved_values=(
                1,
                2,
            ),
        ),
        desired_values=(
            1,
            2,
        ),
    )

    assert (
        desired.status
        is DesiredDerivationStatus.DERIVED
    )
    assert desired.regions_for(
        TARGET
    ) == (
        fragment(),
    )
    assert {
        value
        for intent in desired.intents
        for value in intent.interactions
    } == {
        identity(1),
        identity(2),
    }


def test_placement_ambiguity_selects_no_target():
    desired = desired_policy(
        contribution(
            placement_status=PlacementStatus.AMBIGUOUS,
            targets=(
                TARGET,
                OTHER_TARGET,
            ),
        )
    )

    assert (
        desired.status
        is DesiredDerivationStatus.AMBIGUOUS
    )
    assert desired.intents == ()


def test_no_enforcement_is_derived_diagnostic_not_guessed_target():
    desired = desired_policy(
        contribution(
            placement_status=PlacementStatus.NO_ENFORCEMENT,
            targets=(),
        )
    )

    assert (
        desired.status
        is DesiredDerivationStatus.DERIVED
    )
    assert desired.intents == ()
    assert (
        desired.no_enforcement_rule_references
        == ("rule:1",)
    )


def test_attachment_granularity_keeps_targets_distinct():
    desired = desired_policy(
        contribution(
            targets=(
                TARGET,
                OTHER_TARGET,
            ),
        )
    )

    assert desired.regions_for(
        TARGET
    ) == (
        fragment(),
    )
    assert desired.regions_for(
        OTHER_TARGET
    ) == (
        fragment(),
    )
    assert TARGET != OTHER_TARGET


def test_material_configured_domain_ambiguity_blocks_satisfied():
    desired = desired_policy(
        contribution()
    )
    ambiguous = resolution(
        1,
        2,
    )

    result = reconcile(
        desired,
        configured(
            (fragment(),),
            resolutions=(
                ambiguous,
            ),
        ),
    )

    assert (
        result.status
        is ReconciliationStatus.AMBIGUOUS
    )
    assert result.required_change is None


def test_configured_ambiguity_is_not_material_when_all_meanings_desired():
    desired = desired_policy(
        contribution(
            1,
            resolved_values=(
                1,
                2,
            ),
        ),
        contribution(
            2,
            resolved_values=(
                1,
                2,
            ),
        ),
        desired_values=(
            1,
            2,
        ),
    )

    result = reconcile(
        desired,
        configured(
            (fragment(),),
            resolutions=(
                resolution(
                    1,
                    2,
                ),
            ),
        ),
    )

    assert (
        result.status
        is ReconciliationStatus.SATISFIED
    )
    assert (
        result.required_change
        is RequiredSemanticChange.NO_OP
    )
