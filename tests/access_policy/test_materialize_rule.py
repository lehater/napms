from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import UUID

import pytest

from napms.access_policy.application.materialize_rule import (
    MaterializationOutcome,
    MaterializeAllowedAccessRule,
    SubmitAccessRuleProposal,
)
from napms.access_policy.application.ports import (
    AuthorityAction,
    AuthorityCheck,
    ConnectivityDecision,
    DecisionOutcome,
    InteractionCheck,
    InteractionOutcome,
    TernaryOutcome,
)
from napms.access_policy.domain.model import OperationalState, RuleSemanticIdentity


SOURCE = UUID("00000000-0000-0000-0000-000000000001")
DEST = UUID("00000000-0000-0000-0000-000000000002")
DCS = UUID("00000000-0000-0000-0000-000000000003")
RULE = UUID("00000000-0000-0000-0000-000000000004")
NOW = datetime(2026, 9, 8, tzinfo=timezone.utc)


class MemoryRules:
    def __init__(self):
        self.by_identity = {}
        self.add_calls = 0

    def find_by_identity(self, identity):
        return self.by_identity.get(identity)

    def add(self, rule):
        self.add_calls += 1
        if rule.semantic_identity in self.by_identity:
            raise AssertionError("duplicate semantic identity")
        self.by_identity[rule.semantic_identity] = rule


class FakeAuthority:
    def __init__(self, outcome=TernaryOutcome.PERMITTED, reference="auth-1"):
        self.outcome = outcome
        self.reference = reference
        self.calls = 0
        self.last_check = None

    def check(self, **kwargs):
        self.calls += 1
        self.last_check = kwargs
        return AuthorityCheck(
            self.outcome,
            self.reference if self.outcome is TernaryOutcome.PERMITTED else None,
        )


class FakeCatalogue:
    def __init__(self, outcome=InteractionOutcome.VALID):
        self.outcome = outcome
        self.calls = 0

    def resolve_directed_interaction(self, **_):
        self.calls += 1
        return InteractionCheck(self.outcome, "catalogue-1")


class FakeDecisions:
    def __init__(
        self,
        outcome=DecisionOutcome.ALLOWED,
        subject=None,
        reference="decision-1",
    ):
        self.outcome = outcome
        self.subject = subject
        self.reference = reference
        self.calls = 0

    def obtain(self, *, subject):
        self.calls += 1
        return ConnectivityDecision(
            self.outcome,
            self.subject or subject,
            self.reference,
        )


def command(**changes):
    values = dict(
        actor_id="actor-1",
        authority_scope="scope-1",
        effective_time=NOW,
        source_component_deployment_id=SOURCE,
        destination_component_deployment_id=DEST,
        dcs_contract_revision_id=DCS,
        proposal_reference="proposal-1",
    )
    values.update(changes)
    return SubmitAccessRuleProposal(**values)


def service(authority=None, catalogue=None, decisions=None, rules=None, new_rule_id=None):
    return MaterializeAllowedAccessRule(
        authority=authority or FakeAuthority(),
        catalogue=catalogue or FakeCatalogue(),
        decisions=decisions or FakeDecisions(),
        rules=rules or MemoryRules(),
        new_rule_id=new_rule_id or (lambda: RULE),
    )


def test_allowed_creates_active_rule_and_preserves_provenance():
    result = service().execute(command())
    assert result.outcome is MaterializationOutcome.MATERIALIZED
    assert result.rule.rule_id == RULE
    assert result.rule.semantic_identity == command().semantic_identity
    assert result.rule.operational_state is OperationalState.ACTIVE
    assert result.rule.decision.subject == command().semantic_identity
    assert result.rule.decision.decision_id == "decision-1"
    assert result.rule.authority_reference == "auth-1"
    assert result.rule.proposal_reference == "proposal-1"


def test_allowed_without_opaque_decision_reference_still_materializes():
    result = service(decisions=FakeDecisions(reference=None)).execute(command())
    assert result.outcome is MaterializationOutcome.MATERIALIZED
    assert result.rule.decision.subject == command().semantic_identity
    assert result.rule.decision.decision_id is None


def test_allowed_retry_resolves_same_rule_without_second_add():
    rules = MemoryRules()
    ids = iter([RULE, UUID(int=5)])
    use_case = service(rules=rules, new_rule_id=lambda: next(ids))
    first = use_case.execute(command())
    second = use_case.execute(command())
    assert second.outcome is MaterializationOutcome.RESOLVED
    assert second.rule.rule_id == first.rule.rule_id == RULE
    assert rules.add_calls == 1
    assert len(rules.by_identity) == 1


@pytest.mark.parametrize(
    "authority_outcome,expected",
    [
        (TernaryOutcome.DENIED, MaterializationOutcome.AUTHORITY_DENIED),
        (TernaryOutcome.UNKNOWN, MaterializationOutcome.AUTHORITY_UNKNOWN),
    ],
)
def test_authority_failures_short_circuit(authority_outcome, expected):
    catalogue = FakeCatalogue()
    decisions = FakeDecisions()
    rules = MemoryRules()
    result = service(
        authority=FakeAuthority(authority_outcome),
        catalogue=catalogue,
        decisions=decisions,
        rules=rules,
    ).execute(command())
    assert result.outcome is expected
    assert catalogue.calls == 0
    assert decisions.calls == 0
    assert rules.add_calls == 0
    assert not rules.by_identity


def test_permitted_authority_without_required_provenance_fails_closed():
    rules = MemoryRules()
    result = service(authority=FakeAuthority(reference=None), rules=rules).execute(command())
    assert result.outcome is MaterializationOutcome.AUTHORITY_UNKNOWN
    assert rules.add_calls == 0


@pytest.mark.parametrize(
    "interaction_outcome,expected",
    [
        (InteractionOutcome.INVALID, MaterializationOutcome.INTERACTION_INVALID),
        (InteractionOutcome.UNKNOWN, MaterializationOutcome.INTERACTION_UNKNOWN),
    ],
)
def test_interaction_failures_short_circuit_decision(interaction_outcome, expected):
    decisions = FakeDecisions()
    rules = MemoryRules()
    result = service(
        catalogue=FakeCatalogue(interaction_outcome),
        decisions=decisions,
        rules=rules,
    ).execute(command())
    assert result.outcome is expected
    assert decisions.calls == 0
    assert rules.add_calls == 0


def test_not_allowed_creates_no_rule():
    rules = MemoryRules()
    result = service(
        decisions=FakeDecisions(DecisionOutcome.NOT_ALLOWED), rules=rules
    ).execute(command())
    assert result.outcome is MaterializationOutcome.NOT_ALLOWED
    assert rules.add_calls == 0
    assert not rules.by_identity


def test_unknown_decision_is_distinct_from_not_allowed_and_creates_no_rule():
    rules = MemoryRules()
    result = service(
        decisions=FakeDecisions(DecisionOutcome.UNKNOWN), rules=rules
    ).execute(command())
    assert result.outcome is MaterializationOutcome.DECISION_UNKNOWN
    assert result.outcome is not MaterializationOutcome.NOT_ALLOWED
    assert rules.add_calls == 0


def test_decision_subject_mismatch_fails_closed():
    other = RuleSemanticIdentity(SOURCE, DEST, UUID(int=99))
    rules = MemoryRules()
    result = service(decisions=FakeDecisions(subject=other), rules=rules).execute(command())
    assert result.outcome is MaterializationOutcome.DECISION_SUBJECT_MISMATCH
    assert rules.add_calls == 0


def test_semantic_identity_is_value_equal_and_each_member_is_identity_defining():
    identity = command().semantic_identity
    assert identity == RuleSemanticIdentity(SOURCE, DEST, DCS)
    assert identity != RuleSemanticIdentity(UUID(int=10), DEST, DCS)
    assert identity != RuleSemanticIdentity(SOURCE, UUID(int=11), DCS)
    assert identity != RuleSemanticIdentity(SOURCE, DEST, UUID(int=12))


def test_semantic_identity_and_materialized_rule_are_immutable():
    result = service().execute(command())
    with pytest.raises(FrozenInstanceError):
        result.rule.semantic_identity.source_component_deployment_id = UUID(int=13)
    with pytest.raises(FrozenInstanceError):
        result.rule.semantic_identity = RuleSemanticIdentity(UUID(int=13), DEST, DCS)


def test_different_semantic_identity_materializes_different_rule():
    rules = MemoryRules()
    ids = iter([RULE, UUID(int=5)])
    use_case = service(rules=rules, new_rule_id=lambda: next(ids))
    first = use_case.execute(command())
    second = use_case.execute(command(dcs_contract_revision_id=UUID(int=12)))
    assert first.outcome is MaterializationOutcome.MATERIALIZED
    assert second.outcome is MaterializationOutcome.MATERIALIZED
    assert first.rule.rule_id != second.rule.rule_id
    assert len(rules.by_identity) == 2


def test_authority_check_uses_explicit_propose_connectivity_action():
    authority = FakeAuthority()
    result = service(authority=authority).execute(command())
    assert result.outcome is MaterializationOutcome.MATERIALIZED
    assert authority.last_check["action"] is AuthorityAction.PROPOSE_CONNECTIVITY
    assert authority.last_check["actor_id"] == "actor-1"
    assert authority.last_check["scope"] == "scope-1"
    assert authority.last_check["effective_time"] == NOW
