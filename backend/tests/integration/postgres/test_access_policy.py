import os
from datetime import datetime, timezone
from uuid import UUID

import psycopg
import pytest

from napms.contexts.access_policy.domain.model import (
    AccessRequest,
    AccessSubject,
    AuthorizationEvidence,
    JustificationAssociation,
    PolicyRule,
    RequestAuthorityEvidence,
)
from napms.contexts.access_policy.infrastructure.persistence.postgres.migration import migrate
from napms.contexts.access_policy.infrastructure.persistence.postgres.repository import (
    PostgresAccessPolicyRepository,
)


pytestmark = pytest.mark.postgres
DSN = os.environ["NAPMS_TEST_POSTGRES_DSN"]
NOW = datetime(2026, 9, 21, 16, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def fresh_schema() -> None:
    with psycopg.connect(DSN) as connection:
        connection.execute("DROP SCHEMA IF EXISTS access_policy CASCADE")
        migrate(connection)


def test_request_and_rule_evidence_round_trip() -> None:
    repository = PostgresAccessPolicyRepository(DSN)
    subject = AccessSubject(
        source_deployment_ref=UUID(int=1),
        destination_deployment_ref=UUID(int=2),
        interaction_revision_ref=UUID(int=3),
    )
    request = AccessRequest.submit(
        request_ref=UUID(int=10),
        access_subject=subject,
        initial_need_ref=UUID(int=11),
        validated_business_process_version=4,
        submitter_subject="subject:alice",
        submitted_at=NOW,
        authority_evidence=(
            RequestAuthorityEvidence(
                evidence_ref=UUID(int=12),
                scope_ref="scope:a",
                action="access.request",
                grant_effective_from=None,
                grant_effective_until=None,
                evaluated_at=NOW,
            ),
        ),
    )
    repository.add_request(request)

    evidence = AuthorizationEvidence(
        evidence_ref=UUID(int=20),
        access_request_ref=request.request_ref,
        external_decision_ref="decision-1",
        decided_by_subject="subject:approver",
        decided_at=NOW,
    )
    justification = JustificationAssociation(
        association_ref=UUID(int=21),
        need_ref=request.initial_need_ref,
        attached_at=NOW,
        attached_by_subject="subject:approver",
        source_access_request_ref=request.request_ref,
    )
    rule = PolicyRule.create_allowed(
        rule_ref=UUID(int=22),
        access_subject=subject,
        authorization_evidence=evidence,
        justification=justification,
        history_ref=UUID(int=23),
    )
    repository.add_rule(rule)

    assert repository.get_request(request.request_ref) == request
    assert repository.get_rule(rule.rule_ref) == rule
    assert repository.find_rule_by_subject(subject) == rule
