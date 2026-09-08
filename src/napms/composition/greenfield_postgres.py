from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from importlib.resources import files
from typing import Iterator

import psycopg

from napms.access_policy.adapters.postgres import PostgresAccessRuleRepository
from napms.application_catalogue.adapters.access_policy import (
    AccessPolicyCommunicationCatalogueAdapter,
    AccessPolicyProposalInteractionCatalogueAdapter,
)
from napms.application_catalogue.adapters.dcs_json_codec import JsonDcsProjectionCodec
from napms.application_catalogue.adapters.policy_export import (
    PolicyExportApplicationCatalogueAdapter,
)
from napms.application_catalogue.adapters.postgres import (
    PostgresApplicationCatalogueRepository,
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
    AccessPolicyProposalScopeAdapter,
)
from napms.authority_management.adapters.postgres import (
    PostgresAuthorityAssignmentRepository,
)
from napms.authority_management.application.check_authority import CheckAuthority
from napms.authority_management.application.list_scopes import (
    ListEffectiveAuthorityScopes,
)
from napms.composition.config import ApplicationConfig
from napms.resource_catalogue.adapters.policy_export import (
    PolicyExportResourceCatalogueAdapter,
)
from napms.resource_catalogue.adapters.postgres import (
    PostgresResourceCatalogueRepository,
)
from napms.resource_catalogue.application.resolve import ResolveResourceRealization


_MIGRATION_PACKAGES = (
    "napms.access_policy.adapters.postgres",
    "napms.authority_management.adapters.postgres",
    "napms.application_catalogue.adapters.postgres",
    "napms.resource_catalogue.adapters.postgres",
)


@dataclass(slots=True)
class GreenfieldPostgresScope:
    authority: AccessPolicyAuthorityAdapter
    proposal_scope_discovery: AccessPolicyProposalScopeAdapter
    proposal_catalogue: AccessPolicyCommunicationCatalogueAdapter
    proposal_interaction_catalogue: AccessPolicyProposalInteractionCatalogueAdapter
    application_projection: PolicyExportApplicationCatalogueAdapter
    resource_projection: PolicyExportResourceCatalogueAdapter
    access_rules: PostgresAccessRuleRepository
    dcs_decoder: JsonDcsProjectionCodec


def apply_greenfield_migrations(config: ApplicationConfig) -> None:
    with psycopg.connect(config.postgres.dsn, autocommit=True) as connection:
        for package in _MIGRATION_PACKAGES:
            migrations = files(package).joinpath("migrations")
            for migration in sorted(
                (
                    path
                    for path in migrations.iterdir()
                    if path.name.endswith(".sql")
                ),
                key=lambda path: path.name,
            ):
                connection.execute(migration.read_text(encoding="utf-8"))


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

        yield GreenfieldPostgresScope(
            authority=authority,
            proposal_scope_discovery=proposal_scope_discovery,
            proposal_catalogue=proposal_catalogue,
            proposal_interaction_catalogue=proposal_interaction_catalogue,
            application_projection=application_projection,
            resource_projection=resource_projection,
            access_rules=PostgresAccessRuleRepository(access_policy_connection),
            dcs_decoder=JsonDcsProjectionCodec(),
        )
