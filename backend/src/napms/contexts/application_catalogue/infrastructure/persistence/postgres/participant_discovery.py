from psycopg import Connection, Error as PsycopgError

from napms.contexts.application_catalogue.application.participant_discovery import (
    ApplicationCatalogueParticipant,
)
from napms.contexts.application_catalogue.application.ports import CataloguePersistenceError


class PostgresApplicationCatalogueParticipantRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def list_active_participants(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None,
    ) -> tuple[ApplicationCatalogueParticipant, ...]:
        try:
            if search:
                pattern = f"%{search}%"
                rows = self._connection.execute(
                    """
                    SELECT
                        a.application_id,
                        a.display_name,
                        c.component_id,
                        c.display_name,
                        d.component_deployment_id,
                        d.display_name
                    FROM napms_application_catalogue.applications AS a
                    JOIN napms_application_catalogue.components AS c
                      ON c.application_id = a.application_id
                    JOIN napms_application_catalogue.component_deployments AS d
                      ON d.component_id = c.component_id
                    WHERE a.lifecycle_state = 'Active'
                      AND c.lifecycle_state = 'Active'
                      AND d.lifecycle_state = 'Active'
                      AND (
                          a.display_name ILIKE %s
                          OR c.display_name ILIKE %s
                          OR COALESCE(d.display_name, '') ILIKE %s
                          OR a.application_id::text ILIKE %s
                          OR c.component_id::text ILIKE %s
                          OR d.component_deployment_id::text ILIKE %s
                      )
                    ORDER BY
                        a.display_name,
                        c.display_name,
                        d.display_name NULLS LAST,
                        d.component_deployment_id
                    OFFSET %s LIMIT %s
                    """,
                    (
                        pattern,
                        pattern,
                        pattern,
                        pattern,
                        pattern,
                        pattern,
                        offset,
                        limit,
                    ),
                ).fetchall()
            else:
                rows = self._connection.execute(
                    """
                    SELECT
                        a.application_id,
                        a.display_name,
                        c.component_id,
                        c.display_name,
                        d.component_deployment_id,
                        d.display_name
                    FROM napms_application_catalogue.applications AS a
                    JOIN napms_application_catalogue.components AS c
                      ON c.application_id = a.application_id
                    JOIN napms_application_catalogue.component_deployments AS d
                      ON d.component_id = c.component_id
                    WHERE a.lifecycle_state = 'Active'
                      AND c.lifecycle_state = 'Active'
                      AND d.lifecycle_state = 'Active'
                    ORDER BY
                        a.display_name,
                        c.display_name,
                        d.display_name NULLS LAST,
                        d.component_deployment_id
                    OFFSET %s LIMIT %s
                    """,
                    (offset, limit),
                ).fetchall()
        except PsycopgError as exc:
            raise CataloguePersistenceError() from exc

        return tuple(
            ApplicationCatalogueParticipant(
                application_id=row[0],
                application_display_name=row[1],
                component_id=row[2],
                component_display_name=row[3],
                component_deployment_id=row[4],
                deployment_display_name=row[5],
            )
            for row in rows
        )
