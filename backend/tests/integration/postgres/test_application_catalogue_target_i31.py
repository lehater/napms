import os
from datetime import datetime, timezone
from importlib.resources import files

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.contexts.application_catalogue.infrastructure.local.curation_support import (
    LocalApplicationCatalogueIdentityFactory,
    LocalApplicationCatalogueProvenanceFactory,
    LocalDeploymentBindingIdentityFactory,
    LocalDeploymentBindingProvenanceFactory,
)
from napms.contexts.application_catalogue.infrastructure.integrations.dcs_authoring import (
    JsonDcsAuthoringProjectionEncoder,
)
from napms.contexts.application_catalogue.infrastructure.persistence.postgres import (
    PostgresTargetApplicationCatalogueRepository,
)
from napms.contexts.application_catalogue.infrastructure.integrations.resource_binding_target import (
    ResourceCatalogueBindingTargetAdapter,
)
from napms.contexts.application_catalogue.application.binding_curation import (
    CreateDeploymentResourceBinding,
)
from napms.contexts.application_catalogue.application.curation import (
    CreateApplication,
    CreateApplicationCommand,
    CreateApplicationOutcome,
)
from napms.contexts.application_catalogue.application.deployment_curation import (
    CreateComponentDeployment,
    CreateComponentDeploymentCommand,
)
from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
    CatalogueConcurrencyConflict,
)
from napms.contexts.application_catalogue.application.structure_curation import (
    CatalogueMutationOutcome,
    CreateComponent,
    CreateComponentCommand,
)
from napms.contexts.application_catalogue.application.target_binding_curation import (
    CreateDeploymentInteractionResourceBinding,
    CreateDeploymentInteractionResourceBindingCommand,
)
from napms.contexts.application_catalogue.application.target_curation import (
    CreateApplicationDeployment,
    CreateApplicationDeploymentCommand,
    CreateInteractionDefinition,
    CreateInteractionDefinitionCommand,
    SelectDeploymentInteraction,
    SelectDeploymentInteractionCommand,
    TargetMutationOutcome,
)
from napms.contexts.application_catalogue.application.target_metadata_curation import (
    UpdateApplicationDefinitionMetadata,
    UpdateApplicationDefinitionMetadataCommand,
    UpdateComponentMetadata,
    UpdateComponentMetadataCommand,
)
from napms.contexts.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortRange,
)
from napms.contexts.application_catalogue.domain.target_model import DeploymentInteractionSide
from napms.contexts.resource_catalogue.infrastructure.local.curation_support import (
    LocalResourceCatalogueIdentityFactory,
    LocalResourceCatalogueProvenanceFactory,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres import (
    PostgresResourceCatalogueCurationRepository,
)
from napms.contexts.resource_catalogue.application.curation import (
    CreateResource,
    CreateResourceCommand,
    CreateResourceOutcome,
)
from napms.contexts.resource_catalogue.application.ports import (
    ResourceCatalogueAuthorityCheck,
    ResourceCatalogueAuthorityOutcome,
)


pytestmark = pytest.mark.postgres
NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_catalogues(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        for package in (
            "napms.contexts.application_catalogue.infrastructure.persistence.postgres",
            "napms.contexts.resource_catalogue.infrastructure.persistence.postgres",
        ):
            migrations = files(package).joinpath("migrations")
            for migration in sorted(
                (path for path in migrations.iterdir() if path.name.endswith(".sql")),
                key=lambda path: path.name,
            ):
                connection.execute(migration.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def clean_catalogues(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_application_catalogue.deployment_interaction_compatibility_sides,
                napms_application_catalogue.deployment_interaction_compatibility,
                napms_application_catalogue.deployment_interactions,
                napms_application_catalogue.application_deployments,
                napms_application_catalogue.interaction_definitions,
                napms_application_catalogue.curation_command_receipts,
                napms_application_catalogue.deployment_resource_bindings,
                napms_application_catalogue.dcs_revisions,
                napms_application_catalogue.component_deployments,
                napms_application_catalogue.components,
                napms_application_catalogue.applications,
                napms_resource_catalogue.curation_command_receipts,
                napms_resource_catalogue.resource_responsibilities,
                napms_resource_catalogue.resource_endpoints,
                napms_resource_catalogue.resource_realization_versions,
                napms_resource_catalogue.resource_scope_affiliations,
                napms_resource_catalogue.resources
            CASCADE
            """
        )


class PermittedAccAuthority:
    def check_curation(self, **kwargs):
        return ApplicationCatalogueAuthorityCheck(
            outcome=ApplicationCatalogueAuthorityOutcome.PERMITTED,
            authority_reference="test:acc-authority",
        )


class PermittedRcAuthority:
    def check_curation(self, **kwargs):
        return ResourceCatalogueAuthorityCheck(
            outcome=ResourceCatalogueAuthorityOutcome.PERMITTED,
            authority_reference="test:rc-authority",
        )


def _traffic():
    return (
        AuthoredDcsTrafficAlternative(
            protocol="tcp",
            source_ports=DcsPortConstraint.any(),
            destination_ports=DcsPortConstraint.ranged(DcsPortRange(443, 443)),
            service_reference="https",
        ),
        AuthoredDcsTrafficAlternative(
            protocol="udp",
            source_ports=DcsPortConstraint.any(),
            destination_ports=DcsPortConstraint.ranged(DcsPortRange(53, 53)),
            service_reference="dns",
        ),
    )


def _create_resource(repository, *, name: str, key: str) -> str:
    result = CreateResource(
        authority=PermittedRcAuthority(),
        resources=repository,
        identities=LocalResourceCatalogueIdentityFactory(),
        provenance=LocalResourceCatalogueProvenanceFactory(),
    ).execute(
        CreateResourceCommand(
            display_name=name,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key=key,
        )
    )
    assert result.outcome is CreateResourceOutcome.CREATED
    assert result.resource is not None
    return result.resource.resource_reference


def test_target_chain_persists_compatibility_projection_and_keeps_legacy_distinct(
    postgres_dsn,
) -> None:
    with psycopg.connect(postgres_dsn) as connection:
        acc = PostgresTargetApplicationCatalogueRepository(connection)
        rc = PostgresResourceCatalogueCurationRepository(connection)
        identities = LocalApplicationCatalogueIdentityFactory()
        provenance = LocalApplicationCatalogueProvenanceFactory()

        source_resource = _create_resource(rc, name="Web node", key="resource-web")
        destination_resource = _create_resource(rc, name="API node", key="resource-api")

        application_result = CreateApplication(
            authority=PermittedAccAuthority(),
            applications=acc,
            identities=identities,
            provenance=provenance,
        ).execute(
            CreateApplicationCommand(
                display_name="CRM",
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="application-crm",
            )
        )
        assert application_result.outcome is CreateApplicationOutcome.CREATED
        application = application_result.application
        assert application is not None

        component_ids = []
        for name, key in (("Web", "component-web"), ("API", "component-api")):
            result = CreateComponent(
                authority=PermittedAccAuthority(),
                catalogue=acc,
                identities=identities,
                provenance=provenance,
            ).execute(
                CreateComponentCommand(
                    application_id=application.application_id,
                    display_name=name,
                    actor_id="actor-1",
                    effective_time=NOW,
                    idempotency_key=key,
                )
            )
            assert result.outcome is CatalogueMutationOutcome.CREATED
            assert result.component is not None
            component_ids.append(result.component.component_id)

        metadata = UpdateApplicationDefinitionMetadata(
            authority=PermittedAccAuthority(),
            catalogue=acc,
        ).execute(
            UpdateApplicationDefinitionMetadataCommand(
                application_id=application.application_id,
                display_name="CRM",
                description="Customer Relationship Management",
                domain="Sales",
                owner_reference="CRM Team",
                expected_version=application.version,
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="application-metadata",
            )
        )
        assert metadata.outcome is TargetMutationOutcome.UPDATED

        web = acc.get_component(component_ids[0])
        assert web is not None
        component_metadata = UpdateComponentMetadata(
            authority=PermittedAccAuthority(),
            catalogue=acc,
        ).execute(
            UpdateComponentMetadataCommand(
                component_id=web.component_id,
                display_name="Web",
                component_type="Frontend",
                description="CRM frontend",
                expected_version=web.version,
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="component-metadata",
            )
        )
        assert component_metadata.outcome is TargetMutationOutcome.UPDATED

        legacy = CreateComponentDeployment(
            authority=PermittedAccAuthority(),
            catalogue=acc,
            identities=identities,
            provenance=provenance,
        ).execute(
            CreateComponentDeploymentCommand(
                component_id=component_ids[0],
                display_name="Legacy production",
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="legacy-deployment",
            )
        )
        assert legacy.outcome is CatalogueMutationOutcome.CREATED
        assert legacy.deployment is not None

        definition = CreateInteractionDefinition(
            authority=PermittedAccAuthority(),
            catalogue=acc,
            identities=identities,
            provenance=provenance,
        ).execute(
            CreateInteractionDefinitionCommand(
                application_id=application.application_id,
                source_component_id=component_ids[0],
                destination_component_id=component_ids[1],
                traffic_alternatives=_traffic(),
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="interaction-web-api",
            )
        )
        assert definition.outcome is TargetMutationOutcome.CREATED
        assert definition.interaction_definition is not None

        deployment = CreateApplicationDeployment(
            authority=PermittedAccAuthority(),
            catalogue=acc,
            identities=identities,
            provenance=provenance,
        ).execute(
            CreateApplicationDeploymentCommand(
                application_id=application.application_id,
                company_reference="Company A",
                environment="Production",
                scope_reference="Moscow",
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="crm-company-a-production",
            )
        )
        assert deployment.outcome is TargetMutationOutcome.CREATED
        assert deployment.application_deployment is not None

        select_command = SelectDeploymentInteractionCommand(
            application_deployment_id=deployment.application_deployment.application_deployment_id,
            interaction_definition_id=definition.interaction_definition.interaction_definition_id,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="select-web-api",
        )
        selector = SelectDeploymentInteraction(
            authority=PermittedAccAuthority(),
            catalogue=acc,
            identities=identities,
            provenance=provenance,
            encoder=JsonDcsAuthoringProjectionEncoder(),
        )
        selected = selector.execute(select_command)
        replay = selector.execute(select_command)

        assert selected.outcome is TargetMutationOutcome.CREATED
        assert replay.outcome is TargetMutationOutcome.RESOLVED
        assert selected.deployment_interaction is not None
        assert selected.compatibility is not None
        assert selected.dcs_revision is not None
        assert replay.compatibility == selected.compatibility
        assert replay.dcs_revision == selected.dcs_revision

        create_binding = CreateDeploymentResourceBinding(
            authority=PermittedAccAuthority(),
            catalogue=acc,
            resources=ResourceCatalogueBindingTargetAdapter(rc),
            identities=LocalDeploymentBindingIdentityFactory(),
            provenance=LocalDeploymentBindingProvenanceFactory(),
        )
        target_binding = CreateDeploymentInteractionResourceBinding(
            catalogue=acc,
            create_binding=create_binding,
        )
        source_binding = target_binding.execute(
            CreateDeploymentInteractionResourceBindingCommand(
                deployment_interaction_id=selected.deployment_interaction.deployment_interaction_id,
                side=DeploymentInteractionSide.SOURCE,
                resource_reference=source_resource,
                valid_from=NOW,
                valid_to=None,
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="bind-source",
            )
        )
        destination_binding = target_binding.execute(
            CreateDeploymentInteractionResourceBindingCommand(
                deployment_interaction_id=selected.deployment_interaction.deployment_interaction_id,
                side=DeploymentInteractionSide.DESTINATION,
                resource_reference=destination_resource,
                valid_from=NOW,
                valid_to=None,
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="bind-destination",
            )
        )
        assert source_binding.outcome is TargetMutationOutcome.CREATED
        assert destination_binding.outcome is TargetMutationOutcome.CREATED
        assert source_binding.binding is not None
        assert not hasattr(source_binding.binding, "component_deployment_id")

        persisted = PostgresTargetApplicationCatalogueRepository(connection)
        persisted_application = persisted.get_application(application.application_id)
        persisted_definition = persisted.get_interaction_definition(
            definition.interaction_definition.interaction_definition_id
        )
        persisted_deployment = persisted.get_application_deployment(
            deployment.application_deployment.application_deployment_id
        )
        persisted_interaction = persisted.get_deployment_interaction(
            selected.deployment_interaction.deployment_interaction_id
        )
        persisted_compatibility = persisted.get_compatibility_projection(
            selected.deployment_interaction.deployment_interaction_id
        )

        assert persisted_application is not None
        assert persisted_application.description == "Customer Relationship Management"
        assert persisted_application.domain == "Sales"
        assert persisted_application.owner_reference == "CRM Team"
        assert persisted_definition == definition.interaction_definition
        assert persisted_deployment == deployment.application_deployment
        assert persisted_interaction == selected.deployment_interaction
        assert persisted_compatibility == selected.compatibility

        persisted_web = persisted.get_component(component_ids[0])
        assert persisted_web is not None
        assert persisted_web.component_type == "Frontend"
        assert persisted_web.description == "CRM frontend"

        source_effective = persisted.find_effective_bindings(
            component_deployment_id=selected.compatibility.source_component_deployment_id,
            as_of=NOW,
        )
        destination_effective = persisted.find_effective_bindings(
            component_deployment_id=selected.compatibility.destination_component_deployment_id,
            as_of=NOW,
        )
        assert tuple(item.resource_reference for item in source_effective) == (source_resource,)
        assert tuple(item.resource_reference for item in destination_effective) == (
            destination_resource,
        )

        legacy_rows = persisted.list_active_legacy_component_deployments(
            component_id=component_ids[0]
        )
        assert tuple(item.deployment_id for item in legacy_rows) == (
            legacy.deployment.deployment_id,
        )

        side_rows = connection.execute(
            """
            SELECT side, component_deployment_id
            FROM napms_application_catalogue.deployment_interaction_compatibility_sides
            WHERE deployment_interaction_id = %s
            ORDER BY side
            """,
            (selected.deployment_interaction.deployment_interaction_id,),
        ).fetchall()
        assert len(side_rows) == 2
        assert {row[1] for row in side_rows} == {
            selected.compatibility.source_component_deployment_id,
            selected.compatibility.destination_component_deployment_id,
        }
        assert legacy.deployment.deployment_id not in {row[1] for row in side_rows}


def test_target_repository_rejects_stale_application_deployment_version(postgres_dsn) -> None:
    with psycopg.connect(postgres_dsn) as connection:
        acc = PostgresTargetApplicationCatalogueRepository(connection)
        identities = LocalApplicationCatalogueIdentityFactory()
        provenance = LocalApplicationCatalogueProvenanceFactory()
        application = CreateApplication(
            authority=PermittedAccAuthority(),
            applications=acc,
            identities=identities,
            provenance=provenance,
        ).execute(
            CreateApplicationCommand(
                display_name="CRM",
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="stale-application",
            )
        ).application
        assert application is not None
        deployment = CreateApplicationDeployment(
            authority=PermittedAccAuthority(),
            catalogue=acc,
            identities=identities,
            provenance=provenance,
        ).execute(
            CreateApplicationDeploymentCommand(
                application_id=application.application_id,
                company_reference="Company A",
                environment="Production",
                scope_reference="Moscow",
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="stale-deployment",
            )
        ).application_deployment
        assert deployment is not None

        changed = deployment.changed_context(
            company_reference="Company B",
            environment="Production",
            scope_reference="Moscow",
        )
        with pytest.raises(CatalogueConcurrencyConflict):
            acc.save_application_deployment(changed, expected_version=deployment.version + 10)

        reloaded = PostgresTargetApplicationCatalogueRepository(connection).get_application_deployment(
            deployment.application_deployment_id
        )
        assert reloaded == deployment


def test_target_migration_replay_does_not_promote_legacy_component_deployment(
    postgres_dsn,
) -> None:
    migration = (
        files("napms.contexts.application_catalogue.infrastructure.persistence.postgres")
        .joinpath("migrations", "0005_application_catalogue_target.sql")
        .read_text(encoding="utf-8")
    )
    with psycopg.connect(postgres_dsn) as connection:
        application_id = LocalApplicationCatalogueIdentityFactory().new_application_id()
        component_id = LocalApplicationCatalogueIdentityFactory().new_component_id()
        legacy_id = LocalApplicationCatalogueIdentityFactory().new_component_deployment_id()
        connection.execute(
            """
            INSERT INTO napms_application_catalogue.applications (
                application_id, display_name, provenance_reference
            ) VALUES (%s, 'Legacy app', 'legacy:app')
            """,
            (application_id,),
        )
        connection.execute(
            """
            INSERT INTO napms_application_catalogue.components (
                component_id, application_id, display_name, provenance_reference
            ) VALUES (%s, %s, 'Legacy component', 'legacy:component')
            """,
            (component_id, application_id),
        )
        connection.execute(
            """
            INSERT INTO napms_application_catalogue.component_deployments (
                component_deployment_id, component_id, provenance_reference, display_name
            ) VALUES (%s, %s, 'legacy:deployment', 'Legacy production')
            """,
            (legacy_id, component_id),
        )

        connection.execute(migration)
        connection.execute(migration)

        assert connection.execute(
            """
            SELECT count(*)
            FROM napms_application_catalogue.deployment_interaction_compatibility_sides
            WHERE component_deployment_id = %s
            """,
            (legacy_id,),
        ).fetchone()[0] == 0
        assert connection.execute(
            """
            SELECT count(*)
            FROM napms_application_catalogue.application_deployments
            WHERE application_id = %s
            """,
            (application_id,),
        ).fetchone()[0] == 0
        connection.rollback()
