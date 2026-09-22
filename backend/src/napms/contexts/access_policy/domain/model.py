from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from uuid import UUID


class PermissionDecision(str, Enum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"


class RuleEffectState(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@dataclass(frozen=True)
class AccessSubject:
    source_deployment_ref: UUID
    destination_deployment_ref: UUID
    interaction_revision_ref: UUID


@dataclass(frozen=True)
class RequestAuthorityEvidence:
    evidence_ref: UUID
    scope_ref: str
    action: str
    grant_effective_from: datetime | None
    grant_effective_until: datetime | None
    evaluated_at: datetime


@dataclass(frozen=True)
class AccessRequest:
    request_ref: UUID
    access_subject: AccessSubject
    initial_need_ref: UUID
    validated_business_process_version: int
    submitter_subject: str
    submitted_at: datetime
    authority_evidence: tuple[RequestAuthorityEvidence, ...]
    version: int = 1
    decision_result: PermissionDecision | None = None
    external_decision_ref: str | None = None
    decided_by_subject: str | None = None
    decided_at: datetime | None = None

    @classmethod
    def submit(
        cls,
        *,
        request_ref: UUID,
        access_subject: AccessSubject,
        initial_need_ref: UUID,
        validated_business_process_version: int,
        submitter_subject: str,
        submitted_at: datetime,
        authority_evidence: tuple[RequestAuthorityEvidence, ...],
    ) -> AccessRequest:
        if not submitter_subject.strip():
            raise ValueError("submitter_subject must be non-empty")
        _require_aware(submitted_at)
        if not authority_evidence:
            raise ValueError("request authority evidence must be non-empty")
        return cls(
            request_ref=request_ref,
            access_subject=access_subject,
            initial_need_ref=initial_need_ref,
            validated_business_process_version=validated_business_process_version,
            submitter_subject=submitter_subject,
            submitted_at=submitted_at,
            authority_evidence=authority_evidence,
        )

    def decide(
        self,
        *,
        result: PermissionDecision,
        decided_by_subject: str,
        decided_at: datetime,
        external_decision_ref: str | None = None,
    ) -> AccessRequest:
        if self.decision_result is not None:
            raise ValueError("access request already has a final decision")
        if not decided_by_subject.strip():
            raise ValueError("decided_by_subject must be non-empty")
        _require_aware(decided_at)
        return replace(
            self,
            decision_result=result,
            external_decision_ref=_optional_text(external_decision_ref),
            decided_by_subject=decided_by_subject,
            decided_at=decided_at,
            version=self.version + 1,
        )


@dataclass(frozen=True)
class EffectiveWindow:
    effective_from: datetime | None = None
    effective_until: datetime | None = None

    def __post_init__(self) -> None:
        if self.effective_from is not None:
            _require_aware(self.effective_from)
        if self.effective_until is not None:
            _require_aware(self.effective_until)
        if (
            self.effective_from is not None
            and self.effective_until is not None
            and self.effective_until <= self.effective_from
        ):
            raise ValueError("effective_until must be later than effective_from")

    def contains(self, evaluated_at: datetime) -> bool:
        _require_aware(evaluated_at)
        if self.effective_from is not None and evaluated_at < self.effective_from:
            return False
        if self.effective_until is not None and evaluated_at >= self.effective_until:
            return False
        return True


@dataclass(frozen=True)
class AuthorizationEvidence:
    evidence_ref: UUID
    access_request_ref: UUID
    external_decision_ref: str | None
    decided_by_subject: str
    decided_at: datetime


@dataclass(frozen=True)
class JustificationAssociation:
    association_ref: UUID
    need_ref: UUID
    attached_at: datetime
    attached_by_subject: str
    source_access_request_ref: UUID | None


@dataclass(frozen=True)
class OperationalHistory:
    history_ref: UUID
    rule_version: int
    effect_state: RuleEffectState
    effective_window: EffectiveWindow
    changed_by_subject: str
    changed_at: datetime


@dataclass(frozen=True)
class PolicyRule:
    rule_ref: UUID
    access_subject: AccessSubject
    effect_state: RuleEffectState
    effective_window: EffectiveWindow
    version: int
    authorization_evidence: tuple[AuthorizationEvidence, ...] = ()
    justifications: tuple[JustificationAssociation, ...] = ()
    operational_history: tuple[OperationalHistory, ...] = ()

    @classmethod
    def create_allowed(
        cls,
        *,
        rule_ref: UUID,
        access_subject: AccessSubject,
        authorization_evidence: AuthorizationEvidence,
        justification: JustificationAssociation,
        history_ref: UUID,
    ) -> PolicyRule:
        initial_window = EffectiveWindow()
        initial_history = OperationalHistory(
            history_ref=history_ref,
            rule_version=1,
            effect_state=RuleEffectState.ACTIVE,
            effective_window=initial_window,
            changed_by_subject=authorization_evidence.decided_by_subject,
            changed_at=authorization_evidence.decided_at,
        )
        return cls(
            rule_ref=rule_ref,
            access_subject=access_subject,
            effect_state=RuleEffectState.ACTIVE,
            effective_window=initial_window,
            version=1,
            authorization_evidence=(authorization_evidence,),
            justifications=(justification,),
            operational_history=(initial_history,),
        )

    def add_authorization_evidence(
        self,
        evidence: AuthorizationEvidence,
    ) -> PolicyRule:
        if any(
            item.access_request_ref == evidence.access_request_ref
            for item in self.authorization_evidence
        ):
            return self
        return replace(
            self,
            authorization_evidence=self.authorization_evidence + (evidence,),
        )

    def attach_justification(
        self,
        association: JustificationAssociation,
    ) -> PolicyRule:
        if any(item.need_ref == association.need_ref for item in self.justifications):
            return self
        return replace(self, justifications=self.justifications + (association,))

    def set_operational_state(
        self,
        *,
        effect_state: RuleEffectState,
        effective_window: EffectiveWindow,
        history_ref: UUID,
        changed_by_subject: str,
        changed_at: datetime,
    ) -> PolicyRule:
        if not changed_by_subject.strip():
            raise ValueError("changed_by_subject must be non-empty")
        _require_aware(changed_at)
        next_version = self.version + 1
        history = OperationalHistory(
            history_ref=history_ref,
            rule_version=next_version,
            effect_state=effect_state,
            effective_window=effective_window,
            changed_by_subject=changed_by_subject,
            changed_at=changed_at,
        )
        return replace(
            self,
            effect_state=effect_state,
            effective_window=effective_window,
            version=next_version,
            operational_history=self.operational_history + (history,),
        )

    def is_effective(self, evaluated_at: datetime) -> bool:
        return self.effect_state is RuleEffectState.ACTIVE and self.effective_window.contains(
            evaluated_at
        )


def _require_aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None
