from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from napms.contexts.access_policy.domain.model import (
    AccessRequest,
    AccessSubject,
    AuthorizationEvidence,
    EffectiveWindow,
    JustificationAssociation,
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


def request() -> AccessRequest:
    return AccessRequest.submit(
        request_ref=UUID(int=10),
        access_subject=SUBJECT,
        initial_need_ref=UUID(int=11),
        validated_business_process_version=7,
        submitter_subject="subject:alice",
        submitted_at=NOW,
        authority_evidence=(
            RequestAuthorityEvidence(
                evidence_ref=UUID(int=12),
                scope_ref="scope:a",
                action="access.request",
                grant_effective_from=None,
                grant_effective_until=None,
                evaluated_at=NOW,
            ),
        ),
    )


def test_access_request_is_finalized_once_and_preserves_access_subject() -> None:
    value = request()
    decided = value.decide(
        result=PermissionDecision.ALLOWED,
        decided_by_subject="subject:approver",
        decided_at=NOW + timedelta(minutes=1),
    )

    assert decided.access_subject == SUBJECT
    assert decided.version == 2
    with pytest.raises(ValueError):
        decided.decide(
            result=PermissionDecision.DENIED,
            decided_by_subject="subject:approver",
            decided_at=NOW + timedelta(minutes=2),
        )


def test_rule_identity_survives_operational_state_and_window_changes() -> None:
    evidence = AuthorizationEvidence(
        evidence_ref=UUID(int=20),
        access_request_ref=UUID(int=10),
        external_decision_ref=None,
        decided_by_subject="subject:approver",
        decided_at=NOW,
    )
    justification = JustificationAssociation(
        association_ref=UUID(int=21),
        need_ref=UUID(int=11),
        attached_at=NOW,
        attached_by_subject="subject:approver",
        source_access_request_ref=UUID(int=10),
    )
    rule = PolicyRule.create_allowed(
        rule_ref=UUID(int=22),
        access_subject=SUBJECT,
        authorization_evidence=evidence,
        justification=justification,
        history_ref=UUID(int=23),
    )
    updated = rule.set_operational_state(
        effect_state=RuleEffectState.INACTIVE,
        effective_window=EffectiveWindow(
            effective_from=NOW + timedelta(hours=1),
            effective_until=NOW + timedelta(hours=2),
        ),
        history_ref=UUID(int=24),
        changed_by_subject="subject:operator",
        changed_at=NOW + timedelta(minutes=5),
    )

    assert updated.rule_ref == rule.rule_ref
    assert updated.access_subject == rule.access_subject
    assert updated.effect_state is RuleEffectState.INACTIVE
    assert updated.version == 2
    assert len(updated.operational_history) == 2


def test_effective_window_is_inclusive_from_and_exclusive_until() -> None:
    window = EffectiveWindow(
        effective_from=NOW,
        effective_until=NOW + timedelta(hours=1),
    )
    assert window.contains(NOW)
    assert window.contains(NOW + timedelta(minutes=59))
    assert not window.contains(NOW + timedelta(hours=1))
