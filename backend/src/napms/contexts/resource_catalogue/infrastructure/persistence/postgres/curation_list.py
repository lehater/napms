from datetime import datetime

from psycopg import Connection, Error as PsycopgError

from napms.contexts.resource_catalogue.application.curation_read import (
    ResourceCatalogueListItem,
)
from napms.contexts.resource_catalogue.application.ports import ResourceCataloguePersistenceError
from napms.contexts.resource_catalogue.domain.model import (
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
        data_state: str | None,
        as_of: datetime,
    ) -> tuple[ResourceCatalogueListItem, ...]:
        conditions = ["(%(include_retired)s OR r.lifecycle_state = 'Active')"]
        params = {
            "as_of": as_of,
            "include_retired": include_retired,
            "offset": offset,
            "limit": limit,
        }

        effective_realization = """
            EXISTS (
                SELECT 1
                FROM napms_resource_catalogue.resource_realization_versions rr
                WHERE rr.resource_reference = r.resource_reference
                  AND rr.valid_from <= %(as_of)s
                  AND (rr.valid_to IS NULL OR %(as_of)s < rr.valid_to)
            )
        """
        effective_scope = """
            EXISTS (
                SELECT 1
                FROM napms_resource_catalogue.resource_scope_affiliations rsa
                WHERE rsa.resource_reference = r.resource_reference
                  AND rsa.valid_from <= %(as_of)s
                  AND (rsa.valid_to IS NULL OR %(as_of)s < rsa.valid_to)
            )
        """
        effective_responsibility = """
            EXISTS (
                SELECT 1
                FROM napms_resource_catalogue.resource_responsibilities rsp
                WHERE rsp.resource_reference = r.resource_reference
                  AND rsp.valid_from <= %(as_of)s
                  AND (rsp.valid_to IS NULL OR %(as_of)s < rsp.valid_to)
            )
        """

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

        if data_state == "missing-address":
            conditions.append(f"NOT ({effective_realization})")
        elif data_state == "missing-scope":
            conditions.append(f"NOT ({effective_scope})")
        elif data_state == "missing-responsibility":
            conditions.append(f"NOT ({effective_responsibility})")

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
                    OR EXISTS (
                        SELECT 1
                        FROM napms_resource_catalogue.resource_scope_affiliations rsa
                        WHERE rsa.resource_reference = r.resource_reference
                          AND rsa.valid_from <= %(as_of)s
                          AND (rsa.valid_to IS NULL OR %(as_of)s < rsa.valid_to)
                          AND rsa.responsibility_scope ILIKE %(pattern)s
                    )
                    OR EXISTS (
                        SELECT 1
                        FROM napms_resource_catalogue.resource_realization_versions rr
                        JOIN napms_resource_catalogue.resource_endpoints e
                          ON e.fact_reference = rr.fact_reference
                        WHERE rr.resource_reference = r.resource_reference
                          AND rr.valid_from <= %(as_of)s
                          AND (rr.valid_to IS NULL OR %(as_of)s < rr.valid_to)
                          AND e.technical_address ILIKE %(pattern)s
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
                    {effective_realization} AS has_effective_realization,
                    {effective_scope} AS has_effective_scope_affiliation,
                    {effective_responsibility} AS has_effective_responsibility,
                    EXISTS (
                        SELECT 1
                        FROM napms_resource_catalogue.resource_responsibilities rsp
                        WHERE rsp.resource_reference = r.resource_reference
                          AND rsp.valid_from <= %(as_of)s
                          AND (rsp.valid_to IS NULL OR %(as_of)s < rsp.valid_to)
                          AND rsp.contact IS NOT NULL
                          AND btrim(rsp.contact) <> ''
                    ) AS has_effective_contact,
                    ARRAY(
                        SELECT DISTINCT e.technical_address
                        FROM napms_resource_catalogue.resource_realization_versions rr
                        JOIN napms_resource_catalogue.resource_endpoints e
                          ON e.fact_reference = rr.fact_reference
                        WHERE rr.resource_reference = r.resource_reference
                          AND rr.valid_from <= %(as_of)s
                          AND (rr.valid_to IS NULL OR %(as_of)s < rr.valid_to)
                        ORDER BY e.technical_address
                    ) AS current_addresses,
                    ARRAY(
                        SELECT DISTINCT rsa.responsibility_scope
                        FROM napms_resource_catalogue.resource_scope_affiliations rsa
                        WHERE rsa.resource_reference = r.resource_reference
                          AND rsa.valid_from <= %(as_of)s
                          AND (rsa.valid_to IS NULL OR %(as_of)s < rsa.valid_to)
                        ORDER BY rsa.responsibility_scope
                    ) AS current_scopes,
                    ARRAY(
                        SELECT DISTINCT rsp.display_name
                        FROM napms_resource_catalogue.resource_responsibilities rsp
                        WHERE rsp.resource_reference = r.resource_reference
                          AND rsp.role = 'TechnicalOwner'
                          AND rsp.valid_from <= %(as_of)s
                          AND (rsp.valid_to IS NULL OR %(as_of)s < rsp.valid_to)
                        ORDER BY rsp.display_name
                    ) AS technical_owners
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
            current_addresses=tuple(row[10] or ()),
            current_scopes=tuple(row[11] or ()),
            technical_owners=tuple(row[12] or ()),
        )
