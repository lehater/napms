from psycopg import Error as PsycopgError
from psycopg.errors import UniqueViolation

from napms.resource_catalogue.adapters.postgres.curation_repository import (
    PostgresResourceCatalogueCurationRepository,
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
