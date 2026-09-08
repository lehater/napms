from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from napms.access_policy.application.ports import (
    AccessRulePersistenceError,
    AuthorityAction,
    AuthorityCheck,
    TernaryOutcome,
)
from napms.access_policy.application.select_effective_policy import (
    EffectivePolicySelectionOutcome,
    SelectAccessPolicyEffectiveDesiredPolicy,
    SelectEffectiveDesiredPolicy,
)
from napms.access_policy.application.set_effective_window import (
    EffectiveWindowMutationOutcome,
    SetAccessRuleEffectiveWindow,
    SetRuleEffectiveWindow,
)
from napms.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    DomainInvariantError,
    EffectiveWindow,
    OperationalState,
    ProposalProvenance,
    RuleSemanticIdentity,
)


NOW = datetime(2026, 9, 8, 18, 0, tzinfo=timezone.utc)
START = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)
END = datetime(2026, 9, 10, 18, 0, tzinfo=timezone.utc)


def identity(seed):
    return RuleSemanticIdentity(UUID(int=seed), UUID(int=seed + 100), UUID(int=seed + 200))


def active_rule(*, rule_id=1, scope="scope-1"):
    semantic_identity = identity(rule_id)
    return AccessRule.materialized_from_allowed_decision(
        rule_id=UUID(int=rule_id),
        semantic_identity=semantic_identity,
        decision=DecisionReference(
            semantic_identity,
            ConnectivityDecisionResult.ALLOWED,
            f"decision-{rule_id}",
        ),
        proposal_provenance=ProposalProvenance(
            actor_id="proposer",
            authority_scope=scope,
            effective_time=NOW,
            authority_reference="proposal-auth",
            catalogue_reference="catalogue-1",
        ),
    )


def with_window(rule, window):
    return rule.with_effective_window(
        window=window,
        actor_id="window-admin",
        effective_time=NOW,
        authority_reference="window-auth",
    )


def inactive(rule):
    return rule.with_operational_state(
        target_state=OperationalState.INACTIVE,
        actor_id="state-admin",
        effective_time=NOW,
        authority_reference="state-auth",
    )


class FakeAuthority:
    def __init__(self, outcome=TernaryOutcome.PERMITTED, reference="authority-1"):
        self.outcome = outcome
        self.reference = reference
        self.calls = []

    def check(self, **kwargs):
        self.calls.append(kwargs)
        return AuthorityCheck(
            self.outcome,
            self.reference if self.outcome is TernaryOutcome.PERMITTED else None,
        )


class MemoryRules:
    def __init__(self, rules=(), *, fail_commit=False, scope_override=None):
        self.rules = {rule.rule_id: rule for rule in rules}
        self.fail_commit = fail_commit
        self.scope_override = scope_override
        self.saved = []
        self.commit_calls = 0
        self.list_calls = []

    def get_by_id(self, rule_id):
        return self.rules.get(rule_id)

    def find_by_identity(self, semantic_identity):
        return next(
            (
                rule
                for rule in self.rules.values()
                if rule.semantic_identity == semantic_identity
            ),
            None,
        )

    def list_by_governance_scope(self, scope):
        self.list_calls.append(scope)
        if self.scope_override is not None:
            return tuple(self.scope_override)
        return tuple(rule for rule in self.rules.values() if rule.governance_scope == scope)

    def add(self, rule):
        self.rules[rule.rule_id] = rule

    def save(self, rule):
        self.saved.append(rule)
        self.rules[rule.rule_id] = rule

    def commit(self):
        self.commit_calls += 1
        if self.fail_commit:
            raise AccessRulePersistenceError()


def test_effective_window_is_half_open_and_accepts_offset_aware_instants():
    window = EffectiveWindow(START, END)

    assert window.contains(START)
    assert window.contains(START + timedelta(hours=1))
    assert not window.contains(START - timedelta(microseconds=1))
    assert not window.contains(END)
    assert not window.contains(END + timedelta(microseconds=1))


@pytest.mark.parametrize(
    "start,end",
    [
        (START, START),
        (END, START),
        (START.replace(tzinfo=None), END),
        (START, END.replace(tzinfo=None)),
    ],
)
def test_invalid_effective_window_is_rejected(start, end):
    with pytest.raises(DomainInvariantError):
        EffectiveWindow(start, end)


def test_window_rejects_naive_as_of():
    with pytest.raises(DomainInvariantError):
        EffectiveWindow(START, END).contains(START.replace(tzinfo=None))


def test_active_rule_without_window_is_effective_and_inactive_rule_is_not():
    rule = active_rule()

    assert rule.contributes_effect_at(START)
    assert not inactive(rule).contributes_effect_at(START)


def test_effective_window_controls_active_rule_without_mutating_operational_state():
    rule = with_window(active_rule(), EffectiveWindow(START, END))

    assert rule.operational_state is OperationalState.ACTIVE
    assert not rule.contributes_effect_at(START - timedelta(seconds=1))
    assert rule.contributes_effect_at(START)
    assert rule.contributes_effect_at(END - timedelta(microseconds=1))
    assert not rule.contributes_effect_at(END)


def test_set_effective_window_uses_rule_governance_scope_and_records_audit():
    original = active_rule(scope="governance-1")
    authority = FakeAuthority(reference="window-authority-1")
    rules = MemoryRules([original])
    use_case = SetAccessRuleEffectiveWindow(authority=authority, rules=rules)
    window = EffectiveWindow(START, END)

    result = use_case.execute(
        SetRuleEffectiveWindow(
            rule_id=original.rule_id,
            window=window,
            actor_id="operator-1",
            effective_time=NOW,
        )
    )

    assert result.outcome is EffectiveWindowMutationOutcome.UPDATED
    assert result.rule.rule_id == original.rule_id
    assert result.rule.semantic_identity == original.semantic_identity
    assert result.rule.decision == original.decision
    assert result.rule.operational_state == original.operational_state
    assert result.rule.governance_scope == "governance-1"
    assert result.rule.effective_window == window
    assert original.effective_window is None
    assert rules.saved == [result.rule]
    assert rules.commit_calls == 1
    assert authority.calls == [
        {
            "actor_id": "operator-1",
            "action": AuthorityAction.SET_RULE_EFFECTIVE_WINDOW,
            "scope": "governance-1",
            "effective_time": NOW,
        }
    ]

    audit = result.rule.effective_window_history[0]
    assert audit.rule_id == original.rule_id
    assert audit.previous_window is None
    assert audit.new_window == window
    assert audit.actor_id == "operator-1"
    assert audit.effective_time == NOW
    assert audit.governance_scope == "governance-1"
    assert audit.authority_reference == "window-authority-1"


def test_effective_window_can_be_removed_and_history_is_appended():
    original = with_window(active_rule(), EffectiveWindow(START, END))
    rules = MemoryRules([original])
    result = SetAccessRuleEffectiveWindow(
        authority=FakeAuthority(reference="remove-auth"),
        rules=rules,
    ).execute(
        SetRuleEffectiveWindow(
            rule_id=original.rule_id,
            window=None,
            actor_id="operator-2",
            effective_time=NOW + timedelta(minutes=1),
        )
    )

    assert result.outcome is EffectiveWindowMutationOutcome.UPDATED
    assert result.rule.effective_window is None
    assert len(result.rule.effective_window_history) == 2
    assert result.rule.effective_window_history[-1].previous_window == EffectiveWindow(
        START, END
    )
    assert result.rule.effective_window_history[-1].new_window is None


@pytest.mark.parametrize(
    "outcome,expected",
    [
        (TernaryOutcome.DENIED, EffectiveWindowMutationOutcome.AUTHORITY_DENIED),
        (TernaryOutcome.UNKNOWN, EffectiveWindowMutationOutcome.AUTHORITY_UNKNOWN),
    ],
)
def test_window_mutation_authority_fails_closed(outcome, expected):
    original = active_rule()
    rules = MemoryRules([original])
    result = SetAccessRuleEffectiveWindow(
        authority=FakeAuthority(outcome),
        rules=rules,
    ).execute(
        SetRuleEffectiveWindow(
            rule_id=original.rule_id,
            window=EffectiveWindow(START, END),
            actor_id="operator",
            effective_time=NOW,
        )
    )

    assert result.outcome is expected
    assert rules.saved == []
    assert rules.commit_calls == 0
    assert original.effective_window is None
    assert original.effective_window_history == ()


def test_window_mutation_permitted_without_authority_provenance_fails_closed():
    original = active_rule()
    rules = MemoryRules([original])
    result = SetAccessRuleEffectiveWindow(
        authority=FakeAuthority(reference=None),
        rules=rules,
    ).execute(
        SetRuleEffectiveWindow(
            original.rule_id,
            EffectiveWindow(START, END),
            "operator",
            NOW,
        )
    )

    assert result.outcome is EffectiveWindowMutationOutcome.AUTHORITY_UNKNOWN
    assert rules.saved == []
    assert rules.commit_calls == 0


def test_unknown_rule_short_circuits_window_authority():
    authority = FakeAuthority()
    rules = MemoryRules()
    result = SetAccessRuleEffectiveWindow(authority=authority, rules=rules).execute(
        SetRuleEffectiveWindow(
            UUID(int=999),
            EffectiveWindow(START, END),
            "operator",
            NOW,
        )
    )

    assert result.outcome is EffectiveWindowMutationOutcome.RULE_NOT_FOUND
    assert authority.calls == []
    assert rules.saved == []


def test_same_effective_window_is_explicit_no_change_after_authority_check():
    window = EffectiveWindow(START, END)
    original = with_window(active_rule(), window)
    authority = FakeAuthority()
    rules = MemoryRules([original])

    result = SetAccessRuleEffectiveWindow(authority=authority, rules=rules).execute(
        SetRuleEffectiveWindow(original.rule_id, window, "operator", NOW)
    )

    assert result.outcome is EffectiveWindowMutationOutcome.ALREADY_IN_REQUESTED_WINDOW
    assert result.rule is original
    assert len(authority.calls) == 1
    assert rules.saved == []
    assert rules.commit_calls == 0
    assert len(result.rule.effective_window_history) == 1


def test_window_mutation_command_has_no_caller_supplied_scope():
    names = {field.name for field in fields(SetRuleEffectiveWindow)}
    assert "scope" not in names
    assert "authority_scope" not in names


def test_domain_rejects_same_window_change_directly():
    window = EffectiveWindow(START, END)
    rule = with_window(active_rule(), window)

    with pytest.raises(DomainInvariantError):
        rule.with_effective_window(
            window=window,
            actor_id="operator",
            effective_time=NOW,
            authority_reference="auth",
        )


def test_window_change_audit_and_rule_are_immutable():
    original = active_rule()
    result = SetAccessRuleEffectiveWindow(
        authority=FakeAuthority(),
        rules=MemoryRules([original]),
    ).execute(
        SetRuleEffectiveWindow(
            original.rule_id,
            EffectiveWindow(START, END),
            "operator",
            NOW,
        )
    )

    with pytest.raises(FrozenInstanceError):
        result.rule.effective_window = None
    with pytest.raises(FrozenInstanceError):
        result.rule.effective_window_history[0].actor_id = "other"


def test_window_persistence_failure_is_not_reported_as_success():
    original = active_rule()
    rules = MemoryRules([original], fail_commit=True)

    with pytest.raises(AccessRulePersistenceError):
        SetAccessRuleEffectiveWindow(
            authority=FakeAuthority(),
            rules=rules,
        ).execute(
            SetRuleEffectiveWindow(
                original.rule_id,
                EffectiveWindow(START, END),
                "operator",
                NOW,
            )
        )


def selection_service(rules, authority=None):
    return SelectAccessPolicyEffectiveDesiredPolicy(
        authority=authority or FakeAuthority(reference="read-auth"),
        rules=rules,
    )


def selection_command(*, scope="scope-1", as_of=START, actor="reader"):
    return SelectEffectiveDesiredPolicy(scope=scope, as_of=as_of, actor_id=actor)


def test_selection_uses_read_authority_for_requested_scope_and_as_of():
    authority = FakeAuthority(reference="read-auth-1")
    rules = MemoryRules([active_rule(scope="scope-1")])

    result = selection_service(rules, authority).execute(selection_command())

    assert result.outcome is EffectivePolicySelectionOutcome.SELECTED
    assert result.scope == "scope-1"
    assert result.as_of == START
    assert result.authority_reference == "read-auth-1"
    assert authority.calls == [
        {
            "actor_id": "reader",
            "action": AuthorityAction.READ_EFFECTIVE_DESIRED_POLICY,
            "scope": "scope-1",
            "effective_time": START,
        }
    ]
    assert rules.list_calls == ["scope-1"]


@pytest.mark.parametrize(
    "outcome,expected",
    [
        (TernaryOutcome.DENIED, EffectivePolicySelectionOutcome.AUTHORITY_DENIED),
        (TernaryOutcome.UNKNOWN, EffectivePolicySelectionOutcome.AUTHORITY_UNKNOWN),
    ],
)
def test_selection_denied_or_unknown_returns_no_policy_data(outcome, expected):
    rules = MemoryRules([active_rule()])
    result = selection_service(rules, FakeAuthority(outcome)).execute(selection_command())

    assert result.outcome is expected
    assert result.rules == ()
    assert result.authority_reference is None
    assert rules.list_calls == []


def test_selection_permitted_without_authority_provenance_returns_no_policy_data():
    rules = MemoryRules([active_rule()])
    result = selection_service(rules, FakeAuthority(reference=None)).execute(
        selection_command()
    )

    assert result.outcome is EffectivePolicySelectionOutcome.AUTHORITY_UNKNOWN
    assert result.rules == ()
    assert rules.list_calls == []


def test_selection_includes_only_active_rules_effective_at_exact_as_of():
    always = active_rule(rule_id=1)
    starts_now = with_window(
        active_rule(rule_id=2),
        EffectiveWindow(START, END),
    )
    ended_now = with_window(
        active_rule(rule_id=3),
        EffectiveWindow(START - timedelta(hours=2), START),
    )
    not_started = with_window(
        active_rule(rule_id=4),
        EffectiveWindow(START + timedelta(seconds=1), END),
    )
    suspended = inactive(active_rule(rule_id=5))

    result = selection_service(
        MemoryRules([always, starts_now, ended_now, not_started, suspended])
    ).execute(selection_command(as_of=START))

    assert result.outcome is EffectivePolicySelectionOutcome.SELECTED
    assert tuple(rule.rule_id for rule in result.rules) == (UUID(int=1), UUID(int=2))


def test_selection_is_isolated_to_one_governance_scope():
    selected = active_rule(rule_id=1, scope="scope-1")
    other = active_rule(rule_id=2, scope="scope-2")
    rules = MemoryRules([selected, other])

    result = selection_service(rules).execute(selection_command(scope="scope-1"))

    assert result.rules == (selected,)
    assert other not in result.rules


def test_repository_scope_contract_violation_fails_closed():
    wrong_scope = active_rule(rule_id=2, scope="scope-2")
    rules = MemoryRules(
        [wrong_scope],
        scope_override=[wrong_scope],
    )

    with pytest.raises(AccessRulePersistenceError, match="outside requested governance scope"):
        selection_service(rules).execute(selection_command(scope="scope-1"))


def test_selection_rejects_naive_as_of_before_authority_or_repository_access():
    with pytest.raises(DomainInvariantError):
        selection_command(as_of=START.replace(tzinfo=None))


def test_selection_result_is_deterministic_by_rule_id():
    rules = MemoryRules(
        [
            active_rule(rule_id=30),
            active_rule(rule_id=10),
            active_rule(rule_id=20),
        ]
    )

    result = selection_service(rules).execute(selection_command())

    assert tuple(rule.rule_id for rule in result.rules) == (
        UUID(int=10),
        UUID(int=20),
        UUID(int=30),
    )
