from datetime import datetime
from uuid import UUID

from psycopg import Connection, Error as PsycopgError

from napms.application_catalogue.application.ports import CataloguePersistenceError
from napms.application_catalogue.domain.model import (
    CatalogueInvariantError,
    DcsRevision,
    DeploymentResourceBinding,
)


class PostgresApplicationCatalogueRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def get_dcs_revision(self, revision_id: UUID) -> DcsRevision | None:
        try:
            row = self._connection.execute(
                """
                SELECT
                    revision_id,
                    source_component_deployment_id,
                    destination_component_deployment_id,
                    projection_payload,
                    provenance_reference
                FROM napms_application_catalogue.dcs_revisions
                WHERE revision_id = %s
                """,
                (revision_id,),
            ).fetchone()
            if row is None:
                return None
            return DcsRevision(
                revision_id=row[0],
                source_component_deployment_id=row[1],
                destination_component_deployment_id=row[2],
                projection_payload=bytes(row[3]),
                provenance_reference=row[4],
            )
        except CataloguePersistenceError:
            raise
        except (PsycopgError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError() from exc

    def list_dcs_revisions(
        self,
        *,
        offset: int,
        limit: int,
    ) -> tuple[DcsRevision, ...]:
        try:
            rows = self._connection.execute(
                """
                SELECT
                    revision_id,
                    source_component_deployment_id,
                    destination_component_deployment_id,
                    projection_payload,
                    provenance_reference
                FROM napms_application_catalogue.dcs_revisions
                ORDER BY revision_id
                OFFSET %s
                LIMIT %s
                """,
                (offset, limit),
            ).fetchall()
            return tuple(
                DcsRevision(
                    revision_id=row[0],
                    source_component_deployment_id=row[1],
                    destination_component_deployment_id=row[2],
                    projection_payload=bytes(row[3]),
                    provenance_reference=row[4],
                )
                for row in rows
            )
        except CataloguePersistenceError:
            raise
        except (PsycopgError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError() from exc

    def find_effective_bindings(
        self,
        *,
        component_deployment_id: UUID,
        as_of: datetime,
    ) -> tuple[DeploymentResourceBinding, ...]:
        try:
            rows = self._connection.execute(
                """
                SELECT
                    reference_id,
                    component_deployment_id,
                    resource_reference,
                    valid_from,
                    valid_to,
                    provenance_reference
                FROM napms_application_catalogue.deployment_resource_bindings
                WHERE component_deployment_id = %s
                  AND valid_from <= %s
                  AND (valid_to IS NULL OR %s < valid_to)
                ORDER BY resource_reference, reference_id
                """,
                (component_deployment_id, as_of, as_of),
            ).fetchall()
            return tuple(
                DeploymentResourceBinding(
                    reference_id=row[0],
                    component_deployment_id=row[1],
                    resource_reference=row[2],
                    valid_from=row[3],
                    valid_to=row[4],
                    provenance_reference=row[5],
                )
                for row in rows
            )
        except CataloguePersistenceError:
            raise
        except (PsycopgError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError() from exc
