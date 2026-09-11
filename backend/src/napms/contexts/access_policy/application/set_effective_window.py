from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from napms.contexts.access_policy.application.ports import (
    AccessRuleRepository,
    AuthorityAction,
    AuthorityPort,
    TernaryOutcome,
)
from napms.contexts.access_policy.domain.model import AccessRule, EffectiveWindow


class EffectiveWindowMutationOutcome(str, Enum):
    UPDATED = "Updated"
    RULE_NOT_FOUND = "RuleNotFound"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    ALREADY_IN_REQUESTED_WINDOW = "AlreadyInRequestedWindow"


@dataclass(frozen=True, slots=True)
class SetRuleEffectiveWindow:
    rule_id: UUID
    window: EffectiveWindow | None
    actor_id: str
    effective_time: datetime


@dataclass(frozen=True, slots=True)
class EffectiveWindowMutationResult:
    outcome: EffectiveWindowMutationOutcome
    rule: AccessRule | None = None


class SetAccessRuleEffectiveWindow:
    def __init__(self, *, authority: AuthorityPort, rules: AccessRuleRepository) -> None:
        self._authority = authority
        self._rules = rules

    def execute(self, command: SetRuleEffectiveWindow) -> EffectiveWindowMutationResult:
        rule = self._rules.get_by_id(command.rule_id)
        if rule is None:
            return EffectiveWindowMutationResult(
                EffectiveWindowMutationOutcome.RULE_NOT_FOUND
            )

        authority = self._authority.check(
            actor_id=command.actor_id,
            action=AuthorityAction.SET_RULE_EFFECTIVE_WINDOW,
            scope=rule.governance_scope,
            effective_time=command.effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return EffectiveWindowMutationResult(
                EffectiveWindowMutationOutcome.AUTHORITY_DENIED
            )
        if authority.outcome is TernaryOutcome.UNKNOWN or authority.authority_reference is None:
            return EffectiveWindowMutationResult(
                EffectiveWindowMutationOutcome.AUTHORITY_UNKNOWN
            )

        if rule.effective_window == command.window:
            return EffectiveWindowMutationResult(
                EffectiveWindowMutationOutcome.ALREADY_IN_REQUESTED_WINDOW,
                rule,
            )

        updated = rule.with_effective_window(
            window=command.window,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
            authority_reference=authority.authority_reference,
        )
        self._rules.save(updated)
        self._rules.commit()
        return EffectiveWindowMutationResult(
            EffectiveWindowMutationOutcome.UPDATED,
            updated,
        )
