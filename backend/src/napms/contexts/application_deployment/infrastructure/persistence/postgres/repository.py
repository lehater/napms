from typing import Any
from uuid import UUID

import psycopg

from napms.contexts.application_deployment.application.queries import (
    DeploymentCataloguePage,
    DeploymentCatalogueQuery,
    DeploymentSortField,
    SortDirection,
)
from napms.contexts.application_deployment.domain.model import ComponentDeployment


class PostgresComponentDeploymentRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def add(self, deployment: ComponentDeployment) -> None:
        with psycopg.connect(self._dsn) as connection:
            connection.execute(
                """
                INSERT INTO application_deployment.component_deployment
                    (deployment_ref, component_ref, resource_ref)
                VALUES (%s, %s, %s)
                """,
                (
                    deployment.deployment_ref,
                    deployment.component_ref,
                    deployment.resource_ref,
                ),
            )

    def query_deployments(
        self,
        query: DeploymentCatalogueQuery,
    ) -> DeploymentCataloguePage:
        conditions: list[str] = []
        parameters: list[object] = []

        if query.search:
            search = query.search.strip()
            if search:
                conditions.append(
                    """
                    (
                        CAST(deployment_ref AS text) ILIKE %s
                        OR CAST(component_ref AS text) ILIKE %s
                        OR CAST(resource_ref AS text) ILIKE %s
                    )
                    """
                )
                pattern = f"%{search}%"
                parameters.extend((pattern, pattern, pattern))

        if query.component_ref is not None:
            conditions.append("component_ref = %s")
            parameters.append(query.component_ref)

        if query.resource_ref is not None:
            conditions.append("resource_ref = %s")
            parameters.append(query.resource_ref)

        where = "" if not conditions else " WHERE " + " AND ".join(conditions)
        order_by = {
            DeploymentSortField.DEPLOYMENT_REF: "deployment_ref",
            DeploymentSortField.COMPONENT_REF: "component_ref",
            DeploymentSortField.RESOURCE_REF: "resource_ref",
        }[query.sort_by]
        direction = "ASC" if query.sort_direction is SortDirection.ASC else "DESC"
        offset = (query.page - 1) * query.page_size

        with psycopg.connect(self._dsn) as connection:
            total_row = connection.execute(
                f"""
                SELECT COUNT(*)
                FROM application_deployment.component_deployment
                {where}
                """,
                parameters,
            ).fetchone()
            total = 0 if total_row is None else total_row[0]
            rows = connection.execute(
                f"""
                SELECT deployment_ref, component_ref, resource_ref
                FROM application_deployment.component_deployment
                {where}
                ORDER BY {order_by} {direction}, deployment_ref ASC
                LIMIT %s OFFSET %s
                """,
                (*parameters, query.page_size, offset),
            ).fetchall()

        return DeploymentCataloguePage(
            items=tuple(
                ComponentDeployment(
                    deployment_ref=row[0],
                    component_ref=row[1],
                    resource_ref=row[2],
                )
                for row in rows
            ),
            total=total,
            page=query.page,
            page_size=query.page_size,
        )

    def resolve_deployment(self, deployment_ref: UUID) -> ComponentDeployment | None:
        with psycopg.connect(self._dsn) as connection:
            return self.resolve_deployment_in(connection, deployment_ref)

    @staticmethod
    def resolve_deployment_in(
        connection: psycopg.Connection[Any],
        deployment_ref: UUID,
    ) -> ComponentDeployment | None:
        row = connection.execute(
            """
            SELECT deployment_ref, component_ref, resource_ref
            FROM application_deployment.component_deployment
            WHERE deployment_ref = %s
            """,
            (deployment_ref,),
        ).fetchone()
        if row is None:
            return None
        return ComponentDeployment(
            deployment_ref=row[0],
            component_ref=row[1],
            resource_ref=row[2],
        )
