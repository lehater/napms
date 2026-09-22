from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from uuid import UUID

import psycopg

from napms.contexts.resource_catalogue.application.ports import ResourceVersionConflict
from napms.contexts.resource_catalogue.application.queries import (
    ResourceCataloguePage,
    ResourceCatalogueQuery,
    ResourceSortField,
    SortDirection,
)
from napms.contexts.resource_catalogue.domain.model import (
    AddressFact,
    AddressKind,
    AddressRealization,
    Resource,
    ResourceEndpoint,
    ResponsibilityFact,
    ResponsibilityRole,
    SiteFact,
)


class PostgresResourceCatalogueRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def add(self, resource: Resource) -> None:
        with psycopg.connect(self._dsn) as connection:
            connection.execute(
                """
                INSERT INTO resource_catalogue.resource
                    (resource_ref, display_name, authority_scope_ref, version)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    resource.resource_ref,
                    resource.display_name,
                    resource.authority_scope_ref,
                    resource.version,
                ),
            )

    def query(self, query: ResourceCatalogueQuery) -> ResourceCataloguePage:
        conditions: list[str] = []
        parameters: list[object] = []

        if query.search:
            search = query.search.strip()
            if search:
                conditions.append(
                    "(r.display_name ILIKE %s OR CAST(r.resource_ref AS text) ILIKE %s)"
                )
                pattern = f"%{search}%"
                parameters.extend((pattern, pattern))

        if query.authority_scope_ref:
            conditions.append("r.authority_scope_ref = %s")
            parameters.append(query.authority_scope_ref)

        if query.site_ref is not None:
            conditions.append(
                """
                EXISTS (
                    SELECT 1
                    FROM resource_catalogue.resource_site_history AS site
                    WHERE site.resource_ref = r.resource_ref
                      AND site.effective_to IS NULL
                      AND site.site_ref = %s
                )
                """
            )
            parameters.append(query.site_ref)

        where = "" if not conditions else " WHERE " + " AND ".join(conditions)
        order_by = {
            ResourceSortField.DISPLAY_NAME: "r.display_name",
            ResourceSortField.RESOURCE_REF: "r.resource_ref",
            ResourceSortField.AUTHORITY_SCOPE_REF: "r.authority_scope_ref",
        }[query.sort_by]
        direction = "ASC" if query.sort_direction is SortDirection.ASC else "DESC"
        offset = (query.page - 1) * query.page_size

        with psycopg.connect(self._dsn) as connection:
            total_row = connection.execute(
                f"SELECT COUNT(*) FROM resource_catalogue.resource AS r{where}",
                parameters,
            ).fetchone()
            total = 0 if total_row is None else total_row[0]
            rows = connection.execute(
                f"""
                SELECT r.resource_ref
                FROM resource_catalogue.resource AS r
                {where}
                ORDER BY {order_by} {direction}, r.resource_ref ASC
                LIMIT %s OFFSET %s
                """,
                (*parameters, query.page_size, offset),
            ).fetchall()

        items = tuple(resource for (ref,) in rows if (resource := self.get(ref)) is not None)
        return ResourceCataloguePage(
            items=items,
            total=total,
            page=query.page,
            page_size=query.page_size,
        )

    def get(self, resource_ref: UUID) -> Resource | None:
        with psycopg.connect(self._dsn) as connection:
            row = connection.execute(
                """
                SELECT resource_ref, display_name, authority_scope_ref, version
                FROM resource_catalogue.resource
                WHERE resource_ref = %s
                """,
                (resource_ref,),
            ).fetchone()
            if row is None:
                return None

            endpoint_rows = connection.execute(
                """
                SELECT endpoint_ref
                FROM resource_catalogue.resource_endpoint
                WHERE resource_ref = %s
                ORDER BY created_at, endpoint_ref
                """,
                (resource_ref,),
            ).fetchall()
            endpoints = tuple(
                self._load_endpoint(connection, endpoint_ref) for (endpoint_ref,) in endpoint_rows
            )

            site_rows = connection.execute(
                """
                SELECT history_ref, site_ref, effective_from, effective_to, changed_by_subject
                FROM resource_catalogue.resource_site_history
                WHERE resource_ref = %s
                ORDER BY effective_from, history_ref
                """,
                (resource_ref,),
            ).fetchall()
            site_facts = tuple(
                SiteFact(
                    fact_ref=history_ref,
                    site_ref=site_ref,
                    effective_from=effective_from,
                    effective_to=effective_to,
                    changed_by_subject=changed_by_subject,
                )
                for (
                    history_ref,
                    site_ref,
                    effective_from,
                    effective_to,
                    changed_by_subject,
                ) in site_rows
                if site_ref is not None
            )

            responsibility_rows = connection.execute(
                """
                SELECT assignment_ref, role, group_ref, effective_from, effective_to,
                       changed_by_subject
                FROM resource_catalogue.resource_responsibility_history
                WHERE resource_ref = %s
                ORDER BY effective_from, assignment_ref
                """,
                (resource_ref,),
            ).fetchall()
            responsibility_facts = tuple(
                ResponsibilityFact(
                    fact_ref=assignment_ref,
                    role=ResponsibilityRole(role),
                    group_ref=group_ref,
                    effective_from=effective_from,
                    effective_to=effective_to,
                    changed_by_subject=changed_by_subject,
                )
                for (
                    assignment_ref,
                    role,
                    group_ref,
                    effective_from,
                    effective_to,
                    changed_by_subject,
                ) in responsibility_rows
            )

            return Resource(
                resource_ref=row[0],
                display_name=row[1],
                authority_scope_ref=row[2],
                version=row[3],
                endpoints=endpoints,
                current_site=next(
                    (fact for fact in site_facts if fact.effective_to is None),
                    None,
                ),
                site_history=tuple(fact for fact in site_facts if fact.effective_to is not None),
                responsibilities=tuple(
                    fact for fact in responsibility_facts if fact.effective_to is None
                ),
                responsibility_history=tuple(
                    fact for fact in responsibility_facts if fact.effective_to is not None
                ),
            )

    def resolve_resource(self, resource_ref: UUID) -> Resource | None:
        return self.get(resource_ref)

    @classmethod
    def resolve_resource_in(
        cls,
        connection: psycopg.Connection[Any],
        resource_ref: UUID,
    ) -> Resource | None:
        row = connection.execute(
            """
            SELECT resource_ref, display_name, authority_scope_ref, version
            FROM resource_catalogue.resource
            WHERE resource_ref = %s
            """,
            (resource_ref,),
        ).fetchone()
        if row is None:
            return None
        endpoint_rows = connection.execute(
            """
            SELECT endpoint_ref
            FROM resource_catalogue.resource_endpoint
            WHERE resource_ref = %s
            ORDER BY endpoint_ref
            """,
            (resource_ref,),
        ).fetchall()
        return Resource(
            resource_ref=row[0],
            display_name=row[1],
            authority_scope_ref=row[2],
            version=row[3],
            endpoints=tuple(
                cls._load_endpoint(connection, endpoint_ref) for (endpoint_ref,) in endpoint_rows
            ),
        )

    @staticmethod
    def resolve_authority_scope_in(
        connection: psycopg.Connection[Any],
        resource_ref: UUID,
    ) -> str | None:
        row = connection.execute(
            """
            SELECT authority_scope_ref
            FROM resource_catalogue.resource
            WHERE resource_ref = %s
            """,
            (resource_ref,),
        ).fetchone()
        return None if row is None else row[0]

    def save(self, resource: Resource, *, expected_version: int) -> None:
        with psycopg.connect(self._dsn) as connection:
            updated = connection.execute(
                """
                UPDATE resource_catalogue.resource
                SET version = %s
                WHERE resource_ref = %s AND version = %s
                """,
                (resource.version, resource.resource_ref, expected_version),
            )
            if updated.rowcount != 1:
                raise ResourceVersionConflict(str(resource.resource_ref))

            for endpoint in resource.endpoints:
                connection.execute(
                    """
                    INSERT INTO resource_catalogue.resource_endpoint
                        (endpoint_ref, resource_ref)
                    VALUES (%s, %s)
                    ON CONFLICT (endpoint_ref) DO NOTHING
                    """,
                    (endpoint.endpoint_ref, resource.resource_ref),
                )
                self._upsert_address_facts(
                    connection,
                    endpoint.endpoint_ref,
                    (*endpoint.address_history,)
                    + (() if endpoint.current_address is None else (endpoint.current_address,)),
                )

            self._upsert_site_facts(
                connection,
                resource.resource_ref,
                (*resource.site_history,)
                + (() if resource.current_site is None else (resource.current_site,)),
            )
            self._upsert_responsibility_facts(
                connection,
                resource.resource_ref,
                (*resource.responsibility_history, *resource.responsibilities),
            )

    @staticmethod
    def _load_endpoint(
        connection: psycopg.Connection[Any],
        endpoint_ref: UUID,
    ) -> ResourceEndpoint:
        rows = connection.execute(
            """
            SELECT address_fact_ref, address_kind, address_value, effective_from,
                   effective_to, changed_by_subject
            FROM resource_catalogue.resource_endpoint_address_history
            WHERE endpoint_ref = %s
            ORDER BY effective_from, address_fact_ref
            """,
            (endpoint_ref,),
        ).fetchall()
        facts = tuple(
            AddressFact(
                fact_ref=fact_ref,
                address=AddressRealization(
                    kind=AddressKind(kind),
                    value=value,
                ),
                effective_from=effective_from,
                effective_to=effective_to,
                changed_by_subject=changed_by_subject,
            )
            for fact_ref, kind, value, effective_from, effective_to, changed_by_subject in rows
        )
        return ResourceEndpoint(
            endpoint_ref=endpoint_ref,
            current_address=next((fact for fact in facts if fact.effective_to is None), None),
            address_history=tuple(fact for fact in facts if fact.effective_to is not None),
        )

    @staticmethod
    def _upsert_address_facts(
        connection: psycopg.Connection[Any],
        endpoint_ref: UUID,
        facts: Iterable[AddressFact],
    ) -> None:
        for fact in facts:
            connection.execute(
                """
                INSERT INTO resource_catalogue.resource_endpoint_address_history
                    (address_fact_ref, endpoint_ref, address_kind, address_value,
                     effective_from, effective_to, changed_by_subject)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (address_fact_ref) DO UPDATE
                SET effective_to = EXCLUDED.effective_to
                """,
                (
                    fact.fact_ref,
                    endpoint_ref,
                    fact.address.kind.value,
                    fact.address.value,
                    fact.effective_from,
                    fact.effective_to,
                    fact.changed_by_subject,
                ),
            )

    @staticmethod
    def _upsert_site_facts(
        connection: psycopg.Connection[Any],
        resource_ref: UUID,
        facts: Iterable[SiteFact],
    ) -> None:
        for fact in facts:
            connection.execute(
                """
                INSERT INTO resource_catalogue.resource_site_history
                    (history_ref, resource_ref, site_ref, effective_from,
                     effective_to, changed_by_subject)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (history_ref) DO UPDATE
                SET effective_to = EXCLUDED.effective_to
                """,
                (
                    fact.fact_ref,
                    resource_ref,
                    fact.site_ref,
                    fact.effective_from,
                    fact.effective_to,
                    fact.changed_by_subject,
                ),
            )

    @staticmethod
    def _upsert_responsibility_facts(
        connection: psycopg.Connection[Any],
        resource_ref: UUID,
        facts: Iterable[ResponsibilityFact],
    ) -> None:
        for fact in facts:
            connection.execute(
                """
                INSERT INTO resource_catalogue.resource_responsibility_history
                    (assignment_ref, resource_ref, role, group_ref, effective_from,
                     effective_to, changed_by_subject)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (assignment_ref) DO UPDATE
                SET effective_to = EXCLUDED.effective_to
                """,
                (
                    fact.fact_ref,
                    resource_ref,
                    fact.role.value,
                    fact.group_ref,
                    fact.effective_from,
                    fact.effective_to,
                    fact.changed_by_subject,
                ),
            )
