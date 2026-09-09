from datetime import datetime
from uuid import UUID

from psycopg import Connection, Error as PsycopgError

from napms.application_catalogue.application.ports import CataloguePersistenceError
from napms.application_catalogue.domain.model import (
    CatalogueInvariantError,
    ComponentDeployment,
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
                    provenance_reference,
                    display_name
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
                display_name=row[5],
            )
        except CataloguePersistenceError:
            raise
        except (PsycopgError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError() from exc

    def get_dcs_revisions(
        self,
        revision_ids: tuple[UUID, ...],
    ) -> tuple[DcsRevision, ...]:
        if not revision_ids:
            return ()
        try:
            rows = self._connection.execute(
                """
                SELECT
                    revision_id,
                    source_component_deployment_id,
                    destination_component_deployment_id,
                    projection_payload,
                    provenance_reference,
                    display_name
                FROM napms_application_catalogue.dcs_revisions
                WHERE revision_id = ANY(%s)
                ORDER BY revision_id
                """,
                (list(revision_ids),),
            ).fetchall()
            return tuple(
                DcsRevision(
                    revision_id=row[0],
                    source_component_deployment_id=row[1],
                    destination_component_deployment_id=row[2],
                    projection_payload=bytes(row[3]),
                    provenance_reference=row[4],
                    display_name=row[5],
                )
                for row in rows
            )
        except CataloguePersistenceError:
            raise
        except (PsycopgError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError() from exc

    def get_component_deployments(
        self,
        deployment_ids: tuple[UUID, ...],
    ) -> tuple[ComponentDeployment, ...]:
        if not deployment_ids:
            return ()
        try:
            rows = self._connection.execute(
                """
                SELECT
                    component_deployment_id,
                    provenance_reference,
                    display_name
                FROM napms_application_catalogue.component_deployments
                WHERE component_deployment_id = ANY(%s)
                ORDER BY component_deployment_id
                """,
                (list(deployment_ids),),
            ).fetchall()
            return tuple(
                ComponentDeployment(
                    deployment_id=row[0],
                    provenance_reference=row[1],
                    display_name=row[2],
                )
                for row in rows
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
        search: str | None = None,
    ) -> tuple[DcsRevision, ...]:
        try:
            if search:
                pattern = f"%{search}%"
                rows = self._connection.execute(
                    """
                    SELECT
                        d.revision_id,
                        d.source_component_deployment_id,
                        d.destination_component_deployment_id,
                        d.projection_payload,
                        d.provenance_reference,
                        d.display_name
                    FROM napms_application_catalogue.dcs_revisions AS d
                    JOIN napms_application_catalogue.component_deployments AS source
                      ON source.component_deployment_id = d.source_component_deployment_id
                    JOIN napms_application_catalogue.component_deployments AS destination
                      ON destination.component_deployment_id = d.destination_component_deployment_id
                    WHERE d.display_name ILIKE %s
                       OR source.display_name ILIKE %s
                       OR destination.display_name ILIKE %s
                       OR d.revision_id::text ILIKE %s
                       OR d.source_component_deployment_id::text ILIKE %s
                       OR d.destination_component_deployment_id::text ILIKE %s
                    ORDER BY d.revision_id
                    OFFSET %s
                    LIMIT %s
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
                        revision_id,
                        source_component_deployment_id,
                        destination_component_deployment_id,
                        projection_payload,
                        provenance_reference,
                        display_name
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
                    display_name=row[5],
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


    def find_effective_bindings_for_resources(
        self,
        *,
        resource_references: tuple[str, ...],
        as_of: datetime,
        limit: int | None = None,
    ) -> tuple[DeploymentResourceBinding, ...]:
        if not resource_references:
            return ()
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
                WHERE resource_reference = ANY(%s)
                  AND valid_from <= %s
                  AND (valid_to IS NULL OR %s < valid_to)
                ORDER BY resource_reference, component_deployment_id, reference_id
                LIMIT %s
                """,
                (
                    list(resource_references),
                    as_of,
                    as_of,
                    limit if limit is not None else 2147483647,
                ),
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

    def find_effective_bindings_for_components(
        self,
        *,
        component_deployment_ids: tuple[UUID, ...],
        as_of: datetime,
        limit: int | None = None,
    ) -> tuple[DeploymentResourceBinding, ...]:
        if not component_deployment_ids:
            return ()
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
                WHERE component_deployment_id = ANY(%s)
                  AND valid_from <= %s
                  AND (valid_to IS NULL OR %s < valid_to)
                ORDER BY component_deployment_id, resource_reference, reference_id
                LIMIT %s
                """,
                (
                    list(component_deployment_ids),
                    as_of,
                    as_of,
                    limit if limit is not None else 2147483647,
                ),
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

    def list_dcs_revisions_for_components(
        self,
        *,
        component_deployment_ids: tuple[UUID, ...],
        limit: int | None = None,
    ) -> tuple[DcsRevision, ...]:
        if not component_deployment_ids:
            return ()
        try:
            rows = self._connection.execute(
                """
                SELECT
                    revision_id,
                    source_component_deployment_id,
                    destination_component_deployment_id,
                    projection_payload,
                    provenance_reference,
                    display_name
                FROM napms_application_catalogue.dcs_revisions
                WHERE source_component_deployment_id = ANY(%s)
                   OR destination_component_deployment_id = ANY(%s)
                ORDER BY revision_id
                LIMIT %s
                """,
                (
                    list(component_deployment_ids),
                    list(component_deployment_ids),
                    limit if limit is not None else 2147483647,
                ),
            ).fetchall()
            return tuple(
                DcsRevision(
                    revision_id=row[0],
                    source_component_deployment_id=row[1],
                    destination_component_deployment_id=row[2],
                    projection_payload=bytes(row[3]),
                    provenance_reference=row[4],
                    display_name=row[5],
                )
                for row in rows
            )
        except CataloguePersistenceError:
            raise
        except (PsycopgError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError() from exc
