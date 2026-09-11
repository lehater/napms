from datetime import datetime

from psycopg import Error as PsycopgError
from psycopg.errors import UniqueViolation

from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.curation_list import (
    PostgresResourceCatalogueListQuery,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.curation_repository import (
    PostgresResourceCatalogueCurationRepository,
)
from napms.contexts.resource_catalogue.application.curation_read import (
    ResourceCatalogueListItem,
)
from napms.contexts.resource_catalogue.application.ports import (
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
        data_state: str | None,
        as_of: datetime,
    ) -> tuple[ResourceCatalogueListItem, ...]:
        return PostgresResourceCatalogueListQuery(self._connection).list_resources(
            offset=offset,
            limit=limit,
            search=search,
            include_retired=include_retired,
            responsibility_scope=responsibility_scope,
            data_state=data_state,
            as_of=as_of,
        )

    def list_realizations(self, *, resource_reference: str):
        rows = self._realization_rows(
            "WHERE r.resource_reference = %s",
            (resource_reference,),
        )
        return self._realizations(rows)

    def list_scope_affiliations(self, *, resource_reference: str):
        rows = self._fetchall(
            """
            SELECT affiliation_reference, resource_reference, responsibility_scope,
                   valid_from, valid_to, provenance_reference,
                   end_provenance_reference, version
            FROM napms_resource_catalogue.resource_scope_affiliations
            WHERE resource_reference = %s
            ORDER BY valid_from DESC, affiliation_reference
            """,
            (resource_reference,),
        )
        return tuple(self._affiliation(row) for row in rows)

    def list_responsibilities(self, *, resource_reference: str):
        rows = self._fetchall(
            """
            SELECT assignment_reference, resource_reference, party_reference,
                   party_kind, role, display_name, contact, valid_from, valid_to,
                   provenance_reference, end_provenance_reference, version
            FROM napms_resource_catalogue.resource_responsibilities
            WHERE resource_reference = %s
            ORDER BY valid_from DESC, assignment_reference
            """,
            (resource_reference,),
        )
        return tuple(self._responsibility(row) for row in rows)

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
