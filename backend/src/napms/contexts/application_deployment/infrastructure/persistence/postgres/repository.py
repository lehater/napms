from typing import Any
from uuid import UUID

import psycopg

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
