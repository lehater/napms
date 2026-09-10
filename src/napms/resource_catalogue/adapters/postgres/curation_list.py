from datetime import datetime

from psycopg import Connection, Error as PsycopgError

from napms.resource_catalogue.application.curation_read import (
    ResourceCatalogueListItem,
)
from napms.resource_catalogue.application.ports import ResourceCataloguePersistenceError
from napms.resource_catalogue.domain.model import (
    Resource,
    ResourceCatalogueInvariantError,
    ResourceLifecycleState,
)


class PostgresResourceCatalogueListQuery:
    """Read projection for the Resources workspace at one logical as-of time."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def list_resources(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None,
        include_retired: bool,
        responsibility_scope: str | None,
        as_of: datetime,
    ) -> tuple[ResourceCatalogueListItem, ...]:
        conditions = ["(%(include_retired)s OR r.lifecycle_state = 'Active')"]
        params = {
            "as_of": as_of,
            "include_retired": include_retired,
            "offset": offset,
            "limit": limit,
        }

        if responsibility_scope is not None:
            conditions.append(
                """
                EXISTS (
                    SELECT 1
                    FROM napms_resource_catalogue.resource_scope_affiliations rsa
                    WHERE rsa.resource_reference = r.resource_reference
                      AND rsa.responsibility_scope = %(scope)s
                      AND rsa.valid_from <= %(as_of)s
                      AND (rsa.valid_to IS NULL OR %(as_of)s < rsa.valid_to)
                )
                """
            )
            params["scope"] = responsibility_scope

        if search is not None:
            conditions.append(
                """
                (
                    r.resource_reference ILIKE %(pattern)s
                    OR r.display_name ILIKE %(pattern)s
                    OR EXISTS (
                        SELECT 1
                        FROM napms_resource_catalogue.resource_responsibilities rsp
                        WHERE rsp.resource_reference = r.resource_reference
                          AND rsp.valid_from <= %(as_of)s
                          AND (rsp.valid_to IS NULL OR %(as_of)s < rsp.valid_to)
                          AND (
                              rsp.party_reference ILIKE %(pattern)s
                              OR rsp.display_name ILIKE %(pattern)s
                              OR rsp.contact ILIKE %(pattern)s
                          )
                    )
                )
                """
            )
            params["pattern"] = f"%{search}%"

        where_sql = " AND ".join(conditions)
        try:
            rows = self._connection.execute(
                f"""
                SELECT
                    r.resource_reference,
                    r.provenance_reference,
                    r.display_name,
                    r.lifecycle_state,
                    r.retirement_provenance_reference,
                    r.version,
                    EXISTS (
                        SELECT 1
                        FROM napms_resource_catalogue.resource_realization_versions rr
                        WHERE rr.resource_reference = r.resource_reference
                          AND rr.valid_from <= %(as_of)s
                          AND (rr.valid_to IS NULL OR %(as_of)s < rr.valid_to)
                    ) AS has_effective_realization,
                    EXISTS (
                        SELECT 1
                        FROM napms_resource_catalogue.resource_scope_affiliations rsa
                        WHERE rsa.resource_reference = r.resource_reference
                          AND rsa.valid_from <= %(as_of)s
                          AND (rsa.valid_to IS NULL OR %(as_of)s < rsa.valid_to)
                    ) AS has_effective_scope_affiliation,
                    EXISTS (
                        SELECT 1
                        FROM napms_resource_catalogue.resource_responsibilities rsp
                        WHERE rsp.resource_reference = r.resource_reference
                          AND rsp.valid_from <= %(as_of)s
                          AND (rsp.valid_to IS NULL OR %(as_of)s < rsp.valid_to)
                    ) AS has_effective_responsibility,
                    EXISTS (
                        SELECT 1
                        FROM napms_resource_catalogue.resource_responsibilities rsp
                        WHERE rsp.resource_reference = r.resource_reference
                          AND rsp.valid_from <= %(as_of)s
                          AND (rsp.valid_to IS NULL OR %(as_of)s < rsp.valid_to)
                          AND rsp.contact IS NOT NULL
                          AND btrim(rsp.contact) <> ''
                    ) AS has_effective_contact
                FROM napms_resource_catalogue.resources r
                WHERE {where_sql}
                ORDER BY r.display_name NULLS LAST, r.resource_reference
                OFFSET %(offset)s LIMIT %(limit)s
                """,
                params,
            ).fetchall()
        except PsycopgError as exc:
            raise ResourceCataloguePersistenceError() from exc

        return tuple(self._item(row) for row in rows)

    @staticmethod
    def _item(row) -> ResourceCatalogueListItem:
        try:
            resource = Resource(
                resource_reference=row[0],
                provenance_reference=row[1],
                display_name=row[2],
                lifecycle_state=ResourceLifecycleState(row[3]),
                retirement_provenance_reference=row[4],
                version=row[5],
            )
        except (ValueError, ResourceCatalogueInvariantError) as exc:
            raise ResourceCataloguePersistenceError(
                "invalid persisted Resource workspace row"
            ) from exc

        return ResourceCatalogueListItem(
            resource=resource,
            has_effective_realization=bool(row[6]),
            has_effective_scope_affiliation=bool(row[7]),
            has_effective_responsibility=bool(row[8]),
            has_effective_contact=bool(row[9]),
        )
