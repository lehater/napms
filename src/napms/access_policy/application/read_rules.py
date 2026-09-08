from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from napms.access_policy.application.ports import (
    AccessRuleReadAuthorityDiscoveryPort,
    AccessRuleRepository,
    AuthorityAction,
    AuthorityPort,
    TernaryOutcome,
)
from napms.access_policy.domain.model import AccessRule


class AccessRuleDetailOutcome(str, Enum):
    FOUND = "Found"
    RULE_NOT_FOUND = "RuleNotFound"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"


@dataclass(frozen=True, slots=True)
class AccessRulePage:
    rules: tuple[AccessRule, ...]
    page: int
    page_size: int
    has_more: bool
    ambiguous_scopes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AccessRuleDetailResult:
    outcome: AccessRuleDetailOutcome
    rule: AccessRule | None = None
    read_authority_reference: str | None = None
    state_mutation_admission: TernaryOutcome | None = None
    effective_window_mutation_admission: TernaryOutcome | None = None


class ListAuthorizedAccessRules:
    def __init__(
        self,
        *,
        read_authority: AccessRuleReadAuthorityDiscoveryPort,
        rules: AccessRuleRepository,
    ) -> None:
        self._read_authority = read_authority
        self._rules = rules

    def execute(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
        page: int = 1,
        page_size: int = 50,
    ) -> AccessRulePage:
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")

        scopes = self._read_authority.list_effective_read_rule_scopes(
            actor_id=actor_id,
            effective_time=effective_time,
        )
        if not scopes.permitted_scopes:
            return AccessRulePage(
                rules=(),
                page=page,
                page_size=page_size,
                has_more=False,
                ambiguous_scopes=scopes.ambiguous_scopes,
            )

        rows = self._rules.list_by_governance_scopes(
            scopes.permitted_scopes,
            offset=(page - 1) * page_size,
            limit=page_size + 1,
        )
        return AccessRulePage(
            rules=rows[:page_size],
            page=page,
            page_size=page_size,
            has_more=len(rows) > page_size,
            ambiguous_scopes=scopes.ambiguous_scopes,
        )


class GetAuthorizedAccessRule:
    def __init__(self, *, authority: AuthorityPort, rules: AccessRuleRepository) -> None:
        self._authority = authority
        self._rules = rules

    def execute(
        self,
        *,
        rule_id: UUID,
        actor_id: str,
        effective_time: datetime,
    ) -> AccessRuleDetailResult:
        rule = self._rules.get_by_id(rule_id)
        if rule is None:
            return AccessRuleDetailResult(AccessRuleDetailOutcome.RULE_NOT_FOUND)

        read = self._authority.check(
            actor_id=actor_id,
            action=AuthorityAction.READ_ACCESS_RULE,
            scope=rule.governance_scope,
            effective_time=effective_time,
        )
        if read.outcome is TernaryOutcome.DENIED:
            return AccessRuleDetailResult(AccessRuleDetailOutcome.AUTHORITY_DENIED)
        if read.outcome is TernaryOutcome.UNKNOWN or read.authority_reference is None:
            return AccessRuleDetailResult(AccessRuleDetailOutcome.AUTHORITY_UNKNOWN)

        state_mutation = self._authority.check(
            actor_id=actor_id,
            action=AuthorityAction.SET_RULE_OPERATIONAL_STATE,
            scope=rule.governance_scope,
            effective_time=effective_time,
        )
        state_mutation_admission = state_mutation.outcome
        if (
            state_mutation.outcome is TernaryOutcome.PERMITTED
            and state_mutation.authority_reference is None
        ):
            state_mutation_admission = TernaryOutcome.UNKNOWN

        window_mutation = self._authority.check(
            actor_id=actor_id,
            action=AuthorityAction.SET_RULE_EFFECTIVE_WINDOW,
            scope=rule.governance_scope,
            effective_time=effective_time,
        )
        window_mutation_admission = window_mutation.outcome
        if (
            window_mutation.outcome is TernaryOutcome.PERMITTED
            and window_mutation.authority_reference is None
        ):
            window_mutation_admission = TernaryOutcome.UNKNOWN

        return AccessRuleDetailResult(
            AccessRuleDetailOutcome.FOUND,
            rule=rule,
            read_authority_reference=read.authority_reference,
            state_mutation_admission=state_mutation_admission,
            effective_window_mutation_admission=window_mutation_admission,
        )
