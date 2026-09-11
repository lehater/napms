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
from napms.contexts.access_policy.domain.model import AccessRule, OperationalState


class OperationalStateMutationOutcome(str, Enum):
    UPDATED = "Updated"
    RULE_NOT_FOUND = "RuleNotFound"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    ALREADY_IN_REQUESTED_STATE = "AlreadyInRequestedState"


@dataclass(frozen=True, slots=True)
class SetRuleOperationalState:
    rule_id: UUID
    target_state: OperationalState
    actor_id: str
    effective_time: datetime


@dataclass(frozen=True, slots=True)
class OperationalStateMutationResult:
    outcome: OperationalStateMutationOutcome
    rule: AccessRule | None = None


class SetAccessRuleOperationalState:
    def __init__(self, *, authority: AuthorityPort, rules: AccessRuleRepository) -> None:
        self._authority = authority
        self._rules = rules

    def execute(self, command: SetRuleOperationalState) -> OperationalStateMutationResult:
        rule = self._rules.get_by_id(command.rule_id)
        if rule is None:
            return OperationalStateMutationResult(
                OperationalStateMutationOutcome.RULE_NOT_FOUND
            )

        authority = self._authority.check(
            actor_id=command.actor_id,
            action=AuthorityAction.SET_RULE_OPERATIONAL_STATE,
            scope=rule.governance_scope,
            effective_time=command.effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return OperationalStateMutationResult(
                OperationalStateMutationOutcome.AUTHORITY_DENIED
            )
        if authority.outcome is TernaryOutcome.UNKNOWN or authority.authority_reference is None:
            return OperationalStateMutationResult(
                OperationalStateMutationOutcome.AUTHORITY_UNKNOWN
            )

        if rule.operational_state is command.target_state:
            return OperationalStateMutationResult(
                OperationalStateMutationOutcome.ALREADY_IN_REQUESTED_STATE,
                rule,
            )

        updated = rule.with_operational_state(
            target_state=command.target_state,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
            authority_reference=authority.authority_reference,
        )
        self._rules.save(updated)
        self._rules.commit()
        return OperationalStateMutationResult(
            OperationalStateMutationOutcome.UPDATED,
            updated,
        )
