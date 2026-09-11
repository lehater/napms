from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from typing import Iterator

import psycopg

from napms.access_policy.adapters.postgres import PostgresAccessRuleRepository
from napms.access_policy.adapters.requirement_policy_alignment import (
    AccessPolicyAlignmentAdapter,
)
from napms.access_policy.adapters.scoped_connectivity_inventory import (
    AccessPolicyScopedConnectivityAdapter,
)
from napms.application_catalogue.adapters.access_policy import (
    AccessPolicyCommunicationCatalogueAdapter,
    AccessPolicyProposalInteractionCatalogueAdapter,
)
from napms.application_catalogue.adapters.connectivity_decision import (
    ConnectivityDecisionCatalogueAdapter,
    ConnectivityDecisionInteractionDiscoveryAdapter,
)
from napms.application_catalogue.adapters.connectivity_requirements import (
    ConnectivityRequirementsCatalogueAdapter,
    ConnectivityRequirementsInteractionDiscoveryAdapter,
)
from napms.application_catalogue.adapters.dcs_json_codec import JsonDcsProjectionCodec
from napms.application_catalogue.adapters.policy_export import (
    PolicyExportApplicationCatalogueAdapter,
)
from napms.application_catalogue.adapters.postgres import (
    PostgresApplicationCatalogueRepository,
)
from napms.application_catalogue.adapters.scoped_connectivity_inventory import (
    ApplicationCatalogueScopedConnectivityAdapter,
)
from napms.application_catalogue.application.describe_interactions import (
    DescribeDirectedInteractions,
)
from napms.application_catalogue.application.list_interactions import (
    ListDirectedInteractions,
)
from napms.application_catalogue.application.resolve import (
    ResolveApplicationProjection,
    ValidateDirectedInteraction,
)
from napms.authority_management.adapters.access_policy import (
    AccessPolicyAuthorityAdapter,
    AccessPolicyEffectivePolicyReadScopeAdapter,
    AccessPolicyProposalScopeAdapter,
    AccessPolicyRuleReadScopeAdapter,
)
from napms.authority_management.adapters.connectivity_decision import (
    ConnectivityDecisionAuthorityAdapter,
    ConnectivityDecisionReadScopeAdapter,
    ConnectivityDecisionScopeAdapter,
)
from napms.authority_management.adapters.connectivity_requirements import (
    ConnectivityRequirementsAuthorityAdapter,
    ConnectivityRequirementsDeclarationScopeAdapter,
    ConnectivityRequirementsReadScopeAdapter,
)
from napms.authority_management.adapters.postgres import (
    PostgresAuthorityAssignmentRepository,
)
from napms.authority_management.adapters.scoped_connectivity_inventory import (
    AuthorityManagementScopedConnectivityAdapter,
)
from napms.authority_management.application.check_authority import CheckAuthority
from napms.authority_management.application.list_scopes import (
    ListEffectiveAuthorityScopes,
)
from napms.composition.config import ApplicationConfig
from napms.connectivity_decision.adapters.postgres import (
    PostgresConnectivityDecisionRepository,
)
from napms.connectivity_decision.adapters.scoped_connectivity_inventory import (
    ConnectivityDecisionScopedConnectivityAdapter,
)
from napms.connectivity_requirements.adapters.postgres import (
    PostgresConnectivityRequirementRepository,
)
from napms.connectivity_requirements.adapters.requirement_policy_alignment import (
    ConnectivityRequirementsAlignmentAdapter,
)
from napms.connectivity_requirements.adapters.scoped_connectivity_inventory import (
    ConnectivityRequirementsScopedConnectivityAdapter,
)
from napms.connectivity_requirements.application.read import (
    GetAuthorizedRequirement,
    ListConnectivityRequirements,
)
from napms.composition.postgres_migrations import apply_greenfield_migrations
from napms.resource_catalogue.adapters.policy_export import (
    PolicyExportResourceCatalogueAdapter,
)
from napms.resource_catalogue.adapters.postgres import (
    PostgresResourceCatalogueRepository,
)
from napms.resource_catalogue.adapters.scoped_connectivity_inventory import (
    ResourceCatalogueScopedConnectivityAdapter,
)
from napms.resource_catalogue.application.list_scope_resources import (
    ListResourcesInResponsibilityScope,
)
from napms.resource_catalogue.application.resolve import ResolveResourceRealization
from napms.scoped_connectivity_inventory.application.read import (
    DiscoverScopedConnectivityScopes,
    ReadScopedConnectivityInventory,
)



@dataclass(slots=True)
class GreenfieldPostgresScope:
    authority: AccessPolicyAuthorityAdapter
    proposal_scope_discovery: AccessPolicyProposalScopeAdapter
    rule_read_scope_discovery: AccessPolicyRuleReadScopeAdapter
    effective_policy_scope_discovery: AccessPolicyEffectivePolicyReadScopeAdapter
    proposal_catalogue: AccessPolicyCommunicationCatalogueAdapter
    proposal_interaction_catalogue: AccessPolicyProposalInteractionCatalogueAdapter
    catalogue_describer: DescribeDirectedInteractions
    application_projection: PolicyExportApplicationCatalogueAdapter
    resource_projection: PolicyExportResourceCatalogueAdapter
    application_catalogue: PostgresApplicationCatalogueRepository
    resource_catalogue: PostgresResourceCatalogueRepository
    access_rules: PostgresAccessRuleRepository
    dcs_decoder: JsonDcsProjectionCodec
    decision_authority: ConnectivityDecisionAuthorityAdapter
    decision_scopes: ConnectivityDecisionScopeAdapter
    decision_read_scopes: ConnectivityDecisionReadScopeAdapter
    decision_catalogue: ConnectivityDecisionCatalogueAdapter
    decision_interaction_catalogue: ConnectivityDecisionInteractionDiscoveryAdapter
    connectivity_decisions: PostgresConnectivityDecisionRepository
    requirement_authority: ConnectivityRequirementsAuthorityAdapter
    requirement_declaration_scopes: ConnectivityRequirementsDeclarationScopeAdapter
    requirement_read_scopes: ConnectivityRequirementsReadScopeAdapter
    requirement_catalogue: ConnectivityRequirementsCatalogueAdapter
    requirement_interaction_catalogue: ConnectivityRequirementsInteractionDiscoveryAdapter
    connectivity_requirements: PostgresConnectivityRequirementRepository
    requirement_alignment: ConnectivityRequirementsAlignmentAdapter
    policy_alignment: AccessPolicyAlignmentAdapter
    scoped_connectivity_scopes: DiscoverScopedConnectivityScopes
    scoped_connectivity_inventory: ReadScopedConnectivityInventory


@contextmanager
def open_greenfield_scope(
    config: ApplicationConfig,
) -> Iterator[GreenfieldPostgresScope]:
    with ExitStack() as stack:
        authority_connection = stack.enter_context(
            psycopg.connect(config.postgres.dsn)
        )
        acc_connection = stack.enter_context(psycopg.connect(config.postgres.dsn))
        rc_connection = stack.enter_context(psycopg.connect(config.postgres.dsn))
        access_policy_connection = stack.enter_context(
            psycopg.connect(config.postgres.dsn)
        )
        connectivity_requirements_connection = stack.enter_context(
            psycopg.connect(config.postgres.dsn)
        )
        connectivity_decision_connection = stack.enter_context(
            psycopg.connect(config.postgres.dsn)
        )

        # Catalogue reads participating in one logical snapshot attempt must
        # remain stable even if another transaction appends newer fact versions.
        acc_connection.execute(
            "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
        )
        rc_connection.execute(
            "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
        )

        authority_repository = PostgresAuthorityAssignmentRepository(
            authority_connection
        )
        authority = AccessPolicyAuthorityAdapter(
            checker=CheckAuthority(assignments=authority_repository)
        )
        proposal_scope_discovery = AccessPolicyProposalScopeAdapter(
            discovery=ListEffectiveAuthorityScopes(assignments=authority_repository)
        )
        rule_read_scope_discovery = AccessPolicyRuleReadScopeAdapter(
            discovery=ListEffectiveAuthorityScopes(assignments=authority_repository)
        )
        effective_policy_scope_discovery = AccessPolicyEffectivePolicyReadScopeAdapter(
            discovery=ListEffectiveAuthorityScopes(assignments=authority_repository)
        )

        decision_authority = ConnectivityDecisionAuthorityAdapter(
            checker=CheckAuthority(assignments=authority_repository)
        )
        decision_scopes = ConnectivityDecisionScopeAdapter(
            discovery=ListEffectiveAuthorityScopes(assignments=authority_repository)
        )
        decision_read_scopes = ConnectivityDecisionReadScopeAdapter(
            discovery=ListEffectiveAuthorityScopes(assignments=authority_repository)
        )

        requirement_authority = ConnectivityRequirementsAuthorityAdapter(
            checker=CheckAuthority(assignments=authority_repository)
        )
        requirement_declaration_scopes = (
            ConnectivityRequirementsDeclarationScopeAdapter(
                discovery=ListEffectiveAuthorityScopes(
                    assignments=authority_repository
                )
            )
        )
        requirement_read_scopes = ConnectivityRequirementsReadScopeAdapter(
            discovery=ListEffectiveAuthorityScopes(
                assignments=authority_repository
            )
        )

        application_repository = PostgresApplicationCatalogueRepository(
            acc_connection
        )
        proposal_catalogue = AccessPolicyCommunicationCatalogueAdapter(
            validator=ValidateDirectedInteraction(
                catalogue=application_repository
            )
        )
        proposal_interaction_catalogue = AccessPolicyProposalInteractionCatalogueAdapter(
            discovery=ListDirectedInteractions(catalogue=application_repository)
        )
        catalogue_describer = DescribeDirectedInteractions(
            catalogue=application_repository
        )
        decision_catalogue = ConnectivityDecisionCatalogueAdapter(
            validator=ValidateDirectedInteraction(
                catalogue=application_repository
            )
        )
        decision_interaction_catalogue = (
            ConnectivityDecisionInteractionDiscoveryAdapter(
                discovery=ListDirectedInteractions(
                    catalogue=application_repository
                )
            )
        )
        requirement_catalogue = ConnectivityRequirementsCatalogueAdapter(
            validator=ValidateDirectedInteraction(
                catalogue=application_repository
            )
        )
        requirement_interaction_catalogue = (
            ConnectivityRequirementsInteractionDiscoveryAdapter(
                discovery=ListDirectedInteractions(
                    catalogue=application_repository
                )
            )
        )
        application_projection = PolicyExportApplicationCatalogueAdapter(
            resolver=ResolveApplicationProjection(
                catalogue=application_repository
            )
        )

        resource_repository = PostgresResourceCatalogueRepository(rc_connection)
        resource_projection = PolicyExportResourceCatalogueAdapter(
            resolver=ResolveResourceRealization(
                catalogue=resource_repository
            )
        )

        access_rules = PostgresAccessRuleRepository(access_policy_connection)
        connectivity_requirements = PostgresConnectivityRequirementRepository(
            connectivity_requirements_connection
        )
        connectivity_decisions = PostgresConnectivityDecisionRepository(
            connectivity_decision_connection
        )
        requirement_alignment = ConnectivityRequirementsAlignmentAdapter(
            reader=GetAuthorizedRequirement(
                authority=requirement_authority,
                requirements=connectivity_requirements,
            ),
            lister=ListConnectivityRequirements(
                read_scopes=requirement_read_scopes,
                requirements=connectivity_requirements,
            ),
        )
        policy_alignment = AccessPolicyAlignmentAdapter(rules=access_rules)

        scoped_authority = AuthorityManagementScopedConnectivityAdapter(
            checker=CheckAuthority(assignments=authority_repository),
            scope_lister=ListEffectiveAuthorityScopes(
                assignments=authority_repository
            ),
        )
        scoped_resources = ResourceCatalogueScopedConnectivityAdapter(
            lister=ListResourcesInResponsibilityScope(
                affiliations=resource_repository
            ),
            catalogue=resource_repository,
        )
        scoped_catalogue = ApplicationCatalogueScopedConnectivityAdapter(
            catalogue=application_repository,
            decoder=JsonDcsProjectionCodec(),
        )
        scoped_requirements = ConnectivityRequirementsScopedConnectivityAdapter(
            requirements=connectivity_requirements,
        )
        scoped_policy = AccessPolicyScopedConnectivityAdapter(
            rules=access_rules,
        )
        scoped_decisions = ConnectivityDecisionScopedConnectivityAdapter(
            decisions=connectivity_decisions,
        )
        scoped_connectivity_scopes = DiscoverScopedConnectivityScopes(
            authority=scoped_authority,
        )
        scoped_connectivity_inventory = ReadScopedConnectivityInventory(
            authority=scoped_authority,
            resources=scoped_resources,
            catalogue=scoped_catalogue,
            requirements=scoped_requirements,
            decisions=scoped_decisions,
            policy=scoped_policy,
        )

        yield GreenfieldPostgresScope(
            authority=authority,
            proposal_scope_discovery=proposal_scope_discovery,
            rule_read_scope_discovery=rule_read_scope_discovery,
            effective_policy_scope_discovery=effective_policy_scope_discovery,
            proposal_catalogue=proposal_catalogue,
            proposal_interaction_catalogue=proposal_interaction_catalogue,
            catalogue_describer=catalogue_describer,
            application_projection=application_projection,
            resource_projection=resource_projection,
            application_catalogue=application_repository,
            resource_catalogue=resource_repository,
            access_rules=access_rules,
            dcs_decoder=JsonDcsProjectionCodec(),
            decision_authority=decision_authority,
            decision_scopes=decision_scopes,
            decision_read_scopes=decision_read_scopes,
            decision_catalogue=decision_catalogue,
            decision_interaction_catalogue=decision_interaction_catalogue,
            connectivity_decisions=connectivity_decisions,
            requirement_authority=requirement_authority,
            requirement_declaration_scopes=requirement_declaration_scopes,
            requirement_read_scopes=requirement_read_scopes,
            requirement_catalogue=requirement_catalogue,
            requirement_interaction_catalogue=requirement_interaction_catalogue,
            connectivity_requirements=connectivity_requirements,
            requirement_alignment=requirement_alignment,
            policy_alignment=policy_alignment,
            scoped_connectivity_scopes=scoped_connectivity_scopes,
            scoped_connectivity_inventory=scoped_connectivity_inventory,
        )
