from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from uuid import UUID, uuid4

import psycopg

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
    def __init__(
        self,
        *,
        dsn: str,
        new_ref: Callable[[], UUID] = uuid4,
    ) -> None:
        self._dsn = dsn
        self._new_ref = new_ref

    def attach(
        self,
        *,
        rule_ref: UUID,
        need_ref: UUID,
        attached_by_subject: str,
        expected_version: int,
    ) -> PolicyRule:
        with psycopg.connect(self._dsn) as connection:
            if (
                PostgresBusinessConnectivityRepository.lock_current_need_in(
                    connection, need_ref
                )
                is None
            ):
                raise JustificationRejected(str(need_ref))
            repository = _TransactionRuleRepository(connection)
            existing = repository.get_rule(rule_ref)
            if existing is None:
                from napms.contexts.access_policy.application.ports import AccessPolicyNotFound

                raise AccessPolicyNotFound(str(rule_ref))
            if existing.version != expected_version:
                from napms.contexts.access_policy.application.ports import (
                    AccessPolicyVersionConflict,
                )

                raise AccessPolicyVersionConflict(str(rule_ref))
            service = AccessPolicyService(
                requests=repository,
                rules=repository,
                new_ref=self._new_ref,
            )
            return service.attach_justification(
                rule_ref=rule_ref,
                need_ref=need_ref,
                attached_by_subject=attached_by_subject,
                attached_at=self._now(connection),
            )

    @staticmethod
    def _now(connection: psycopg.Connection[object]) -> datetime:
        row = connection.execute("SELECT transaction_timestamp()").fetchone()
        assert row is not None
        return row[0]


class _TransactionRuleRepository:
    def __init__(self, connection: psycopg.Connection[object]) -> None:
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
