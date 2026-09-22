from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from uuid import UUID, uuid4

from napms.contexts.access_policy.application.ports import (
    AccessPolicyNotFound,
    AccessPolicyVersionConflict,
    AccessRequestRepository,
    PolicyRuleRepository,
)
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


class AccessPolicyService:
    def __init__(
        self,
        *,
        requests: AccessRequestRepository,
        rules: PolicyRuleRepository,
        new_ref: Callable[[], UUID] = uuid4,
    ) -> None:
        self._requests = requests
        self._rules = rules
        self._new_ref = new_ref

    def submit_validated_request(
        self,
        *,
        access_subject: AccessSubject,
        initial_need_ref: UUID,
        validated_business_process_version: int,
        submitter_subject: str,
        submitted_at: datetime,
        authority_evidence: tuple[RequestAuthorityEvidence, ...],
    ) -> AccessRequest:
        request = AccessRequest.submit(
            request_ref=self._new_ref(),
            access_subject=access_subject,
            initial_need_ref=initial_need_ref,
            validated_business_process_version=validated_business_process_version,
            submitter_subject=submitter_subject,
            submitted_at=submitted_at,
            authority_evidence=authority_evidence,
        )
        self._requests.add_request(request)
        return request

    def record_permission_decision(
        self,
        *,
        request_ref: UUID,
        result: PermissionDecision,
        decided_by_subject: str,
        decided_at: datetime,
        expected_version: int,
        external_decision_ref: str | None = None,
    ) -> tuple[AccessRequest, PolicyRule | None]:
        request = self._required_request(request_ref)
        if request.version != expected_version:
            raise AccessPolicyVersionConflict(str(request_ref))
        decided = request.decide(
            result=result,
            decided_by_subject=decided_by_subject,
            decided_at=decided_at,
            external_decision_ref=external_decision_ref,
        )
        self._requests.save_request(decided, expected_version=expected_version)

        if result is PermissionDecision.DENIED:
            return decided, None

        authorization = AuthorizationEvidence(
            evidence_ref=self._new_ref(),
            access_request_ref=decided.request_ref,
            external_decision_ref=decided.external_decision_ref,
            decided_by_subject=decided_by_subject,
            decided_at=decided_at,
        )
        justification = JustificationAssociation(
            association_ref=self._new_ref(),
            need_ref=decided.initial_need_ref,
            attached_at=decided_at,
            attached_by_subject=decided_by_subject,
            source_access_request_ref=decided.request_ref,
        )
        existing = self._rules.find_rule_by_subject(decided.access_subject)
        if existing is None:
            rule = PolicyRule.create_allowed(
                rule_ref=self._new_ref(),
                access_subject=decided.access_subject,
                authorization_evidence=authorization,
                justification=justification,
                history_ref=self._new_ref(),
            )
            self._rules.add_rule(rule)
            return decided, rule

        updated = existing.add_authorization_evidence(authorization)
        updated = updated.attach_justification(justification)
        self._rules.save_rule(updated, expected_version=existing.version)
        return decided, updated

    def attach_justification(
        self,
        *,
        rule_ref: UUID,
        need_ref: UUID,
        attached_by_subject: str,
        attached_at: datetime,
    ) -> PolicyRule:
        rule = self._required_rule(rule_ref)
        updated = rule.attach_justification(
            JustificationAssociation(
                association_ref=self._new_ref(),
                need_ref=need_ref,
                attached_at=attached_at,
                attached_by_subject=attached_by_subject,
                source_access_request_ref=None,
            )
        )
        if updated != rule:
            self._rules.save_rule(updated, expected_version=rule.version)
        return updated

    def set_policy_rule_operational_state(
        self,
        *,
        rule_ref: UUID,
        effect_state: RuleEffectState,
        effective_window: EffectiveWindow,
        changed_by_subject: str,
        changed_at: datetime,
        expected_version: int,
    ) -> PolicyRule:
        rule = self._required_rule(rule_ref)
        if rule.version != expected_version:
            raise AccessPolicyVersionConflict(str(rule_ref))
        updated = rule.set_operational_state(
            effect_state=effect_state,
            effective_window=effective_window,
            history_ref=self._new_ref(),
            changed_by_subject=changed_by_subject,
            changed_at=changed_at,
        )
        self._rules.save_rule(updated, expected_version=expected_version)
        return updated

    def _required_request(self, request_ref: UUID) -> AccessRequest:
        request = self._requests.get_request(request_ref)
        if request is None:
            raise AccessPolicyNotFound(str(request_ref))
        return request

    def _required_rule(self, rule_ref: UUID) -> PolicyRule:
        rule = self._rules.get_rule(rule_ref)
        if rule is None:
            raise AccessPolicyNotFound(str(rule_ref))
        return rule
