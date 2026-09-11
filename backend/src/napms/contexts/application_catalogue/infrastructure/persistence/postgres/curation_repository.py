from uuid import UUID

from psycopg import Connection, Error as PsycopgError
from psycopg.errors import UniqueViolation

from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueCommandReceipt,
    CatalogueConcurrencyConflict,
    CatalogueIdempotencyConflict,
    CataloguePersistenceError,
    CataloguePersistenceOutcomeUnknown,
)
from napms.contexts.application_catalogue.domain.model import (
    Application,
    CatalogueInvariantError,
    CatalogueLifecycleState,
    Component,
    ComponentDeployment,
    DcsRevision,
    DeploymentResourceBinding,
)


class PostgresApplicationCatalogueCurationRepository:
    """Task-oriented ACC curation repository and transaction boundary."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection
        self._pending_receipt: tuple[str, str, ApplicationCatalogueCommandReceipt] | None = None

    def get_application(self, application_id: UUID) -> Application | None:
        row = self._fetchone(
            """
            SELECT application_id, display_name, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version
            FROM napms_application_catalogue.applications
            WHERE application_id = %s
            """,
            (application_id,),
        )
        return self._application(row) if row is not None else None

    def add_application(self, application: Application) -> None:
        self._execute(
            """
            INSERT INTO napms_application_catalogue.applications (
                application_id, display_name, provenance_reference,
                lifecycle_state, retirement_provenance_reference, version
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                application.application_id,
                application.display_name,
                application.provenance_reference,
                application.lifecycle_state.value,
                application.retirement_provenance_reference,
                application.version,
            ),
        )

    def save_application(self, application: Application, *, expected_version: int) -> None:
        result = self._execute(
            """
            UPDATE napms_application_catalogue.applications
            SET display_name = %s,
                lifecycle_state = %s,
                retirement_provenance_reference = %s,
                version = %s
            WHERE application_id = %s
              AND version = %s
            """,
            (
                application.display_name,
                application.lifecycle_state.value,
                application.retirement_provenance_reference,
                application.version,
                application.application_id,
                expected_version,
            ),
        )
        self._require_updated(result)

    def has_active_components(self, *, application_id: UUID) -> bool:
        row = self._fetchone(
            """
            SELECT 1
            FROM napms_application_catalogue.components
            WHERE application_id = %s
              AND lifecycle_state = 'Active'
            LIMIT 1
            """,
            (application_id,),
        )
        return row is not None

    def get_component(self, component_id: UUID) -> Component | None:
        row = self._fetchone(
            """
            SELECT component_id, application_id, display_name, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version
            FROM napms_application_catalogue.components
            WHERE component_id = %s
            """,
            (component_id,),
        )
        return self._component(row) if row is not None else None

    def add_component(self, component: Component) -> None:
        self._execute(
            """
            INSERT INTO napms_application_catalogue.components (
                component_id, application_id, display_name, provenance_reference,
                lifecycle_state, retirement_provenance_reference, version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                component.component_id,
                component.application_id,
                component.display_name,
                component.provenance_reference,
                component.lifecycle_state.value,
                component.retirement_provenance_reference,
                component.version,
            ),
        )

    def save_component(self, component: Component, *, expected_version: int) -> None:
        result = self._execute(
            """
            UPDATE napms_application_catalogue.components
            SET display_name = %s,
                lifecycle_state = %s,
                retirement_provenance_reference = %s,
                version = %s
            WHERE component_id = %s
              AND version = %s
            """,
            (
                component.display_name,
                component.lifecycle_state.value,
                component.retirement_provenance_reference,
                component.version,
                component.component_id,
                expected_version,
            ),
        )
        self._require_updated(result)

    def has_active_component_deployments(self, *, component_id: UUID) -> bool:
        row = self._fetchone(
            """
            SELECT 1
            FROM napms_application_catalogue.component_deployments
            WHERE component_id = %s
              AND lifecycle_state = 'Active'
            LIMIT 1
            """,
            (component_id,),
        )
        return row is not None

    def get_component_deployment(self, deployment_id: UUID) -> ComponentDeployment | None:
        row = self._fetchone(
            """
            SELECT component_deployment_id, component_id, provenance_reference,
                   display_name, lifecycle_state, retirement_provenance_reference, version
            FROM napms_application_catalogue.component_deployments
            WHERE component_deployment_id = %s
            """,
            (deployment_id,),
        )
        return self._deployment(row) if row is not None else None

    def add_component_deployment(self, deployment: ComponentDeployment) -> None:
        self._execute(
            """
            INSERT INTO napms_application_catalogue.component_deployments (
                component_deployment_id, component_id, provenance_reference, display_name,
                lifecycle_state, retirement_provenance_reference, version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                deployment.deployment_id,
                deployment.component_id,
                deployment.provenance_reference,
                deployment.display_name,
                deployment.lifecycle_state.value,
                deployment.retirement_provenance_reference,
                deployment.version,
            ),
        )

    def save_component_deployment(
        self,
        deployment: ComponentDeployment,
        *,
        expected_version: int,
    ) -> None:
        result = self._execute(
            """
            UPDATE napms_application_catalogue.component_deployments
            SET display_name = %s,
                lifecycle_state = %s,
                retirement_provenance_reference = %s,
                version = %s
            WHERE component_deployment_id = %s
              AND component_id = %s
              AND version = %s
            """,
            (
                deployment.display_name,
                deployment.lifecycle_state.value,
                deployment.retirement_provenance_reference,
                deployment.version,
                deployment.deployment_id,
                deployment.component_id,
                expected_version,
            ),
        )
        self._require_updated(result)

    def get_dcs_revision(self, revision_id: UUID) -> DcsRevision | None:
        row = self._fetchone(
            """
            SELECT revision_id, source_component_deployment_id,
                   destination_component_deployment_id, projection_payload,
                   provenance_reference, display_name
            FROM napms_application_catalogue.dcs_revisions
            WHERE revision_id = %s
            """,
            (revision_id,),
        )
        return self._dcs(row) if row is not None else None

    def add_dcs_revision(self, revision: DcsRevision) -> None:
        self._execute(
            """
            INSERT INTO napms_application_catalogue.dcs_revisions (
                revision_id, source_component_deployment_id,
                destination_component_deployment_id, projection_payload,
                provenance_reference, display_name
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                revision.revision_id,
                revision.source_component_deployment_id,
                revision.destination_component_deployment_id,
                revision.projection_payload,
                revision.provenance_reference,
                revision.display_name,
            ),
        )

    def get_binding(self, reference_id: str) -> DeploymentResourceBinding | None:
        row = self._fetchone(
            """
            SELECT reference_id, component_deployment_id, resource_reference,
                   valid_from, valid_to, provenance_reference,
                   end_provenance_reference, version
            FROM napms_application_catalogue.deployment_resource_bindings
            WHERE reference_id = %s
            """,
            (reference_id,),
        )
        return self._binding(row) if row is not None else None

    def find_overlapping_bindings(
        self,
        *,
        component_deployment_id: UUID,
        resource_reference: str,
        valid_from,
        valid_to,
    ) -> tuple[DeploymentResourceBinding, ...]:
        rows = self._fetchall(
            """
            SELECT reference_id, component_deployment_id, resource_reference,
                   valid_from, valid_to, provenance_reference,
                   end_provenance_reference, version
            FROM napms_application_catalogue.deployment_resource_bindings
            WHERE component_deployment_id = %s
              AND resource_reference = %s
              AND valid_from < COALESCE(%s, 'infinity'::timestamptz)
              AND %s < COALESCE(valid_to, 'infinity'::timestamptz)
            ORDER BY valid_from, reference_id
            """,
            (component_deployment_id, resource_reference, valid_to, valid_from),
        )
        return tuple(self._binding(row) for row in rows)

    def add_binding(self, binding: DeploymentResourceBinding) -> None:
        self._execute(
            """
            INSERT INTO napms_application_catalogue.deployment_resource_bindings (
                reference_id, component_deployment_id, resource_reference,
                valid_from, valid_to, provenance_reference,
                end_provenance_reference, version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                binding.reference_id,
                binding.component_deployment_id,
                binding.resource_reference,
                binding.valid_from,
                binding.valid_to,
                binding.provenance_reference,
                binding.end_provenance_reference,
                binding.version,
            ),
        )

    def save_binding(
        self,
        binding: DeploymentResourceBinding,
        *,
        expected_version: int,
    ) -> None:
        result = self._execute(
            """
            UPDATE napms_application_catalogue.deployment_resource_bindings
            SET valid_to = %s,
                end_provenance_reference = %s,
                version = %s
            WHERE reference_id = %s
              AND component_deployment_id = %s
              AND resource_reference = %s
              AND version = %s
            """,
            (
                binding.valid_to,
                binding.end_provenance_reference,
                binding.version,
                binding.reference_id,
                binding.component_deployment_id,
                binding.resource_reference,
                expected_version,
            ),
        )
        self._require_updated(result)

    def list_applications(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None,
        include_retired: bool,
    ) -> tuple[Application, ...]:
        pattern = f"%{search}%" if search else None
        rows = self._fetchall(
            """
            SELECT application_id, display_name, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version
            FROM napms_application_catalogue.applications
            WHERE (%s OR lifecycle_state = 'Active')
              AND (%s::text IS NULL OR display_name ILIKE %s OR application_id::text ILIKE %s)
            ORDER BY display_name, application_id
            OFFSET %s LIMIT %s
            """,
            (include_retired, pattern, pattern, pattern, offset, limit),
        )
        return tuple(self._application(row) for row in rows)

    def list_components(
        self,
        *,
        application_id: UUID,
        include_retired: bool,
    ) -> tuple[Component, ...]:
        rows = self._fetchall(
            """
            SELECT component_id, application_id, display_name, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version
            FROM napms_application_catalogue.components
            WHERE application_id = %s
              AND (%s OR lifecycle_state = 'Active')
            ORDER BY display_name, component_id
            """,
            (application_id, include_retired),
        )
        return tuple(self._component(row) for row in rows)

    def list_component_deployments(
        self,
        *,
        component_id: UUID,
        include_retired: bool,
    ) -> tuple[ComponentDeployment, ...]:
        rows = self._fetchall(
            """
            SELECT component_deployment_id, component_id, provenance_reference,
                   display_name, lifecycle_state, retirement_provenance_reference, version
            FROM napms_application_catalogue.component_deployments
            WHERE component_id = %s
              AND (%s OR lifecycle_state = 'Active')
            ORDER BY display_name NULLS LAST, component_deployment_id
            """,
            (component_id, include_retired),
        )
        return tuple(self._deployment(row) for row in rows)

    def find_command_receipt(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
    ) -> ApplicationCatalogueCommandReceipt | None:
        row = self._fetchone(
            """
            SELECT command_kind, request_fingerprint,
                   result_uuid, result_reference, result_version
            FROM napms_application_catalogue.curation_command_receipts
            WHERE actor_id = %s AND idempotency_key = %s
            """,
            (actor_id, idempotency_key),
        )
        if row is None:
            return None
        result_id = row[2] if row[2] is not None else row[3]
        return ApplicationCatalogueCommandReceipt(
            command_kind=row[0],
            request_fingerprint=row[1],
            result_id=result_id,
            result_version=row[4],
        )

    def record_command_receipt(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
        receipt: ApplicationCatalogueCommandReceipt,
    ) -> None:
        if self._pending_receipt is not None:
            raise CataloguePersistenceError("only one command receipt may be staged")
        self._pending_receipt = (actor_id, idempotency_key, receipt)

    def commit(self) -> None:
        try:
            if self._pending_receipt is not None:
                actor_id, idempotency_key, receipt = self._pending_receipt
                is_uuid = isinstance(receipt.result_id, UUID)
                self._connection.execute(
                    """
                    INSERT INTO napms_application_catalogue.curation_command_receipts (
                        actor_id, idempotency_key, command_kind,
                        request_fingerprint, result_uuid, result_reference, result_version
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        actor_id,
                        idempotency_key,
                        receipt.command_kind,
                        receipt.request_fingerprint,
                        receipt.result_id if is_uuid else None,
                        None if is_uuid else str(receipt.result_id),
                        receipt.result_version,
                    ),
                )
            self._connection.commit()
            self._pending_receipt = None
        except UniqueViolation as exc:
            self._connection.rollback()
            self._pending_receipt = None
            raise CatalogueIdempotencyConflict() from exc
        except PsycopgError as exc:
            self._pending_receipt = None
            raise CataloguePersistenceOutcomeUnknown() from exc

    def _require_updated(self, result) -> None:
        if result.rowcount != 1:
            self._connection.rollback()
            self._pending_receipt = None
            raise CatalogueConcurrencyConflict()

    def _execute(self, sql: str, params: tuple):
        try:
            return self._connection.execute(sql, params)
        except PsycopgError as exc:
            self._connection.rollback()
            self._pending_receipt = None
            raise CataloguePersistenceError() from exc

    def _fetchone(self, sql: str, params: tuple):
        try:
            return self._connection.execute(sql, params).fetchone()
        except PsycopgError as exc:
            raise CataloguePersistenceError() from exc

    def _fetchall(self, sql: str, params: tuple):
        try:
            return self._connection.execute(sql, params).fetchall()
        except PsycopgError as exc:
            raise CataloguePersistenceError() from exc

    @staticmethod
    def _application(row) -> Application:
        try:
            return Application(
                application_id=row[0],
                display_name=row[1],
                provenance_reference=row[2],
                lifecycle_state=CatalogueLifecycleState(row[3]),
                retirement_provenance_reference=row[4],
                version=row[5],
            )
        except (ValueError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError("invalid persisted Application") from exc

    @staticmethod
    def _component(row) -> Component:
        try:
            return Component(
                component_id=row[0],
                application_id=row[1],
                display_name=row[2],
                provenance_reference=row[3],
                lifecycle_state=CatalogueLifecycleState(row[4]),
                retirement_provenance_reference=row[5],
                version=row[6],
            )
        except (ValueError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError("invalid persisted Component") from exc

    @staticmethod
    def _deployment(row) -> ComponentDeployment:
        try:
            return ComponentDeployment(
                deployment_id=row[0],
                component_id=row[1],
                provenance_reference=row[2],
                display_name=row[3],
                lifecycle_state=CatalogueLifecycleState(row[4]),
                retirement_provenance_reference=row[5],
                version=row[6],
            )
        except (ValueError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError(
                "invalid persisted Component Deployment"
            ) from exc

    @staticmethod
    def _dcs(row) -> DcsRevision:
        try:
            return DcsRevision(
                revision_id=row[0],
                source_component_deployment_id=row[1],
                destination_component_deployment_id=row[2],
                projection_payload=bytes(row[3]),
                provenance_reference=row[4],
                display_name=row[5],
            )
        except CatalogueInvariantError as exc:
            raise CataloguePersistenceError("invalid persisted DCS revision") from exc

    @staticmethod
    def _binding(row) -> DeploymentResourceBinding:
        try:
            return DeploymentResourceBinding(
                reference_id=row[0],
                component_deployment_id=row[1],
                resource_reference=row[2],
                valid_from=row[3],
                valid_to=row[4],
                provenance_reference=row[5],
                end_provenance_reference=row[6],
                version=row[7],
            )
        except CatalogueInvariantError as exc:
            raise CataloguePersistenceError(
                "invalid persisted Deployment Resource Binding"
            ) from exc
