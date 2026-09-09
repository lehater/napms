from uuid import UUID

from psycopg import Connection, Error as PsycopgError
from psycopg.errors import UniqueViolation

from napms.connectivity_requirements.application.ports import (
    ActiveRequirementSemanticConflict,
    RequirementCommitOutcomeUnknown,
    RequirementPersistenceError,
    RequirementVersionConflict,
)
from napms.connectivity_requirements.domain.model import (
    ConnectivityRequirement,
    RequiredSemanticInteraction,
    RequirementApplicability,
    RequirementApplicabilityChange,
    RequirementApplicabilityKind,
    RequirementDeclarationProvenance,
    RequirementInvariantError,
    RequirementJustificationChange,
    RequirementLifecycleState,
    RequirementLifecycleTransition,
    RequirementSemanticKey,
)


_COLUMNS = """
    requirement_id,
    governance_scope,
    dependent_component_deployment_id,
    source_component_deployment_id,
    destination_component_deployment_id,
    dcs_contract_revision_id,
    applicability_kind,
    applicability_start,
    applicability_end,
    justification,
    lifecycle_state,
    declaration_actor_id,
    declaration_effective_time,
    declaration_authority_reference,
    declaration_catalogue_reference,
    version
"""
_ACTIVE_UNIQUE = "uq_connectivity_requirements_active_semantic"


class PostgresConnectivityRequirementRepository:
    """Operation-scoped PostgreSQL repository/UoW for Connectivity Requirements."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def find_active_by_semantic_key(
        self,
        key: RequirementSemanticKey,
    ) -> ConnectivityRequirement | None:
        try:
            row = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_connectivity_requirements.connectivity_requirements
                WHERE lifecycle_state = 'Active'
                  AND governance_scope = %s
                  AND dependent_component_deployment_id = %s
                  AND source_component_deployment_id = %s
                  AND destination_component_deployment_id = %s
                  AND dcs_contract_revision_id = %s
                """,
                (
                    key.governance_scope,
                    key.dependent_component_deployment_id,
                    key.required_interaction.source_component_deployment_id,
                    key.required_interaction.destination_component_deployment_id,
                    key.required_interaction.dcs_contract_revision_id,
                ),
            ).fetchone()
            return self._hydrate(row) if row is not None else None
        except RequirementPersistenceError:
            raise
        except (PsycopgError, ValueError, RequirementInvariantError) as exc:
            raise RequirementPersistenceError() from exc

    def get_by_id(
        self,
        requirement_id: UUID,
    ) -> ConnectivityRequirement | None:
        try:
            row = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_connectivity_requirements.connectivity_requirements
                WHERE requirement_id = %s
                """,
                (requirement_id,),
            ).fetchone()
            return self._hydrate(row) if row is not None else None
        except RequirementPersistenceError:
            raise
        except (PsycopgError, ValueError, RequirementInvariantError) as exc:
            raise RequirementPersistenceError() from exc

    def list_by_governance_scopes(
        self,
        scopes: tuple[str, ...],
        *,
        offset: int,
        limit: int,
    ) -> tuple[ConnectivityRequirement, ...]:
        if not scopes:
            return ()
        try:
            rows = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_connectivity_requirements.connectivity_requirements
                WHERE governance_scope = ANY(%s)
                ORDER BY requirement_id
                OFFSET %s
                LIMIT %s
                """,
                (list(scopes), offset, limit),
            ).fetchall()
            return tuple(self._hydrate(row) for row in rows)
        except RequirementPersistenceError:
            raise
        except (PsycopgError, ValueError, RequirementInvariantError) as exc:
            raise RequirementPersistenceError() from exc

    def list_by_scope_and_interactions(
        self,
        *,
        governance_scope: str,
        interactions: tuple[RequiredSemanticInteraction, ...],
    ) -> tuple[ConnectivityRequirement, ...]:
        if not interactions:
            return ()
        try:
            sources = [
                value.source_component_deployment_id for value in interactions
            ]
            destinations = [
                value.destination_component_deployment_id for value in interactions
            ]
            revisions = [
                value.dcs_contract_revision_id for value in interactions
            ]
            rows = self._connection.execute(
                f"""
                WITH wanted AS (
                    SELECT *
                    FROM unnest(
                        %s::uuid[],
                        %s::uuid[],
                        %s::uuid[]
                    ) AS value(source_id, destination_id, dcs_id)
                )
                SELECT {_COLUMNS}
                FROM napms_connectivity_requirements.connectivity_requirements AS r
                JOIN wanted AS w
                  ON w.source_id = r.source_component_deployment_id
                 AND w.destination_id = r.destination_component_deployment_id
                 AND w.dcs_id = r.dcs_contract_revision_id
                WHERE r.governance_scope = %s
                ORDER BY r.requirement_id
                """,
                (sources, destinations, revisions, governance_scope),
            ).fetchall()
            return tuple(self._hydrate(row) for row in rows)
        except RequirementPersistenceError:
            raise
        except (PsycopgError, ValueError, RequirementInvariantError) as exc:
            raise RequirementPersistenceError() from exc

    def add(self, requirement: ConnectivityRequirement) -> None:
        if (
            requirement.version != 1
            or requirement.lifecycle_state is not RequirementLifecycleState.ACTIVE
            or requirement.applicability_history
            or requirement.justification_history
            or requirement.lifecycle_history
        ):
            raise RequirementPersistenceError(
                "new Requirement must be a pristine Active declaration"
            )
        app_kind, app_start, app_end = _applicability_columns(
            requirement.applicability
        )
        try:
            self._connection.execute(
                """
                INSERT INTO napms_connectivity_requirements.connectivity_requirements (
                    requirement_id,
                    governance_scope,
                    dependent_component_deployment_id,
                    source_component_deployment_id,
                    destination_component_deployment_id,
                    dcs_contract_revision_id,
                    applicability_kind,
                    applicability_start,
                    applicability_end,
                    justification,
                    lifecycle_state,
                    declaration_actor_id,
                    declaration_effective_time,
                    declaration_authority_reference,
                    declaration_catalogue_reference,
                    version
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                """,
                (
                    requirement.requirement_id,
                    requirement.governance_scope,
                    requirement.dependent_component_deployment_id,
                    requirement.required_interaction.source_component_deployment_id,
                    requirement.required_interaction.destination_component_deployment_id,
                    requirement.required_interaction.dcs_contract_revision_id,
                    app_kind,
                    app_start,
                    app_end,
                    requirement.justification,
                    requirement.lifecycle_state.value,
                    requirement.declaration_provenance.actor_id,
                    requirement.declaration_provenance.effective_time,
                    requirement.declaration_provenance.authority_reference,
                    requirement.declaration_provenance.catalogue_reference,
                    requirement.version,
                ),
            )
        except UniqueViolation as exc:
            self._connection.rollback()
            if exc.diag.constraint_name == _ACTIVE_UNIQUE:
                raise ActiveRequirementSemanticConflict() from exc
            raise RequirementPersistenceError() from exc
        except PsycopgError as exc:
            self._connection.rollback()
            raise RequirementPersistenceError() from exc

    def save(
        self,
        requirement: ConnectivityRequirement,
        *,
        expected_version: int,
    ) -> None:
        try:
            row = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_connectivity_requirements.connectivity_requirements
                WHERE requirement_id = %s
                FOR UPDATE
                """,
                (requirement.requirement_id,),
            ).fetchone()
            if row is None:
                raise RequirementPersistenceError(
                    "Requirement disappeared before save"
                )
            persisted = self._hydrate(row)
            if persisted.version != expected_version:
                raise RequirementVersionConflict()
            if requirement.version != expected_version + 1:
                raise RequirementPersistenceError(
                    "accepted mutation must increment version exactly once"
                )
            if (
                requirement.semantic_key != persisted.semantic_key
                or requirement.requirement_id != persisted.requirement_id
                or requirement.declaration_provenance
                != persisted.declaration_provenance
            ):
                raise RequirementPersistenceError(
                    "immutable Requirement identity/provenance changed"
                )

            deltas = (
                len(requirement.applicability_history)
                - len(persisted.applicability_history),
                len(requirement.justification_history)
                - len(persisted.justification_history),
                len(requirement.lifecycle_history)
                - len(persisted.lifecycle_history),
            )
            if deltas == (1, 0, 0):
                self._save_applicability(requirement, persisted)
            elif deltas == (0, 1, 0):
                self._save_justification(requirement, persisted)
            elif deltas == (0, 0, 1):
                self._save_lifecycle(requirement, persisted)
            else:
                raise RequirementPersistenceError(
                    "save must contain exactly one new aggregate mutation"
                )
        except RequirementVersionConflict:
            self._connection.rollback()
            raise
        except RequirementPersistenceError:
            self._connection.rollback()
            raise
        except (PsycopgError, ValueError, RequirementInvariantError) as exc:
            self._connection.rollback()
            raise RequirementPersistenceError() from exc

    def commit(self) -> None:
        try:
            self._connection.commit()
        except PsycopgError as exc:
            raise RequirementCommitOutcomeUnknown() from exc

    def _save_applicability(
        self,
        requirement: ConnectivityRequirement,
        persisted: ConnectivityRequirement,
    ) -> None:
        if (
            requirement.applicability_history[:-1]
            != persisted.applicability_history
            or requirement.justification_history != persisted.justification_history
            or requirement.lifecycle_history != persisted.lifecycle_history
        ):
            raise RequirementPersistenceError(
                "applicability mutation does not extend persisted history"
            )
        change = requirement.applicability_history[-1]
        if (
            change.previous_applicability != persisted.applicability
            or change.new_applicability != requirement.applicability
            or change.governance_scope != persisted.governance_scope
        ):
            raise RequirementPersistenceError(
                "stale or inconsistent applicability change"
            )
        kind, start, end = _applicability_columns(change.new_applicability)
        updated = self._connection.execute(
            """
            UPDATE napms_connectivity_requirements.connectivity_requirements
            SET applicability_kind = %s,
                applicability_start = %s,
                applicability_end = %s,
                version = %s
            WHERE requirement_id = %s
              AND version = %s
            """,
            (
                kind,
                start,
                end,
                requirement.version,
                requirement.requirement_id,
                persisted.version,
            ),
        )
        if updated.rowcount != 1:
            raise RequirementVersionConflict()

        prev_kind, prev_start, prev_end = _applicability_columns(
            change.previous_applicability
        )
        new_kind, new_start, new_end = _applicability_columns(
            change.new_applicability
        )
        self._connection.execute(
            """
            INSERT INTO napms_connectivity_requirements.applicability_changes (
                requirement_id,
                sequence_no,
                previous_kind,
                previous_start,
                previous_end,
                new_kind,
                new_start,
                new_end,
                actor_id,
                effective_time,
                governance_scope,
                authority_reference
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                requirement.requirement_id,
                len(requirement.applicability_history),
                prev_kind,
                prev_start,
                prev_end,
                new_kind,
                new_start,
                new_end,
                change.actor_id,
                change.effective_time,
                change.governance_scope,
                change.authority_reference,
            ),
        )

    def _save_justification(
        self,
        requirement: ConnectivityRequirement,
        persisted: ConnectivityRequirement,
    ) -> None:
        if (
            requirement.justification_history[:-1]
            != persisted.justification_history
            or requirement.applicability_history != persisted.applicability_history
            or requirement.lifecycle_history != persisted.lifecycle_history
        ):
            raise RequirementPersistenceError(
                "justification mutation does not extend persisted history"
            )
        change = requirement.justification_history[-1]
        if (
            change.previous_justification != persisted.justification
            or change.new_justification != requirement.justification
            or change.governance_scope != persisted.governance_scope
        ):
            raise RequirementPersistenceError(
                "stale or inconsistent justification change"
            )
        updated = self._connection.execute(
            """
            UPDATE napms_connectivity_requirements.connectivity_requirements
            SET justification = %s,
                version = %s
            WHERE requirement_id = %s
              AND version = %s
            """,
            (
                requirement.justification,
                requirement.version,
                requirement.requirement_id,
                persisted.version,
            ),
        )
        if updated.rowcount != 1:
            raise RequirementVersionConflict()
        self._connection.execute(
            """
            INSERT INTO napms_connectivity_requirements.justification_changes (
                requirement_id,
                sequence_no,
                previous_justification,
                new_justification,
                actor_id,
                effective_time,
                governance_scope,
                authority_reference
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                requirement.requirement_id,
                len(requirement.justification_history),
                change.previous_justification,
                change.new_justification,
                change.actor_id,
                change.effective_time,
                change.governance_scope,
                change.authority_reference,
            ),
        )

    def _save_lifecycle(
        self,
        requirement: ConnectivityRequirement,
        persisted: ConnectivityRequirement,
    ) -> None:
        if (
            requirement.lifecycle_history[:-1] != persisted.lifecycle_history
            or requirement.applicability_history != persisted.applicability_history
            or requirement.justification_history != persisted.justification_history
        ):
            raise RequirementPersistenceError(
                "lifecycle mutation does not extend persisted history"
            )
        transition = requirement.lifecycle_history[-1]
        if (
            transition.from_state is not persisted.lifecycle_state
            or transition.to_state is not requirement.lifecycle_state
            or transition.governance_scope != persisted.governance_scope
        ):
            raise RequirementPersistenceError(
                "stale or inconsistent lifecycle transition"
            )
        updated = self._connection.execute(
            """
            UPDATE napms_connectivity_requirements.connectivity_requirements
            SET lifecycle_state = %s,
                version = %s
            WHERE requirement_id = %s
              AND version = %s
            """,
            (
                requirement.lifecycle_state.value,
                requirement.version,
                requirement.requirement_id,
                persisted.version,
            ),
        )
        if updated.rowcount != 1:
            raise RequirementVersionConflict()
        self._connection.execute(
            """
            INSERT INTO napms_connectivity_requirements.lifecycle_transitions (
                requirement_id,
                sequence_no,
                from_state,
                to_state,
                actor_id,
                effective_time,
                governance_scope,
                authority_reference
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                requirement.requirement_id,
                len(requirement.lifecycle_history),
                transition.from_state.value,
                transition.to_state.value,
                transition.actor_id,
                transition.effective_time,
                transition.governance_scope,
                transition.authority_reference,
            ),
        )

    def _hydrate(self, row: tuple) -> ConnectivityRequirement:
        interaction = RequiredSemanticInteraction(
            source_component_deployment_id=row[3],
            destination_component_deployment_id=row[4],
            dcs_contract_revision_id=row[5],
        )
        applicability = _applicability_from_columns(row[6], row[7], row[8])
        applicability_history = self._load_applicability_history(row[0], row[1])
        justification_history = self._load_justification_history(row[0], row[1])
        lifecycle_history = self._load_lifecycle_history(row[0], row[1])

        expected_applicability = (
            applicability_history[0].previous_applicability
            if applicability_history
            else applicability
        )
        for change in applicability_history:
            if change.previous_applicability != expected_applicability:
                raise RequirementPersistenceError(
                    "broken Requirement applicability audit chain"
                )
            expected_applicability = change.new_applicability
        if expected_applicability != applicability:
            raise RequirementPersistenceError(
                "current Requirement applicability does not match audit history"
            )

        expected_justification = (
            justification_history[0].previous_justification
            if justification_history
            else row[9]
        )
        for change in justification_history:
            if change.previous_justification != expected_justification:
                raise RequirementPersistenceError(
                    "broken Requirement justification audit chain"
                )
            expected_justification = change.new_justification
        if expected_justification != row[9]:
            raise RequirementPersistenceError(
                "current Requirement justification does not match audit history"
            )

        expected_state = RequirementLifecycleState.ACTIVE
        for transition in lifecycle_history:
            if transition.from_state is not expected_state:
                raise RequirementPersistenceError(
                    "broken Requirement lifecycle audit chain"
                )
            expected_state = transition.to_state
        lifecycle_state = RequirementLifecycleState(row[10])
        if expected_state is not lifecycle_state:
            raise RequirementPersistenceError(
                "current Requirement lifecycle does not match audit history"
            )

        expected_version = (
            1
            + len(applicability_history)
            + len(justification_history)
            + len(lifecycle_history)
        )
        if row[15] != expected_version:
            raise RequirementPersistenceError(
                "Requirement version does not match accepted mutation history"
            )

        return ConnectivityRequirement(
            requirement_id=row[0],
            governance_scope=row[1],
            dependent_component_deployment_id=row[2],
            required_interaction=interaction,
            applicability=applicability,
            justification=row[9],
            lifecycle_state=lifecycle_state,
            declaration_provenance=RequirementDeclarationProvenance(
                actor_id=row[11],
                effective_time=row[12],
                governance_scope=row[1],
                authority_reference=row[13],
                catalogue_reference=row[14],
            ),
            applicability_history=applicability_history,
            justification_history=justification_history,
            lifecycle_history=lifecycle_history,
            version=row[15],
        )

    def _load_applicability_history(
        self,
        requirement_id: UUID,
        governance_scope: str,
    ) -> tuple[RequirementApplicabilityChange, ...]:
        rows = self._connection.execute(
            """
            SELECT
                sequence_no,
                previous_kind,
                previous_start,
                previous_end,
                new_kind,
                new_start,
                new_end,
                actor_id,
                effective_time,
                governance_scope,
                authority_reference
            FROM napms_connectivity_requirements.applicability_changes
            WHERE requirement_id = %s
            ORDER BY sequence_no
            """,
            (requirement_id,),
        ).fetchall()
        result = []
        for expected, row in enumerate(rows, start=1):
            if row[0] != expected or row[9] != governance_scope:
                raise RequirementPersistenceError(
                    "invalid Requirement applicability audit"
                )
            result.append(
                RequirementApplicabilityChange(
                    requirement_id=requirement_id,
                    previous_applicability=_applicability_from_columns(
                        row[1], row[2], row[3]
                    ),
                    new_applicability=_applicability_from_columns(
                        row[4], row[5], row[6]
                    ),
                    actor_id=row[7],
                    effective_time=row[8],
                    governance_scope=row[9],
                    authority_reference=row[10],
                )
            )
        return tuple(result)

    def _load_justification_history(
        self,
        requirement_id: UUID,
        governance_scope: str,
    ) -> tuple[RequirementJustificationChange, ...]:
        rows = self._connection.execute(
            """
            SELECT
                sequence_no,
                previous_justification,
                new_justification,
                actor_id,
                effective_time,
                governance_scope,
                authority_reference
            FROM napms_connectivity_requirements.justification_changes
            WHERE requirement_id = %s
            ORDER BY sequence_no
            """,
            (requirement_id,),
        ).fetchall()
        result = []
        for expected, row in enumerate(rows, start=1):
            if row[0] != expected or row[5] != governance_scope:
                raise RequirementPersistenceError(
                    "invalid Requirement justification audit"
                )
            result.append(
                RequirementJustificationChange(
                    requirement_id=requirement_id,
                    previous_justification=row[1],
                    new_justification=row[2],
                    actor_id=row[3],
                    effective_time=row[4],
                    governance_scope=row[5],
                    authority_reference=row[6],
                )
            )
        return tuple(result)

    def _load_lifecycle_history(
        self,
        requirement_id: UUID,
        governance_scope: str,
    ) -> tuple[RequirementLifecycleTransition, ...]:
        rows = self._connection.execute(
            """
            SELECT
                sequence_no,
                from_state,
                to_state,
                actor_id,
                effective_time,
                governance_scope,
                authority_reference
            FROM napms_connectivity_requirements.lifecycle_transitions
            WHERE requirement_id = %s
            ORDER BY sequence_no
            """,
            (requirement_id,),
        ).fetchall()
        result = []
        for expected, row in enumerate(rows, start=1):
            if row[0] != expected or row[5] != governance_scope:
                raise RequirementPersistenceError(
                    "invalid Requirement lifecycle audit"
                )
            result.append(
                RequirementLifecycleTransition(
                    requirement_id=requirement_id,
                    from_state=RequirementLifecycleState(row[1]),
                    to_state=RequirementLifecycleState(row[2]),
                    actor_id=row[3],
                    effective_time=row[4],
                    governance_scope=row[5],
                    authority_reference=row[6],
                )
            )
        return tuple(result)


def _applicability_columns(
    value: RequirementApplicability,
) -> tuple[str, object | None, object | None]:
    return value.kind.value, value.start, value.end


def _applicability_from_columns(
    kind,
    start,
    end,
) -> RequirementApplicability:
    parsed = RequirementApplicabilityKind(kind)
    if parsed is RequirementApplicabilityKind.ONGOING:
        if start is not None or end is not None:
            raise RequirementPersistenceError(
                "persisted Ongoing applicability contains a window"
            )
        return RequirementApplicability.ongoing()
    if start is None or end is None:
        raise RequirementPersistenceError(
            "persisted AbsoluteWindow applicability is partial"
        )
    return RequirementApplicability.absolute_window(start=start, end=end)
