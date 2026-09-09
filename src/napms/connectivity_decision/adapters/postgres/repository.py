from uuid import UUID

from psycopg import Connection, Error as PsycopgError
from psycopg.types.json import Jsonb

from napms.connectivity_decision.application.ports import (
    DecisionCommitOutcomeUnknown,
    DecisionCurrentConflict,
    DecisionPersistenceError,
)
from napms.connectivity_decision.domain.model import (
    ConnectivityDecision,
    DecisionEvidenceReference,
    DecisionInvariantError,
    DecisionOutcome,
    DecisionProvenance,
    DecisionSubject,
    DecisionValidity,
)


_COLUMNS = """
    decision_id,
    governance_scope,
    source_component_deployment_id,
    destination_component_deployment_id,
    dcs_contract_revision_id,
    outcome,
    valid_from,
    valid_until,
    reason_code,
    reason_text,
    evidence_references,
    deciding_actor_id,
    decided_at,
    authority_reference,
    supersedes_decision_id
"""


class PostgresConnectivityDecisionRepository:
    """Operation-scoped append-only PostgreSQL repository/UoW."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def get_by_id(self, decision_id: UUID) -> ConnectivityDecision | None:
        try:
            row = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_connectivity_decision.connectivity_decisions
                WHERE decision_id = %s
                """,
                (decision_id,),
            ).fetchone()
            return self._hydrate(row) if row is not None else None
        except DecisionPersistenceError:
            raise
        except (PsycopgError, ValueError, TypeError, DecisionInvariantError) as exc:
            raise DecisionPersistenceError() from exc

    def find_current(
        self,
        *,
        subject: DecisionSubject,
        governance_scope: str,
        as_of,
    ) -> tuple[ConnectivityDecision, ...]:
        try:
            rows = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_connectivity_decision.connectivity_decisions d
                WHERE d.governance_scope = %s
                  AND d.source_component_deployment_id = %s
                  AND d.destination_component_deployment_id = %s
                  AND d.dcs_contract_revision_id = %s
                  AND d.valid_from <= %s
                  AND (d.valid_until IS NULL OR %s < d.valid_until)
                  AND NOT EXISTS (
                      SELECT 1
                      FROM napms_connectivity_decision.connectivity_decisions successor
                      WHERE successor.supersedes_decision_id = d.decision_id
                        AND successor.valid_from <= %s
                  )
                ORDER BY d.valid_from DESC, d.decision_id
                """,
                (
                    governance_scope,
                    subject.source_component_deployment_id,
                    subject.destination_component_deployment_id,
                    subject.dcs_contract_revision_id,
                    as_of,
                    as_of,
                    as_of,
                ),
            ).fetchall()
            return tuple(self._hydrate(row) for row in rows)
        except DecisionPersistenceError:
            raise
        except (PsycopgError, ValueError, TypeError, DecisionInvariantError) as exc:
            raise DecisionPersistenceError() from exc

    def list_by_governance_scopes(
        self,
        scopes: tuple[str, ...],
        *,
        offset: int,
        limit: int,
    ) -> tuple[ConnectivityDecision, ...]:
        if not scopes:
            return ()
        try:
            rows = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_connectivity_decision.connectivity_decisions
                WHERE governance_scope = ANY(%s)
                ORDER BY decided_at DESC, decision_id
                OFFSET %s
                LIMIT %s
                """,
                (list(scopes), offset, limit),
            ).fetchall()
            return tuple(self._hydrate(row) for row in rows)
        except DecisionPersistenceError:
            raise
        except (PsycopgError, ValueError, TypeError, DecisionInvariantError) as exc:
            raise DecisionPersistenceError() from exc

    def add(self, decision: ConnectivityDecision) -> None:
        """Append one Decision after serializing the subject/scope current-head check."""
        try:
            self._lock_subject_scope(decision)
            current = self.find_current(
                subject=decision.subject,
                governance_scope=decision.governance_scope,
                as_of=decision.validity.valid_from,
            )
            if decision.supersedes_decision_id is None:
                if current:
                    raise DecisionCurrentConflict()
            elif (
                len(current) != 1
                or current[0].decision_id != decision.supersedes_decision_id
            ):
                raise DecisionCurrentConflict()

            if self._has_future_current_start_inside(decision):
                raise DecisionCurrentConflict()

            self._connection.execute(
                """
                INSERT INTO napms_connectivity_decision.connectivity_decisions (
                    decision_id,
                    governance_scope,
                    source_component_deployment_id,
                    destination_component_deployment_id,
                    dcs_contract_revision_id,
                    outcome,
                    valid_from,
                    valid_until,
                    reason_code,
                    reason_text,
                    evidence_references,
                    deciding_actor_id,
                    decided_at,
                    authority_reference,
                    supersedes_decision_id
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                """,
                (
                    decision.decision_id,
                    decision.governance_scope,
                    decision.subject.source_component_deployment_id,
                    decision.subject.destination_component_deployment_id,
                    decision.subject.dcs_contract_revision_id,
                    decision.outcome.value,
                    decision.validity.valid_from,
                    decision.validity.valid_until,
                    decision.reason_code,
                    decision.reason_text,
                    Jsonb(
                        [
                            {
                                "kind": value.kind,
                                "reference": value.reference,
                            }
                            for value in decision.evidence_references
                        ]
                    ),
                    decision.provenance.actor_id,
                    decision.provenance.decided_at,
                    decision.provenance.authority_reference,
                    decision.supersedes_decision_id,
                ),
            )
        except DecisionCurrentConflict:
            self._connection.rollback()
            raise
        except DecisionPersistenceError:
            raise
        except PsycopgError as exc:
            self._connection.rollback()
            raise DecisionPersistenceError() from exc

    def commit(self) -> None:
        try:
            self._connection.commit()
        except PsycopgError as exc:
            raise DecisionCommitOutcomeUnknown() from exc

    def _lock_subject_scope(self, decision: ConnectivityDecision) -> None:
        key = "|".join(
            (
                decision.governance_scope,
                str(decision.subject.source_component_deployment_id),
                str(decision.subject.destination_component_deployment_id),
                str(decision.subject.dcs_contract_revision_id),
            )
        )
        self._connection.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
            (key,),
        )

    def _has_future_current_start_inside(
        self,
        decision: ConnectivityDecision,
    ) -> bool:
        upper_bound_clause = ""
        params = [
            decision.governance_scope,
            decision.subject.source_component_deployment_id,
            decision.subject.destination_component_deployment_id,
            decision.subject.dcs_contract_revision_id,
            decision.validity.valid_from,
        ]
        if decision.validity.valid_until is not None:
            upper_bound_clause = "AND future.valid_from < %s"
            params.append(decision.validity.valid_until)

        row = self._connection.execute(
            f"""
            SELECT future.decision_id
            FROM napms_connectivity_decision.connectivity_decisions future
            WHERE future.governance_scope = %s
              AND future.source_component_deployment_id = %s
              AND future.destination_component_deployment_id = %s
              AND future.dcs_contract_revision_id = %s
              AND future.valid_from > %s
              {upper_bound_clause}
              AND NOT EXISTS (
                  SELECT 1
                  FROM napms_connectivity_decision.connectivity_decisions successor
                  WHERE successor.supersedes_decision_id = future.decision_id
                    AND successor.valid_from <= future.valid_from
              )
            LIMIT 1
            """,
            tuple(params),
        ).fetchone()
        return row is not None

    def _hydrate(self, row: tuple) -> ConnectivityDecision:
        evidence = row[10]
        if not isinstance(evidence, list):
            raise DecisionPersistenceError(
                "persisted Decision evidence must be a JSON array"
            )
        return ConnectivityDecision(
            decision_id=row[0],
            governance_scope=row[1],
            subject=DecisionSubject(
                source_component_deployment_id=row[2],
                destination_component_deployment_id=row[3],
                dcs_contract_revision_id=row[4],
            ),
            outcome=DecisionOutcome(row[5]),
            validity=DecisionValidity(
                valid_from=row[6],
                valid_until=row[7],
            ),
            reason_code=row[8],
            reason_text=row[9],
            evidence_references=tuple(
                DecisionEvidenceReference(
                    kind=item["kind"],
                    reference=item["reference"],
                )
                for item in evidence
            ),
            provenance=DecisionProvenance(
                actor_id=row[11],
                decided_at=row[12],
                authority_reference=row[13],
            ),
            supersedes_decision_id=row[14],
        )
