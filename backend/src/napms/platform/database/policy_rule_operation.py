from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import psycopg

from napms.contexts.access_policy.application.service import AccessPolicyService
from napms.contexts.access_policy.domain.model import (
    AccessSubject,
    EffectiveWindow,
    PolicyRule,
    RuleEffectState,
)
from napms.contexts.access_policy.infrastructure.persistence.postgres.repository import (
    PostgresAccessPolicyRepository,
)


class PostgresPolicyRuleOperation:
    def __init__(self, *, dsn: str, new_ref: Callable[[], UUID] = uuid4) -> None:
        self._dsn = dsn
        self._new_ref = new_ref

    def set_state(
        self,
        *,
        rule_ref: UUID,
        effect_state: RuleEffectState,
        effective_window: EffectiveWindow,
        changed_by_subject: str,
        expected_version: int,
    ) -> PolicyRule:
        with psycopg.connect(self._dsn) as connection:
            repository = _TransactionRuleRepository(connection)
            service = AccessPolicyService(
                requests=repository,
                rules=repository,
                new_ref=self._new_ref,
            )
            return service.set_policy_rule_operational_state(
                rule_ref=rule_ref,
                effect_state=effect_state,
                effective_window=effective_window,
                changed_by_subject=changed_by_subject,
                changed_at=self._now(connection),
                expected_version=expected_version,
            )

    @staticmethod
    def _now(connection: psycopg.Connection[Any]) -> datetime:
        row = connection.execute("SELECT transaction_timestamp()").fetchone()
        assert row is not None
        return row[0]


class _TransactionRuleRepository:
    def __init__(self, connection: psycopg.Connection[Any]) -> None:
        self._connection = connection

    def add_request(self, request) -> None:
        PostgresAccessPolicyRepository.add_request_in(self._connection, request)

    def get_request(self, request_ref):
        return PostgresAccessPolicyRepository.get_request_in(self._connection, request_ref)

    def save_request(self, request, *, expected_version: int) -> None:
        PostgresAccessPolicyRepository.save_request_in(
            self._connection, request, expected_version=expected_version
        )

    def find_rule_by_subject(self, subject: AccessSubject) -> PolicyRule | None:
        return PostgresAccessPolicyRepository.find_rule_by_subject_in(self._connection, subject)

    def add_rule(self, rule: PolicyRule) -> None:
        PostgresAccessPolicyRepository.add_rule_in(self._connection, rule)

    def save_rule(self, rule: PolicyRule, *, expected_version: int) -> None:
        PostgresAccessPolicyRepository.save_rule_in(
            self._connection, rule, expected_version=expected_version
        )

    def get_rule(self, rule_ref: UUID) -> PolicyRule | None:
        return PostgresAccessPolicyRepository.get_rule_in(self._connection, rule_ref)
