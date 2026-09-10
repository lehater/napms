from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from typing import Iterator

import psycopg

from napms.application_catalogue.adapters.curation_support import (
    LocalApplicationCatalogueIdentityFactory,
    LocalApplicationCatalogueProvenanceFactory,
    LocalDeploymentBindingIdentityFactory,
    LocalDeploymentBindingProvenanceFactory,
)
from napms.application_catalogue.adapters.dcs_authoring import (
    JsonDcsAuthoringProjectionEncoder,
)
from napms.application_catalogue.adapters.postgres.transactional_target_repository import (
    TransactionalPostgresTargetApplicationCatalogueRepository,
)
from napms.application_catalogue.adapters.resource_binding_target import (
    ResourceCatalogueBindingTargetAdapter,
)
from napms.application_catalogue.application.binding_curation import (
    CreateDeploymentResourceBinding,
    EndDeploymentResourceBinding,
)
from napms.application_catalogue.application.curation import CreateApplication
from napms.application_catalogue.application.target_binding_curation import (
    CreateDeploymentInteractionResourceBinding,
    EndDeploymentInteractionResourceBinding,
)
from napms.application_catalogue.application.target_curation import (
    CreateApplicationDeployment,
    CreateInteractionDefinition,
    SelectDeploymentInteraction,
    UpdateInteractionDefinitionEndpoints,
)
from napms.application_catalogue.application.target_metadata_curation import (
    UpdateApplicationDefinitionMetadata,
    UpdateApplicationDeploymentContext,
    UpdateComponentMetadata,
)
from napms.application_catalogue.application.target_structure_curation import (
    CreateTargetComponent,
)
from napms.authority_management.adapters.catalogue_curation import (
    ApplicationCatalogueCurationAuthorityAdapter,
)
from napms.authority_management.adapters.postgres import (
    PostgresAuthorityAssignmentRepository,
)
from napms.authority_management.application.check_authority import CheckAuthority
from napms.composition.application_catalogue_target_read_postgres import (
    PostgresApplicationCatalogueTargetReadModel,
)
from napms.composition.config import ApplicationConfig
from napms.resource_catalogue.adapters.postgres.transactional_curation_repository import (
    TransactionalPostgresResourceCatalogueCurationRepository,
)


@dataclass(slots=True)
class TargetApplicationCatalogueServices:
    read: PostgresApplicationCatalogueTargetReadModel
    create_definition: CreateApplication
    update_definition_metadata: UpdateApplicationDefinitionMetadata
    create_component: CreateTargetComponent
    update_component_metadata: UpdateComponentMetadata
    create_interaction_definition: CreateInteractionDefinition
    update_interaction_endpoints: UpdateInteractionDefinitionEndpoints
    create_application_deployment: CreateApplicationDeployment
    update_application_deployment_context: UpdateApplicationDeploymentContext
    select_deployment_interaction: SelectDeploymentInteraction
    create_resource_binding: CreateDeploymentInteractionResourceBinding
    end_resource_binding: EndDeploymentInteractionResourceBinding


@dataclass(slots=True)
class CatalogueTargetPostgresScope:
    applications: TargetApplicationCatalogueServices
    application_repository: TransactionalPostgresTargetApplicationCatalogueRepository
    resource_repository: TransactionalPostgresResourceCatalogueCurationRepository


@contextmanager
def open_catalogue_target_scope(
    config: ApplicationConfig,
) -> Iterator[CatalogueTargetPostgresScope]:
    """Open owner UoWs plus the query-only I31 read projection for one request."""

    with ExitStack() as stack:
        authority_connection = stack.enter_context(psycopg.connect(config.postgres.dsn))
        application_connection = stack.enter_context(psycopg.connect(config.postgres.dsn))
        resource_connection = stack.enter_context(psycopg.connect(config.postgres.dsn))

        authority_repository = PostgresAuthorityAssignmentRepository(authority_connection)
        application_authority = ApplicationCatalogueCurationAuthorityAdapter(
            checker=CheckAuthority(assignments=authority_repository)
        )
        application_repository = TransactionalPostgresTargetApplicationCatalogueRepository(
            application_connection
        )
        resource_repository = TransactionalPostgresResourceCatalogueCurationRepository(
            resource_connection
        )
        resource_target = ResourceCatalogueBindingTargetAdapter(resource_repository)

        identities = LocalApplicationCatalogueIdentityFactory()
        provenance = LocalApplicationCatalogueProvenanceFactory()
        binding_identities = LocalDeploymentBindingIdentityFactory()
        binding_provenance = LocalDeploymentBindingProvenanceFactory()
        traffic = JsonDcsAuthoringProjectionEncoder()

        create_legacy_binding = CreateDeploymentResourceBinding(
            authority=application_authority,
            catalogue=application_repository,
            resources=resource_target,
            identities=binding_identities,
            provenance=binding_provenance,
        )
        end_legacy_binding = EndDeploymentResourceBinding(
            authority=application_authority,
            catalogue=application_repository,
            provenance=binding_provenance,
        )

        services = TargetApplicationCatalogueServices(
            read=PostgresApplicationCatalogueTargetReadModel(application_connection),
            create_definition=CreateApplication(
                authority=application_authority,
                applications=application_repository,
                identities=identities,
                provenance=provenance,
            ),
            update_definition_metadata=UpdateApplicationDefinitionMetadata(
                authority=application_authority,
                catalogue=application_repository,
            ),
            create_component=CreateTargetComponent(
                authority=application_authority,
                catalogue=application_repository,
                identities=identities,
                provenance=provenance,
            ),
            update_component_metadata=UpdateComponentMetadata(
                authority=application_authority,
                catalogue=application_repository,
            ),
            create_interaction_definition=CreateInteractionDefinition(
                authority=application_authority,
                catalogue=application_repository,
                identities=identities,
                provenance=provenance,
            ),
            update_interaction_endpoints=UpdateInteractionDefinitionEndpoints(
                authority=application_authority,
                catalogue=application_repository,
            ),
            create_application_deployment=CreateApplicationDeployment(
                authority=application_authority,
                catalogue=application_repository,
                identities=identities,
                provenance=provenance,
            ),
            update_application_deployment_context=UpdateApplicationDeploymentContext(
                authority=application_authority,
                catalogue=application_repository,
            ),
            select_deployment_interaction=SelectDeploymentInteraction(
                authority=application_authority,
                catalogue=application_repository,
                identities=identities,
                provenance=provenance,
                encoder=traffic,
            ),
            create_resource_binding=CreateDeploymentInteractionResourceBinding(
                catalogue=application_repository,
                create_binding=create_legacy_binding,
            ),
            end_resource_binding=EndDeploymentInteractionResourceBinding(
                catalogue=application_repository,
                bindings=application_repository,
                end_binding=end_legacy_binding,
            ),
        )

        yield CatalogueTargetPostgresScope(
            applications=services,
            application_repository=application_repository,
            resource_repository=resource_repository,
        )
