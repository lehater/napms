from datetime import datetime, timedelta, timezone
from uuid import UUID

from napms.access_policy.adapters.scoped_connectivity_inventory import (
    AccessPolicyScopedConnectivityAdapter,
)
from napms.access_policy.application.inventory_summary import (
    AccessRuleInventorySnapshot,
)
from napms.access_policy.application.ports import AccessRulePersistenceError
from napms.access_policy.domain.model import (
    EffectiveWindow,
    OperationalState,
    RuleSemanticIdentity,
)
from napms.scoped_connectivity_inventory.application.model import (
    EffectiveAtAsOf,
    InteractionIdentity,
    PolicyOperationalState,
    RuleExists,
)
from napms.scoped_connectivity_inventory.application.ports import (
    DependencyAvailability,
)


AS_OF = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
SOURCE = UUID("00000000-0000-0000-0000-000000000101")
DESTINATION = UUID("00000000-0000-0000-0000-000000000102")
DCS = UUID("00000000-0000-0000-0000-000000000103")
IDENTITY = InteractionIdentity(SOURCE, DESTINATION, DCS)
RULE_IDENTITY = RuleSemanticIdentity(SOURCE, DESTINATION, DCS)


class FakeRules:
    def __init__(self, values=(), *, fail=False):
        self.values = tuple(values)
        self.fail = fail

    def find_inventory_summaries(self, identities):
        if self.fail:
            raise AccessRulePersistenceError()
        return self.values


def test_no_rule_is_safe_explicit_absence():
    result = AccessPolicyScopedConnectivityAdapter(
        rules=FakeRules()
    ).summarize_policy(
        identities=(IDENTITY,),
        as_of=AS_OF,
    )

    assert result.availability is DependencyAvailability.AVAILABLE
    item = result.items[0]
    assert item.rule_exists is RuleExists.NO
    assert item.operational_state is PolicyOperationalState.UNAVAILABLE
    assert item.effective_at_as_of is EffectiveAtAsOf.UNAVAILABLE


def test_active_rule_without_window_is_effective():
    result = AccessPolicyScopedConnectivityAdapter(
        rules=FakeRules(
            (
                AccessRuleInventorySnapshot(
                    semantic_identity=RULE_IDENTITY,
                    operational_state=OperationalState.ACTIVE,
                    effective_window=None,
                ),
            )
        )
    ).summarize_policy(
        identities=(IDENTITY,),
        as_of=AS_OF,
    )

    item = result.items[0]
    assert item.rule_exists is RuleExists.YES
    assert item.operational_state is PolicyOperationalState.ACTIVE
    assert item.effective_at_as_of is EffectiveAtAsOf.YES


def test_active_rule_outside_window_is_not_effective():
    result = AccessPolicyScopedConnectivityAdapter(
        rules=FakeRules(
            (
                AccessRuleInventorySnapshot(
                    semantic_identity=RULE_IDENTITY,
                    operational_state=OperationalState.ACTIVE,
                    effective_window=EffectiveWindow(
                        AS_OF + timedelta(days=1),
                        AS_OF + timedelta(days=2),
                    ),
                ),
            )
        )
    ).summarize_policy(
        identities=(IDENTITY,),
        as_of=AS_OF,
    )

    assert result.items[0].effective_at_as_of is EffectiveAtAsOf.NO


def test_inactive_rule_is_not_effective():
    result = AccessPolicyScopedConnectivityAdapter(
        rules=FakeRules(
            (
                AccessRuleInventorySnapshot(
                    semantic_identity=RULE_IDENTITY,
                    operational_state=OperationalState.INACTIVE,
                    effective_window=None,
                ),
            )
        )
    ).summarize_policy(
        identities=(IDENTITY,),
        as_of=AS_OF,
    )

    item = result.items[0]
    assert item.operational_state is PolicyOperationalState.INACTIVE
    assert item.effective_at_as_of is EffectiveAtAsOf.NO


def test_policy_persistence_failure_is_unavailable_not_no_rule():
    result = AccessPolicyScopedConnectivityAdapter(
        rules=FakeRules(fail=True)
    ).summarize_policy(
        identities=(IDENTITY,),
        as_of=AS_OF,
    )

    assert result.availability is DependencyAvailability.UNAVAILABLE
    assert result.items == ()
