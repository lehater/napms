from uuid import UUID

from psycopg.errors import UniqueViolation

from napms.application_catalogue.adapters.dcs_authoring import (
    JsonDcsAuthoringProjectionEncoder,
)
from napms.application_catalogue.adapters.postgres.curation_repository import (
    PostgresApplicationCatalogueCurationRepository,
)
from napms.application_catalogue.application.ports import (
    CatalogueConcurrencyConflict,
    CataloguePersistenceError,
)
from napms.application_catalogue.domain.model import (
    Application,
    CatalogueInvariantError,
    CatalogueLifecycleState,
    Component,
    ComponentDeployment,
    DeploymentResourceBinding,
)
from napms.application_catalogue.domain.target_model import (
    ApplicationDeployment,
    DeploymentInteraction,
    DeploymentInteractionCompatibility,
    DeploymentInteractionSide,
    InteractionDefinition,
)
from napms.policy_export.application.normalization_ports import DcsProjectionDecodeError


class PostgresTargetApplicationCatalogueRepository(
    PostgresApplicationCatalogueCurationRepository
):
    """PostgreSQL UoW for the I31 target model plus retained compatibility rows."""

    def __init__(self, connection) -> None:
        super().__init__(connection)
        self._traffic_codec = JsonDcsAuthoringProjectionEncoder()

    # Application / Component overrides retain the I27 identity while adding target metadata.
    def get_application(self, application_id: UUID) -> Application | None:
        row = self._fetchone(
            """
            SELECT application_id, display_name, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version,
                   description, domain, owner_reference
            FROM napms_application_catalogue.applications
            WHERE application_id = %s
            """,
            (application_id,),
        )
        return self._target_application(row) if row is not None else None

    def add_application(self, application: Application) -> None:
        self._execute(
            """
            INSERT INTO napms_application_catalogue.applications (
                application_id, display_name, provenance_reference,
                lifecycle_state, retirement_provenance_reference, version,
                description, domain, owner_reference
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                application.application_id,
                application.display_name,
                application.provenance_reference,
                application.lifecycle_state.value,
                application.retirement_provenance_reference,
                application.version,
                application.description,
                application.domain,
                application.owner_reference,
            ),
        )

    def save_application(self, application: Application, *, expected_version: int) -> None:
        result = self._execute(
            """
            UPDATE napms_application_catalogue.applications
            SET display_name = %s,
                lifecycle_state = %s,
                retirement_provenance_reference = %s,
                version = %s,
                description = %s,
                domain = %s,
                owner_reference = %s
            WHERE application_id = %s
              AND version = %s
            """,
            (
                application.display_name,
                application.lifecycle_state.value,
                application.retirement_provenance_reference,
                application.version,
                application.description,
                application.domain,
                application.owner_reference,
                application.application_id,
                expected_version,
            ),
        )
        self._require_updated(result)

    def get_component(self, component_id: UUID) -> Component | None:
        row = self._fetchone(
            """
            SELECT component_id, application_id, display_name, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version,
                   component_type, description
            FROM napms_application_catalogue.components
            WHERE component_id = %s
            """,
            (component_id,),
        )
        return self._target_component(row) if row is not None else None

    def add_component(self, component: Component) -> None:
        self._execute(
            """
            INSERT INTO napms_application_catalogue.components (
                component_id, application_id, display_name, provenance_reference,
                lifecycle_state, retirement_provenance_reference, version,
                component_type, description
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                component.component_id,
                component.application_id,
                component.display_name,
                component.provenance_reference,
                component.lifecycle_state.value,
                component.retirement_provenance_reference,
                component.version,
                component.component_type,
                component.description,
            ),
        )

    def save_component(self, component: Component, *, expected_version: int) -> None:
        result = self._execute(
            """
            UPDATE napms_application_catalogue.components
            SET display_name = %s,
                lifecycle_state = %s,
                retirement_provenance_reference = %s,
                version = %s,
                component_type = %s,
                description = %s
            WHERE component_id = %s
              AND version = %s
            """,
            (
                component.display_name,
                component.lifecycle_state.value,
                component.retirement_provenance_reference,
                component.version,
                component.component_type,
                component.description,
                component.component_id,
                expected_version,
            ),
        )
        self._require_updated(result)

    # Target structural persistence.
    def get_interaction_definition(
        self,
        interaction_definition_id: UUID,
    ) -> InteractionDefinition | None:
        row = self._fetchone(
            """
            SELECT interaction_definition_id, application_id,
                   source_component_id, destination_component_id,
                   traffic_payload, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version
            FROM napms_application_catalogue.interaction_definitions
            WHERE interaction_definition_id = %s
            """,
            (interaction_definition_id,),
        )
        return self._interaction_definition(row) if row is not None else None

    def add_interaction_definition(self, value: InteractionDefinition) -> None:
        self._execute(
            """
            INSERT INTO napms_application_catalogue.interaction_definitions (
                interaction_definition_id, application_id,
                source_component_id, destination_component_id,
                traffic_payload, provenance_reference,
                lifecycle_state, retirement_provenance_reference, version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                value.interaction_definition_id,
                value.application_id,
                value.source_component_id,
                value.destination_component_id,
                self._traffic_codec.encode(value.traffic_alternatives),
                value.provenance_reference,
                value.lifecycle_state.value,
                value.retirement_provenance_reference,
                value.version,
            ),
        )

    def save_interaction_definition(
        self,
        value: InteractionDefinition,
        *,
        expected_version: int,
    ) -> None:
        result = self._execute(
            """
            UPDATE napms_application_catalogue.interaction_definitions
            SET source_component_id = %s,
                destination_component_id = %s,
                traffic_payload = %s,
                lifecycle_state = %s,
                retirement_provenance_reference = %s,
                version = %s
            WHERE interaction_definition_id = %s
              AND version = %s
            """,
            (
                value.source_component_id,
                value.destination_component_id,
                self._traffic_codec.encode(value.traffic_alternatives),
                value.lifecycle_state.value,
                value.retirement_provenance_reference,
                value.version,
                value.interaction_definition_id,
                expected_version,
            ),
        )
        self._require_updated(result)

    def list_active_deployment_interactions_for_definition(
        self,
        *,
        interaction_definition_id: UUID,
    ) -> tuple[DeploymentInteraction, ...]:
        rows = self._fetchall(
            """
            SELECT deployment_interaction_id, application_deployment_id,
                   interaction_definition_id, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version
            FROM napms_application_catalogue.deployment_interactions
            WHERE interaction_definition_id = %s
              AND lifecycle_state = 'Active'
            ORDER BY deployment_interaction_id
            """,
            (interaction_definition_id,),
        )
        return tuple(self._deployment_interaction(row) for row in rows)

    def get_application_deployment(
        self,
        application_deployment_id: UUID,
    ) -> ApplicationDeployment | None:
        row = self._fetchone(
            """
            SELECT application_deployment_id, application_id,
                   company_reference, environment, scope_reference,
                   provenance_reference, lifecycle_state,
                   retirement_provenance_reference, version
            FROM napms_application_catalogue.application_deployments
            WHERE application_deployment_id = %s
            """,
            (application_deployment_id,),
        )
        return self._application_deployment(row) if row is not None else None

    def add_application_deployment(self, value: ApplicationDeployment) -> None:
        self._execute(
            """
            INSERT INTO napms_application_catalogue.application_deployments (
                application_deployment_id, application_id,
                company_reference, environment, scope_reference,
                provenance_reference, lifecycle_state,
                retirement_provenance_reference, version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                value.application_deployment_id,
                value.application_id,
                value.company_reference,
                value.environment,
                value.scope_reference,
                value.provenance_reference,
                value.lifecycle_state.value,
                value.retirement_provenance_reference,
                value.version,
            ),
        )

    def save_application_deployment(
        self,
        value: ApplicationDeployment,
        *,
        expected_version: int,
    ) -> None:
        result = self._execute(
            """
            UPDATE napms_application_catalogue.application_deployments
            SET company_reference = %s,
                environment = %s,
                scope_reference = %s,
                lifecycle_state = %s,
                retirement_provenance_reference = %s,
                version = %s
            WHERE application_deployment_id = %s
              AND version = %s
            """,
            (
                value.company_reference,
                value.environment,
                value.scope_reference,
                value.lifecycle_state.value,
                value.retirement_provenance_reference,
                value.version,
                value.application_deployment_id,
                expected_version,
            ),
        )
        self._require_updated(result)

    def get_deployment_interaction(
        self,
        deployment_interaction_id: UUID,
    ) -> DeploymentInteraction | None:
        row = self._fetchone(
            """
            SELECT deployment_interaction_id, application_deployment_id,
                   interaction_definition_id, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version
            FROM napms_application_catalogue.deployment_interactions
            WHERE deployment_interaction_id = %s
            """,
            (deployment_interaction_id,),
        )
        return self._deployment_interaction(row) if row is not None else None

    def find_active_deployment_interaction(
        self,
        *,
        application_deployment_id: UUID,
        interaction_definition_id: UUID,
    ) -> DeploymentInteraction | None:
        row = self._fetchone(
            """
            SELECT deployment_interaction_id, application_deployment_id,
                   interaction_definition_id, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version
            FROM napms_application_catalogue.deployment_interactions
            WHERE application_deployment_id = %s
              AND interaction_definition_id = %s
              AND lifecycle_state = 'Active'
            """,
            (application_deployment_id, interaction_definition_id),
        )
        return self._deployment_interaction(row) if row is not None else None

    def add_deployment_interaction(self, value: DeploymentInteraction) -> None:
        self._execute_unique_as_concurrency(
            """
            INSERT INTO napms_application_catalogue.deployment_interactions (
                deployment_interaction_id, application_deployment_id,
                interaction_definition_id, provenance_reference,
                lifecycle_state, retirement_provenance_reference, version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                value.deployment_interaction_id,
                value.application_deployment_id,
                value.interaction_definition_id,
                value.provenance_reference,
                value.lifecycle_state.value,
                value.retirement_provenance_reference,
                value.version,
            ),
        )

    def save_deployment_interaction(
        self,
        value: DeploymentInteraction,
        *,
        expected_version: int,
    ) -> None:
        result = self._execute(
            """
            UPDATE napms_application_catalogue.deployment_interactions
            SET lifecycle_state = %s,
                retirement_provenance_reference = %s,
                version = %s
            WHERE deployment_interaction_id = %s
              AND version = %s
            """,
            (
                value.lifecycle_state.value,
                value.retirement_provenance_reference,
                value.version,
                value.deployment_interaction_id,
                expected_version,
            ),
        )
        self._require_updated(result)

    def get_compatibility_projection(
        self,
        deployment_interaction_id: UUID,
    ) -> DeploymentInteractionCompatibility | None:
        row = self._fetchone(
            """
            SELECT c.deployment_interaction_id,
                   source.component_deployment_id,
                   destination.component_deployment_id,
                   c.current_dcs_revision_id,
                   c.version
            FROM napms_application_catalogue.deployment_interaction_compatibility AS c
            JOIN napms_application_catalogue.deployment_interaction_compatibility_sides AS source
              ON source.deployment_interaction_id = c.deployment_interaction_id
             AND source.side = 'Source'
            JOIN napms_application_catalogue.deployment_interaction_compatibility_sides AS destination
              ON destination.deployment_interaction_id = c.deployment_interaction_id
             AND destination.side = 'Destination'
            WHERE c.deployment_interaction_id = %s
            """,
            (deployment_interaction_id,),
        )
        if row is None:
            return None
        try:
            return DeploymentInteractionCompatibility(
                deployment_interaction_id=row[0],
                source_component_deployment_id=row[1],
                destination_component_deployment_id=row[2],
                current_dcs_revision_id=row[3],
                version=row[4],
            )
        except CatalogueInvariantError as exc:
            raise CataloguePersistenceError(
                "invalid persisted Deployment Interaction compatibility"
            ) from exc

    def add_compatibility_projection(
        self,
        value: DeploymentInteractionCompatibility,
    ) -> None:
        for side, component_deployment_id in (
            (DeploymentInteractionSide.SOURCE, value.source_component_deployment_id),
            (
                DeploymentInteractionSide.DESTINATION,
                value.destination_component_deployment_id,
            ),
        ):
            self._execute_unique_as_concurrency(
                """
                INSERT INTO napms_application_catalogue.deployment_interaction_compatibility_sides (
                    deployment_interaction_id, side, component_deployment_id
                )
                VALUES (%s, %s, %s)
                """,
                (
                    value.deployment_interaction_id,
                    side.value,
                    component_deployment_id,
                ),
            )
        self._execute_unique_as_concurrency(
            """
            INSERT INTO napms_application_catalogue.deployment_interaction_compatibility (
                deployment_interaction_id, current_dcs_revision_id, version
            )
            VALUES (%s, %s, %s)
            """,
            (
                value.deployment_interaction_id,
                value.current_dcs_revision_id,
                value.version,
            ),
        )

    def save_compatibility_projection(
        self,
        value: DeploymentInteractionCompatibility,
        *,
        expected_version: int,
    ) -> None:
        result = self._execute(
            """
            UPDATE napms_application_catalogue.deployment_interaction_compatibility
            SET current_dcs_revision_id = %s,
                version = %s
            WHERE deployment_interaction_id = %s
              AND version = %s
            """,
            (
                value.current_dcs_revision_id,
                value.version,
                value.deployment_interaction_id,
                expected_version,
            ),
        )
        self._require_updated(result)

    def find_effective_bindings(
        self,
        *,
        component_deployment_id: UUID,
        as_of,
    ) -> tuple[DeploymentResourceBinding, ...]:
        rows = self._fetchall(
            """
            SELECT reference_id, component_deployment_id, resource_reference,
                   valid_from, valid_to, provenance_reference,
                   end_provenance_reference, version
            FROM napms_application_catalogue.deployment_resource_bindings
            WHERE component_deployment_id = %s
              AND valid_from <= %s
              AND (valid_to IS NULL OR %s < valid_to)
            ORDER BY resource_reference, valid_from, reference_id
            """,
            (component_deployment_id, as_of, as_of),
        )
        return tuple(self._binding(row) for row in rows)

    # Lifecycle dependency queries.
    def list_active_components_for_application(
        self,
        *,
        application_id: UUID,
    ) -> tuple[Component, ...]:
        rows = self._fetchall(
            """
            SELECT component_id, application_id, display_name, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version,
                   component_type, description
            FROM napms_application_catalogue.components
            WHERE application_id = %s
              AND lifecycle_state = 'Active'
            ORDER BY component_id
            """,
            (application_id,),
        )
        return tuple(self._target_component(row) for row in rows)

    def list_active_interaction_definitions_for_application(
        self,
        *,
        application_id: UUID,
    ) -> tuple[InteractionDefinition, ...]:
        rows = self._fetchall(
            """
            SELECT interaction_definition_id, application_id,
                   source_component_id, destination_component_id,
                   traffic_payload, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version
            FROM napms_application_catalogue.interaction_definitions
            WHERE application_id = %s
              AND lifecycle_state = 'Active'
            ORDER BY interaction_definition_id
            """,
            (application_id,),
        )
        return tuple(self._interaction_definition(row) for row in rows)

    def list_active_application_deployments_for_application(
        self,
        *,
        application_id: UUID,
    ) -> tuple[ApplicationDeployment, ...]:
        rows = self._fetchall(
            """
            SELECT application_deployment_id, application_id,
                   company_reference, environment, scope_reference,
                   provenance_reference, lifecycle_state,
                   retirement_provenance_reference, version
            FROM napms_application_catalogue.application_deployments
            WHERE application_id = %s
              AND lifecycle_state = 'Active'
            ORDER BY application_deployment_id
            """,
            (application_id,),
        )
        return tuple(self._application_deployment(row) for row in rows)

    def list_active_interaction_definitions_for_component(
        self,
        *,
        component_id: UUID,
    ) -> tuple[InteractionDefinition, ...]:
        rows = self._fetchall(
            """
            SELECT interaction_definition_id, application_id,
                   source_component_id, destination_component_id,
                   traffic_payload, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version
            FROM napms_application_catalogue.interaction_definitions
            WHERE lifecycle_state = 'Active'
              AND (source_component_id = %s OR destination_component_id = %s)
            ORDER BY interaction_definition_id
            """,
            (component_id, component_id),
        )
        return tuple(self._interaction_definition(row) for row in rows)

    def list_active_legacy_component_deployments(
        self,
        *,
        component_id: UUID,
    ) -> tuple[ComponentDeployment, ...]:
        rows = self._fetchall(
            """
            SELECT d.component_deployment_id, d.component_id, d.provenance_reference,
                   d.display_name, d.lifecycle_state,
                   d.retirement_provenance_reference, d.version
            FROM napms_application_catalogue.component_deployments AS d
            WHERE d.component_id = %s
              AND d.lifecycle_state = 'Active'
              AND NOT EXISTS (
                  SELECT 1
                  FROM napms_application_catalogue.deployment_interaction_compatibility_sides AS s
                  WHERE s.component_deployment_id = d.component_deployment_id
              )
            ORDER BY d.component_deployment_id
            """,
            (component_id,),
        )
        return tuple(self._deployment(row) for row in rows)

    def list_active_deployment_interactions_for_deployment(
        self,
        *,
        application_deployment_id: UUID,
    ) -> tuple[DeploymentInteraction, ...]:
        rows = self._fetchall(
            """
            SELECT deployment_interaction_id, application_deployment_id,
                   interaction_definition_id, provenance_reference,
                   lifecycle_state, retirement_provenance_reference, version
            FROM napms_application_catalogue.deployment_interactions
            WHERE application_deployment_id = %s
              AND lifecycle_state = 'Active'
            ORDER BY deployment_interaction_id
            """,
            (application_deployment_id,),
        )
        return tuple(self._deployment_interaction(row) for row in rows)

    def _execute_unique_as_concurrency(self, sql: str, params: tuple):
        try:
            return self._connection.execute(sql, params)
        except UniqueViolation as exc:
            self._connection.rollback()
            self._pending_receipt = None
            raise CatalogueConcurrencyConflict() from exc
        except Exception as exc:
            # Preserve the base repository's persistence abstraction for other
            # database failures without treating them as semantic uniqueness.
            self._connection.rollback()
            self._pending_receipt = None
            raise CataloguePersistenceError() from exc

    def _interaction_definition(self, row) -> InteractionDefinition:
        try:
            return InteractionDefinition(
                interaction_definition_id=row[0],
                application_id=row[1],
                source_component_id=row[2],
                destination_component_id=row[3],
                traffic_alternatives=self._traffic_codec.decode(bytes(row[4])),
                provenance_reference=row[5],
                lifecycle_state=CatalogueLifecycleState(row[6]),
                retirement_provenance_reference=row[7],
                version=row[8],
            )
        except (ValueError, CatalogueInvariantError, DcsProjectionDecodeError) as exc:
            raise CataloguePersistenceError(
                "invalid persisted Interaction Definition"
            ) from exc

    @staticmethod
    def _application_deployment(row) -> ApplicationDeployment:
        try:
            return ApplicationDeployment(
                application_deployment_id=row[0],
                application_id=row[1],
                company_reference=row[2],
                environment=row[3],
                scope_reference=row[4],
                provenance_reference=row[5],
                lifecycle_state=CatalogueLifecycleState(row[6]),
                retirement_provenance_reference=row[7],
                version=row[8],
            )
        except (ValueError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError(
                "invalid persisted Application Deployment"
            ) from exc

    @staticmethod
    def _deployment_interaction(row) -> DeploymentInteraction:
        try:
            return DeploymentInteraction(
                deployment_interaction_id=row[0],
                application_deployment_id=row[1],
                interaction_definition_id=row[2],
                provenance_reference=row[3],
                lifecycle_state=CatalogueLifecycleState(row[4]),
                retirement_provenance_reference=row[5],
                version=row[6],
            )
        except (ValueError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError(
                "invalid persisted Deployment Interaction"
            ) from exc

    @staticmethod
    def _target_application(row) -> Application:
        try:
            return Application(
                application_id=row[0],
                display_name=row[1],
                provenance_reference=row[2],
                lifecycle_state=CatalogueLifecycleState(row[3]),
                retirement_provenance_reference=row[4],
                version=row[5],
                description=row[6],
                domain=row[7],
                owner_reference=row[8],
            )
        except (ValueError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError("invalid persisted Application") from exc

    @staticmethod
    def _target_component(row) -> Component:
        try:
            return Component(
                component_id=row[0],
                application_id=row[1],
                display_name=row[2],
                provenance_reference=row[3],
                lifecycle_state=CatalogueLifecycleState(row[4]),
                retirement_provenance_reference=row[5],
                version=row[6],
                component_type=row[7],
                description=row[8],
            )
        except (ValueError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError("invalid persisted Component") from exc
