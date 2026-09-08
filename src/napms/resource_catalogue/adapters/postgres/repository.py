from datetime import datetime

from psycopg import Connection, Error as PsycopgError

from napms.resource_catalogue.application.ports import (
    ResourceCataloguePersistenceError,
)
from napms.resource_catalogue.domain.model import (
    EndpointAddress,
    ResourceCatalogueInvariantError,
    ResourceRealizationVersion,
)


class PostgresResourceCatalogueRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def find_effective_realizations(
        self,
        *,
        resource_reference: str,
        as_of: datetime,
    ) -> tuple[ResourceRealizationVersion, ...]:
        try:
            rows = self._connection.execute(
                """
                SELECT
                    fact_reference,
                    resource_reference,
                    valid_from,
                    valid_to,
                    provenance_reference
                FROM napms_resource_catalogue.resource_realization_versions
                WHERE resource_reference = %s
                  AND valid_from <= %s
                  AND (valid_to IS NULL OR %s < valid_to)
                ORDER BY fact_reference
                """,
                (resource_reference, as_of, as_of),
            ).fetchall()
            return tuple(self._hydrate(row) for row in rows)
        except ResourceCataloguePersistenceError:
            raise
        except (PsycopgError, ResourceCatalogueInvariantError) as exc:
            raise ResourceCataloguePersistenceError() from exc

    def has_realization_facts(self, *, resource_reference: str) -> bool:
        try:
            row = self._connection.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM napms_resource_catalogue.resource_realization_versions
                    WHERE resource_reference = %s
                )
                """,
                (resource_reference,),
            ).fetchone()
            return bool(row[0])
        except PsycopgError as exc:
            raise ResourceCataloguePersistenceError() from exc

    def _hydrate(self, row: tuple) -> ResourceRealizationVersion:
        endpoint_rows = self._connection.execute(
            """
            SELECT endpoint_reference, technical_address
            FROM napms_resource_catalogue.resource_endpoints
            WHERE fact_reference = %s
            ORDER BY endpoint_reference, technical_address
            """,
            (row[0],),
        ).fetchall()
        try:
            return ResourceRealizationVersion(
                fact_reference=row[0],
                resource_reference=row[1],
                endpoint_realizations=tuple(
                    EndpointAddress(
                        endpoint_reference=endpoint_row[0],
                        technical_address=endpoint_row[1],
                    )
                    for endpoint_row in endpoint_rows
                ),
                valid_from=row[2],
                valid_to=row[3],
                provenance_reference=row[4],
            )
        except ResourceCatalogueInvariantError as exc:
            raise ResourceCataloguePersistenceError(
                "invalid persisted Resource realization"
            ) from exc
