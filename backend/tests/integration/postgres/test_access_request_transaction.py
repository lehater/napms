import os
from datetime import datetime, timezone
from uuid import UUID

import psycopg
import pytest

from napms.contexts.access_policy.infrastructure.persistence.postgres.migration import (
    migrate as migrate_access_policy,
)
from napms.contexts.access_policy.infrastructure.persistence.postgres.repository import (
    PostgresAccessPolicyRepository,
)
from napms.contexts.application_communication_catalogue.infrastructure.persistence.postgres.migration import (
    migrate as migrate_acc,
)
from napms.contexts.application_deployment.infrastructure.persistence.postgres.migration import (
    migrate as migrate_deployment,
)
from napms.contexts.authority_management.application.service import RequireScopedAuthority
from napms.contexts.authority_management.domain.model import AuthorityGrant, Principal
from napms.contexts.access_policy.domain.model import (
    AccessRequest,
    AccessSubject,
    RequestAuthorityEvidence,
    AuthorizationEvidence,
    JustificationAssociation,
    PolicyRule,
)
from napms.platform.database.policy_materialization import PostgresPolicyMaterialization
from napms.contexts.business_connectivity.infrastructure.persistence.postgres.migration import (
    migrate as migrate_business,
)
from napms.contexts.business_connectivity.infrastructure.persistence.postgres.repository import (
    PostgresBusinessProcessRepository,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.migration import (
    migrate as migrate_resource,
)
from napms.platform.database.access_request_submission import PostgresAccessRequestSubmission


pytestmark = pytest.mark.postgres
DSN = os.environ["NAPMS_TEST_POSTGRES_DSN"]


@pytest.fixture(autouse=True)
def fresh_schemas() -> None:
    with psycopg.connect(DSN) as connection:
        for schema in (
            "access_policy",
            "business_connectivity",
            "application_deployment",
            "application_communication_catalogue",
            "resource_catalogue",
        ):
            connection.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
        migrate_resource(connection)
        migrate_acc(connection)
        migrate_deployment(connection)
        migrate_business(connection)
        migrate_access_policy(connection)


def seed_journey() -> dict[str, UUID]:
    ids = {
        "source_resource": UUID(int=1),
        "destination_resource": UUID(int=2),
        "application": UUID(int=3),
        "source_component": UUID(int=4),
        "destination_component": UUID(int=5),
        "interaction": UUID(int=6),
        "revision": UUID(int=7),
        "source_deployment": UUID(int=8),
        "destination_deployment": UUID(int=9),
        "process": UUID(int=10),
        "need": UUID(int=11),
        "clause": UUID(int=12),
    }
    with psycopg.connect(DSN) as connection:
        connection.execute(
            """
            INSERT INTO resource_catalogue.resource
                (resource_ref, display_name, authority_scope_ref, version)
            VALUES (%s, 'source', 'scope:source', 1),
                   (%s, 'destination', 'scope:destination', 1)
            """,
            (ids["source_resource"], ids["destination_resource"]),
        )
        connection.execute(
            """
            INSERT INTO application_communication_catalogue.application
                (application_ref, name, version)
            VALUES (%s, 'Orders', 1)
            """,
            (ids["application"],),
        )
        connection.execute(
            """
            INSERT INTO application_communication_catalogue.component
                (component_ref, application_ref, name)
            VALUES (%s, %s, 'source'),
                   (%s, %s, 'destination')
            """,
            (
                ids["source_component"],
                ids["application"],
                ids["destination_component"],
                ids["application"],
            ),
        )
        connection.execute(
            """
            INSERT INTO application_communication_catalogue.interaction
                (interaction_ref, source_component_ref, destination_component_ref,
                 purpose, version)
            VALUES (%s, %s, %s, 'orders', 2)
            """,
            (
                ids["interaction"],
                ids["source_component"],
                ids["destination_component"],
            ),
        )
        connection.execute(
            """
            INSERT INTO application_communication_catalogue.interaction_revision
                (revision_ref, interaction_ref, revision_no, created_by_subject)
            VALUES (%s, %s, 1, 'subject:author')
            """,
            (ids["revision"], ids["interaction"]),
        )
        connection.execute(
            """
            INSERT INTO application_communication_catalogue.interaction_traffic_clause
                (clause_ref, revision_ref, clause_ordinal, ip_protocol)
            VALUES (%s, %s, 0, 1)
            """,
            (ids["clause"], ids["revision"]),
        )
        connection.execute(
            """
            INSERT INTO application_deployment.component_deployment
                (deployment_ref, component_ref, resource_ref)
            VALUES (%s, %s, %s), (%s, %s, %s)
            """,
            (
                ids["source_deployment"],
                ids["source_component"],
                ids["source_resource"],
                ids["destination_deployment"],
                ids["destination_component"],
                ids["destination_resource"],
            ),
        )
        connection.execute(
            """
            INSERT INTO business_connectivity.business_process
                (process_ref, name, version)
            VALUES (%s, 'Fulfillment', 1)
            """,
            (ids["process"],),
        )
        connection.execute(
            """
            INSERT INTO business_connectivity.connectivity_need
                (need_ref, process_ref, interaction_ref,
                 participant_component_ref, business_basis,
                 status, created_by_subject)
            VALUES (%s, %s, %s, %s, 'orders', 'ACTIVE', 'subject:business')
            """,
            (
                ids["need"],
                ids["process"],
                ids["interaction"],
                ids["source_component"],
            ),
        )
    return ids


def test_submit_request_uses_one_transaction_and_exact_scoped_authority() -> None:
    ids = seed_journey()
    refs = iter((UUID(int=100), UUID(int=101), UUID(int=102)))
    principal = Principal(
        subject="subject:alice",
        authority_grants=(AuthorityGrant(action="access.request", scope="scope:source"),),
    )
    submission = PostgresAccessRequestSubmission(
        dsn=DSN,
        authority=RequireScopedAuthority(),
        new_ref=lambda: next(refs),
    )

    request = submission.submit(
        principal=principal,
        source_deployment_ref=ids["source_deployment"],
        destination_deployment_ref=ids["destination_deployment"],
        interaction_revision_ref=ids["revision"],
        need_ref=ids["need"],
    )

    persisted = PostgresAccessPolicyRepository(DSN).get_request(request.request_ref)
    assert persisted == request
    assert request.validated_business_process_version == 1
    assert tuple(item.scope_ref for item in request.authority_evidence) == ("scope:source",)


def test_current_need_lock_blocks_retirement_until_owner_transaction_ends() -> None:
    ids = seed_journey()
    first = psycopg.connect(DSN)
    second = psycopg.connect(DSN)
    try:
        locked = PostgresBusinessProcessRepository.lock_current_need_in(first, ids["need"])
        assert locked is not None

        second.execute("SET lock_timeout = '100ms'")
        with pytest.raises(psycopg.errors.LockNotAvailable):
            second.execute(
                """
                UPDATE business_connectivity.connectivity_need
                SET status = 'RETIRED'
                WHERE need_ref = %s
                """,
                (ids["need"],),
            )
        second.rollback()

        first.commit()
        second.execute(
            """
            UPDATE business_connectivity.connectivity_need
            SET status = 'RETIRED'
            WHERE need_ref = %s
            """,
            (ids["need"],),
        )
        second.commit()
    finally:
        first.close()
        second.close()


def seed_materializable_rule(*, with_addresses: bool) -> tuple[dict[str, UUID], UUID]:
    ids = seed_journey()
    rule_ref = UUID(int=300)
    request_ref = UUID(int=301)
    now = datetime.now(timezone.utc)
    request = AccessRequest.submit(
        request_ref=request_ref,
        access_subject=AccessSubject(
            source_deployment_ref=ids["source_deployment"],
            destination_deployment_ref=ids["destination_deployment"],
            interaction_revision_ref=ids["revision"],
        ),
        initial_need_ref=ids["need"],
        validated_business_process_version=1,
        submitter_subject="subject:requester",
        submitted_at=now,
        authority_evidence=(
            RequestAuthorityEvidence(
                evidence_ref=UUID(int=302),
                scope_ref="scope:source",
                action="access.request",
                grant_effective_from=None,
                grant_effective_until=None,
                evaluated_at=now,
            ),
        ),
    )
    policy = PostgresAccessPolicyRepository(DSN)
    policy.add_request(request)
    rule = PolicyRule.create_allowed(
        rule_ref=rule_ref,
        access_subject=request.access_subject,
        authorization_evidence=AuthorizationEvidence(
            evidence_ref=UUID(int=303),
            access_request_ref=request_ref,
            external_decision_ref="decision:materialization",
            decided_by_subject="subject:approver",
            decided_at=now,
        ),
        justification=JustificationAssociation(
            association_ref=UUID(int=304),
            need_ref=ids["need"],
            attached_at=now,
            attached_by_subject="subject:approver",
            source_access_request_ref=request_ref,
        ),
        history_ref=UUID(int=305),
    )
    policy.add_rule(rule)
    if with_addresses:
        with psycopg.connect(DSN) as connection:
            connection.execute(
                """
                INSERT INTO resource_catalogue.resource_endpoint(endpoint_ref, resource_ref)
                VALUES (%s, %s), (%s, %s)
                """,
                (UUID(int=306), ids["source_resource"], UUID(int=307), ids["destination_resource"]),
            )
            connection.execute(
                """
                INSERT INTO resource_catalogue.resource_endpoint_address_history
                    (address_fact_ref, endpoint_ref, address_kind, address_value,
                     effective_from, changed_by_subject)
                VALUES (%s, %s, 'HOST', '10.0.0.1', %s, 'subject:network'),
                       (%s, %s, 'HOST', '10.0.0.2', %s, 'subject:network')
                """,
                (UUID(int=308), UUID(int=306), now, UUID(int=309), UUID(int=307), now),
            )
    return ids, rule_ref


def export_principal() -> Principal:
    return Principal(
        subject="subject:exporter",
        authority_grants=(
            AuthorityGrant(action="policy.export", scope="scope:source"),
            AuthorityGrant(action="policy.export", scope="scope:destination"),
        ),
    )


def test_policy_materialization_resolves_addresses_and_emits_provenance() -> None:
    _, rule_ref = seed_materializable_rule(with_addresses=True)
    result = PostgresPolicyMaterialization(dsn=DSN).materialize(
        principal=export_principal(),
        rule_refs=(rule_ref,),
    )

    assert result.status == "COMPLETE"
    assert result.issues == ()
    assert len(result.rows) == 1
    assert result.rows[0]["technicalStatus"] == "READY"
    assert result.rows[0]["sourceResourceName"] == "source"
    assert result.rows[0]["destinationResourceName"] == "destination"
    assert result.rows[0]["sourceAddress"] == "10.0.0.1"
    assert result.rows[0]["destinationAddress"] == "10.0.0.2"
    assert result.rows[0]["ipProtocol"] == 1
    assert {item["scopeRef"] for item in result.export_authority_evidence} == {
        "scope:source",
        "scope:destination",
    }
    assert result.rule_provenance[0]["policyRuleRef"] == str(rule_ref)


def test_policy_materialization_keeps_policy_row_when_address_is_missing() -> None:
    _, rule_ref = seed_materializable_rule(with_addresses=False)
    result = PostgresPolicyMaterialization(dsn=DSN).materialize(
        principal=export_principal(),
        rule_refs=(rule_ref,),
    )

    assert result.status == "COMPLETE"
    assert len(result.rows) == 1
    row = result.rows[0]
    assert row["technicalStatus"] == "INCOMPLETE"
    assert row["sourceResourceName"] == "source"
    assert row["destinationResourceName"] == "destination"
    assert row["sourceAddress"] is None
    assert row["destinationAddress"] is None
    assert row["ipProtocol"] == 1
    assert [issue.reason for issue in result.issues] == ["current address realization incomplete"]
    assert {item["scopeRef"] for item in result.export_authority_evidence} == {
        "scope:source",
        "scope:destination",
    }
