import json
import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.access_policy_realization.adapters.catalogues import (
    CatalogueDomainKnowledgeAdapter,
)
from napms.access_policy_realization.adapters.technical_access_evidence import (
    TechnicalAccessEvidenceProjectionAdapter,
)
from napms.access_policy_realization.application.resolve import (
    ResolveTechnicalAccess,
)
from napms.access_policy_realization.domain.model import (
    ResolutionStatus,
)
from napms.application_catalogue.adapters.dcs_json_codec import (
    JsonDcsProjectionCodec,
)
from napms.application_catalogue.adapters.postgres import (
    PostgresApplicationCatalogueRepository,
)
from napms.composition.config import (
    ApplicationConfig,
    PostgresConfig,
)
from napms.composition.greenfield_postgres import (
    apply_greenfield_migrations,
)
from napms.composition.technical_access_evidence_postgres import (
    open_technical_access_evidence_scope,
)
from napms.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    PortConstraint,
    PortRange,
)
from napms.resource_catalogue.adapters.postgres import (
    PostgresResourceCatalogueRepository,
)
from napms.technical_access_evidence.adapters.local_import import (
    LocalEvidenceImportAdapter,
)
from napms.technical_access_evidence.application.read import (
    EvidenceSetDetailOutcome,
)
from napms.technical_access_evidence.application.record import (
    RecordEvidenceOutcome,
)


pytestmark = pytest.mark.postgres

AS_OF = datetime(
    2026,
    9,
    9,
    10,
    tzinfo=timezone.utc,
)
REALIZATION_CHANGE = AS_OF + timedelta(
    hours=2
)
SOURCE = UUID(int=1801)
DESTINATION = UUID(int=1802)
DCS = UUID(int=1803)
DCS_COMPETITOR = UUID(int=1804)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get(
        "NAPMS_TEST_POSTGRES_DSN"
    )
    if not dsn:
        pytest.skip(
            "NAPMS_TEST_POSTGRES_DSN is required "
            "for PostgreSQL integration tests"
        )
    return dsn


@pytest.fixture(scope="session")
def greenfield_config(postgres_dsn):
    config = ApplicationConfig(
        environment="local-dev",
        postgres=PostgresConfig(
            postgres_dsn
        ),
    )
    apply_greenfield_migrations(
        config
    )
    return config


@pytest.fixture(autouse=True)
def clean_i18(
    postgres_dsn,
    greenfield_config,
):
    with psycopg.connect(
        postgres_dsn,
        autocommit=True,
    ) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_technical_access_evidence.evidence_sets,
                napms_application_catalogue.deployment_resource_bindings,
                napms_application_catalogue.dcs_revisions,
                napms_application_catalogue.component_deployments,
                napms_resource_catalogue.resource_endpoints,
                napms_resource_catalogue.resource_realization_versions,
                napms_resource_catalogue.resources,
                napms_access_policy.access_rules,
                napms_connectivity_decision.connectivity_decisions
            CASCADE
            """
        )


def _dcs_payload():
    return JsonDcsProjectionCodec().encode(
        (
            DcsTrafficAlternative(
                protocol="tcp",
                source_ports=(
                    PortConstraint.any()
                ),
                destination_ports=(
                    PortConstraint.ranged(
                        PortRange(
                            443,
                            443,
                        )
                    )
                ),
            ),
        )
    )


def _seed_domain(
    connection,
    *,
    ambiguous=False,
):
    for deployment, provenance in (
        (
            SOURCE,
            "acc:source-deployment",
        ),
        (
            DESTINATION,
            "acc:destination-deployment",
        ),
    ):
        connection.execute(
            """
            INSERT INTO napms_application_catalogue.component_deployments (
                component_deployment_id,
                provenance_reference
            )
            VALUES (%s, %s)
            """,
            (
                deployment,
                provenance,
            ),
        )

    for revision in (
        (DCS, DCS_COMPETITOR)
        if ambiguous
        else (DCS,)
    ):
        connection.execute(
            """
            INSERT INTO napms_application_catalogue.dcs_revisions (
                revision_id,
                source_component_deployment_id,
                destination_component_deployment_id,
                projection_payload,
                provenance_reference
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                revision,
                SOURCE,
                DESTINATION,
                _dcs_payload(),
                (
                    "acc:dcs:"
                    + str(revision)
                ),
            ),
        )

    for (
        reference,
        deployment,
        resource,
    ) in (
        (
            "binding:source",
            SOURCE,
            "resource:source",
        ),
        (
            "binding:destination",
            DESTINATION,
            "resource:destination",
        ),
    ):
        connection.execute(
            """
            INSERT INTO napms_application_catalogue.deployment_resource_bindings (
                reference_id,
                component_deployment_id,
                resource_reference,
                valid_from,
                valid_to,
                provenance_reference
            )
            VALUES (%s, %s, %s, %s, NULL, %s)
            """,
            (
                reference,
                deployment,
                resource,
                AS_OF
                - timedelta(days=1),
                "acc:" + reference,
            ),
        )

    for resource in (
        "resource:source",
        "resource:destination",
    ):
        connection.execute(
            """
            INSERT INTO napms_resource_catalogue.resources (
                resource_reference,
                provenance_reference
            )
            VALUES (%s, %s)
            """,
            (
                resource,
                "rc:" + resource,
            ),
        )

    _seed_realization(
        connection,
        fact="fact:source:old",
        resource="resource:source",
        address="198.51.100.10",
        valid_from=(
            AS_OF
            - timedelta(days=1)
        ),
        valid_to=REALIZATION_CHANGE,
    )
    _seed_realization(
        connection,
        fact="fact:source:new",
        resource="resource:source",
        address="198.51.100.99",
        valid_from=REALIZATION_CHANGE,
        valid_to=None,
    )
    _seed_realization(
        connection,
        fact="fact:destination",
        resource="resource:destination",
        address="203.0.113.20",
        valid_from=(
            AS_OF
            - timedelta(days=1)
        ),
        valid_to=None,
    )


def _seed_realization(
    connection,
    *,
    fact,
    resource,
    address,
    valid_from,
    valid_to,
):
    connection.execute(
        """
        INSERT INTO napms_resource_catalogue.resource_realization_versions (
            fact_reference,
            resource_reference,
            valid_from,
            valid_to,
            provenance_reference
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            fact,
            resource,
            valid_from,
            valid_to,
            "rc:" + fact,
        ),
    )
    connection.execute(
        """
        INSERT INTO napms_resource_catalogue.resource_endpoints (
            fact_reference,
            endpoint_reference,
            technical_address
        )
        VALUES (%s, %s, %s)
        """,
        (
            fact,
            "endpoint:" + fact,
            address,
        ),
    )


def _import_document():
    return {
        "source_reference": (
            "i18-fixture"
        ),
        "source_scope_reference": (
            "scope-a"
        ),
        "source_capture_reference": (
            "capture-a"
        ),
        "evidence_time": {
            "kind": "Instant",
            "at": AS_OF.isoformat(),
        },
        "entries": [
            {
                "source_addresses": {
                    "kind": "Ranges",
                    "ranges": [
                        {
                            "first": "198.51.100.10",
                            "last": "198.51.100.10",
                        }
                    ],
                },
                "destination_addresses": {
                    "kind": "Ranges",
                    "ranges": [
                        {
                            "first": "203.0.113.20",
                            "last": "203.0.113.20",
                        }
                    ],
                },
                "protocol": "tcp",
                "source_ports": {
                    "kind": "Any"
                },
                "destination_ports": {
                    "kind": "Ranges",
                    "ranges": [
                        {
                            "first": 443,
                            "last": 443,
                        }
                    ],
                },
                "action": "Block",
                "source_entry_reference": (
                    "configured-rule-7"
                ),
                "source_position": 7,
            }
        ],
    }


def _record_and_read(
    greenfield_config,
):
    command = (
        LocalEvidenceImportAdapter()
        .normalize(
            json.dumps(
                _import_document()
            )
        )
    )
    with open_technical_access_evidence_scope(
        greenfield_config
    ) as scope:
        recorded = (
            scope.record_technical_access_evidence
            .execute(command)
        )
    assert (
        recorded.outcome
        is RecordEvidenceOutcome.RECORDED
    )
    evidence_set_id = (
        recorded.evidence_set.evidence_set_id
    )

    with open_technical_access_evidence_scope(
        greenfield_config
    ) as scope:
        detail = (
            scope.get_technical_access_evidence
            .execute(evidence_set_id)
        )
    assert (
        detail.outcome
        is EvidenceSetDetailOutcome.FOUND
    )
    return detail.evidence_set


def _resolver(connection):
    return ResolveTechnicalAccess(
        domain_knowledge=(
            CatalogueDomainKnowledgeAdapter(
                application_catalogue=(
                    PostgresApplicationCatalogueRepository(
                        connection
                    )
                ),
                resource_catalogue=(
                    PostgresResourceCatalogueRepository(
                        connection
                    )
                ),
                dcs_decoder=(
                    JsonDcsProjectionCodec()
                ),
            )
        )
    )


def test_durable_evidence_resolves_exactly_without_authority_side_effects(
    postgres_dsn,
    greenfield_config,
):
    with psycopg.connect(
        postgres_dsn
    ) as connection:
        _seed_domain(connection)
        connection.commit()

    evidence = _record_and_read(
        greenfield_config
    )
    projected = (
        TechnicalAccessEvidenceProjectionAdapter()
        .project_entry(
            evidence_set=evidence,
            evidence_entry_id=(
                evidence.entries[
                    0
                ].evidence_entry_id
            ),
        )
    )

    with psycopg.connect(
        postgres_dsn
    ) as connection:
        exact = _resolver(
            connection
        ).execute(
            predicate=(
                projected.predicate
            ),
            as_of=AS_OF,
            input_provenance=(
                projected.input_provenance
            ),
        )
        after_change = _resolver(
            connection
        ).execute(
            predicate=(
                projected.predicate
            ),
            as_of=REALIZATION_CHANGE,
            input_provenance=(
                projected.input_provenance
            ),
        )

    assert (
        exact.status
        is ResolutionStatus.EXACT
    )
    assert (
        after_change.status
        is ResolutionStatus.UNRESOLVED
    )
    assert (
        exact.input_provenance
        == projected.input_provenance
    )
    assert any(
        value.startswith(
            "tae-action:Block"
        )
        for value
        in exact.input_provenance.references
    )
    assert any(
        value.startswith(
            "fact:"
        )
        for value
        in exact.correspondences[
            0
        ].provenance.source_rc_references
    )

    with psycopg.connect(
        postgres_dsn
    ) as connection:
        rule_count = connection.execute(
            """
            SELECT count(*)
            FROM napms_access_policy.access_rules
            """
        ).fetchone()[0]
        decision_count = connection.execute(
            """
            SELECT count(*)
            FROM napms_connectivity_decision.connectivity_decisions
            """
        ).fetchone()[0]
        evidence_count = connection.execute(
            """
            SELECT count(*)
            FROM napms_technical_access_evidence.evidence_sets
            """
        ).fetchone()[0]

    assert rule_count == 0
    assert decision_count == 0
    assert evidence_count == 1


def test_distinct_dcs_with_same_technical_region_is_ambiguous(
    postgres_dsn,
    greenfield_config,
):
    with psycopg.connect(
        postgres_dsn
    ) as connection:
        _seed_domain(
            connection,
            ambiguous=True,
        )
        connection.commit()

    evidence = _record_and_read(
        greenfield_config
    )
    projected = (
        TechnicalAccessEvidenceProjectionAdapter()
        .project_entry(
            evidence_set=evidence,
            evidence_entry_id=(
                evidence.entries[
                    0
                ].evidence_entry_id
            ),
        )
    )

    with psycopg.connect(
        postgres_dsn
    ) as connection:
        result = _resolver(
            connection
        ).execute(
            predicate=(
                projected.predicate
            ),
            as_of=AS_OF,
            input_provenance=(
                projected.input_provenance
            ),
        )

    assert (
        result.status
        is ResolutionStatus.AMBIGUOUS
    )
    assert {
        value.interaction.dcs_contract_revision_id
        for value
        in result.correspondences
    } == {
        DCS,
        DCS_COMPETITOR,
    }
    assert result.ambiguities
