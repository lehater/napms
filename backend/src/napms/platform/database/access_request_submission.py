from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import psycopg

from napms.contexts.access_policy.application.service import AccessPolicyService
from napms.contexts.access_policy.application.submission import AccessRequestSubmissionService
from napms.contexts.access_policy.domain.model import AccessRequest, AccessSubject, PolicyRule
from napms.contexts.access_policy.infrastructure.persistence.postgres.repository import (
    PostgresAccessPolicyRepository,
)
from napms.contexts.application_communication_catalogue.application.ports import (
    ResolvedInteractionRevision,
)
from napms.contexts.application_communication_catalogue.domain.model import Interaction
from napms.contexts.application_communication_catalogue.infrastructure.persistence.postgres.repository import (
    PostgresApplicationCommunicationCatalogue,
)
from napms.contexts.application_deployment.domain.model import ComponentDeployment
from napms.contexts.application_deployment.infrastructure.persistence.postgres.repository import (
    PostgresComponentDeploymentRepository,
)
from napms.contexts.authority_management.application.service import RequireScopedAuthority
from napms.contexts.authority_management.domain.model import Principal
from napms.contexts.business_connectivity.domain.model import ConnectivityNeed
from napms.contexts.business_connectivity.infrastructure.persistence.postgres.repository import (
    PostgresBusinessProcessRepository,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.repository import (
    PostgresResourceCatalogueRepository,
)


class _TransactionOwnerPorts:
    def __init__(self, connection: psycopg.Connection[Any]) -> None:
        self._connection = connection

    def lock_current_need(self, need_ref: UUID) -> tuple[ConnectivityNeed, int] | None:
        return PostgresBusinessProcessRepository.lock_current_need_in(
            self._connection,
            need_ref,
        )

    def resolve_deployment(self, deployment_ref: UUID) -> ComponentDeployment | None:
        return PostgresComponentDeploymentRepository.resolve_deployment_in(
            self._connection,
            deployment_ref,
        )

    def resolve_revision(self, revision_ref: UUID) -> ResolvedInteractionRevision | None:
        return PostgresApplicationCommunicationCatalogue.resolve_revision_in(
            self._connection,
            revision_ref,
        )

    def get_interaction(self, interaction_ref: UUID) -> Interaction | None:
        return PostgresApplicationCommunicationCatalogue.resolve_interaction_in(
            self._connection,
            interaction_ref,
        )

    def resolve_authority_scope(self, resource_ref: UUID) -> str | None:
        return PostgresResourceCatalogueRepository.resolve_authority_scope_in(
            self._connection,
            resource_ref,
        )


class _TransactionAccessPolicyRepository:
    def __init__(self, connection: psycopg.Connection[Any]) -> None:
        self._connection = connection

    def add_request(self, request: AccessRequest) -> None:
        PostgresAccessPolicyRepository.add_request_in(self._connection, request)

    def get_request(self, request_ref: UUID) -> AccessRequest | None:
        return PostgresAccessPolicyRepository.get_request_in(self._connection, request_ref)

    def save_request(self, request: AccessRequest, *, expected_version: int) -> None:
        PostgresAccessPolicyRepository.save_request_in(
            self._connection,
            request,
            expected_version=expected_version,
        )

    def find_rule_by_subject(self, subject: AccessSubject) -> PolicyRule | None:
        return PostgresAccessPolicyRepository.find_rule_by_subject_in(
            self._connection,
            subject,
        )

    def add_rule(self, rule: PolicyRule) -> None:
        PostgresAccessPolicyRepository.add_rule_in(self._connection, rule)

    def save_rule(self, rule: PolicyRule, *, expected_version: int) -> None:
        PostgresAccessPolicyRepository.save_rule_in(
            self._connection,
            rule,
            expected_version=expected_version,
        )

    def get_rule(self, rule_ref: UUID) -> PolicyRule | None:
        return PostgresAccessPolicyRepository.get_rule_in(self._connection, rule_ref)


class PostgresAccessRequestSubmission:
    def __init__(
        self,
        *,
        dsn: str,
        authority: RequireScopedAuthority,
        new_ref: Callable[[], UUID] = uuid4,
    ) -> None:
        self._dsn = dsn
        self._authority = authority
        self._new_ref = new_ref

    def submit(
        self,
        *,
        principal: Principal,
        source_deployment_ref: UUID,
        destination_deployment_ref: UUID,
        interaction_revision_ref: UUID,
        need_ref: UUID,
    ) -> AccessRequest:
        with psycopg.connect(self._dsn) as connection:
            admission_at = self._admission_at(connection)
            owners = _TransactionOwnerPorts(connection)
            policy_repository = _TransactionAccessPolicyRepository(connection)
            policy = AccessPolicyService(
                requests=policy_repository,
                rules=policy_repository,
                new_ref=self._new_ref,
            )
            submission = AccessRequestSubmissionService(
                policy=policy,
                needs=owners,
                deployments=owners,
                revisions=owners,
                interactions=owners,
                resource_scopes=owners,
                authority=self._authority,
                new_ref=self._new_ref,
            )
            return submission.submit(
                principal=principal,
                source_deployment_ref=source_deployment_ref,
                destination_deployment_ref=destination_deployment_ref,
                interaction_revision_ref=interaction_revision_ref,
                need_ref=need_ref,
                admission_at=admission_at,
            )

    @staticmethod
    def _admission_at(connection: psycopg.Connection[Any]) -> datetime:
        row = connection.execute("SELECT transaction_timestamp()").fetchone()
        assert row is not None
        return row[0]
