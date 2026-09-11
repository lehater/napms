from datetime import datetime

from psycopg import Error as PsycopgError

from napms.connectivity_requirements.application.ports import RequirementPersistenceError
from napms.connectivity_requirements.domain.model import RequiredSemanticInteraction


class PostgresConnectivityRequirementDependencyQuery:
    """Owner-defined active/effective Requirement references for ACC dependency checks."""

    def __init__(self, connection) -> None:
        self._connection = connection

    def page(
        self,
        *,
        subjects: tuple[RequiredSemanticInteraction, ...],
        as_of: datetime,
        offset: int,
        limit: int,
    ) -> tuple[int, tuple[str, ...]]:
        _validate(as_of=as_of, offset=offset, limit=limit)
        unique = tuple(dict.fromkeys(subjects))
        if not unique:
            return 0, ()
        values, identity_params = _values(unique)
        predicate = """
            r.lifecycle_state = 'Active'
            AND (
                r.applicability_kind = 'Ongoing'
                OR (
                    r.applicability_kind = 'AbsoluteWindow'
                    AND r.applicability_start <= %s
                    AND %s < r.applicability_end
                )
            )
        """
        try:
            total = self._connection.execute(
                f"""
                WITH wanted(source_id, destination_id, dcs_id) AS (VALUES {values})
                SELECT count(DISTINCT r.requirement_id)
                  FROM napms_connectivity_requirements.connectivity_requirements r
                  JOIN wanted w
                    ON w.source_id = r.source_component_deployment_id
                   AND w.destination_id = r.destination_component_deployment_id
                   AND w.dcs_id = r.dcs_contract_revision_id
                 WHERE {predicate}
                """,
                identity_params + (as_of, as_of),
            ).fetchone()[0]
            rows = self._connection.execute(
                f"""
                WITH wanted(source_id, destination_id, dcs_id) AS (VALUES {values})
                SELECT DISTINCT r.requirement_id::text
                  FROM napms_connectivity_requirements.connectivity_requirements r
                  JOIN wanted w
                    ON w.source_id = r.source_component_deployment_id
                   AND w.destination_id = r.destination_component_deployment_id
                   AND w.dcs_id = r.dcs_contract_revision_id
                 WHERE {predicate}
                 ORDER BY r.requirement_id::text
                 OFFSET %s LIMIT %s
                """,
                identity_params + (as_of, as_of, offset, limit),
            ).fetchall()
            return int(total), tuple(row[0] for row in rows)
        except PsycopgError as exc:
            raise RequirementPersistenceError() from exc


def _values(subjects: tuple[RequiredSemanticInteraction, ...]) -> tuple[str, tuple]:
    sql = ", ".join("(%s::uuid, %s::uuid, %s::uuid)" for _ in subjects)
    params: list[object] = []
    for subject in subjects:
        params.extend(
            (
                subject.source_component_deployment_id,
                subject.destination_component_deployment_id,
                subject.dcs_contract_revision_id,
            )
        )
    return sql, tuple(params)


def _validate(*, as_of: datetime, offset: int, limit: int) -> None:
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("as_of must be offset-aware")
    if offset < 0 or not 1 <= limit <= 200:
        raise ValueError("dependency page must use offset >= 0 and limit within 1..200")
