from uuid import UUID

from psycopg import Error as PsycopgError
from psycopg.errors import UniqueViolation

from napms.contexts.application_catalogue.infrastructure.persistence.postgres.curation_repository import (
    PostgresApplicationCatalogueCurationRepository,
)
from napms.contexts.application_catalogue.application.ports import (
    CatalogueIdempotencyConflict,
    CataloguePersistenceError,
    CataloguePersistenceOutcomeUnknown,
)


class TransactionalPostgresApplicationCatalogueCurationRepository(
    PostgresApplicationCatalogueCurationRepository
):
    """ACC curation repository with explicit pre-commit vs commit failure semantics."""

    def commit(self) -> None:
        if self._pending_receipt is not None:
            actor_id, idempotency_key, receipt = self._pending_receipt
            is_uuid = isinstance(receipt.result_id, UUID)
            try:
                self._connection.execute(
                    """
                    INSERT INTO napms_application_catalogue.curation_command_receipts (
                        actor_id, idempotency_key, command_kind,
                        request_fingerprint, result_uuid, result_reference, result_version
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        actor_id,
                        idempotency_key,
                        receipt.command_kind,
                        receipt.request_fingerprint,
                        receipt.result_id if is_uuid else None,
                        None if is_uuid else str(receipt.result_id),
                        receipt.result_version,
                    ),
                )
            except UniqueViolation as exc:
                self._connection.rollback()
                self._pending_receipt = None
                raise CatalogueIdempotencyConflict() from exc
            except PsycopgError as exc:
                self._connection.rollback()
                self._pending_receipt = None
                raise CataloguePersistenceError() from exc

        try:
            self._connection.commit()
        except PsycopgError as exc:
            self._pending_receipt = None
            raise CataloguePersistenceOutcomeUnknown() from exc

        self._pending_receipt = None
