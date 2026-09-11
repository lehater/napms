from datetime import datetime, timedelta, timezone
from uuid import UUID

from napms.connectivity_requirements.adapters.scoped_connectivity_inventory import (
    ConnectivityRequirementsScopedConnectivityAdapter,
)
from napms.connectivity_requirements.application.inventory_summary import (
    ConnectivityRequirementInventorySnapshot,
)
from napms.connectivity_requirements.application.ports import RequirementPersistenceError
from napms.connectivity_requirements.domain.model import (
    RequiredSemanticInteraction,
    RequirementApplicability,
    RequirementLifecycleState,
)
from napms.scoped_connectivity_inventory.application.model import (
    CoverageSummary,
    InteractionIdentity,
    RequirementCurrent,
)
from napms.scoped_connectivity_inventory.application.ports import (
    DependencyAvailability,
)


AS_OF = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
SOURCE = UUID("00000000-0000-0000-0000-000000000101")
DESTINATION = UUID("00000000-0000-0000-0000-000000000102")
DCS = UUID("00000000-0000-0000-0000-000000000103")
IDENTITY = InteractionIdentity(SOURCE, DESTINATION, DCS)
REQUIRED = RequiredSemanticInteraction(SOURCE, DESTINATION, DCS)


class FakeRequirements:
    def __init__(self, values=(), *, fail=False):
        self.values = tuple(values)
        self.fail = fail

    def list_inventory_summaries(self, *, governance_scope, interactions):
        if self.fail:
            raise RequirementPersistenceError()
        return self.values


def summary(
    *,
    scope="scope-a",
    lifecycle=RequirementLifecycleState.ACTIVE,
    applicability=None,
):
    return ConnectivityRequirementInventorySnapshot(
        governance_scope=scope,
        required_interaction=REQUIRED,
        lifecycle_state=lifecycle,
        applicability=applicability or RequirementApplicability.ongoing(),
    )


def execute(values=()):
    return ConnectivityRequirementsScopedConnectivityAdapter(
        requirements=FakeRequirements(values)
    ).summarize_requirements(
        responsibility_scope="scope-a",
        identities=(IDENTITY,),
        as_of=AS_OF,
    )


def test_current_requirement_is_required_and_coverage_is_left_for_composition():
    result = execute((summary(),))

    item = result.items[0]
    assert item.current is RequirementCurrent.REQUIRED
    assert item.historical_only is False
    assert item.coverage is CoverageSummary.UNKNOWN


def test_no_requirement_is_explicit_none_not_unknown():
    item = execute().items[0]

    assert item.current is RequirementCurrent.NONE
    assert item.historical_only is False
    assert item.coverage is CoverageSummary.NOT_APPLICABLE


def test_retired_requirement_is_historical_only():
    item = execute(
        (summary(lifecycle=RequirementLifecycleState.RETIRED),)
    ).items[0]

    assert item.current is RequirementCurrent.NONE
    assert item.historical_only is True
    assert item.coverage is CoverageSummary.NOT_CURRENT


def test_active_requirement_outside_applicability_is_historical_only():
    item = execute(
        (
            summary(
                applicability=RequirementApplicability.absolute_window(
                    start=AS_OF - timedelta(days=2),
                    end=AS_OF - timedelta(days=1),
                )
            ),
        )
    ).items[0]

    assert item.current is RequirementCurrent.NONE
    assert item.historical_only is True
    assert item.coverage is CoverageSummary.NOT_CURRENT


def test_unexpected_scope_from_owner_port_fails_closed():
    result = execute((summary(scope="scope-b"),))

    assert result.availability is DependencyAvailability.UNAVAILABLE
    assert result.items == ()


def test_requirement_persistence_failure_is_unavailable():
    result = ConnectivityRequirementsScopedConnectivityAdapter(
        requirements=FakeRequirements(fail=True)
    ).summarize_requirements(
        responsibility_scope="scope-a",
        identities=(IDENTITY,),
        as_of=AS_OF,
    )

    assert result.availability is DependencyAvailability.UNAVAILABLE
    assert result.items == ()
