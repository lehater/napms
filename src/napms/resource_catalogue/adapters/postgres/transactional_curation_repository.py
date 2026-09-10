from datetime import datetime

from psycopg import Error as PsycopgError
from psycopg.errors import UniqueViolation

from napms.resource_catalogue.adapters.postgres.curation_list import (
    PostgresResourceCatalogueListQuery,
)
from napms.resource_catalogue.adapters.postgres.curation_repository import (
    PostgresResourceCatalogueCurationRepository,
)
from napms.resource_catalogue.application.curation_read import (
    ResourceCatalogueListItem,
)
from napms.resource_catalogue.application.ports import (
    ResourceCatalogueIdempotencyConflict,
    ResourceCataloguePersistenceError,
    ResourceCataloguePersistenceOutcomeUnknown,
)


class TransactionalPostgresResourceCatalogueCurationRepository(
    PostgresResourceCatalogueCurationRepository
):
    """RC curation repository with explicit pre-commit vs commit failure semantics."""

    def list_workspace_resources(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None,
        include_retired: bool,
        responsibility_scope: str | None,
        as_of: datetime,
    ) -> tuple[ResourceCatalogueListItem, ...]:
        return PostgresResourceCatalogueListQuery(self._connection).list_resources(
            offset=offset,
            limit=limit,
            search=search,
            include_retired=include_retired,
            responsibility_scope=responsibility_scope,
            as_of=as_of,
        )

    def commit(self) -> None:
        if self._pending_receipt is not None:
            actor_id, idempotency_key, receipt = self._pending_receipt
            try:
                self._connection.execute(
                    """
                    INSERT INTO napms_resource_catalogue.curation_command_receipts (
                        actor_id, idempotency_key, command_kind,
                        request_fingerprint, result_reference, result_version
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        actor_id,
                        idempotency_key,
                        receipt.command_kind,
                        receipt.request_fingerprint,
                        receipt.result_reference,
                        receipt.result_version,
                    ),
                )
            except UniqueViolation as exc:
                self._connection.rollback()
                self._pending_receipt = None
                raise ResourceCatalogueIdempotencyConflict() from exc
            except PsycopgError as exc:
                self._connection.rollback()
                self._pending_receipt = None
                raise ResourceCataloguePersistenceError() from exc

        try:
            self._connection.commit()
        except PsycopgError as exc:
            self._pending_receipt = None
            raise ResourceCataloguePersistenceOutcomeUnknown() from exc

        self._pending_receipt = None
