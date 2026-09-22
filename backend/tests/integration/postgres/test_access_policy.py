import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import psycopg
import pytest

from napms.contexts.access_policy.application.queries import (
    AccessRequestCatalogueQuery,
    AccessRequestSortField,
    SortDirection,
)
from napms.contexts.access_policy.domain.model import (
    AccessRequest,
    AccessSubject,
    AuthorizationEvidence,
    JustificationAssociation,
    PermissionDecision,
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


def test_access_request_catalogue_query_applies_filters_sort_and_paging() -> None:
    repository = PostgresAccessPolicyRepository(DSN)
    source_a = UUID(int=101)
    source_b = UUID(int=102)
    destination = UUID(int=201)

    def make_request(
        ref: int,
        *,
        source: UUID,
        submitted_offset: int,
        decision: PermissionDecision | None,
    ) -> AccessRequest:
        submitted_at = NOW + timedelta(minutes=submitted_offset)
        value = AccessRequest.submit(
            request_ref=UUID(int=ref),
            access_subject=AccessSubject(source, destination, UUID(int=301)),
            initial_need_ref=UUID(int=401),
            validated_business_process_version=1,
            submitter_subject="subject:alice",
            submitted_at=submitted_at,
            authority_evidence=(
                RequestAuthorityEvidence(
                    UUID(int=ref + 1000),
                    "scope:a",
                    "access.request",
                    None,
                    None,
                    submitted_at,
                ),
            ),
        )
        if decision is None:
            return value
        return value.decide(
            result=decision,
            decided_by_subject="subject:approver",
            decided_at=submitted_at + timedelta(minutes=1),
        )

    allowed_old = make_request(
        501,
        source=source_a,
        submitted_offset=1,
        decision=PermissionDecision.ALLOWED,
    )
    allowed_new = make_request(
        502,
        source=source_a,
        submitted_offset=2,
        decision=PermissionDecision.ALLOWED,
    )
    denied = make_request(
        503,
        source=source_b,
        submitted_offset=3,
        decision=PermissionDecision.DENIED,
    )
    for value in (allowed_old, allowed_new, denied):
        repository.add_request(value)

    first = repository.query_requests(
        AccessRequestCatalogueQuery(
            source_deployment_ref=source_a,
            destination_deployment_ref=destination,
            decision_result=PermissionDecision.ALLOWED,
            sort_by=AccessRequestSortField.SUBMITTED_AT,
            sort_direction=SortDirection.DESC,
            page=1,
            page_size=1,
        )
    )
    assert first.total == 2
    assert [item.request_ref for item in first.items] == [allowed_new.request_ref]

    second = repository.query_requests(
        AccessRequestCatalogueQuery(
            source_deployment_ref=source_a,
            decision_result=PermissionDecision.ALLOWED,
            sort_by=AccessRequestSortField.SUBMITTED_AT,
            sort_direction=SortDirection.DESC,
            page=2,
            page_size=1,
        )
    )
    assert [item.request_ref for item in second.items] == [allowed_old.request_ref]

    searched = repository.query_requests(
        AccessRequestCatalogueQuery(search=str(denied.request_ref)[-8:])
    )
    assert searched.total == 1
    assert [item.request_ref for item in searched.items] == [denied.request_ref]
