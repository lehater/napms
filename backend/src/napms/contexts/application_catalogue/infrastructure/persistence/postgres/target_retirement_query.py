from datetime import datetime
from uuid import UUID

from psycopg import Error as PsycopgError

from napms.contexts.application_catalogue.application.ports import CataloguePersistenceError
from napms.contexts.application_catalogue.application.target_lifecycle import RetirementDependencyKind
from napms.contexts.application_catalogue.application.target_ports import (
    ActiveDependencyReference,
    ActiveDependencySummary,
)
from napms.contexts.application_catalogue.application.target_retirement import RetirementSubjectKind


class PostgresApplicationCatalogueRetirementDependencyQuery:
    """ACC-owned exact count + bounded preview/page for local retirement dependencies."""

    def __init__(self, connection) -> None:
        self._connection = connection

    def page(
        self,
        *,
        subject_kind: RetirementSubjectKind,
        subject_id: UUID,
        dependency_kind: RetirementDependencyKind,
        as_of: datetime,
        offset: int,
        limit: int,
    ) -> ActiveDependencySummary:
        _validate(as_of=as_of, offset=offset, limit=limit)
        from_where, params = _query(
            subject_kind=subject_kind,
            subject_id=subject_id,
            dependency_kind=dependency_kind,
            as_of=as_of,
        )
        try:
            total = int(
                self._connection.execute(
                    f"SELECT count(*) {from_where}",
                    params,
                ).fetchone()[0]
            )
            rows = self._connection.execute(
                f"SELECT dependency_reference {from_where} "
                "ORDER BY dependency_reference OFFSET %s LIMIT %s",
                params + (offset, limit),
            ).fetchall()
            return ActiveDependencySummary(
                total=total,
                references=tuple(
                    ActiveDependencyReference(str(row[0])) for row in rows
                ),
            )
        except PsycopgError as exc:
            raise CataloguePersistenceError(
                "target retirement dependency projection failed"
            ) from exc


def _query(
    *,
    subject_kind: RetirementSubjectKind,
    subject_id: UUID,
    dependency_kind: RetirementDependencyKind,
    as_of: datetime,
) -> tuple[str, tuple]:
    key = (subject_kind, dependency_kind)

    if key == (
        RetirementSubjectKind.APPLICATION_DEFINITION,
        RetirementDependencyKind.COMPONENTS,
    ):
        return (
            "FROM (SELECT c.component_id::text AS dependency_reference "
            "FROM napms_application_catalogue.components c "
            "WHERE c.application_id = %s AND c.lifecycle_state = 'Active') q",
            (subject_id,),
        )
    if key == (
        RetirementSubjectKind.APPLICATION_DEFINITION,
        RetirementDependencyKind.INTERACTIONS,
    ):
        return (
            "FROM (SELECT i.interaction_definition_id::text AS dependency_reference "
            "FROM napms_application_catalogue.interaction_definitions i "
            "WHERE i.application_id = %s AND i.lifecycle_state = 'Active') q",
            (subject_id,),
        )
    if key == (
        RetirementSubjectKind.APPLICATION_DEFINITION,
        RetirementDependencyKind.APPLICATION_DEPLOYMENTS,
    ):
        return (
            "FROM (SELECT d.application_deployment_id::text AS dependency_reference "
            "FROM napms_application_catalogue.application_deployments d "
            "WHERE d.application_id = %s AND d.lifecycle_state = 'Active') q",
            (subject_id,),
        )
    if key == (
        RetirementSubjectKind.COMPONENT,
        RetirementDependencyKind.INTERACTIONS,
    ):
        return (
            "FROM (SELECT i.interaction_definition_id::text AS dependency_reference "
            "FROM napms_application_catalogue.interaction_definitions i "
            "WHERE i.lifecycle_state = 'Active' "
            "AND (i.source_component_id = %s OR i.destination_component_id = %s)) q",
            (subject_id, subject_id),
        )
    if key == (
        RetirementSubjectKind.COMPONENT,
        RetirementDependencyKind.LEGACY_COMPONENT_DEPLOYMENTS,
    ):
        return (
            "FROM (SELECT d.component_deployment_id::text AS dependency_reference "
            "FROM napms_application_catalogue.component_deployments d "
            "WHERE d.component_id = %s AND d.lifecycle_state = 'Active' "
            "AND NOT EXISTS ("
            "SELECT 1 FROM napms_application_catalogue.deployment_interaction_compatibility_sides s "
            "WHERE s.component_deployment_id = d.component_deployment_id)) q",
            (subject_id,),
        )
    if key == (
        RetirementSubjectKind.INTERACTION_DEFINITION,
        RetirementDependencyKind.DEPLOYMENT_INTERACTIONS,
    ):
        return (
            "FROM (SELECT di.deployment_interaction_id::text AS dependency_reference "
            "FROM napms_application_catalogue.deployment_interactions di "
            "WHERE di.interaction_definition_id = %s "
            "AND di.lifecycle_state = 'Active') q",
            (subject_id,),
        )
    if key == (
        RetirementSubjectKind.APPLICATION_DEPLOYMENT,
        RetirementDependencyKind.DEPLOYMENT_INTERACTIONS,
    ):
        return (
            "FROM (SELECT di.deployment_interaction_id::text AS dependency_reference "
            "FROM napms_application_catalogue.deployment_interactions di "
            "WHERE di.application_deployment_id = %s "
            "AND di.lifecycle_state = 'Active') q",
            (subject_id,),
        )
    if key == (
        RetirementSubjectKind.DEPLOYMENT_INTERACTION,
        RetirementDependencyKind.RESOURCE_BINDINGS,
    ):
        return (
            "FROM (SELECT b.reference_id AS dependency_reference "
            "FROM napms_application_catalogue.deployment_interaction_compatibility_sides s "
            "JOIN napms_application_catalogue.deployment_resource_bindings b "
            "ON b.component_deployment_id = s.component_deployment_id "
            "WHERE s.deployment_interaction_id = %s "
            "AND b.valid_from <= %s "
            "AND (b.valid_to IS NULL OR %s < b.valid_to)) q",
            (subject_id, as_of, as_of),
        )
    raise ValueError("unsupported ACC retirement dependency query")


def _validate(*, as_of: datetime, offset: int, limit: int) -> None:
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("as_of must be offset-aware")
    if offset < 0 or not 1 <= limit <= 200:
        raise ValueError("dependency page must use offset >= 0 and limit within 1..200")
