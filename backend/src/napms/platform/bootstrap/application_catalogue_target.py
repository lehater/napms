from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from typing import Iterator

import psycopg

from napms.contexts.access_policy.infrastructure.persistence.postgres.application_catalogue_dependency_query import (
    PostgresAccessRuleDependencyQuery,
)
from napms.contexts.access_policy.application.active_dependency_references import (
    ReadActiveAccessRuleReferences,
)
from napms.contexts.application_catalogue.infrastructure.local.curation_support import (
    LocalApplicationCatalogueIdentityFactory,
    LocalApplicationCatalogueProvenanceFactory,
    LocalDeploymentBindingIdentityFactory,
    LocalDeploymentBindingProvenanceFactory,
)
from napms.contexts.application_catalogue.infrastructure.integrations.dcs_authoring import (
    JsonDcsAuthoringProjectionEncoder,
)
from napms.contexts.application_catalogue.infrastructure.persistence.postgres.target_retirement_query import (
    PostgresApplicationCatalogueRetirementDependencyQuery,
)
from napms.contexts.application_catalogue.infrastructure.persistence.postgres.transactional_target_repository import (
    TransactionalPostgresTargetApplicationCatalogueRepository,
)
from napms.contexts.application_catalogue.infrastructure.integrations.resource_binding_target import (
    ResourceCatalogueBindingTargetAdapter,
)
from napms.contexts.application_catalogue.application.curation.bindings import (
    CreateDeploymentResourceBinding,
    EndDeploymentResourceBinding,
)
from napms.contexts.application_catalogue.application.curation.create_application import CreateApplication
from napms.contexts.application_catalogue.application.target.bindings import (
    CreateDeploymentInteractionResourceBinding,
    EndDeploymentInteractionResourceBinding,
)
from napms.contexts.application_catalogue.application.target.curation import (
    CreateApplicationDeployment,
    CreateInteractionDefinition,
    SelectDeploymentInteraction,
    UpdateInteractionDefinitionEndpoints,
    UpdateInteractionDefinitionTraffic,
)
from napms.contexts.application_catalogue.application.target.lifecycle import (
    RetireApplicationDefinition,
    RetireApplicationDeployment,
    RetireComponentTarget,
    RetireDeploymentInteraction,
    RetireInteractionDefinition,
    TargetRetirementDependencies,
)
from napms.contexts.application_catalogue.application.target.metadata import (
    UpdateApplicationDefinitionMetadata,
    UpdateApplicationDeploymentContext,
    UpdateComponentMetadata,
)
from napms.contexts.application_catalogue.application.target.retirement import (
    BoundedRetirementService,
    RetirementSubjectKind,
    TargetRetirementDependencyReader,
)
from napms.contexts.application_catalogue.application.target.selection import (
    ReadDeploymentInteraction,
)
from napms.contexts.application_catalogue.application.target.structure import (
    CreateTargetComponent,
)
from napms.contexts.authority_management.infrastructure.integrations.catalogue_curation import (
    ApplicationCatalogueCurationAuthorityAdapter,
)
from napms.contexts.authority_management.infrastructure.persistence.postgres import (
    PostgresAuthorityAssignmentRepository,
)
from napms.contexts.authority_management.application.check_authority import CheckAuthority
from napms.contexts.application_catalogue.infrastructure.integrations.target_dependencies import (
    AccessRuleDependencyAdapter,
    ConnectivityDecisionDependencyAdapter,
    ConnectivityRequirementDependencyAdapter,
)
from napms.contexts.application_catalogue.infrastructure.read_models.postgres.target import (
    PostgresApplicationCatalogueTargetReadModel,
)
from napms.platform.bootstrap.config import ApplicationConfig
from napms.contexts.connectivity_decision.infrastructure.persistence.postgres.application_catalogue_dependency_query import (
    PostgresConnectivityDecisionDependencyQuery,
)
from napms.contexts.connectivity_decision.application.active_dependency_references import (
    ReadActiveConnectivityDecisionReferences,
)
from napms.contexts.connectivity_requirements.infrastructure.persistence.postgres.application_catalogue_dependency_query import (
    PostgresConnectivityRequirementDependencyQuery,
)
from napms.contexts.connectivity_requirements.application.active_dependency_references import (
    ReadActiveConnectivityRequirementReferences,
)
from napms.contexts.resource_catalogue.application.read_resource_references import (
    ReadResourceReferences,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.resource_reference_query import (
    PostgresResourceReferenceQuery,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.transactional_curation_repository import (
    TransactionalPostgresResourceCatalogueCurationRepository,
)


@dataclass(slots=True)
class TargetApplicationCatalogueServices:
    read: PostgresApplicationCatalogueTargetReadModel
    deployment_interaction_read: ReadDeploymentInteraction
    retirement_dependencies: TargetRetirementDependencyReader
    create_definition: CreateApplication
    update_definition_metadata: UpdateApplicationDefinitionMetadata
    retire_definition: BoundedRetirementService
    create_component: CreateTargetComponent
    update_component_metadata: UpdateComponentMetadata
    retire_component: BoundedRetirementService
    create_interaction_definition: CreateInteractionDefinition
    update_interaction_endpoints: UpdateInteractionDefinitionEndpoints
    update_interaction_traffic: UpdateInteractionDefinitionTraffic
    retire_interaction_definition: BoundedRetirementService
    create_application_deployment: CreateApplicationDeployment
    update_application_deployment_context: UpdateApplicationDeploymentContext
    retire_application_deployment: BoundedRetirementService
    select_deployment_interaction: SelectDeploymentInteraction
    retire_deployment_interaction: BoundedRetirementService
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
    """Open owner UoWs plus query-only I31 projections for one request."""

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

        requirements = ConnectivityRequirementDependencyAdapter(
            ReadActiveConnectivityRequirementReferences(
                query=PostgresConnectivityRequirementDependencyQuery(application_connection)
            )
        )
        decisions = ConnectivityDecisionDependencyAdapter(
            ReadActiveConnectivityDecisionReferences(
                query=PostgresConnectivityDecisionDependencyQuery(application_connection)
            )
        )
        access_rules = AccessRuleDependencyAdapter(
            ReadActiveAccessRuleReferences(
                query=PostgresAccessRuleDependencyQuery(application_connection)
            )
        )
        lifecycle_dependencies = TargetRetirementDependencies(
            catalogue=application_repository,
            requirements=requirements,
            decisions=decisions,
            access_rules=access_rules,
        )
        retirement_dependencies = TargetRetirementDependencyReader(
            catalogue=application_repository,
            local=PostgresApplicationCatalogueRetirementDependencyQuery(
                application_connection
            ),
            requirements=requirements,
            decisions=decisions,
            access_rules=access_rules,
        )

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

        retire_definition = RetireApplicationDefinition(
            authority=application_authority,
            catalogue=application_repository,
            provenance=provenance,
            dependencies=lifecycle_dependencies,
        )
        retire_component = RetireComponentTarget(
            authority=application_authority,
            catalogue=application_repository,
            provenance=provenance,
            dependencies=lifecycle_dependencies,
        )
        retire_interaction_definition = RetireInteractionDefinition(
            authority=application_authority,
            catalogue=application_repository,
            provenance=provenance,
            dependencies=lifecycle_dependencies,
        )
        retire_application_deployment = RetireApplicationDeployment(
            authority=application_authority,
            catalogue=application_repository,
            provenance=provenance,
            dependencies=lifecycle_dependencies,
        )
        retire_deployment_interaction = RetireDeploymentInteraction(
            authority=application_authority,
            catalogue=application_repository,
            provenance=provenance,
            dependencies=lifecycle_dependencies,
        )

        services = TargetApplicationCatalogueServices(
            read=PostgresApplicationCatalogueTargetReadModel(
                application_connection,
                resources=ReadResourceReferences(
                    query=PostgresResourceReferenceQuery(resource_connection)
                ),
            ),
            deployment_interaction_read=ReadDeploymentInteraction(
                catalogue=application_repository
            ),
            retirement_dependencies=retirement_dependencies,
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
            retire_definition=BoundedRetirementService(
                authority=application_authority,
                subject_kind=RetirementSubjectKind.APPLICATION_DEFINITION,
                subject_id_attribute="application_id",
                dependencies=retirement_dependencies,
                delegate=retire_definition,
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
            retire_component=BoundedRetirementService(
                authority=application_authority,
                subject_kind=RetirementSubjectKind.COMPONENT,
                subject_id_attribute="component_id",
                dependencies=retirement_dependencies,
                delegate=retire_component,
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
            update_interaction_traffic=UpdateInteractionDefinitionTraffic(
                authority=application_authority,
                catalogue=application_repository,
                identities=identities,
                provenance=provenance,
                encoder=traffic,
                requirements=requirements,
                decisions=decisions,
                access_rules=access_rules,
            ),
            retire_interaction_definition=BoundedRetirementService(
                authority=application_authority,
                subject_kind=RetirementSubjectKind.INTERACTION_DEFINITION,
                subject_id_attribute="interaction_definition_id",
                dependencies=retirement_dependencies,
                delegate=retire_interaction_definition,
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
            retire_application_deployment=BoundedRetirementService(
                authority=application_authority,
                subject_kind=RetirementSubjectKind.APPLICATION_DEPLOYMENT,
                subject_id_attribute="application_deployment_id",
                dependencies=retirement_dependencies,
                delegate=retire_application_deployment,
            ),
            select_deployment_interaction=SelectDeploymentInteraction(
                authority=application_authority,
                catalogue=application_repository,
                identities=identities,
                provenance=provenance,
                encoder=traffic,
            ),
            retire_deployment_interaction=BoundedRetirementService(
                authority=application_authority,
                subject_kind=RetirementSubjectKind.DEPLOYMENT_INTERACTION,
                subject_id_attribute="deployment_interaction_id",
                dependencies=retirement_dependencies,
                delegate=retire_deployment_interaction,
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
