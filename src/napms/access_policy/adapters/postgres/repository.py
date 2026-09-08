from uuid import UUID

from psycopg import Connection, Error as PsycopgError
from psycopg.errors import UniqueViolation

from napms.access_policy.application.ports import (
    AccessRuleCommitOutcomeUnknown,
    AccessRulePersistenceError,
    RuleSemanticIdentityConflict,
)
from napms.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
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

    def add(self, rule: AccessRule) -> None:
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
        if not rule.operational_state_history:
            raise AccessRulePersistenceError()

        transition = rule.operational_state_history[-1]
        if (
            transition.rule_id != rule.rule_id
            or transition.to_state is not rule.operational_state
            or transition.governance_scope != rule.governance_scope
        ):
            raise AccessRulePersistenceError()

        try:
            updated = self._connection.execute(
                """
                UPDATE napms_access_policy.access_rules
                SET operational_state = %s
                WHERE rule_id = %s
                  AND operational_state = %s
                """,
                (
                    transition.to_state.value,
                    rule.rule_id,
                    transition.from_state.value,
                ),
            )
            if updated.rowcount != 1:
                self._connection.rollback()
                raise AccessRulePersistenceError()

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
        except AccessRulePersistenceError:
            raise
        except PsycopgError as exc:
            self._connection.rollback()
            raise AccessRulePersistenceError() from exc

    def commit(self) -> None:
        try:
            self._connection.commit()
        except PsycopgError as exc:
            # A client-side commit failure can be ambiguous: the server may have
            # committed even when acknowledgement was lost. Never report success.
            raise AccessRuleCommitOutcomeUnknown() from exc

    def _hydrate(self, row: tuple) -> AccessRule:
        history_rows = self._connection.execute(
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
            (row[0],),
        ).fetchall()

        history = []
        for expected_sequence, history_row in enumerate(history_rows, start=1):
            if history_row[0] != expected_sequence:
                raise AccessRulePersistenceError()
            history.append(
                OperationalStateTransition(
                    rule_id=row[0],
                    from_state=OperationalState(history_row[1]),
                    to_state=OperationalState(history_row[2]),
                    actor_id=history_row[3],
                    effective_time=history_row[4],
                    governance_scope=history_row[5],
                    authority_reference=history_row[6],
                )
            )

        operational_state = OperationalState(row[4])
        if history:
            if history[-1].to_state is not operational_state:
                raise AccessRulePersistenceError()
            if any(item.governance_scope != row[8] for item in history):
                raise AccessRulePersistenceError()

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
            operational_state_history=tuple(history),
        )
