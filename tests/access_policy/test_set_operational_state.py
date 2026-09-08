from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone
from uuid import UUID

import pytest

from napms.access_policy.application.ports import (
    AccessRulePersistenceError,
    AuthorityAction,
    AuthorityCheck,
    TernaryOutcome,
)
from napms.access_policy.application.set_operational_state import (
    OperationalStateMutationOutcome,
    SetAccessRuleOperationalState,
    SetRuleOperationalState,
)
from napms.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    DomainInvariantError,
    OperationalState,
    ProposalProvenance,
    RuleSemanticIdentity,
)


RULE_ID = UUID("00000000-0000-0000-0000-000000000010")
IDENTITY = RuleSemanticIdentity(
    UUID("00000000-0000-0000-0000-000000000001"),
    UUID("00000000-0000-0000-0000-000000000002"),
    UUID("00000000-0000-0000-0000-000000000003"),
)
NOW = datetime(2026, 9, 8, 18, 30, tzinfo=timezone.utc)


def active_rule():
    return AccessRule.materialized_from_allowed_decision(
        rule_id=RULE_ID,
        semantic_identity=IDENTITY,
        decision=DecisionReference(
            subject=IDENTITY,
            result=ConnectivityDecisionResult.ALLOWED,
            decision_id="decision-1",
        ),
        proposal_provenance=ProposalProvenance(
            actor_id="proposer",
            authority_scope="governance-scope-1",
            effective_time=datetime(2026, 9, 8, 17, 0, tzinfo=timezone.utc),
            authority_reference="proposal-auth-1",
            catalogue_reference="catalogue-1",
        ),
    )


class FakeAuthority:
    def __init__(self, outcome=TernaryOutcome.PERMITTED, reference="mutation-auth-1"):
        self.outcome = outcome
        self.reference = reference
        self.calls = []

    def check(self, **kwargs):
        self.calls.append(kwargs)
        return AuthorityCheck(
            outcome=self.outcome,
            authority_reference=self.reference
            if self.outcome is TernaryOutcome.PERMITTED
            else None,
        )


class MemoryRules:
    def __init__(self, rule=None, fail_commit=False):
        self.rule = rule
        self.saved = []
        self.commit_calls = 0
        self.fail_commit = fail_commit

    def get_by_id(self, rule_id):
        if self.rule is not None and self.rule.rule_id == rule_id:
            return self.rule
        return None

    def find_by_identity(self, identity):
        if self.rule is not None and self.rule.semantic_identity == identity:
            return self.rule
        return None

    def add(self, rule):
        self.rule = rule

    def save(self, rule):
        self.saved.append(rule)
        self.rule = rule

    def commit(self):
        self.commit_calls += 1
        if self.fail_commit:
            raise AccessRulePersistenceError()


def command(target=OperationalState.INACTIVE):
    return SetRuleOperationalState(
        rule_id=RULE_ID,
        target_state=target,
        actor_id="operator-1",
        effective_time=NOW,
    )


def service(rule=None, authority=None, rules=None):
    repository = rules or MemoryRules(rule or active_rule())
    return (
        SetAccessRuleOperationalState(
            authority=authority or FakeAuthority(),
            rules=repository,
        ),
        repository,
    )


def test_active_to_inactive_preserves_rule_identity_decision_and_governance_scope():
    original = active_rule()
    authority = FakeAuthority()
    use_case, rules = service(rule=original, authority=authority)

    result = use_case.execute(command())

    assert result.outcome is OperationalStateMutationOutcome.UPDATED
    assert result.rule.rule_id == original.rule_id
    assert result.rule.semantic_identity == original.semantic_identity
    assert result.rule.decision == original.decision
    assert result.rule.governance_scope == "governance-scope-1"
    assert result.rule.operational_state is OperationalState.INACTIVE
    assert original.operational_state is OperationalState.ACTIVE
    assert rules.saved == [result.rule]
    assert rules.commit_calls == 1

    assert authority.calls == [
        {
            "actor_id": "operator-1",
            "action": AuthorityAction.SET_RULE_OPERATIONAL_STATE,
            "scope": "governance-scope-1",
            "effective_time": NOW,
        }
    ]


def test_accepted_transition_records_minimum_business_audit():
    result = service()[0].execute(command())

    assert len(result.rule.operational_state_history) == 1
    audit = result.rule.operational_state_history[0]
    assert audit.rule_id == RULE_ID
    assert audit.from_state is OperationalState.ACTIVE
    assert audit.to_state is OperationalState.INACTIVE
    assert audit.actor_id == "operator-1"
    assert audit.effective_time == NOW
    assert audit.governance_scope == "governance-scope-1"
    assert audit.authority_reference == "mutation-auth-1"


def test_inactive_to_active_preserves_prior_audit_and_appends_transition():
    inactive = active_rule().with_operational_state(
        target_state=OperationalState.INACTIVE,
        actor_id="operator-previous",
        effective_time=datetime(2026, 9, 8, 18, 0, tzinfo=timezone.utc),
        authority_reference="mutation-auth-previous",
    )

    result = service(rule=inactive)[0].execute(command(OperationalState.ACTIVE))

    assert result.outcome is OperationalStateMutationOutcome.UPDATED
    assert result.rule.operational_state is OperationalState.ACTIVE
    assert len(result.rule.operational_state_history) == 2
    assert result.rule.operational_state_history[0] == inactive.operational_state_history[0]
    assert result.rule.operational_state_history[1].from_state is OperationalState.INACTIVE
    assert result.rule.operational_state_history[1].to_state is OperationalState.ACTIVE


@pytest.mark.parametrize(
    "outcome,expected",
    [
        (TernaryOutcome.DENIED, OperationalStateMutationOutcome.AUTHORITY_DENIED),
        (TernaryOutcome.UNKNOWN, OperationalStateMutationOutcome.AUTHORITY_UNKNOWN),
    ],
)
def test_denied_or_unknown_authority_fails_closed_without_state_or_audit_mutation(
    outcome, expected
):
    original = active_rule()
    use_case, rules = service(rule=original, authority=FakeAuthority(outcome))

    result = use_case.execute(command())

    assert result.outcome is expected
    assert rules.saved == []
    assert rules.commit_calls == 0
    assert original.operational_state_history == ()
    assert original.operational_state is OperationalState.ACTIVE


def test_permitted_authority_without_provenance_fails_closed():
    original = active_rule()
    use_case, rules = service(
        rule=original,
        authority=FakeAuthority(TernaryOutcome.PERMITTED, reference=None),
    )

    result = use_case.execute(command())

    assert result.outcome is OperationalStateMutationOutcome.AUTHORITY_UNKNOWN
    assert rules.saved == []
    assert rules.commit_calls == 0


def test_unknown_rule_short_circuits_authority():
    authority = FakeAuthority()
    use_case, rules = service(authority=authority, rules=MemoryRules(rule=None))

    result = use_case.execute(command())

    assert result.outcome is OperationalStateMutationOutcome.RULE_NOT_FOUND
    assert authority.calls == []
    assert rules.saved == []
    assert rules.commit_calls == 0


def test_same_state_is_explicit_non_transition_after_authority_check():
    original = active_rule()
    authority = FakeAuthority()
    use_case, rules = service(rule=original, authority=authority)

    result = use_case.execute(command(OperationalState.ACTIVE))

    assert result.outcome is OperationalStateMutationOutcome.ALREADY_IN_REQUESTED_STATE
    assert result.rule is original
    assert len(authority.calls) == 1
    assert rules.saved == []
    assert rules.commit_calls == 0
    assert result.rule.operational_state_history == ()


def test_command_has_no_caller_supplied_scope_field():
    assert "scope" not in {field.name for field in fields(SetRuleOperationalState)}
    assert "authority_scope" not in {field.name for field in fields(SetRuleOperationalState)}


def test_domain_rejects_same_state_transition_even_if_called_directly():
    with pytest.raises(DomainInvariantError):
        active_rule().with_operational_state(
            target_state=OperationalState.ACTIVE,
            actor_id="operator-1",
            effective_time=NOW,
            authority_reference="mutation-auth-1",
        )


def test_transition_audit_and_rule_are_immutable():
    result = service()[0].execute(command())
    audit = result.rule.operational_state_history[0]

    with pytest.raises(FrozenInstanceError):
        audit.actor_id = "other"
    with pytest.raises(FrozenInstanceError):
        result.rule.operational_state = OperationalState.ACTIVE


def test_persistence_failure_is_not_reported_as_success():
    rules = MemoryRules(active_rule(), fail_commit=True)
    use_case, _ = service(rules=rules)

    with pytest.raises(AccessRulePersistenceError):
        use_case.execute(command())
