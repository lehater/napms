from uuid import UUID

from psycopg import Connection, Error as PsycopgError
from psycopg.errors import UniqueViolation

from napms.access_policy.application.inventory_summary import (
    AccessRuleInventorySnapshot,
)
from napms.access_policy.application.ports import (
    AccessRuleCommitOutcomeUnknown,
    AccessRulePersistenceError,
    RuleSemanticIdentityConflict,
)
from napms.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    DomainInvariantError,
    EffectiveWindow,
    EffectiveWindowChange,
    OperationalState,
    OperationalStateTransition,
    ProposalProvenance,
    RuleSemanticIdentity,
)


_COLUMNS = """
    rule_id,
    source_component_deployment_id,
    destination_component_deployment_id,
    dcs_contract_revision_id,
    operational_state,
    decision_result,
    decision_id,
    proposal_actor_id,
    proposal_authority_scope,
    proposal_effective_time,
    authority_reference,
    catalogue_reference
"""
_SEMANTIC_IDENTITY_CONSTRAINT = "uq_access_rules_semantic_identity"


class PostgresAccessRuleRepository:
    """Operation-scoped PostgreSQL repository/UoW adapter for Access Policy."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def find_by_identity(self, identity: RuleSemanticIdentity) -> AccessRule | None:
        try:
            row = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_access_policy.access_rules
                WHERE source_component_deployment_id = %s
                  AND destination_component_deployment_id = %s
                  AND dcs_contract_revision_id = %s
                """,
                (
                    identity.source_component_deployment_id,
                    identity.destination_component_deployment_id,
                    identity.dcs_contract_revision_id,
                ),
            ).fetchone()
            return self._hydrate(row) if row is not None else None
        except PsycopgError as exc:
            raise AccessRulePersistenceError() from exc

    def find_inventory_summaries(
        self,
        identities: tuple[RuleSemanticIdentity, ...],
    ) -> tuple[AccessRuleInventorySnapshot, ...]:
        if not identities:
            return ()
        try:
            sources = [
                value.source_component_deployment_id for value in identities
            ]
            destinations = [
                value.destination_component_deployment_id for value in identities
            ]
            revisions = [
                value.dcs_contract_revision_id for value in identities
            ]
            rows = self._connection.execute(
                """
                WITH wanted AS (
                    SELECT *
                    FROM unnest(
                        %s::uuid[],
                        %s::uuid[],
                        %s::uuid[]
                    ) AS value(source_id, destination_id, dcs_id)
                )
                SELECT
                    r.source_component_deployment_id,
                    r.destination_component_deployment_id,
                    r.dcs_contract_revision_id,
                    r.operational_state,
                    w.start_at,
                    w.end_at
                FROM napms_access_policy.access_rules AS r
                JOIN wanted AS wanted
                  ON wanted.source_id = r.source_component_deployment_id
                 AND wanted.destination_id = r.destination_component_deployment_id
                 AND wanted.dcs_id = r.dcs_contract_revision_id
                LEFT JOIN napms_access_policy.access_rule_effective_windows AS w
                  ON w.rule_id = r.rule_id
                ORDER BY
                    r.source_component_deployment_id,
                    r.destination_component_deployment_id,
                    r.dcs_contract_revision_id
                """,
                (sources, destinations, revisions),
            ).fetchall()
            snapshots = []
            for row in rows:
                window = (
                    None
                    if row[4] is None and row[5] is None
                    else EffectiveWindow(row[4], row[5])
                )
                snapshots.append(
                    AccessRuleInventorySnapshot(
                        semantic_identity=RuleSemanticIdentity(
                            source_component_deployment_id=row[0],
                            destination_component_deployment_id=row[1],
                            dcs_contract_revision_id=row[2],
                        ),
                        operational_state=OperationalState(row[3]),
                        effective_window=window,
                    )
                )
            return tuple(snapshots)
        except (PsycopgError, ValueError, DomainInvariantError) as exc:
            raise AccessRulePersistenceError() from exc

    def get_by_id(self, rule_id: UUID) -> AccessRule | None:
        try:
            row = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_access_policy.access_rules
                WHERE rule_id = %s
                """,
                (rule_id,),
            ).fetchone()
            return self._hydrate(row) if row is not None else None
        except PsycopgError as exc:
            raise AccessRulePersistenceError() from exc

    def list_by_governance_scope(self, scope: str) -> tuple[AccessRule, ...]:
        try:
            rows = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_access_policy.access_rules
                WHERE proposal_authority_scope = %s
                ORDER BY rule_id
                """,
                (scope,),
            ).fetchall()
            return tuple(self._hydrate(row) for row in rows)
        except PsycopgError as exc:
            raise AccessRulePersistenceError() from exc

    def list_by_governance_scopes(
        self,
        scopes: tuple[str, ...],
        *,
        offset: int,
        limit: int,
    ) -> tuple[AccessRule, ...]:
        if not scopes:
            return ()
        try:
            rows = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_access_policy.access_rules
                WHERE proposal_authority_scope = ANY(%s)
                ORDER BY rule_id
                OFFSET %s
                LIMIT %s
                """,
                (list(scopes), offset, limit),
            ).fetchall()
            return tuple(self._hydrate(row) for row in rows)
        except PsycopgError as exc:
            raise AccessRulePersistenceError() from exc

    def add(self, rule: AccessRule) -> None:
        if (
            rule.operational_state is not OperationalState.ACTIVE
            or rule.operational_state_history
            or rule.effective_window is not None
            or rule.effective_window_history
        ):
            raise AccessRulePersistenceError(
                "new authoritative Rule must be an unmodified Active materialization"
            )

        try:
            self._connection.execute(
                """
                INSERT INTO napms_access_policy.access_rules (
                    rule_id,
                    source_component_deployment_id,
                    destination_component_deployment_id,
                    dcs_contract_revision_id,
                    operational_state,
                    decision_result,
                    decision_id,
                    proposal_actor_id,
                    proposal_authority_scope,
                    proposal_effective_time,
                    authority_reference,
                    catalogue_reference
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    rule.rule_id,
                    rule.semantic_identity.source_component_deployment_id,
                    rule.semantic_identity.destination_component_deployment_id,
                    rule.semantic_identity.dcs_contract_revision_id,
                    rule.operational_state.value,
                    rule.decision.result.value,
                    rule.decision.decision_id,
                    rule.proposal_provenance.actor_id,
                    rule.proposal_provenance.authority_scope,
                    rule.proposal_provenance.effective_time,
                    rule.proposal_provenance.authority_reference,
                    rule.proposal_provenance.catalogue_reference,
                ),
            )
        except UniqueViolation as exc:
            self._connection.rollback()
            if exc.diag.constraint_name == _SEMANTIC_IDENTITY_CONSTRAINT:
                raise RuleSemanticIdentityConflict() from exc
            raise AccessRulePersistenceError() from exc
        except PsycopgError as exc:
            self._connection.rollback()
            raise AccessRulePersistenceError() from exc

    def save(self, rule: AccessRule) -> None:
        try:
            locked = self._connection.execute(
                """
                SELECT operational_state
                FROM napms_access_policy.access_rules
                WHERE rule_id = %s
                FOR UPDATE
                """,
                (rule.rule_id,),
            ).fetchone()
            if locked is None:
                raise AccessRulePersistenceError("Rule disappeared before save")

            persisted_state = OperationalState(locked[0])
            persisted_window = self._load_current_window(rule.rule_id)
            state_count = self._history_count(
                "access_rule_state_transitions", rule.rule_id
            )
            window_count = self._history_count(
                "access_rule_effective_window_changes", rule.rule_id
            )
            state_delta = len(rule.operational_state_history) - state_count
            window_delta = len(rule.effective_window_history) - window_count

            if (state_delta, window_delta) == (1, 0):
                self._save_state_change(rule, persisted_state)
            elif (state_delta, window_delta) == (0, 1):
                self._save_window_change(rule, persisted_window)
            else:
                raise AccessRulePersistenceError(
                    "save must contain exactly one new aggregate mutation"
                )
        except AccessRulePersistenceError:
            self._connection.rollback()
            raise
        except (PsycopgError, ValueError, DomainInvariantError) as exc:
            self._connection.rollback()
            raise AccessRulePersistenceError() from exc

    def commit(self) -> None:
        try:
            self._connection.commit()
        except PsycopgError as exc:
            # A client-side commit failure can be ambiguous: the server may have
            # committed even when acknowledgement was lost. Never report success.
            raise AccessRuleCommitOutcomeUnknown() from exc

    def _save_state_change(
        self, rule: AccessRule, persisted_state: OperationalState
    ) -> None:
        transition = rule.operational_state_history[-1]
        if (
            transition.rule_id != rule.rule_id
            or transition.from_state is not persisted_state
            or transition.to_state is not rule.operational_state
            or transition.governance_scope != rule.governance_scope
        ):
            raise AccessRulePersistenceError("stale or inconsistent state transition")

        updated = self._connection.execute(
            """
            UPDATE napms_access_policy.access_rules
            SET operational_state = %s
            WHERE rule_id = %s
            """,
            (transition.to_state.value, rule.rule_id),
        )
        if updated.rowcount != 1:
            raise AccessRulePersistenceError("state update did not affect one Rule")

        self._connection.execute(
            """
            INSERT INTO napms_access_policy.access_rule_state_transitions (
                rule_id,
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
                transition.rule_id,
                len(rule.operational_state_history),
                transition.from_state.value,
                transition.to_state.value,
                transition.actor_id,
                transition.effective_time,
                transition.governance_scope,
                transition.authority_reference,
            ),
        )

    def _save_window_change(
        self, rule: AccessRule, persisted_window: EffectiveWindow | None
    ) -> None:
        change = rule.effective_window_history[-1]
        if (
            change.rule_id != rule.rule_id
            or change.previous_window != persisted_window
            or change.new_window != rule.effective_window
            or change.governance_scope != rule.governance_scope
        ):
            raise AccessRulePersistenceError("stale or inconsistent EffectiveWindow change")

        if change.new_window is None:
            deleted = self._connection.execute(
                """
                DELETE FROM napms_access_policy.access_rule_effective_windows
                WHERE rule_id = %s
                """,
                (rule.rule_id,),
            )
            if persisted_window is not None and deleted.rowcount != 1:
                raise AccessRulePersistenceError("EffectiveWindow delete lost current row")
        elif persisted_window is None:
            self._connection.execute(
                """
                INSERT INTO napms_access_policy.access_rule_effective_windows (
                    rule_id,
                    start_at,
                    end_at
                )
                VALUES (%s, %s, %s)
                """,
                (
                    rule.rule_id,
                    change.new_window.start,
                    change.new_window.end,
                ),
            )
        else:
            updated = self._connection.execute(
                """
                UPDATE napms_access_policy.access_rule_effective_windows
                SET start_at = %s, end_at = %s
                WHERE rule_id = %s
                """,
                (
                    change.new_window.start,
                    change.new_window.end,
                    rule.rule_id,
                ),
            )
            if updated.rowcount != 1:
                raise AccessRulePersistenceError("EffectiveWindow update lost current row")

        previous_start, previous_end = _window_columns(change.previous_window)
        new_start, new_end = _window_columns(change.new_window)
        self._connection.execute(
            """
            INSERT INTO napms_access_policy.access_rule_effective_window_changes (
                rule_id,
                sequence_no,
                previous_start,
                previous_end,
                new_start,
                new_end,
                actor_id,
                effective_time,
                governance_scope,
                authority_reference
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                change.rule_id,
                len(rule.effective_window_history),
                previous_start,
                previous_end,
                new_start,
                new_end,
                change.actor_id,
                change.effective_time,
                change.governance_scope,
                change.authority_reference,
            ),
        )

    def _history_count(self, table: str, rule_id: UUID) -> int:
        if table not in {
            "access_rule_state_transitions",
            "access_rule_effective_window_changes",
        }:
            raise AccessRulePersistenceError("unsupported history table")
        row = self._connection.execute(
            f"""
            SELECT count(*)
            FROM napms_access_policy.{table}
            WHERE rule_id = %s
            """,
            (rule_id,),
        ).fetchone()
        return row[0]

    def _load_current_window(self, rule_id: UUID) -> EffectiveWindow | None:
        row = self._connection.execute(
            """
            SELECT start_at, end_at
            FROM napms_access_policy.access_rule_effective_windows
            WHERE rule_id = %s
            """,
            (rule_id,),
        ).fetchone()
        if row is None:
            return None
        return EffectiveWindow(row[0], row[1])

    def _hydrate(self, row: tuple) -> AccessRule:
        try:
            state_history = self._load_state_history(row[0], row[8])
            effective_window = self._load_current_window(row[0])
            window_history = self._load_window_history(row[0], row[8])

            operational_state = OperationalState(row[4])
            expected_state = OperationalState.ACTIVE
            for transition in state_history:
                if transition.from_state is not expected_state:
                    raise AccessRulePersistenceError("broken operational-state audit chain")
                expected_state = transition.to_state
            if expected_state is not operational_state:
                raise AccessRulePersistenceError(
                    "current operational state does not match audit history"
                )

            expected_window = None
            for change in window_history:
                if change.previous_window != expected_window:
                    raise AccessRulePersistenceError("broken EffectiveWindow audit chain")
                expected_window = change.new_window
            if expected_window != effective_window:
                raise AccessRulePersistenceError(
                    "current EffectiveWindow does not match audit history"
                )

            identity = RuleSemanticIdentity(
                source_component_deployment_id=row[1],
                destination_component_deployment_id=row[2],
                dcs_contract_revision_id=row[3],
            )
            return AccessRule(
                rule_id=row[0],
                semantic_identity=identity,
                operational_state=operational_state,
                decision=DecisionReference(
                    subject=identity,
                    result=ConnectivityDecisionResult(row[5]),
                    decision_id=row[6],
                ),
                proposal_provenance=ProposalProvenance(
                    actor_id=row[7],
                    authority_scope=row[8],
                    effective_time=row[9],
                    authority_reference=row[10],
                    catalogue_reference=row[11],
                ),
                operational_state_history=state_history,
                effective_window=effective_window,
                effective_window_history=window_history,
            )
        except AccessRulePersistenceError:
            raise
        except (ValueError, DomainInvariantError) as exc:
            raise AccessRulePersistenceError("invalid persisted AccessRule") from exc

    def _load_state_history(
        self, rule_id: UUID, governance_scope: str
    ) -> tuple[OperationalStateTransition, ...]:
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
            FROM napms_access_policy.access_rule_state_transitions
            WHERE rule_id = %s
            ORDER BY sequence_no
            """,
            (rule_id,),
        ).fetchall()

        history = []
        for expected_sequence, history_row in enumerate(rows, start=1):
            if history_row[0] != expected_sequence or history_row[5] != governance_scope:
                raise AccessRulePersistenceError("invalid operational-state audit")
            history.append(
                OperationalStateTransition(
                    rule_id=rule_id,
                    from_state=OperationalState(history_row[1]),
                    to_state=OperationalState(history_row[2]),
                    actor_id=history_row[3],
                    effective_time=history_row[4],
                    governance_scope=history_row[5],
                    authority_reference=history_row[6],
                )
            )
        return tuple(history)

    def _load_window_history(
        self, rule_id: UUID, governance_scope: str
    ) -> tuple[EffectiveWindowChange, ...]:
        rows = self._connection.execute(
            """
            SELECT
                sequence_no,
                previous_start,
                previous_end,
                new_start,
                new_end,
                actor_id,
                effective_time,
                governance_scope,
                authority_reference
            FROM napms_access_policy.access_rule_effective_window_changes
            WHERE rule_id = %s
            ORDER BY sequence_no
            """,
            (rule_id,),
        ).fetchall()

        history = []
        for expected_sequence, history_row in enumerate(rows, start=1):
            if history_row[0] != expected_sequence or history_row[7] != governance_scope:
                raise AccessRulePersistenceError("invalid EffectiveWindow audit")
            history.append(
                EffectiveWindowChange(
                    rule_id=rule_id,
                    previous_window=_window_from_columns(
                        history_row[1], history_row[2]
                    ),
                    new_window=_window_from_columns(history_row[3], history_row[4]),
                    actor_id=history_row[5],
                    effective_time=history_row[6],
                    governance_scope=history_row[7],
                    authority_reference=history_row[8],
                )
            )
        return tuple(history)


def _window_columns(
    window: EffectiveWindow | None,
) -> tuple[object | None, object | None]:
    if window is None:
        return None, None
    return window.start, window.end


def _window_from_columns(start, end) -> EffectiveWindow | None:
    if start is None and end is None:
        return None
    if start is None or end is None:
        raise AccessRulePersistenceError("partial EffectiveWindow persistence")
    return EffectiveWindow(start, end)
