from datetime import datetime
from uuid import UUID

from psycopg import Error as PsycopgError

from napms.contexts.application_catalogue.infrastructure.integrations.dcs_authoring import (
    JsonDcsAuthoringProjectionEncoder,
)
from napms.contexts.application_catalogue.application.ports import CataloguePersistenceError
from napms.contexts.application_catalogue.application.target_read import (
    ApplicationDefinitionSummary,
    ApplicationDeploymentPage,
    ApplicationDeploymentSummary,
    ComponentPage,
    DefinitionSummaryPage,
    DeploymentConnectivityPage,
    DeploymentConnectivityRow,
    InteractionDefinitionPage,
    InteractionDefinitionSummary,
    ResourceSetMember,
    ResourceSetPage,
    TargetPage,
    normalize_bounded_query,
    require_as_of,
)
from napms.contexts.application_catalogue.domain.model import (
    Application,
    CatalogueInvariantError,
    CatalogueLifecycleState,
    Component,
)
from napms.contexts.application_catalogue.domain.target_model import (
    ApplicationDeployment,
    DeploymentInteractionSide,
    InteractionDefinition,
)
from napms.policy_export.application.normalization_ports import DcsProjectionDecodeError


class PostgresApplicationCatalogueTargetReadModel:
    """Query-only I31 projection over ACC truth plus RC display/scope facts.

    This composition projection owns no business state and performs no writes. The
    cross-schema Resource-set join is deliberately outside both bounded-context
    persistence adapters; lifecycle and mutation decisions remain owner-specific.
    """

    def __init__(self, connection) -> None:
        self._connection = connection
        self._traffic = JsonDcsAuthoringProjectionEncoder()

    def list_definitions(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None,
        domain: str | None,
        owner_reference: str | None,
        sort: str,
    ) -> DefinitionSummaryPage:
        offset, limit, search, sort = normalize_bounded_query(
            offset=offset, limit=limit, search=search, sort=sort
        )
        domain = _optional(domain)
        owner_reference = _optional(owner_reference)
        pattern = _pattern(search)
        where = """
            a.lifecycle_state = 'Active'
            AND (%s::text IS NULL OR a.domain = %s)
            AND (%s::text IS NULL OR a.owner_reference = %s)
            AND (
                %s::text IS NULL
                OR a.display_name ILIKE %s
                OR a.application_id::text ILIKE %s
                OR a.domain ILIKE %s
                OR a.owner_reference ILIKE %s
            )
        """
        params = (
            domain,
            domain,
            owner_reference,
            owner_reference,
            search,
            pattern,
            pattern,
            pattern,
            pattern,
        )
        order = _order(
            sort,
            {
                "name": ("a.display_name",),
                "domain": ("COALESCE(a.domain, '')", "a.display_name"),
                "owner": ("COALESCE(a.owner_reference, '')", "a.display_name"),
            },
            default=("a.display_name",),
            tie="a.application_id",
        )
        try:
            total = self._scalar(
                f"SELECT count(*) FROM napms_application_catalogue.applications a WHERE {where}",
                params,
            )
            rows = self._fetchall(
                f"""
                SELECT a.application_id, a.display_name, a.provenance_reference,
                       a.lifecycle_state, a.retirement_provenance_reference, a.version,
                       a.description, a.domain, a.owner_reference,
                       (SELECT count(*)
                          FROM napms_application_catalogue.components c
                         WHERE c.application_id = a.application_id
                           AND c.lifecycle_state = 'Active') AS component_count,
                       (SELECT count(*)
                          FROM napms_application_catalogue.interaction_definitions i
                         WHERE i.application_id = a.application_id
                           AND i.lifecycle_state = 'Active') AS interaction_count,
                       (SELECT count(*)
                          FROM napms_application_catalogue.application_deployments d
                         WHERE d.application_id = a.application_id
                           AND d.lifecycle_state = 'Active') AS deployment_count
                  FROM napms_application_catalogue.applications a
                 WHERE {where}
                 ORDER BY {order}
                 OFFSET %s LIMIT %s
                """,
                params + (offset, limit),
            )
            return DefinitionSummaryPage(
                items=tuple(
                    ApplicationDefinitionSummary(
                        application=_application(row[:9]),
                        component_count=row[9],
                        interaction_count=row[10],
                        deployment_count=row[11],
                    )
                    for row in rows
                ),
                page=TargetPage(offset, limit, total),
            )
        except (PsycopgError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError("target definition projection failed") from exc

    def get_definition(self, *, application_id: UUID) -> Application | None:
        try:
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
            return _application(row) if row is not None else None
        except (PsycopgError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError("target definition read failed") from exc

    def list_components(
        self,
        *,
        application_id: UUID,
        offset: int,
        limit: int,
        search: str | None,
        component_type: str | None,
        sort: str,
    ) -> ComponentPage:
        offset, limit, search, sort = normalize_bounded_query(
            offset=offset, limit=limit, search=search, sort=sort
        )
        component_type = _optional(component_type)
        pattern = _pattern(search)
        where = """
            c.application_id = %s
            AND c.lifecycle_state = 'Active'
            AND (%s::text IS NULL OR c.component_type = %s)
            AND (
                %s::text IS NULL
                OR c.display_name ILIKE %s
                OR c.component_id::text ILIKE %s
                OR c.component_type ILIKE %s
                OR c.description ILIKE %s
            )
        """
        params = (
            application_id,
            component_type,
            component_type,
            search,
            pattern,
            pattern,
            pattern,
            pattern,
        )
        order = _order(
            sort,
            {
                "name": ("c.display_name",),
                "type": ("COALESCE(c.component_type, '')", "c.display_name"),
            },
            default=("c.display_name",),
            tie="c.component_id",
        )
        try:
            total = self._scalar(
                f"SELECT count(*) FROM napms_application_catalogue.components c WHERE {where}",
                params,
            )
            rows = self._fetchall(
                f"""
                SELECT c.component_id, c.application_id, c.display_name,
                       c.provenance_reference, c.lifecycle_state,
                       c.retirement_provenance_reference, c.version,
                       c.component_type, c.description
                  FROM napms_application_catalogue.components c
                 WHERE {where}
                 ORDER BY {order}
                 OFFSET %s LIMIT %s
                """,
                params + (offset, limit),
            )
            return ComponentPage(
                items=tuple(_component(row) for row in rows),
                page=TargetPage(offset, limit, total),
            )
        except (PsycopgError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError("target component projection failed") from exc

    def list_interaction_definitions(
        self,
        *,
        application_id: UUID,
        offset: int,
        limit: int,
        search: str | None,
        source_component_id: UUID | None,
        destination_component_id: UUID | None,
        protocol: str | None,
        sort: str,
    ) -> InteractionDefinitionPage:
        return self._list_interactions(
            application_id=application_id,
            application_deployment_id=None,
            only_unselected=False,
            offset=offset,
            limit=limit,
            search=search,
            source_component_id=source_component_id,
            destination_component_id=destination_component_id,
            protocol=protocol,
            sort=sort,
        )

    def list_available_interactions_for_deployment(
        self,
        *,
        application_deployment_id: UUID,
        offset: int,
        limit: int,
        search: str | None,
        source_component_id: UUID | None,
        destination_component_id: UUID | None,
        protocol: str | None,
        sort: str,
    ) -> InteractionDefinitionPage:
        deployment = self.get_application_deployment(
            application_deployment_id=application_deployment_id
        )
        if deployment is None or deployment.lifecycle_state is not CatalogueLifecycleState.ACTIVE:
            return InteractionDefinitionPage(items=(), page=TargetPage(offset, limit, 0))
        return self._list_interactions(
            application_id=deployment.application_id,
            application_deployment_id=application_deployment_id,
            only_unselected=True,
            offset=offset,
            limit=limit,
            search=search,
            source_component_id=source_component_id,
            destination_component_id=destination_component_id,
            protocol=protocol,
            sort=sort,
        )

    def _list_interactions(
        self,
        *,
        application_id: UUID,
        application_deployment_id: UUID | None,
        only_unselected: bool,
        offset: int,
        limit: int,
        search: str | None,
        source_component_id: UUID | None,
        destination_component_id: UUID | None,
        protocol: str | None,
        sort: str,
    ) -> InteractionDefinitionPage:
        offset, limit, search, sort = normalize_bounded_query(
            offset=offset, limit=limit, search=search, sort=sort
        )
        protocol = _optional(protocol)
        pattern = _pattern(search)
        unselected_clause = ""
        unselected_params: tuple[object, ...] = ()
        if only_unselected:
            unselected_clause = """
                AND NOT EXISTS (
                    SELECT 1
                      FROM napms_application_catalogue.deployment_interactions selected
                     WHERE selected.application_deployment_id = %s
                       AND selected.interaction_definition_id = i.interaction_definition_id
                       AND selected.lifecycle_state = 'Active'
                )
            """
            unselected_params = (application_deployment_id,)
        where = f"""
            i.application_id = %s
            AND i.lifecycle_state = 'Active'
            AND source.lifecycle_state = 'Active'
            AND destination.lifecycle_state = 'Active'
            AND (%s::uuid IS NULL OR i.source_component_id = %s)
            AND (%s::uuid IS NULL OR i.destination_component_id = %s)
            AND (
                %s::text IS NULL OR EXISTS (
                    SELECT 1
                      FROM jsonb_array_elements(
                          (convert_from(i.traffic_payload, 'UTF8')::jsonb)->'alternatives'
                      ) AS alternative
                     WHERE lower(alternative->>'protocol') = lower(%s)
                )
            )
            AND (
                %s::text IS NULL
                OR source.display_name ILIKE %s
                OR destination.display_name ILIKE %s
                OR i.interaction_definition_id::text ILIKE %s
            )
            {unselected_clause}
        """
        params = (
            application_id,
            source_component_id,
            source_component_id,
            destination_component_id,
            destination_component_id,
            protocol,
            protocol,
            search,
            pattern,
            pattern,
            pattern,
        ) + unselected_params
        joins = """
            FROM napms_application_catalogue.interaction_definitions i
            JOIN napms_application_catalogue.components source
              ON source.component_id = i.source_component_id
            JOIN napms_application_catalogue.components destination
              ON destination.component_id = i.destination_component_id
        """
        order = _order(
            sort,
            {
                "source": ("source.display_name", "destination.display_name"),
                "destination": ("destination.display_name", "source.display_name"),
                "traffic": ("convert_from(i.traffic_payload, 'UTF8')",),
            },
            default=("source.display_name", "destination.display_name"),
            tie="i.interaction_definition_id",
        )
        try:
            total = self._scalar(f"SELECT count(*) {joins} WHERE {where}", params)
            rows = self._fetchall(
                f"""
                SELECT i.interaction_definition_id, i.application_id,
                       i.source_component_id, i.destination_component_id,
                       i.traffic_payload, i.provenance_reference, i.lifecycle_state,
                       i.retirement_provenance_reference, i.version,
                       source.display_name, destination.display_name,
                       (SELECT count(*)
                          FROM napms_application_catalogue.deployment_interactions di
                         WHERE di.interaction_definition_id = i.interaction_definition_id
                           AND di.lifecycle_state = 'Active') AS active_deployment_count
                  {joins}
                 WHERE {where}
                 ORDER BY {order}
                 OFFSET %s LIMIT %s
                """,
                params + (offset, limit),
            )
            return InteractionDefinitionPage(
                items=tuple(
                    InteractionDefinitionSummary(
                        interaction=self._interaction(row[:9]),
                        source_component_name=row[9],
                        destination_component_name=row[10],
                        active_deployment_count=row[11],
                    )
                    for row in rows
                ),
                page=TargetPage(offset, limit, total),
            )
        except (PsycopgError, CatalogueInvariantError, DcsProjectionDecodeError) as exc:
            raise CataloguePersistenceError("target interaction projection failed") from exc

    def list_application_deployments(
        self,
        *,
        application_id: UUID | None,
        offset: int,
        limit: int,
        search: str | None,
        company_reference: str | None,
        environment: str | None,
        scope_reference: str | None,
        sort: str,
    ) -> ApplicationDeploymentPage:
        offset, limit, search, sort = normalize_bounded_query(
            offset=offset, limit=limit, search=search, sort=sort
        )
        company_reference = _optional(company_reference)
        environment = _optional(environment)
        scope_reference = _optional(scope_reference)
        pattern = _pattern(search)
        where = """
            d.lifecycle_state = 'Active'
            AND a.lifecycle_state = 'Active'
            AND (%s::uuid IS NULL OR d.application_id = %s)
            AND (%s::text IS NULL OR d.company_reference = %s)
            AND (%s::text IS NULL OR d.environment = %s)
            AND (%s::text IS NULL OR d.scope_reference = %s)
            AND (
                %s::text IS NULL
                OR a.display_name ILIKE %s
                OR d.company_reference ILIKE %s
                OR d.environment ILIKE %s
                OR d.scope_reference ILIKE %s
                OR d.application_deployment_id::text ILIKE %s
            )
        """
        params = (
            application_id,
            application_id,
            company_reference,
            company_reference,
            environment,
            environment,
            scope_reference,
            scope_reference,
            search,
            pattern,
            pattern,
            pattern,
            pattern,
            pattern,
        )
        joins = """
            FROM napms_application_catalogue.application_deployments d
            JOIN napms_application_catalogue.applications a
              ON a.application_id = d.application_id
        """
        order = _order(
            sort,
            {
                "application": ("a.display_name",),
                "company": ("d.company_reference", "a.display_name"),
                "environment": ("d.environment", "a.display_name"),
                "scope": ("d.scope_reference", "a.display_name"),
            },
            default=(
                "a.display_name",
                "d.company_reference",
                "d.environment",
                "d.scope_reference",
            ),
            tie="d.application_deployment_id",
        )
        try:
            total = self._scalar(f"SELECT count(*) {joins} WHERE {where}", params)
            rows = self._fetchall(
                f"""
                SELECT d.application_deployment_id, d.application_id,
                       d.company_reference, d.environment, d.scope_reference,
                       d.provenance_reference, d.lifecycle_state,
                       d.retirement_provenance_reference, d.version,
                       a.display_name,
                       (SELECT count(*)
                          FROM napms_application_catalogue.deployment_interactions di
                         WHERE di.application_deployment_id = d.application_deployment_id
                           AND di.lifecycle_state = 'Active') AS selected_count,
                       (SELECT count(*)
                          FROM napms_application_catalogue.interaction_definitions i
                         WHERE i.application_id = d.application_id
                           AND i.lifecycle_state = 'Active') AS defined_count
                  {joins}
                 WHERE {where}
                 ORDER BY {order}
                 OFFSET %s LIMIT %s
                """,
                params + (offset, limit),
            )
            return ApplicationDeploymentPage(
                items=tuple(
                    ApplicationDeploymentSummary(
                        deployment=_application_deployment(row[:9]),
                        application_name=row[9],
                        selected_interaction_count=row[10],
                        available_interaction_count=row[11],
                    )
                    for row in rows
                ),
                page=TargetPage(offset, limit, total),
            )
        except (PsycopgError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError("target deployment projection failed") from exc

    def get_application_deployment(
        self,
        *,
        application_deployment_id: UUID,
    ) -> ApplicationDeployment | None:
        try:
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
            return _application_deployment(row) if row is not None else None
        except (PsycopgError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError("target deployment read failed") from exc

    def list_deployment_connectivity(
        self,
        *,
        application_deployment_id: UUID,
        as_of: datetime,
        offset: int,
        limit: int,
        search: str | None,
        source_component_id: UUID | None,
        destination_component_id: UUID | None,
        protocol: str | None,
        sort: str,
    ) -> DeploymentConnectivityPage:
        as_of = require_as_of(as_of)
        offset, limit, search, sort = normalize_bounded_query(
            offset=offset, limit=limit, search=search, sort=sort
        )
        protocol = _optional(protocol)
        pattern = _pattern(search)
        where = """
            di.application_deployment_id = %s
            AND di.lifecycle_state = 'Active'
            AND i.lifecycle_state = 'Active'
            AND source.lifecycle_state = 'Active'
            AND destination.lifecycle_state = 'Active'
            AND (%s::uuid IS NULL OR i.source_component_id = %s)
            AND (%s::uuid IS NULL OR i.destination_component_id = %s)
            AND (
                %s::text IS NULL OR EXISTS (
                    SELECT 1
                      FROM jsonb_array_elements(
                          (convert_from(i.traffic_payload, 'UTF8')::jsonb)->'alternatives'
                      ) AS alternative
                     WHERE lower(alternative->>'protocol') = lower(%s)
                )
            )
            AND (
                %s::text IS NULL
                OR source.display_name ILIKE %s
                OR destination.display_name ILIKE %s
                OR di.deployment_interaction_id::text ILIKE %s
            )
        """
        params = (
            application_deployment_id,
            source_component_id,
            source_component_id,
            destination_component_id,
            destination_component_id,
            protocol,
            protocol,
            search,
            pattern,
            pattern,
            pattern,
        )
        joins = """
            FROM napms_application_catalogue.deployment_interactions di
            JOIN napms_application_catalogue.interaction_definitions i
              ON i.interaction_definition_id = di.interaction_definition_id
            JOIN napms_application_catalogue.components source
              ON source.component_id = i.source_component_id
            JOIN napms_application_catalogue.components destination
              ON destination.component_id = i.destination_component_id
            JOIN napms_application_catalogue.deployment_interaction_compatibility_sides source_side
              ON source_side.deployment_interaction_id = di.deployment_interaction_id
             AND source_side.side = 'Source'
            JOIN napms_application_catalogue.deployment_interaction_compatibility_sides destination_side
              ON destination_side.deployment_interaction_id = di.deployment_interaction_id
             AND destination_side.side = 'Destination'
        """
        order = _order(
            sort,
            {
                "source": ("source.display_name", "destination.display_name"),
                "destination": ("destination.display_name", "source.display_name"),
                "traffic": ("convert_from(i.traffic_payload, 'UTF8')",),
            },
            default=("source.display_name", "destination.display_name"),
            tie="di.deployment_interaction_id",
        )
        try:
            total = self._scalar(f"SELECT count(*) {joins} WHERE {where}", params)
            rows = self._fetchall(
                f"""
                SELECT di.deployment_interaction_id, i.interaction_definition_id,
                       i.source_component_id, source.display_name,
                       (SELECT count(*)
                          FROM napms_application_catalogue.deployment_resource_bindings b
                         WHERE b.component_deployment_id = source_side.component_deployment_id
                           AND b.valid_from <= %s
                           AND (b.valid_to IS NULL OR %s < b.valid_to)) AS source_resource_count,
                       i.destination_component_id, destination.display_name,
                       (SELECT count(*)
                          FROM napms_application_catalogue.deployment_resource_bindings b
                         WHERE b.component_deployment_id = destination_side.component_deployment_id
                           AND b.valid_from <= %s
                           AND (b.valid_to IS NULL OR %s < b.valid_to)) AS destination_resource_count,
                       i.traffic_payload
                  {joins}
                 WHERE {where}
                 ORDER BY {order}
                 OFFSET %s LIMIT %s
                """,
                (as_of, as_of, as_of, as_of) + params + (offset, limit),
            )
            return DeploymentConnectivityPage(
                items=tuple(
                    DeploymentConnectivityRow(
                        deployment_interaction_id=row[0],
                        interaction_definition_id=row[1],
                        source_component_id=row[2],
                        source_component_name=row[3],
                        source_resource_count=row[4],
                        destination_component_id=row[5],
                        destination_component_name=row[6],
                        destination_resource_count=row[7],
                        traffic_alternatives=self._traffic.decode(bytes(row[8])),
                    )
                    for row in rows
                ),
                page=TargetPage(offset, limit, total),
                as_of=as_of,
            )
        except (PsycopgError, CatalogueInvariantError, DcsProjectionDecodeError) as exc:
            raise CataloguePersistenceError("target connectivity projection failed") from exc

    def list_resource_set(
        self,
        *,
        deployment_interaction_id: UUID,
        side: DeploymentInteractionSide,
        as_of: datetime,
        offset: int,
        limit: int,
        search: str | None,
        scope_reference: str | None,
        sort: str,
    ) -> ResourceSetPage:
        as_of = require_as_of(as_of)
        offset, limit, search, sort = normalize_bounded_query(
            offset=offset, limit=limit, search=search, sort=sort
        )
        scope_reference = _optional(scope_reference)
        pattern = _pattern(search)
        where = """
            s.deployment_interaction_id = %s
            AND s.side = %s
            AND b.valid_from <= %s
            AND (b.valid_to IS NULL OR %s < b.valid_to)
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
            deployment_interaction_id,
            side.value,
            as_of,
            as_of,
            search,
            pattern,
            pattern,
            scope_reference,
            scope_reference,
            as_of,
            as_of,
        )
        joins = """
            FROM napms_application_catalogue.deployment_interaction_compatibility_sides s
            JOIN napms_application_catalogue.deployment_resource_bindings b
              ON b.component_deployment_id = s.component_deployment_id
            JOIN napms_resource_catalogue.resources r
              ON r.resource_reference = b.resource_reference
        """
        scope_sort = """
            COALESCE((
                SELECT min(rsa.responsibility_scope)
                  FROM napms_resource_catalogue.resource_scope_affiliations rsa
                 WHERE rsa.resource_reference = r.resource_reference
                   AND rsa.valid_from <= %s
                   AND (rsa.valid_to IS NULL OR %s < rsa.valid_to)
            ), '')
        """
        if sort.lstrip("-") == "scope":
            order = _order(
                sort,
                {"scope": (scope_sort,)},
                default=("COALESCE(r.display_name, r.resource_reference)",),
                tie="r.resource_reference",
            )
            order_params: tuple[object, ...] = (as_of, as_of)
        else:
            order = _order(
                sort,
                {"resource": ("COALESCE(r.display_name, r.resource_reference)",)},
                default=("COALESCE(r.display_name, r.resource_reference)",),
                tie="r.resource_reference",
            )
            order_params = ()
        try:
            total = self._scalar(
                f"SELECT count(DISTINCT r.resource_reference) {joins} WHERE {where}",
                params,
            )
            rows = self._fetchall(
                f"""
                SELECT b.reference_id, b.version, r.resource_reference,
                       b.valid_from, b.valid_to, r.display_name,
                       ARRAY(
                           SELECT DISTINCT rsa.responsibility_scope
                             FROM napms_resource_catalogue.resource_scope_affiliations rsa
                            WHERE rsa.resource_reference = r.resource_reference
                              AND rsa.valid_from <= %s
                              AND (rsa.valid_to IS NULL OR %s < rsa.valid_to)
                            ORDER BY rsa.responsibility_scope
                       ) AS scope_references
                  {joins}
                 WHERE {where}
                 GROUP BY b.reference_id, b.version, r.resource_reference,
                          b.valid_from, b.valid_to, r.display_name
                 ORDER BY {order}
                 OFFSET %s LIMIT %s
                """,
                (as_of, as_of) + params + order_params + (offset, limit),
            )
            return ResourceSetPage(
                items=tuple(
                    ResourceSetMember(
                        binding_reference=row[0],
                        binding_version=row[1],
                        resource_reference=row[2],
                        valid_from=row[3],
                        valid_to=row[4],
                        display_name=row[5],
                        scope_references=tuple(row[6]),
                    )
                    for row in rows
                ),
                page=TargetPage(offset, limit, total),
                as_of=as_of,
            )
        except (PsycopgError, CatalogueInvariantError) as exc:
            raise CataloguePersistenceError("target resource-set projection failed") from exc

    def _interaction(self, row) -> InteractionDefinition:
        return InteractionDefinition(
            interaction_definition_id=row[0],
            application_id=row[1],
            source_component_id=row[2],
            destination_component_id=row[3],
            traffic_alternatives=self._traffic.decode(bytes(row[4])),
            provenance_reference=row[5],
            lifecycle_state=CatalogueLifecycleState(row[6]),
            retirement_provenance_reference=row[7],
            version=row[8],
        )

    def _scalar(self, sql: str, params: tuple) -> int:
        return int(self._connection.execute(sql, params).fetchone()[0])

    def _fetchone(self, sql: str, params: tuple):
        return self._connection.execute(sql, params).fetchone()

    def _fetchall(self, sql: str, params: tuple):
        return self._connection.execute(sql, params).fetchall()


def _optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _pattern(value: str | None) -> str | None:
    return f"%{value}%" if value else None


def _order(
    sort: str,
    columns: dict[str, tuple[str, ...]],
    *,
    default: tuple[str, ...],
    tie: str,
) -> str:
    descending = sort.startswith("-")
    key = sort[1:] if descending else sort
    expressions = columns.get(key, default)
    direction = "DESC" if descending else "ASC"
    ordered = tuple(f"{expression} {direction}" for expression in expressions)
    return ", ".join(ordered + (f"{tie} {direction}",))


def _application(row) -> Application:
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


def _component(row) -> Component:
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


def _application_deployment(row) -> ApplicationDeployment:
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
