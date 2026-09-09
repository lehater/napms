import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.access_policy.domain.model import RuleSemanticIdentity
from napms.composition.config import ApplicationConfig, PostgresConfig
from napms.composition.greenfield_postgres import (
    apply_greenfield_migrations,
    open_greenfield_scope,
)
from napms.connectivity_requirements.application.declare import (
    DeclarationOutcome,
    DeclareConnectivityRequirement,
    DeclareRequirement,
)
from napms.connectivity_requirements.application.options import (
    DiscoverRequiredInteractions,
    DiscoverRequirementScopes,
    RequiredInteractionDiscoveryOutcome,
)
from napms.connectivity_requirements.application.read import (
    GetConnectivityRequirement,
    ListConnectivityRequirements,
    RequirementDetailOutcome,
)
from napms.connectivity_requirements.application.retire import (
    RetireConnectivityRequirement,
    RetireRequirement,
    RetirementOutcome,
)
from napms.connectivity_requirements.application.set_applicability import (
    ApplicabilityMutationOutcome,
    SetConnectivityRequirementApplicability,
    SetRequirementApplicability,
)
from napms.connectivity_requirements.application.set_justification import (
    JustificationMutationOutcome,
    SetConnectivityRequirementJustification,
    SetRequirementJustification,
)
from napms.connectivity_requirements.domain.model import (
    RequiredSemanticInteraction,
    RequirementApplicability,
    RequirementLifecycleState,
)


pytestmark = pytest.mark.postgres

ACTOR = "requirements-actor"
SCOPE = "requirements-scope"
SOURCE = UUID(int=9101)
DESTINATION = UUID(int=9102)
DCS = UUID(int=9103)
REQUIREMENT_ID = UUID(int=9104)
REDECLARED_ID = UUID(int=9105)
NOW = datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)
VALID_FROM = NOW - timedelta(days=1)
VALID_TO = NOW + timedelta(days=1)
INTERACTION = RequiredSemanticInteraction(SOURCE, DESTINATION, DCS)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session")
def greenfield_config(postgres_dsn):
    config = ApplicationConfig(
        environment="local-dev",
        postgres=PostgresConfig(postgres_dsn),
    )
    apply_greenfield_migrations(config)
    return config


@pytest.fixture(autouse=True)
def clean_greenfield(postgres_dsn, greenfield_config):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_connectivity_requirements.applicability_changes,
                napms_connectivity_requirements.justification_changes,
                napms_connectivity_requirements.lifecycle_transitions,
                napms_connectivity_requirements.connectivity_requirements
            CASCADE
            """
        )
        connection.execute(
            """
            TRUNCATE TABLE
                napms_access_policy.access_rule_effective_window_changes,
                napms_access_policy.access_rule_effective_windows,
                napms_access_policy.access_rule_state_transitions,
                napms_access_policy.access_rules
            CASCADE
            """
        )
        connection.execute(
            "TRUNCATE TABLE napms_authority.authority_assignments"
        )
        connection.execute(
            """
            TRUNCATE TABLE
                napms_application_catalogue.deployment_resource_bindings,
                napms_application_catalogue.dcs_revisions,
                napms_application_catalogue.component_deployments
            CASCADE
            """
        )


def seed_greenfield(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        for action in (
            "DeclareConnectivityRequirement",
            "ReadConnectivityRequirement",
            "SetConnectivityRequirementApplicability",
            "SetConnectivityRequirementJustification",
            "RetireConnectivityRequirement",
        ):
            connection.execute(
                """
                INSERT INTO napms_authority.authority_assignments (
                    reference_id,
                    actor_id,
                    action,
                    scope,
                    valid_from,
                    valid_to,
                    provenance_reference
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    f"authority:{action}",
                    ACTOR,
                    action,
                    SCOPE,
                    VALID_FROM,
                    VALID_TO,
                    f"provenance:{action}",
                ),
            )

        for deployment, provenance in (
            (SOURCE, "deployment-source-provenance"),
            (DESTINATION, "deployment-destination-provenance"),
        ):
            connection.execute(
                """
                INSERT INTO napms_application_catalogue.component_deployments (
                    component_deployment_id,
                    provenance_reference
                )
                VALUES (%s, %s)
                """,
                (deployment, provenance),
            )

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
                DCS,
                SOURCE,
                DESTINATION,
                b'{"trafficAlternatives":[]}',
                "dcs-provenance",
            ),
        )
        connection.commit()


def declaration(id_factory):
    return DeclareConnectivityRequirement


def test_greenfield_connectivity_requirement_public_core_lifecycle_persists_restart(
    postgres_dsn,
    greenfield_config,
):
    seed_greenfield(postgres_dsn)

    with open_greenfield_scope(greenfield_config) as scope:
        scopes = DiscoverRequirementScopes(
            discovery=scope.requirement_declaration_scopes,
        ).execute(
            actor_id=ACTOR,
            effective_time=NOW,
        )
        assert scopes.permitted_scopes == (SCOPE,)
        assert scopes.ambiguous_scopes == ()

        interactions = DiscoverRequiredInteractions(
            authority=scope.requirement_authority,
            catalogue=scope.requirement_interaction_catalogue,
        ).execute(
            actor_id=ACTOR,
            scope=SCOPE,
            effective_time=NOW,
        )
        assert (
            interactions.outcome
            is RequiredInteractionDiscoveryOutcome.AVAILABLE
        )
        assert interactions.page.interactions == (INTERACTION,)

        declared = DeclareConnectivityRequirement(
            authority=scope.requirement_authority,
            catalogue=scope.requirement_catalogue,
            requirements=scope.connectivity_requirements,
            id_factory=lambda: REQUIREMENT_ID,
        ).execute(
            DeclareRequirement(
                governance_scope=SCOPE,
                dependent_component_deployment_id=SOURCE,
                required_interaction=INTERACTION,
                applicability=RequirementApplicability.ongoing(),
                justification="Checkout requires the Orders API.",
                actor_id=ACTOR,
                effective_time=NOW,
            )
        )
        assert declared.outcome is DeclarationOutcome.DECLARED
        assert declared.requirement.requirement_id == REQUIREMENT_ID

        page = ListConnectivityRequirements(
            read_scopes=scope.requirement_read_scopes,
            requirements=scope.connectivity_requirements,
        ).execute(
            actor_id=ACTOR,
            effective_time=NOW,
        )
        assert tuple(
            value.requirement_id for value in page.requirements
        ) == (REQUIREMENT_ID,)

        detail = GetConnectivityRequirement(
            authority=scope.requirement_authority,
            requirements=scope.connectivity_requirements,
        ).execute(
            requirement_id=REQUIREMENT_ID,
            actor_id=ACTOR,
            effective_time=NOW,
        )
        assert detail.outcome is RequirementDetailOutcome.FOUND
        assert detail.applicability_mutation_admission.value == "Permitted"
        assert detail.justification_mutation_admission.value == "Permitted"
        assert detail.retirement_admission.value == "Permitted"

        window = RequirementApplicability.absolute_window(
            start=NOW,
            end=NOW + timedelta(hours=4),
        )
        applicability = SetConnectivityRequirementApplicability(
            authority=scope.requirement_authority,
            requirements=scope.connectivity_requirements,
        ).execute(
            SetRequirementApplicability(
                requirement_id=REQUIREMENT_ID,
                applicability=window,
                actor_id=ACTOR,
                effective_time=NOW + timedelta(minutes=1),
            )
        )
        assert applicability.outcome is ApplicabilityMutationOutcome.UPDATED

        justification = SetConnectivityRequirementJustification(
            authority=scope.requirement_authority,
            requirements=scope.connectivity_requirements,
        ).execute(
            SetRequirementJustification(
                requirement_id=REQUIREMENT_ID,
                justification="Checkout and fulfilment require the Orders API.",
                actor_id=ACTOR,
                effective_time=NOW + timedelta(minutes=2),
            )
        )
        assert justification.outcome is JustificationMutationOutcome.UPDATED

        retirement = RetireConnectivityRequirement(
            authority=scope.requirement_authority,
            requirements=scope.connectivity_requirements,
        ).execute(
            RetireRequirement(
                requirement_id=REQUIREMENT_ID,
                actor_id=ACTOR,
                effective_time=NOW + timedelta(minutes=3),
            )
        )
        assert retirement.outcome is RetirementOutcome.RETIRED

        assert scope.access_rules.find_by_identity(
            RuleSemanticIdentity(SOURCE, DESTINATION, DCS)
        ) is None

    with open_greenfield_scope(greenfield_config) as scope:
        persisted = GetConnectivityRequirement(
            authority=scope.requirement_authority,
            requirements=scope.connectivity_requirements,
        ).execute(
            requirement_id=REQUIREMENT_ID,
            actor_id=ACTOR,
            effective_time=NOW,
        )

        assert persisted.outcome is RequirementDetailOutcome.FOUND
        requirement = persisted.requirement
        assert requirement.lifecycle_state is RequirementLifecycleState.RETIRED
        assert requirement.version == 4
        assert len(requirement.applicability_history) == 1
        assert len(requirement.justification_history) == 1
        assert len(requirement.lifecycle_history) == 1
        assert requirement.declaration_provenance.actor_id == ACTOR
        assert requirement.declaration_provenance.authority_reference == (
            "authority:DeclareConnectivityRequirement"
        )

        redeclared = DeclareConnectivityRequirement(
            authority=scope.requirement_authority,
            catalogue=scope.requirement_catalogue,
            requirements=scope.connectivity_requirements,
            id_factory=lambda: REDECLARED_ID,
        ).execute(
            DeclareRequirement(
                governance_scope=SCOPE,
                dependent_component_deployment_id=SOURCE,
                required_interaction=INTERACTION,
                applicability=RequirementApplicability.ongoing(),
                justification="The need returned after retirement.",
                actor_id=ACTOR,
                effective_time=NOW,
            )
        )
        assert redeclared.outcome is DeclarationOutcome.DECLARED
        assert redeclared.requirement.requirement_id == REDECLARED_ID
        assert redeclared.requirement.lifecycle_state is RequirementLifecycleState.ACTIVE

        assert scope.access_rules.find_by_identity(
            RuleSemanticIdentity(SOURCE, DESTINATION, DCS)
        ) is None
