import os
from datetime import datetime, timezone
from importlib.resources import files

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.application_catalogue.adapters.curation_support import (
    LocalApplicationCatalogueIdentityFactory,
    LocalApplicationCatalogueProvenanceFactory,
    LocalDeploymentBindingIdentityFactory,
    LocalDeploymentBindingProvenanceFactory,
)
from napms.application_catalogue.adapters.dcs_authoring import (
    JsonDcsAuthoringProjectionEncoder,
)
from napms.application_catalogue.adapters.postgres import (
    PostgresApplicationCatalogueCurationRepository,
)
from napms.application_catalogue.adapters.resource_binding_target import (
    ResourceCatalogueBindingTargetAdapter,
)
from napms.application_catalogue.application.binding_curation import (
    CreateDeploymentResourceBinding,
    CreateDeploymentResourceBindingCommand,
)
from napms.application_catalogue.application.curation import (
    CreateApplication,
    CreateApplicationCommand,
    CreateApplicationOutcome,
)
from napms.application_catalogue.application.dcs_curation import (
    CreateDcsRevision,
    CreateDcsRevisionCommand,
)
from napms.application_catalogue.application.deployment_curation import (
    CreateComponentDeployment,
    CreateComponentDeploymentCommand,
)
from napms.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
)
from napms.application_catalogue.application.structure_curation import (
    CatalogueMutationOutcome,
    CreateComponent,
    CreateComponentCommand,
)
from napms.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortRange,
)
from napms.resource_catalogue.adapters.curation_support import (
    LocalResourceCatalogueIdentityFactory,
    LocalResourceCatalogueProvenanceFactory,
)
from napms.resource_catalogue.adapters.postgres import (
    PostgresResourceCatalogueCurationRepository,
)
from napms.resource_catalogue.application.curation import (
    CreateResource,
    CreateResourceCommand,
    CreateResourceOutcome,
)
from napms.resource_catalogue.application.ports import (
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
            "napms.application_catalogue.adapters.postgres",
            "napms.resource_catalogue.adapters.postgres",
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


def test_postgres_fresh_catalogue_curation_chain(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        rc = PostgresResourceCatalogueCurationRepository(connection)
        acc = PostgresApplicationCatalogueCurationRepository(connection)

        resource_result = CreateResource(
            authority=PermittedRcAuthority(),
            resources=rc,
            identities=LocalResourceCatalogueIdentityFactory(),
            provenance=LocalResourceCatalogueProvenanceFactory(),
        ).execute(
            CreateResourceCommand(
                display_name="Orders database",
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="resource-1",
            )
        )
        assert resource_result.outcome is CreateResourceOutcome.CREATED
        assert resource_result.resource is not None
        resource_reference = resource_result.resource.resource_reference

        acc_ids = LocalApplicationCatalogueIdentityFactory()
        acc_provenance = LocalApplicationCatalogueProvenanceFactory()

        application_result = CreateApplication(
            authority=PermittedAccAuthority(),
            applications=acc,
            identities=acc_ids,
            provenance=acc_provenance,
        ).execute(
            CreateApplicationCommand(
                display_name="Orders",
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="application-1",
            )
        )
        assert application_result.outcome is CreateApplicationOutcome.CREATED
        assert application_result.application is not None
        application_id = application_result.application.application_id

        component_result = CreateComponent(
            authority=PermittedAccAuthority(),
            catalogue=acc,
            identities=acc_ids,
            provenance=acc_provenance,
        ).execute(
            CreateComponentCommand(
                application_id=application_id,
                display_name="Orders API",
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="component-1",
            )
        )
        assert component_result.outcome is CatalogueMutationOutcome.CREATED
        assert component_result.component is not None

        deployment_result = CreateComponentDeployment(
            authority=PermittedAccAuthority(),
            catalogue=acc,
            identities=acc_ids,
            provenance=acc_provenance,
        ).execute(
            CreateComponentDeploymentCommand(
                component_id=component_result.component.component_id,
                display_name="Production",
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="deployment-1",
            )
        )
        assert deployment_result.outcome is CatalogueMutationOutcome.CREATED
        assert deployment_result.deployment is not None
        deployment_id = deployment_result.deployment.deployment_id

        dcs_result = CreateDcsRevision(
            authority=PermittedAccAuthority(),
            catalogue=acc,
            identities=acc_ids,
            provenance=acc_provenance,
            encoder=JsonDcsAuthoringProjectionEncoder(),
        ).execute(
            CreateDcsRevisionCommand(
                source_component_deployment_id=deployment_id,
                destination_component_deployment_id=deployment_id,
                display_name="HTTPS self-check",
                traffic_alternatives=(
                    AuthoredDcsTrafficAlternative(
                        protocol="tcp",
                        source_ports=DcsPortConstraint.any(),
                        destination_ports=DcsPortConstraint.ranged(
                            DcsPortRange(443, 443)
                        ),
                        service_reference="https",
                    ),
                ),
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="dcs-1",
            )
        )
        assert dcs_result.outcome is CatalogueMutationOutcome.CREATED
        assert dcs_result.revision is not None

        binding_result = CreateDeploymentResourceBinding(
            authority=PermittedAccAuthority(),
            catalogue=acc,
            resources=ResourceCatalogueBindingTargetAdapter(rc),
            identities=LocalDeploymentBindingIdentityFactory(),
            provenance=LocalDeploymentBindingProvenanceFactory(),
        ).execute(
            CreateDeploymentResourceBindingCommand(
                component_deployment_id=deployment_id,
                resource_reference=resource_reference,
                valid_from=NOW,
                valid_to=None,
                actor_id="actor-1",
                effective_time=NOW,
                idempotency_key="binding-1",
            )
        )
        assert binding_result.outcome is CatalogueMutationOutcome.CREATED
        assert binding_result.binding is not None

        # Re-create adapters to prove data was committed rather than only retained
        # inside use-case objects.
        persisted_rc = PostgresResourceCatalogueCurationRepository(connection)
        persisted_acc = PostgresApplicationCatalogueCurationRepository(connection)
        persisted_resource = persisted_rc.get_resource(resource_reference)
        persisted_application = persisted_acc.get_application(application_id)
        persisted_deployment = persisted_acc.get_component_deployment(deployment_id)
        persisted_dcs = persisted_acc.get_dcs_revision(dcs_result.revision.revision_id)
        persisted_binding = persisted_acc.get_binding(binding_result.binding.reference_id)

        assert persisted_resource is not None
        assert persisted_resource.display_name == "Orders database"
        assert persisted_application is not None
        assert persisted_application.display_name == "Orders"
        assert persisted_deployment is not None
        assert persisted_deployment.component_id == component_result.component.component_id
        assert persisted_dcs == dcs_result.revision
        assert persisted_binding == binding_result.binding


def test_postgres_create_retry_resolves_persisted_identity(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresResourceCatalogueCurationRepository(connection)
        use_case = CreateResource(
            authority=PermittedRcAuthority(),
            resources=repository,
            identities=LocalResourceCatalogueIdentityFactory(),
            provenance=LocalResourceCatalogueProvenanceFactory(),
        )
        command = CreateResourceCommand(
            display_name="Retry resource",
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="same-resource-key",
        )

        first = use_case.execute(command)
        second = use_case.execute(command)

        assert first.outcome is CreateResourceOutcome.CREATED
        assert second.outcome is CreateResourceOutcome.RESOLVED
        assert first.resource is not None
        assert second.resource is not None
        assert second.resource.resource_reference == first.resource.resource_reference

        count = connection.execute(
            "SELECT count(*) FROM napms_resource_catalogue.resources"
        ).fetchone()[0]
        assert count == 1
