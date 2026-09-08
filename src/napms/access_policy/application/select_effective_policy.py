from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from napms.access_policy.application.ports import (
    AccessRulePersistenceError,
    AccessRuleRepository,
    EffectivePolicyReadAuthorityDiscoveryPort,
    EffectivePolicyReadScopeOptions,
    AuthorityAction,
    AuthorityPort,
    TernaryOutcome,
)
from napms.access_policy.domain.model import AccessRule, DomainInvariantError


class EffectivePolicySelectionOutcome(str, Enum):
    SELECTED = "Selected"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"


@dataclass(frozen=True, slots=True)
class SelectEffectiveDesiredPolicy:
    scope: str
    as_of: datetime
    actor_id: str

    def __post_init__(self) -> None:
        if self.as_of.tzinfo is None or self.as_of.utcoffset() is None:
            raise DomainInvariantError("as_of must be an offset-aware datetime")


@dataclass(frozen=True, slots=True)
class EffectivePolicySelectionResult:
    outcome: EffectivePolicySelectionOutcome
    scope: str
    as_of: datetime
    rules: tuple[AccessRule, ...] = ()
    authority_reference: str | None = None


class DiscoverEffectivePolicyScopes:
    def __init__(
        self,
        *,
        authority: EffectivePolicyReadAuthorityDiscoveryPort,
    ) -> None:
        self._authority = authority

    def execute(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> EffectivePolicyReadScopeOptions:
        return self._authority.list_effective_policy_read_scopes(
            actor_id=actor_id,
            effective_time=effective_time,
        )


class SelectAccessPolicyEffectiveDesiredPolicy:
    def __init__(self, *, authority: AuthorityPort, rules: AccessRuleRepository) -> None:
        self._authority = authority
        self._rules = rules

    def execute(self, command: SelectEffectiveDesiredPolicy) -> EffectivePolicySelectionResult:
        authority = self._authority.check(
            actor_id=command.actor_id,
            action=AuthorityAction.READ_EFFECTIVE_DESIRED_POLICY,
            scope=command.scope,
            effective_time=command.as_of,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return EffectivePolicySelectionResult(
                EffectivePolicySelectionOutcome.AUTHORITY_DENIED,
                command.scope,
                command.as_of,
            )
        if authority.outcome is TernaryOutcome.UNKNOWN or authority.authority_reference is None:
            return EffectivePolicySelectionResult(
                EffectivePolicySelectionOutcome.AUTHORITY_UNKNOWN,
                command.scope,
                command.as_of,
            )

        candidates = self._rules.list_by_governance_scope(command.scope)
        if any(rule.governance_scope != command.scope for rule in candidates):
            raise AccessRulePersistenceError(
                "repository returned Rule outside requested governance scope"
            )

        effective = tuple(
            sorted(
                (
                    rule
                    for rule in candidates
                    if rule.contributes_effect_at(command.as_of)
                ),
                key=lambda rule: rule.rule_id,
            )
        )
        return EffectivePolicySelectionResult(
            EffectivePolicySelectionOutcome.SELECTED,
            command.scope,
            command.as_of,
            effective,
            authority.authority_reference,
        )
