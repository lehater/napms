from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any\nfrom uuid import UUID, uuid4

import psycopg

from napms.contexts.access_policy.application.service import AccessPolicyService
from napms.contexts.access_policy.domain.model import (
    AccessRequest,
    AccessSubject,
    PermissionDecision,
    PolicyRule,
)
from napms.contexts.access_policy.infrastructure.persistence.postgres.repository import (
    PostgresAccessPolicyRepository,
)


class PostgresAccessRequestDecision:
    def __init__(
        self,
        *,
        dsn: str,
        new_ref: Callable[[], UUID] = uuid4,
    ) -> None:
        self._dsn = dsn
        self._new_ref = new_ref

    def decide(
        self,
        *,
        request_ref: UUID,
        result: PermissionDecision,
        decided_by_subject: str,
        expected_version: int,
        external_decision_ref: str | None = None,
    ) -> tuple[AccessRequest, PolicyRule | None]:
        with psycopg.connect(self._dsn) as connection:
            repository = _TransactionRepository(connection)
            service = AccessPolicyService(
                requests=repository,
                rules=repository,
                new_ref=self._new_ref,
            )
            return service.record_permission_decision(
                request_ref=request_ref,
                result=result,
                decided_by_subject=decided_by_subject,
                decided_at=self._decision_at(connection),
                expected_version=expected_version,
                external_decision_ref=external_decision_ref,
            )

    @staticmethod
    def _decision_at(connection: psycopg.Connection[Any]) -> datetime:
        row = connection.execute("SELECT transaction_timestamp()").fetchone()
        assert row is not None
        return row[0]


class _TransactionRepository:
    def __init__(self, connection: psycopg.Connection[Any]) -> None:
        self._connection = connection

    def add_request(self, request: AccessRequest) -> None:
        PostgresAccessPolicyRepository.add_request_in(self._connection, request)

    def get_request(self, request_ref: UUID) -> AccessRequest | None:
        return PostgresAccessPolicyRepository.get_request_in(self._connection, request_ref)

    def save_request(self, request: AccessRequest, *, expected_version: int) -> None:
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
