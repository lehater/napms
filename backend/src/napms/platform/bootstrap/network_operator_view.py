from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from typing import Iterator

import psycopg

from napms.contexts.authority_management.infrastructure.integrations.network_operator_view import (
    AuthorityManagementNetworkOperatorViewAdapter,
)
from napms.contexts.authority_management.infrastructure.persistence.postgres import (
    PostgresAuthorityAssignmentRepository,
)
from napms.contexts.authority_management.application.check_authority import CheckAuthority
from napms.platform.bootstrap.access_policy_realization import (
    open_access_policy_realization_scope,
)
from napms.platform.bootstrap.config import ApplicationConfig
from napms.workflows.network_operator_view.application.read import ReadNetworkOperatorRealization


@dataclass(slots=True)
class NetworkOperatorViewPostgresScope:
    read: ReadNetworkOperatorRealization


@contextmanager
def open_network_operator_view_scope(
    config: ApplicationConfig,
    *,
    actor_id: str,
) -> Iterator[NetworkOperatorViewPostgresScope]:
    with ExitStack() as stack:
        authority_connection = stack.enter_context(
            psycopg.connect(config.postgres.dsn)
        )
        realization = stack.enter_context(
            open_access_policy_realization_scope(config, actor_id=actor_id)
        )
        authority = AuthorityManagementNetworkOperatorViewAdapter(
            checker=CheckAuthority(
                assignments=PostgresAuthorityAssignmentRepository(authority_connection)
            )
        )
        yield NetworkOperatorViewPostgresScope(
            read=ReadNetworkOperatorRealization(
                authority=authority,
                derive_desired=realization.derive_desired,
                build_configured=realization.build_configured,
                reconcile=realization.reconcile,
                render=realization.render,
            )
        )
