from psycopg import Error as PsycopgError

from napms.contexts.resource_catalogue.application.ports import (
    ResourceCataloguePersistenceError,
)
from napms.contexts.resource_catalogue.application.read_resource_references import (
    ResourceReferenceItem,
    ResourceReferencePage,
)


class PostgresResourceReferenceQuery:
    def __init__(self, connection) -> None:
        self._connection = connection

    def page(
        self,
        *,
        candidate_resource_references,
        as_of,
        search,
        scope_reference,
        sort,
        offset,
        limit,
    ) -> ResourceReferencePage:
        candidates = tuple(dict.fromkeys(candidate_resource_references))
        if not candidates:
            return ResourceReferencePage(items=(), total=0)
        pattern = f"%{search}%" if search else None
        where = """
            r.resource_reference = ANY(%s)
            AND (
                %s::text IS NULL
                OR r.resource_reference ILIKE %s
                OR r.display_name ILIKE %s
            )
            AND (
                %s::text IS NULL OR EXISTS (
                    SELECT 1
                      FROM napms_resource_catalogue.resource_scope_affiliations rsa
                     WHERE rsa.resource_reference = r.resource_reference
                       AND rsa.responsibility_scope = %s
                       AND rsa.valid_from <= %s
                       AND (rsa.valid_to IS NULL OR %s < rsa.valid_to)
                )
            )
        """
        params = (
            list(candidates), search, pattern, pattern, scope_reference,
            scope_reference, as_of, as_of,
        )
        scope_sort = """
            COALESCE((
                SELECT min(rsa.responsibility_scope)
                  FROM napms_resource_catalogue.resource_scope_affiliations rsa
                 WHERE rsa.resource_reference = r.resource_reference
                   AND rsa.valid_from <= %s
                   AND (rsa.valid_to IS NULL OR %s < rsa.valid_to)
            ), '')
        """
        descending = sort.startswith("-")
        direction = "DESC" if descending else "ASC"
        if sort.lstrip("-") == "scope":
            order = f"{scope_sort} {direction}, r.resource_reference {direction}"
            order_params = (as_of, as_of)
        else:
            order = (
                f"COALESCE(r.display_name, r.resource_reference) {direction}, "
                f"r.resource_reference {direction}"
            )
            order_params = ()
        try:
            total = self._connection.execute(
                f"SELECT count(*) FROM napms_resource_catalogue.resources r WHERE {where}",
                params,
            ).fetchone()[0]
            rows = self._connection.execute(
                f"""
                SELECT r.resource_reference, r.display_name,
                       ARRAY(
                           SELECT DISTINCT rsa.responsibility_scope
                             FROM napms_resource_catalogue.resource_scope_affiliations rsa
                            WHERE rsa.resource_reference = r.resource_reference
                              AND rsa.valid_from <= %s
                              AND (rsa.valid_to IS NULL OR %s < rsa.valid_to)
                            ORDER BY rsa.responsibility_scope
                       )
                  FROM napms_resource_catalogue.resources r
                 WHERE {where}
                 ORDER BY {order}
                 OFFSET %s LIMIT %s
                """,
                (as_of, as_of) + params + order_params + (offset, limit),
            ).fetchall()
            return ResourceReferencePage(
                items=tuple(
                    ResourceReferenceItem(row[0], row[1], tuple(row[2])) for row in rows
                ),
                total=int(total),
            )
        except PsycopgError as exc:
            raise ResourceCataloguePersistenceError(
                "resource reference projection failed"
            ) from exc
