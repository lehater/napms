import os
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
        authority_grants=(
            AuthorityGrant(action="access.request", scope="scope:source"),
            AuthorityGrant(action="access.request", scope="scope:destination"),
        ),
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
    assert {item.scope_ref for item in request.authority_evidence} == {
        "scope:source",
        "scope:destination",
    }


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
