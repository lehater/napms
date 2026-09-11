from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from typing import Iterator

import psycopg

from napms.contexts.application_catalogue.infrastructure.local.curation_support import (
    LocalApplicationCatalogueIdentityFactory,
    LocalApplicationCatalogueProvenanceFactory,
    LocalDeploymentBindingIdentityFactory,
    LocalDeploymentBindingProvenanceFactory,
)
from napms.contexts.application_catalogue.infrastructure.integrations.dcs_authoring import (
    JsonDcsAuthoringProjectionEncoder,
)
from napms.contexts.application_catalogue.infrastructure.persistence.postgres.curation_detail import (
    PostgresApplicationCatalogueDetailRepository,
)
from napms.contexts.application_catalogue.infrastructure.persistence.postgres.curation_repository import (
    PostgresApplicationCatalogueCurationRepository,
)
from napms.contexts.application_catalogue.infrastructure.persistence.postgres.participant_discovery import (
    PostgresApplicationCatalogueParticipantRepository,
)
from napms.contexts.application_catalogue.infrastructure.persistence.postgres.repository import (
    PostgresApplicationCatalogueRepository,
)
from napms.contexts.application_catalogue.infrastructure.persistence.postgres.transactional_curation_repository import (
    TransactionalPostgresApplicationCatalogueCurationRepository,
)
from napms.contexts.application_catalogue.infrastructure.integrations.resource_binding_target import (
    ResourceCatalogueBindingTargetAdapter,
)
from napms.contexts.application_catalogue.application.binding_curation import (
    CreateDeploymentResourceBinding,
    EndDeploymentResourceBinding,
)
from napms.contexts.application_catalogue.application.curation import CreateApplication
from napms.contexts.application_catalogue.application.curation_detail import (
    ReadApplicationCatalogueTreeDetail,
)
from napms.contexts.application_catalogue.application.curation_read import (
    ListApplicationCatalogue,
    ReadApplicationCatalogueDetail,
)
from napms.contexts.application_catalogue.application.dcs_curation import CreateDcsRevision
from napms.contexts.application_catalogue.application.deployment_curation import (
    CreateComponentDeployment,
    RenameComponentDeployment,
    RetireComponentDeployment,
)
from napms.contexts.application_catalogue.application.participant_discovery import (
    ListApplicationCatalogueParticipants,
)
from napms.contexts.application_catalogue.application.structure_curation import (
    CreateComponent,
    RenameApplication,
    RenameComponent,
    RetireApplication,
    RetireComponent,
)
from napms.contexts.authority_management.infrastructure.integrations.catalogue_curation import (
    ApplicationCatalogueCurationAuthorityAdapter,
    ResourceCatalogueCurationAuthorityAdapter,
)
from napms.contexts.authority_management.infrastructure.persistence.postgres import (
    PostgresAuthorityAssignmentRepository,
)
from napms.contexts.authority_management.application.check_authority import CheckAuthority
from napms.composition.config import ApplicationConfig
from napms.contexts.resource_catalogue.infrastructure.local.curation_support import (
    LocalResourceCatalogueIdentityFactory,
    LocalResourceCatalogueProvenanceFactory,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.curation_repository import (
    PostgresResourceCatalogueCurationRepository,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.transactional_curation_repository import (
    TransactionalPostgresResourceCatalogueCurationRepository,
)
from napms.contexts.resource_catalogue.application.curation import (
    CreateResource,
    RenameResource,
    RetireResource,
)
from napms.contexts.resource_catalogue.application.curation_read import (
    ListResourceCatalogue,
    ReadResourceCatalogueDetail,
)
from napms.contexts.resource_catalogue.application.realization_curation import (
    CreateResourceRealization,
    ReplaceResourceRealization,
)
from napms.contexts.resource_catalogue.application.responsibility_curation import (
    CreateResourceResponsibility,
    EndResourceResponsibility,
)
from napms.contexts.resource_catalogue.application.scope_affiliation_curation import (
    CreateResourceScopeAffiliation,
    EndResourceScopeAffiliation,
)


@dataclass(slots=True)
class ApplicationCatalogueCurationServices:
    list_applications: ListApplicationCatalogue
    list_participants: ListApplicationCatalogueParticipants
    read_application: ReadApplicationCatalogueDetail
    read_application_tree: ReadApplicationCatalogueTreeDetail
    create_application: CreateApplication
    rename_application: RenameApplication
    retire_application: RetireApplication
    create_component: CreateComponent
    rename_component: RenameComponent
    retire_component: RetireComponent
    create_component_deployment: CreateComponentDeployment
    rename_component_deployment: RenameComponentDeployment
    retire_component_deployment: RetireComponentDeployment
    create_dcs_revision: CreateDcsRevision
    create_deployment_resource_binding: CreateDeploymentResourceBinding
    end_deployment_resource_binding: EndDeploymentResourceBinding


@dataclass(slots=True)
class ResourceCatalogueCurationServices:
    list_resources: ListResourceCatalogue
    read_resource: ReadResourceCatalogueDetail
    create_resource: CreateResource
    rename_resource: RenameResource
    retire_resource: RetireResource
    create_realization: CreateResourceRealization
    replace_realization: ReplaceResourceRealization
    create_scope_affiliation: CreateResourceScopeAffiliation
    end_scope_affiliation: EndResourceScopeAffiliation
    create_responsibility: CreateResourceResponsibility
    end_responsibility: EndResourceResponsibility


@dataclass(slots=True)
class CatalogueCurationPostgresScope:
    applications: ApplicationCatalogueCurationServices
    resources: ResourceCatalogueCurationServices
    application_repository: PostgresApplicationCatalogueCurationRepository
    resource_repository: PostgresResourceCatalogueCurationRepository


@contextmanager
def open_catalogue_curation_scope(
    config: ApplicationConfig,
) -> Iterator[CatalogueCurationPostgresScope]:
    """Open owner-specific UoWs for one HTTP/request-level catalogue operation set."""

    with ExitStack() as stack:
        authority_connection = stack.enter_context(psycopg.connect(config.postgres.dsn))
        application_connection = stack.enter_context(psycopg.connect(config.postgres.dsn))
        resource_connection = stack.enter_context(psycopg.connect(config.postgres.dsn))

        authority_repository = PostgresAuthorityAssignmentRepository(
            authority_connection
        )
        checker = CheckAuthority(assignments=authority_repository)
        application_authority = ApplicationCatalogueCurationAuthorityAdapter(
            checker=checker
        )
        resource_authority = ResourceCatalogueCurationAuthorityAdapter(
            checker=checker
        )

        application_repository = (
            TransactionalPostgresApplicationCatalogueCurationRepository(
                application_connection
            )
        )
        application_semantic_repository = PostgresApplicationCatalogueRepository(
            application_connection
        )
        application_detail_repository = PostgresApplicationCatalogueDetailRepository(
            curation=application_repository,
            semantic=application_semantic_repository,
        )
        participant_repository = PostgresApplicationCatalogueParticipantRepository(
            application_connection
        )
        resource_repository = TransactionalPostgresResourceCatalogueCurationRepository(
            resource_connection
        )
        resource_target = ResourceCatalogueBindingTargetAdapter(resource_repository)

        application_identities = LocalApplicationCatalogueIdentityFactory()
        application_provenance = LocalApplicationCatalogueProvenanceFactory()
        binding_identities = LocalDeploymentBindingIdentityFactory()
        binding_provenance = LocalDeploymentBindingProvenanceFactory()
        resource_identities = LocalResourceCatalogueIdentityFactory()
        resource_provenance = LocalResourceCatalogueProvenanceFactory()

        applications = ApplicationCatalogueCurationServices(
            list_applications=ListApplicationCatalogue(
                catalogue=application_repository
            ),
            list_participants=ListApplicationCatalogueParticipants(
                catalogue=participant_repository
            ),
            read_application=ReadApplicationCatalogueDetail(
                catalogue=application_repository
            ),
            read_application_tree=ReadApplicationCatalogueTreeDetail(
                catalogue=application_detail_repository
            ),
            create_application=CreateApplication(
                authority=application_authority,
                applications=application_repository,
                identities=application_identities,
                provenance=application_provenance,
            ),
            rename_application=RenameApplication(
                authority=application_authority,
                catalogue=application_repository,
            ),
            retire_application=RetireApplication(
                authority=application_authority,
                catalogue=application_repository,
                provenance=application_provenance,
            ),
            create_component=CreateComponent(
                authority=application_authority,
                catalogue=application_repository,
                identities=application_identities,
                provenance=application_provenance,
            ),
            rename_component=RenameComponent(
                authority=application_authority,
                catalogue=application_repository,
            ),
            retire_component=RetireComponent(
                authority=application_authority,
                catalogue=application_repository,
                provenance=application_provenance,
            ),
            create_component_deployment=CreateComponentDeployment(
                authority=application_authority,
                catalogue=application_repository,
                identities=application_identities,
                provenance=application_provenance,
            ),
            rename_component_deployment=RenameComponentDeployment(
                authority=application_authority,
                catalogue=application_repository,
            ),
            retire_component_deployment=RetireComponentDeployment(
                authority=application_authority,
                catalogue=application_repository,
                provenance=application_provenance,
            ),
            create_dcs_revision=CreateDcsRevision(
                authority=application_authority,
                catalogue=application_repository,
                identities=application_identities,
                provenance=application_provenance,
                encoder=JsonDcsAuthoringProjectionEncoder(),
            ),
            create_deployment_resource_binding=CreateDeploymentResourceBinding(
                authority=application_authority,
                catalogue=application_repository,
                resources=resource_target,
                identities=binding_identities,
                provenance=binding_provenance,
            ),
            end_deployment_resource_binding=EndDeploymentResourceBinding(
                authority=application_authority,
                catalogue=application_repository,
                provenance=binding_provenance,
            ),
        )

        resources = ResourceCatalogueCurationServices(
            list_resources=ListResourceCatalogue(catalogue=resource_repository),
            read_resource=ReadResourceCatalogueDetail(catalogue=resource_repository),
            create_resource=CreateResource(
                authority=resource_authority,
                resources=resource_repository,
                identities=resource_identities,
                provenance=resource_provenance,
            ),
            rename_resource=RenameResource(
                authority=resource_authority,
                resources=resource_repository,
            ),
            retire_resource=RetireResource(
                authority=resource_authority,
                resources=resource_repository,
                provenance=resource_provenance,
            ),
            create_realization=CreateResourceRealization(
                authority=resource_authority,
                catalogue=resource_repository,
                identities=resource_identities,
                provenance=resource_provenance,
            ),
            replace_realization=ReplaceResourceRealization(
                authority=resource_authority,
                catalogue=resource_repository,
                identities=resource_identities,
                provenance=resource_provenance,
            ),
            create_scope_affiliation=CreateResourceScopeAffiliation(
                authority=resource_authority,
                catalogue=resource_repository,
                identities=resource_identities,
                provenance=resource_provenance,
            ),
            end_scope_affiliation=EndResourceScopeAffiliation(
                authority=resource_authority,
                catalogue=resource_repository,
                provenance=resource_provenance,
            ),
            create_responsibility=CreateResourceResponsibility(
                authority=resource_authority,
                catalogue=resource_repository,
                identities=resource_identities,
                provenance=resource_provenance,
            ),
            end_responsibility=EndResourceResponsibility(
                authority=resource_authority,
                catalogue=resource_repository,
                provenance=resource_provenance,
            ),
        )

        yield CatalogueCurationPostgresScope(
            applications=applications,
            resources=resources,
            application_repository=application_repository,
            resource_repository=resource_repository,
        )
