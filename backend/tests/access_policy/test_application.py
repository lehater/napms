from datetime import datetime, timedelta, timezone
from uuid import UUID

from napms.contexts.access_policy.application.service import AccessPolicyService
from napms.contexts.access_policy.domain.model import (
    AccessRequest,
    AccessSubject,
    EffectiveWindow,
    PermissionDecision,
    PolicyRule,
    RequestAuthorityEvidence,
    RuleEffectState,
)


NOW = datetime(2026, 9, 21, 16, 0, tzinfo=timezone.utc)
SUBJECT = AccessSubject(
    source_deployment_ref=UUID(int=1),
    destination_deployment_ref=UUID(int=2),
    interaction_revision_ref=UUID(int=3),
)


class Requests:
    def __init__(self) -> None:
        self.values: dict[UUID, AccessRequest] = {}

    def add_request(self, request: AccessRequest) -> None:
        self.values[request.request_ref] = request

    def get_request(self, request_ref: UUID) -> AccessRequest | None:
        return self.values.get(request_ref)

    def save_request(self, request: AccessRequest, *, expected_version: int) -> None:
        assert self.values[request.request_ref].version == expected_version
        self.values[request.request_ref] = request


class Rules:
    def __init__(self) -> None:
        self.values: dict[UUID, PolicyRule] = {}

    def find_rule_by_subject(self, subject: AccessSubject) -> PolicyRule | None:
        return next((item for item in self.values.values() if item.access_subject == subject), None)

    def add_rule(self, rule: PolicyRule) -> None:
        self.values[rule.rule_ref] = rule

    def save_rule(self, rule: PolicyRule, *, expected_version: int) -> None:
        assert self.values[rule.rule_ref].version == expected_version
        self.values[rule.rule_ref] = rule

    def get_rule(self, rule_ref: UUID) -> PolicyRule | None:
        return self.values.get(rule_ref)


class Refs:
    def __init__(self, *values: UUID) -> None:
        self.values = iter(values)

    def __call__(self) -> UUID:
        return next(self.values)


def evidence() -> tuple[RequestAuthorityEvidence, ...]:
    return (
        RequestAuthorityEvidence(
            evidence_ref=UUID(int=100),
            scope_ref="scope:a",
            action="access.request",
            grant_effective_from=None,
            grant_effective_until=None,
            evaluated_at=NOW,
        ),
    )


def test_denied_decision_creates_no_rule() -> None:
    requests = Requests()
    rules = Rules()
    service = AccessPolicyService(
        requests=requests,
        rules=rules,
        new_ref=Refs(UUID(int=10)),
    )
    request = service.submit_validated_request(
        access_subject=SUBJECT,
        initial_need_ref=UUID(int=11),
        validated_business_process_version=1,
        submitter_subject="subject:alice",
        submitted_at=NOW,
        authority_evidence=evidence(),
    )

    decided, rule = service.record_permission_decision(
        request_ref=request.request_ref,
        result=PermissionDecision.DENIED,
        decided_by_subject="subject:approver",
        decided_at=NOW + timedelta(minutes=1),
        expected_version=request.version,
    )

    assert decided.decision_result is PermissionDecision.DENIED
    assert rule is None
    assert rules.values == {}


def test_repeated_allowed_decisions_converge_on_one_rule() -> None:
    requests = Requests()
    rules = Rules()
    service = AccessPolicyService(
        requests=requests,
        rules=rules,
        new_ref=Refs(
            UUID(int=10),
            UUID(int=20),
            UUID(int=21),
            UUID(int=22),
            UUID(int=23),
            UUID(int=30),
            UUID(int=31),
            UUID(int=32),
        ),
    )
    first = service.submit_validated_request(
        access_subject=SUBJECT,
        initial_need_ref=UUID(int=11),
        validated_business_process_version=1,
        submitter_subject="subject:alice",
        submitted_at=NOW,
        authority_evidence=evidence(),
    )
    _, first_rule = service.record_permission_decision(
        request_ref=first.request_ref,
        result=PermissionDecision.ALLOWED,
        decided_by_subject="subject:approver",
        decided_at=NOW + timedelta(minutes=1),
        expected_version=first.version,
    )

    second = service.submit_validated_request(
        access_subject=SUBJECT,
        initial_need_ref=UUID(int=12),
        validated_business_process_version=2,
        submitter_subject="subject:bob",
        submitted_at=NOW + timedelta(minutes=2),
        authority_evidence=evidence(),
    )
    _, second_rule = service.record_permission_decision(
        request_ref=second.request_ref,
        result=PermissionDecision.ALLOWED,
        decided_by_subject="subject:approver",
        decided_at=NOW + timedelta(minutes=3),
        expected_version=second.version,
    )

    assert first_rule is not None
    assert second_rule is not None
    assert first_rule.rule_ref == second_rule.rule_ref
    assert len(rules.values) == 1
    persisted = next(iter(rules.values.values()))
    assert len(persisted.authorization_evidence) == 2
    assert {item.need_ref for item in persisted.justifications} == {UUID(int=11), UUID(int=12)}


def test_operational_change_needs_no_new_permission_decision() -> None:
    requests = Requests()
    rules = Rules()
    service = AccessPolicyService(
        requests=requests,
        rules=rules,
        new_ref=Refs(
            UUID(int=10), UUID(int=20), UUID(int=21), UUID(int=22), UUID(int=23), UUID(int=24)
        ),
    )
    request = service.submit_validated_request(
        access_subject=SUBJECT,
        initial_need_ref=UUID(int=11),
        validated_business_process_version=1,
        submitter_subject="subject:alice",
        submitted_at=NOW,
        authority_evidence=evidence(),
    )
    _, rule = service.record_permission_decision(
        request_ref=request.request_ref,
        result=PermissionDecision.ALLOWED,
        decided_by_subject="subject:approver",
        decided_at=NOW + timedelta(minutes=1),
        expected_version=request.version,
    )
    assert rule is not None

    updated = service.set_policy_rule_operational_state(
        rule_ref=rule.rule_ref,
        effect_state=RuleEffectState.INACTIVE,
        effective_window=EffectiveWindow(),
        changed_by_subject="subject:operator",
        changed_at=NOW + timedelta(minutes=2),
        expected_version=rule.version,
    )

    assert updated.rule_ref == rule.rule_ref
    assert updated.effect_state is RuleEffectState.INACTIVE
    assert len(updated.authorization_evidence) == 1
