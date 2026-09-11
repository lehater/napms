from datetime import datetime

from psycopg import Connection, Error as PsycopgError

from napms.contexts.authority_management.application.ports import AuthorityPersistenceError
from napms.contexts.authority_management.domain.model import (
    AuthorityAssignment,
    AuthorityInvariantError,
)


class PostgresAuthorityAssignmentRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def find_effective(
        self,
        *,
        actor_id: str,
        action: str,
        scope: str,
        effective_time: datetime,
    ) -> tuple[AuthorityAssignment, ...]:
        try:
            rows = self._connection.execute(
                """
                SELECT
                    reference_id,
                    actor_id,
                    action,
                    scope,
                    valid_from,
                    valid_to,
                    provenance_reference
                FROM napms_authority.authority_assignments
                WHERE actor_id = %s
                  AND action = %s
                  AND scope = %s
                  AND valid_from <= %s
                  AND (valid_to IS NULL OR %s < valid_to)
                ORDER BY reference_id
                """,
                (
                    actor_id,
                    action,
                    scope,
                    effective_time,
                    effective_time,
                ),
            ).fetchall()
            return tuple(self._hydrate(row) for row in rows)
        except AuthorityPersistenceError:
            raise
        except (PsycopgError, AuthorityInvariantError) as exc:
            raise AuthorityPersistenceError() from exc

    def find_effective_for_actor_action(
        self,
        *,
        actor_id: str,
        action: str,
        effective_time: datetime,
    ) -> tuple[AuthorityAssignment, ...]:
        try:
            rows = self._connection.execute(
                """
                SELECT
                    reference_id,
                    actor_id,
                    action,
                    scope,
                    valid_from,
                    valid_to,
                    provenance_reference
                FROM napms_authority.authority_assignments
                WHERE actor_id = %s
                  AND action = %s
                  AND valid_from <= %s
                  AND (valid_to IS NULL OR %s < valid_to)
                ORDER BY scope, reference_id
                """,
                (
                    actor_id,
                    action,
                    effective_time,
                    effective_time,
                ),
            ).fetchall()
            return tuple(self._hydrate(row) for row in rows)
        except AuthorityPersistenceError:
            raise
        except (PsycopgError, AuthorityInvariantError) as exc:
            raise AuthorityPersistenceError() from exc

    def _hydrate(self, row: tuple) -> AuthorityAssignment:
        try:
            return AuthorityAssignment(
                reference_id=row[0],
                actor_id=row[1],
                action=row[2],
                scope=row[3],
                valid_from=row[4],
                valid_to=row[5],
                provenance_reference=row[6],
            )
        except AuthorityInvariantError as exc:
            raise AuthorityPersistenceError("invalid persisted authority assignment") from exc
