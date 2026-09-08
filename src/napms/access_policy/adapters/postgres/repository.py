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
        except PsycopgError as exc:
            raise AccessRulePersistenceError() from exc
        return _to_access_rule(row) if row is not None else None

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
        except PsycopgError as exc:
            raise AccessRulePersistenceError() from exc
        return _to_access_rule(row) if row is not None else None

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

    def commit(self) -> None:
        try:
            self._connection.commit()
        except PsycopgError as exc:
            # A client-side commit failure can be ambiguous: the server may have
            # committed even when acknowledgement was lost. Never report success.
            raise AccessRuleCommitOutcomeUnknown() from exc


def _to_access_rule(row: tuple) -> AccessRule:
    identity = RuleSemanticIdentity(
        source_component_deployment_id=row[1],
        destination_component_deployment_id=row[2],
        dcs_contract_revision_id=row[3],
    )
    return AccessRule(
        rule_id=row[0],
        semantic_identity=identity,
        operational_state=OperationalState(row[4]),
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
    )
