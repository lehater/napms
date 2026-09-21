from __future__ import annotations

from datetime import datetime
from uuid import UUID

import psycopg

from napms.contexts.access_policy.application.ports import AccessPolicyNotFound, AccessPolicyVersionConflict
from napms.contexts.access_policy.application.service import AccessPolicyService
from napms.contexts.access_policy.domain.model import AccessSubject, PolicyRule
from napms.contexts.access_policy.infrastructure.persistence.postgres.repository import (
    PostgresAccessPolicyRepository,
)
from napms.contexts.business_connectivity.infrastructure.persistence.postgres.repository import (
    PostgresBusinessConnectivityRepository,
)


class JustificationRejected(Exception):
    pass


class PostgresPolicyRuleJustification:
    def __init__(self, *, dsn: str) -> None:
        self._dsn = dsn

    def attach(
        self,
        *,
        rule_ref: UUID,
        need_ref: UUID,
        attached_by_subject: str,
        expected_version: int,
    ) -> PolicyRule:
        with psycopg.connect(self._dsn) as connection:
            current = PostgresBusinessConnectivityRepository.lock_current_need_in(
                connection, need_ref
            )
            if current is None:
                raise JustificationRejected(str(need_ref))
            repository = _TransactionRuleRepository(connection)
            rule = repository.get_rule(rule_ref)
            if rule is None:
                raise AccessPolicyNotFound(str(rule_ref))
            if rule.version != expected_version:
                raise AccessPolicyVersionConflict(str(rule_ref))
            return AccessPolicyService(
                requests=repository,
                rules=repository,
            ).attach_justification(
                rule_ref=rule_ref,
                need_ref=need_ref,
                attached_by_subject=attached_by_subject,
                attached_at=self._attached_at(connection),
            )

    @staticmethod
    def _attached_at(connection: psycopg.Connection[object]) -> datetime:
        row = connection.execute("SELECT transaction_timestamp()").fetchone()
        assert row is not None
        return row[0]


class _TransactionRuleRepository:
    def __init__(self, connection: psycopg.Connection[object]) -> None:
        self._connection = connection

    def get_rule(self, rule_ref: UUID) -> PolicyRule | None:
        return PostgresAccessPolicyRepository.get_rule_in(self._connection, rule_ref)

    def find_rule_by_subject(self, subject: AccessSubject) -> PolicyRule | None:
        return PostgresAccessPolicyRepository.find_rule_by_subject_in(self._connection, subject)

    def add_rule(self, rule: PolicyRule) -> None:
        PostgresAccessPolicyRepository.add_rule_in(self._connection, rule)

    def save_rule(self, rule: PolicyRule, *, expected_version: int) -> None:
        PostgresAccessPolicyRepository.save_rule_in(
            self._connection, rule, expected_version=expected_version
        )

    def add_request(self, request) -> None:
        PostgresAccessPolicyRepository.add_request_in(self._connection, request)

    def get_request(self, request_ref):
        return PostgresAccessPolicyRepository.get_request_in(self._connection, request_ref)

    def save_request(self, request, *, expected_version: int) -> None:
        PostgresAccessPolicyRepository.save_request_in(
            self._connection, request, expected_version=expected_version
        )
