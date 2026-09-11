from datetime import datetime, timezone
from uuid import UUID

import pytest

from napms.access_policy.application.ports import (
    AccessRuleReadScopeOptions,
    AuthorityCheck,
    TernaryOutcome,
)
from napms.access_policy.application.read_rules import (
    AccessRuleDetailOutcome,
    GetAuthorizedAccessRule,
    ListAuthorizedAccessRules,
)
from napms.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    ProposalProvenance,
    RuleSemanticIdentity,
)


NOW = datetime(2026, 9, 9, 8, 0, tzinfo=timezone.utc)


def rule(index: int, scope: str) -> AccessRule:
    identity = RuleSemanticIdentity(
        UUID(int=index * 10 + 1),
        UUID(int=index * 10 + 2),
        UUID(int=index * 10 + 3),
    )
    return AccessRule.materialized_from_allowed_decision(
        rule_id=UUID(int=index),
        semantic_identity=identity,
        decision=DecisionReference(
            subject=identity,
            result=ConnectivityDecisionResult.ALLOWED,
            decision_id=f"decision-{index}",
        ),
        proposal_provenance=ProposalProvenance(
            actor_id="proposer",
            authority_scope=scope,
            effective_time=NOW,
            authority_reference=f"proposal-auth-{index}",
            catalogue_reference=f"catalogue-{index}",
        ),
    )


class FakeReadScopes:
    def __init__(self, permitted=(), ambiguous=()):
        self.permitted = permitted
        self.ambiguous = ambiguous
        self.calls = []

    def list_effective_read_rule_scopes(self, **kwargs):
        self.calls.append(kwargs)
        return AccessRuleReadScopeOptions(self.permitted, self.ambiguous)


class MemoryRules:
    def __init__(self, rules=()):
        self.rules = tuple(rules)
        self.list_calls = []

    def get_by_id(self, rule_id):
        return next((item for item in self.rules if item.rule_id == rule_id), None)

    def list_by_governance_scopes(self, scopes, *, offset, limit):
        self.list_calls.append((scopes, offset, limit))
        visible = tuple(item for item in self.rules if item.governance_scope in scopes)
        return visible[offset : offset + limit]


class FakeAuthority:
    def __init__(self, decisions):
        self.decisions = decisions
        self.calls = []

    def check(self, **kwargs):
        self.calls.append(kwargs)
        outcome, reference = self.decisions[kwargs["action"].value]
        return AuthorityCheck(outcome, reference)


def test_list_returns_only_rules_from_unambiguous_read_scopes():
    rules = MemoryRules(
        (
            rule(1, "scope-a"),
            rule(2, "scope-b"),
            rule(3, "scope-c"),
        )
    )
    scopes = FakeReadScopes(("scope-a", "scope-c"), ("scope-b",))
    result = ListAuthorizedAccessRules(
        read_authority=scopes,
        rules=rules,
    ).execute(
        actor_id="actor-1",
        effective_time=NOW,
        page=1,
        page_size=50,
    )

    assert tuple(item.rule_id for item in result.rules) == (UUID(int=1), UUID(int=3))
    assert result.ambiguous_scopes == ("scope-b",)
    assert rules.list_calls == [(("scope-a", "scope-c"), 0, 51)]


def test_list_with_no_permitted_scopes_returns_no_rule_data():
    rules = MemoryRules((rule(1, "scope-a"),))
    result = ListAuthorizedAccessRules(
        read_authority=FakeReadScopes((), ("scope-a",)),
        rules=rules,
    ).execute(
        actor_id="actor-1",
        effective_time=NOW,
    )

    assert result.rules == ()
    assert result.ambiguous_scopes == ("scope-a",)
    assert rules.list_calls == []


def test_list_paging_is_bounded_and_has_more():
    rules = MemoryRules(tuple(rule(index, "scope-a") for index in range(1, 4)))
    result = ListAuthorizedAccessRules(
        read_authority=FakeReadScopes(("scope-a",)),
        rules=rules,
    ).execute(
        actor_id="actor-1",
        effective_time=NOW,
        page=1,
        page_size=2,
    )

    assert tuple(item.rule_id for item in result.rules) == (UUID(int=1), UUID(int=2))
    assert result.has_more is True
    assert rules.list_calls == [(("scope-a",), 0, 3)]


@pytest.mark.parametrize(("page", "page_size"), ((0, 50), (1, 0), (1, 101)))
def test_list_rejects_invalid_pagination(page, page_size):
    query = ListAuthorizedAccessRules(
        read_authority=FakeReadScopes(("scope-a",)),
        rules=MemoryRules(),
    )
    with pytest.raises(ValueError):
        query.execute(
            actor_id="actor-1",
            effective_time=NOW,
            page=page,
            page_size=page_size,
        )


def test_detail_checks_read_authority_then_separate_state_mutation_admission():
    item = rule(1, "scope-a")
    authority = FakeAuthority(
        {
            "ReadAccessRule": (TernaryOutcome.PERMITTED, "read-auth-1"),
            "SetRuleOperationalState": (
                TernaryOutcome.DENIED,
                None,
            ),
            "SetRuleEffectiveWindow": (
                TernaryOutcome.PERMITTED,
                "window-auth-1",
            ),
        }
    )

    result = GetAuthorizedAccessRule(
        authority=authority,
        rules=MemoryRules((item,)),
    ).execute(
        rule_id=item.rule_id,
        actor_id="actor-1",
        effective_time=NOW,
    )

    assert result.outcome is AccessRuleDetailOutcome.FOUND
    assert result.rule == item
    assert result.read_authority_reference == "read-auth-1"
    assert result.state_mutation_admission is TernaryOutcome.DENIED
    assert result.effective_window_mutation_admission is TernaryOutcome.PERMITTED
    assert [call["action"].value for call in authority.calls] == [
        "ReadAccessRule",
        "SetRuleOperationalState",
        "SetRuleEffectiveWindow",
    ]


@pytest.mark.parametrize(
    ("read_outcome", "reference", "expected"),
    (
        (TernaryOutcome.DENIED, None, AccessRuleDetailOutcome.AUTHORITY_DENIED),
        (TernaryOutcome.UNKNOWN, None, AccessRuleDetailOutcome.AUTHORITY_UNKNOWN),
        (TernaryOutcome.PERMITTED, None, AccessRuleDetailOutcome.AUTHORITY_UNKNOWN),
    ),
)
def test_detail_read_authority_fails_closed_without_rule_data(
    read_outcome,
    reference,
    expected,
):
    item = rule(1, "scope-a")
    authority = FakeAuthority(
        {
            "ReadAccessRule": (read_outcome, reference),
            "SetRuleOperationalState": (TernaryOutcome.PERMITTED, "mutation-auth"),
            "SetRuleEffectiveWindow": (TernaryOutcome.PERMITTED, "window-auth"),
        }
    )

    result = GetAuthorizedAccessRule(
        authority=authority,
        rules=MemoryRules((item,)),
    ).execute(
        rule_id=item.rule_id,
        actor_id="actor-1",
        effective_time=NOW,
    )

    assert result.outcome is expected
    assert result.rule is None
    assert len(authority.calls) == 1


def test_detail_unknown_rule_short_circuits_authority():
    authority = FakeAuthority({})
    result = GetAuthorizedAccessRule(
        authority=authority,
        rules=MemoryRules(),
    ).execute(
        rule_id=UUID(int=999),
        actor_id="actor-1",
        effective_time=NOW,
    )

    assert result.outcome is AccessRuleDetailOutcome.RULE_NOT_FOUND
    assert authority.calls == []


def test_state_mutation_admission_permitted_without_provenance_fails_closed():
    item = rule(1, "scope-a")
    authority = FakeAuthority(
        {
            "ReadAccessRule": (TernaryOutcome.PERMITTED, "read-auth"),
            "SetRuleOperationalState": (TernaryOutcome.PERMITTED, None),
            "SetRuleEffectiveWindow": (TernaryOutcome.PERMITTED, "window-auth"),
        }
    )
    result = GetAuthorizedAccessRule(
        authority=authority,
        rules=MemoryRules((item,)),
    ).execute(
        rule_id=item.rule_id,
        actor_id="actor-1",
        effective_time=NOW,
    )

    assert result.outcome is AccessRuleDetailOutcome.FOUND
    assert result.state_mutation_admission is TernaryOutcome.UNKNOWN



def test_effective_window_admission_permitted_without_provenance_fails_closed():
    item = rule(1, "scope-a")
    authority = FakeAuthority(
        {
            "ReadAccessRule": (TernaryOutcome.PERMITTED, "read-auth"),
            "SetRuleOperationalState": (TernaryOutcome.PERMITTED, "state-auth"),
            "SetRuleEffectiveWindow": (TernaryOutcome.PERMITTED, None),
        }
    )
    result = GetAuthorizedAccessRule(
        authority=authority,
        rules=MemoryRules((item,)),
    ).execute(
        rule_id=item.rule_id,
        actor_id="actor-1",
        effective_time=NOW,
    )

    assert result.outcome is AccessRuleDetailOutcome.FOUND
    assert result.effective_window_mutation_admission is TernaryOutcome.UNKNOWN
