from datetime import datetime

from psycopg import Connection, Error as PsycopgError

from napms.contexts.resource_catalogue.application.curation_read import (
    ResourceCatalogueListItem,
    ResourceCatalogueWorkspaceCounts,
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

    @staticmethod
    def _effective_realization() -> str:
        return """
            EXISTS (
                SELECT 1
                FROM napms_resource_catalogue.resource_realization_versions rr
                WHERE rr.resource_reference = r.resource_reference
                  AND rr.valid_from <= %(as_of)s
                  AND (rr.valid_to IS NULL OR %(as_of)s < rr.valid_to)
            )
        """

    @staticmethod
    def _effective_scope() -> str:
        return """
            EXISTS (
                SELECT 1
                FROM napms_resource_catalogue.resource_scope_affiliations rsa
                WHERE rsa.resource_reference = r.resource_reference
                  AND rsa.valid_from <= %(as_of)s
                  AND (rsa.valid_to IS NULL OR %(as_of)s < rsa.valid_to)
            )
        """

    @staticmethod
    def _effective_responsibility() -> str:
        return """
            EXISTS (
                SELECT 1
                FROM napms_resource_catalogue.resource_responsibilities rsp
                WHERE rsp.resource_reference = r.resource_reference
                  AND rsp.valid_from <= %(as_of)s
                  AND (rsp.valid_to IS NULL OR %(as_of)s < rsp.valid_to)
            )
        """

    def _base_conditions(
        self,
        *,
        search: str | None,
        responsibility_scope: str | None,
        as_of: datetime,
    ) -> tuple[list[str], dict[str, object]]:
        conditions = ["TRUE"]
        params: dict[str, object] = {"as_of": as_of}

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

        return conditions, params

    def _current_conditions(
        self,
        *,
        lifecycle: str,
        data_state: str | None,
    ) -> list[str]:
        conditions: list[str] = []
        if lifecycle == "active":
            conditions.append("r.lifecycle_state = 'Active'")
        elif lifecycle == "retired":
            conditions.append("r.lifecycle_state = 'Retired'")
        elif lifecycle != "all":
            raise ResourceCataloguePersistenceError("unsupported Resource workspace lifecycle")

        if data_state == "missing-address":
            conditions.append(f"NOT ({self._effective_realization()})")
        elif data_state == "missing-scope":
            conditions.append(f"NOT ({self._effective_scope()})")
        elif data_state == "missing-responsibility":
            conditions.append(f"NOT ({self._effective_responsibility()})")
        elif data_state is not None:
            raise ResourceCataloguePersistenceError("unsupported Resource workspace data state")
        return conditions

    @staticmethod
    def _order_by(sort_by: str, sort_direction: str) -> str:
        direction = {"asc": "ASC", "desc": "DESC"}.get(sort_direction)
        if direction is None:
            raise ResourceCataloguePersistenceError("unsupported Resource workspace sort direction")
        if sort_by == "name":
            return f"r.display_name {direction} NULLS LAST, r.resource_reference {direction}"
        if sort_by == "reference":
            return f"r.resource_reference {direction}"
        if sort_by == "lifecycle":
            return f"r.lifecycle_state {direction}, r.display_name ASC NULLS LAST, r.resource_reference ASC"
        raise ResourceCataloguePersistenceError("unsupported Resource workspace sort field")

    def list_resources(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None,
        lifecycle: str,
        responsibility_scope: str | None,
        data_state: str | None,
        sort_by: str,
        sort_direction: str,
        as_of: datetime,
    ) -> tuple[ResourceCatalogueListItem, ...]:
        conditions, params = self._base_conditions(
            search=search,
            responsibility_scope=responsibility_scope,
            as_of=as_of,
        )
        conditions.extend(self._current_conditions(lifecycle=lifecycle, data_state=data_state))
        params.update({"offset": offset, "limit": limit})

        effective_realization = self._effective_realization()
        effective_scope = self._effective_scope()
        effective_responsibility = self._effective_responsibility()
        where_sql = " AND ".join(conditions)
        order_sql = self._order_by(sort_by, sort_direction)

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
                ORDER BY {order_sql}
                OFFSET %(offset)s LIMIT %(limit)s
                """,
                params,
            ).fetchall()
        except PsycopgError as exc:
            raise ResourceCataloguePersistenceError() from exc

        return tuple(self._item(row) for row in rows)

    def summarize_resources(
        self,
        *,
        search: str | None,
        lifecycle: str,
        responsibility_scope: str | None,
        data_state: str | None,
        as_of: datetime,
    ) -> ResourceCatalogueWorkspaceCounts:
        conditions, params = self._base_conditions(
            search=search,
            responsibility_scope=responsibility_scope,
            as_of=as_of,
        )
        current = self._current_conditions(lifecycle=lifecycle, data_state=data_state)
        current_sql = " AND ".join(current) if current else "TRUE"
        where_sql = " AND ".join(conditions)
        effective_realization = self._effective_realization()
        effective_scope = self._effective_scope()
        effective_responsibility = self._effective_responsibility()

        try:
            row = self._connection.execute(
                f"""
                SELECT
                    COUNT(*) FILTER (WHERE {current_sql}) AS current_total,
                    COUNT(*) AS all_count,
                    COUNT(*) FILTER (WHERE r.lifecycle_state = 'Active') AS active_count,
                    COUNT(*) FILTER (WHERE r.lifecycle_state = 'Retired') AS retired_count,
                    COUNT(*) FILTER (WHERE NOT ({effective_realization})) AS missing_address_count,
                    COUNT(*) FILTER (WHERE NOT ({effective_scope})) AS missing_scope_count,
                    COUNT(*) FILTER (WHERE NOT ({effective_responsibility})) AS missing_responsibility_count
                FROM napms_resource_catalogue.resources r
                WHERE {where_sql}
                """,
                params,
            ).fetchone()
        except PsycopgError as exc:
            raise ResourceCataloguePersistenceError() from exc

        return ResourceCatalogueWorkspaceCounts(
            total=int(row[0]),
            all=int(row[1]),
            active=int(row[2]),
            retired=int(row[3]),
            missing_address=int(row[4]),
            missing_scope=int(row[5]),
            missing_responsibility=int(row[6]),
        )

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
