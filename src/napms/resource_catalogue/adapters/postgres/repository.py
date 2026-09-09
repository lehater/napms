from datetime import datetime

from psycopg import Connection, Error as PsycopgError

from napms.resource_catalogue.application.ports import (
    ResourceCataloguePersistenceError,
)
from napms.resource_catalogue.domain.model import (
    EndpointAddress,
    ResourceCatalogueInvariantError,
    ResourceRealizationVersion,
    ResourceScopeAffiliation,
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


    def list_effective_for_scope(
        self,
        *,
        responsibility_scope: str,
        as_of: datetime,
        offset: int,
        limit: int,
        search: str | None = None,
    ) -> tuple[ResourceScopeAffiliation, ...]:
        try:
            ambiguous = self._connection.execute(
                """
                SELECT resource_reference
                FROM napms_resource_catalogue.resource_scope_affiliations
                WHERE responsibility_scope = %s
                  AND valid_from <= %s
                  AND (valid_to IS NULL OR %s < valid_to)
                GROUP BY resource_reference
                HAVING count(*) > 1
                LIMIT 1
                """,
                (responsibility_scope, as_of, as_of),
            ).fetchone()
            if ambiguous is not None:
                raise ResourceCataloguePersistenceError(
                    "ambiguous effective Resource Scope Affiliation"
                )

            params = [responsibility_scope, as_of, as_of]
            search_clause = ""
            if search:
                search_clause = " AND resource_reference ILIKE %s"
                params.append(f"%{search}%")
            params.extend((offset, limit))
            rows = self._connection.execute(
                f"""
                SELECT
                    affiliation_reference,
                    resource_reference,
                    responsibility_scope,
                    valid_from,
                    valid_to,
                    provenance_reference
                FROM napms_resource_catalogue.resource_scope_affiliations
                WHERE responsibility_scope = %s
                  AND valid_from <= %s
                  AND (valid_to IS NULL OR %s < valid_to)
                  {search_clause}
                ORDER BY resource_reference, affiliation_reference
                OFFSET %s
                LIMIT %s
                """,
                tuple(params),
            ).fetchall()
            return tuple(
                ResourceScopeAffiliation(
                    affiliation_reference=row[0],
                    resource_reference=row[1],
                    responsibility_scope=row[2],
                    valid_from=row[3],
                    valid_to=row[4],
                    provenance_reference=row[5],
                )
                for row in rows
            )
        except ResourceCataloguePersistenceError:
            raise
        except (PsycopgError, ResourceCatalogueInvariantError) as exc:
            raise ResourceCataloguePersistenceError() from exc

    def find_effective_realizations_for_resources(
        self,
        *,
        resource_references: tuple[str, ...],
        as_of: datetime,
    ) -> tuple[ResourceRealizationVersion, ...]:
        if not resource_references:
            return ()
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
                WHERE resource_reference = ANY(%s)
                  AND valid_from <= %s
                  AND (valid_to IS NULL OR %s < valid_to)
                ORDER BY resource_reference, fact_reference
                """,
                (list(resource_references), as_of, as_of),
            ).fetchall()
            return tuple(self._hydrate(row) for row in rows)
        except ResourceCataloguePersistenceError:
            raise
        except (PsycopgError, ResourceCatalogueInvariantError) as exc:
            raise ResourceCataloguePersistenceError() from exc

    def find_resources_with_realization_facts(
        self,
        *,
        resource_references: tuple[str, ...],
    ) -> tuple[str, ...]:
        if not resource_references:
            return ()
        try:
            rows = self._connection.execute(
                """
                SELECT DISTINCT resource_reference
                FROM napms_resource_catalogue.resource_realization_versions
                WHERE resource_reference = ANY(%s)
                ORDER BY resource_reference
                """,
                (list(resource_references),),
            ).fetchall()
            return tuple(row[0] for row in rows)
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
