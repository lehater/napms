from datetime import datetime

from psycopg import Error as PsycopgError

from napms.connectivity_decision.application.ports import DecisionPersistenceError
from napms.connectivity_decision.domain.model import DecisionSubject


class PostgresConnectivityDecisionDependencyQuery:
    """Owner-defined current/effective Decision references for ACC dependency checks."""

    def __init__(self, connection) -> None:
        self._connection = connection

    def page(
        self,
        *,
        subjects: tuple[DecisionSubject, ...],
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
            d.valid_from <= %s
            AND (d.valid_until IS NULL OR %s < d.valid_until)
            AND NOT EXISTS (
                SELECT 1
                  FROM napms_connectivity_decision.connectivity_decisions successor
                 WHERE successor.supersedes_decision_id = d.decision_id
                   AND successor.valid_from <= %s
            )
        """
        try:
            total = self._connection.execute(
                f"""
                WITH wanted(source_id, destination_id, dcs_id) AS (VALUES {values})
                SELECT count(DISTINCT d.decision_id)
                  FROM napms_connectivity_decision.connectivity_decisions d
                  JOIN wanted w
                    ON w.source_id = d.source_component_deployment_id
                   AND w.destination_id = d.destination_component_deployment_id
                   AND w.dcs_id = d.dcs_contract_revision_id
                 WHERE {predicate}
                """,
                identity_params + (as_of, as_of, as_of),
            ).fetchone()[0]
            rows = self._connection.execute(
                f"""
                WITH wanted(source_id, destination_id, dcs_id) AS (VALUES {values})
                SELECT DISTINCT d.decision_id::text
                  FROM napms_connectivity_decision.connectivity_decisions d
                  JOIN wanted w
                    ON w.source_id = d.source_component_deployment_id
                   AND w.destination_id = d.destination_component_deployment_id
                   AND w.dcs_id = d.dcs_contract_revision_id
                 WHERE {predicate}
                 ORDER BY d.decision_id::text
                 OFFSET %s LIMIT %s
                """,
                identity_params + (as_of, as_of, as_of, offset, limit),
            ).fetchall()
            return int(total), tuple(row[0] for row in rows)
        except PsycopgError as exc:
            raise DecisionPersistenceError() from exc


def _values(subjects: tuple[DecisionSubject, ...]) -> tuple[str, tuple]:
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
