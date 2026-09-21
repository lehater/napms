from __future__ import annotations

from typing import Any
from uuid import UUID

import psycopg

from napms.contexts.access_policy.application.ports import AccessPolicyVersionConflict
from napms.contexts.access_policy.domain.model import (
    AccessRequest,
    AccessSubject,
    AuthorizationEvidence,
    EffectiveWindow,
    JustificationAssociation,
    OperationalHistory,
    PermissionDecision,
    PolicyRule,
    RequestAuthorityEvidence,
    RuleEffectState,
)


class PostgresAccessPolicyRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def add_request(self, request: AccessRequest) -> None:
        with psycopg.connect(self._dsn) as connection:
            self.add_request_in(connection, request)

    def get_request(self, request_ref: UUID) -> AccessRequest | None:
        with psycopg.connect(self._dsn) as connection:
            return self.get_request_in(connection, request_ref)

    def save_request(self, request: AccessRequest, *, expected_version: int) -> None:
        with psycopg.connect(self._dsn) as connection:
            self.save_request_in(connection, request, expected_version=expected_version)

    def add_rule(self, rule: PolicyRule) -> None:
        with psycopg.connect(self._dsn) as connection:
            self.add_rule_in(connection, rule)

    def get_rule(self, rule_ref: UUID) -> PolicyRule | None:
        with psycopg.connect(self._dsn) as connection:
            return self.get_rule_in(connection, rule_ref)

    def find_rule_by_subject(self, subject: AccessSubject) -> PolicyRule | None:
        with psycopg.connect(self._dsn) as connection:
            return self.find_rule_by_subject_in(connection, subject)

    @classmethod
    def find_rule_by_subject_in(
        cls,
        connection: psycopg.Connection[Any],
        subject: AccessSubject,
    ) -> PolicyRule | None:
        row = connection.execute(
            """
            SELECT rule_ref
            FROM access_policy.policy_rule
            WHERE source_deployment_ref = %s
              AND destination_deployment_ref = %s
              AND interaction_revision_ref = %s
            """,
            (
                subject.source_deployment_ref,
                subject.destination_deployment_ref,
                subject.interaction_revision_ref,
            ),
        ).fetchone()
        return None if row is None else cls.get_rule_in(connection, row[0])

    def save_rule(self, rule: PolicyRule, *, expected_version: int) -> None:
        with psycopg.connect(self._dsn) as connection:
            self.save_rule_in(connection, rule, expected_version=expected_version)

    @staticmethod
    def add_request_in(connection: psycopg.Connection[Any], request: AccessRequest) -> None:
        subject = request.access_subject
        connection.execute(
            """
            INSERT INTO access_policy.access_request
                (request_ref, source_deployment_ref, destination_deployment_ref,
                 interaction_revision_ref, initial_need_ref,
                 validated_business_process_version, submitter_subject,
                 submitted_at, decision_result, external_decision_ref,
                 decided_by_subject, decided_at, version)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                request.request_ref,
                subject.source_deployment_ref,
                subject.destination_deployment_ref,
                subject.interaction_revision_ref,
                request.initial_need_ref,
                request.validated_business_process_version,
                request.submitter_subject,
                request.submitted_at,
                None if request.decision_result is None else request.decision_result.value,
                request.external_decision_ref,
                request.decided_by_subject,
                request.decided_at,
                request.version,
            ),
        )
        for evidence in request.authority_evidence:
            connection.execute(
                """
                INSERT INTO access_policy.access_request_authority_evidence
                    (evidence_ref, request_ref, scope_ref, action,
                     grant_effective_from, grant_effective_until, evaluated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    evidence.evidence_ref,
                    request.request_ref,
                    evidence.scope_ref,
                    evidence.action,
                    evidence.grant_effective_from,
                    evidence.grant_effective_until,
                    evidence.evaluated_at,
                ),
            )

    @staticmethod
    def get_request_in(
        connection: psycopg.Connection[Any],
        request_ref: UUID,
    ) -> AccessRequest | None:
        row = connection.execute(
            """
            SELECT request_ref, source_deployment_ref, destination_deployment_ref,
                   interaction_revision_ref, initial_need_ref,
                   validated_business_process_version, submitter_subject,
                   submitted_at, decision_result, external_decision_ref,
                   decided_by_subject, decided_at, version
            FROM access_policy.access_request
            WHERE request_ref = %s
            """,
            (request_ref,),
        ).fetchone()
        if row is None:
            return None
        evidence_rows = connection.execute(
            """
            SELECT evidence_ref, scope_ref, action, grant_effective_from,
                   grant_effective_until, evaluated_at
            FROM access_policy.access_request_authority_evidence
            WHERE request_ref = %s
            ORDER BY scope_ref, action, evidence_ref
            """,
            (request_ref,),
        ).fetchall()
        return AccessRequest(
            request_ref=row[0],
            access_subject=AccessSubject(
                source_deployment_ref=row[1],
                destination_deployment_ref=row[2],
                interaction_revision_ref=row[3],
            ),
            initial_need_ref=row[4],
            validated_business_process_version=row[5],
            submitter_subject=row[6],
            submitted_at=row[7],
            decision_result=None if row[8] is None else PermissionDecision(row[8]),
            external_decision_ref=row[9],
            decided_by_subject=row[10],
            decided_at=row[11],
            version=row[12],
            authority_evidence=tuple(
                RequestAuthorityEvidence(
                    evidence_ref=evidence_ref,
                    scope_ref=scope_ref,
                    action=action,
                    grant_effective_from=grant_effective_from,
                    grant_effective_until=grant_effective_until,
                    evaluated_at=evaluated_at,
                )
                for (
                    evidence_ref,
                    scope_ref,
                    action,
                    grant_effective_from,
                    grant_effective_until,
                    evaluated_at,
                ) in evidence_rows
            ),
        )

    @staticmethod
    def save_request_in(
        connection: psycopg.Connection[Any],
        request: AccessRequest,
        *,
        expected_version: int,
    ) -> None:
        updated = connection.execute(
            """
            UPDATE access_policy.access_request
            SET decision_result = %s,
                external_decision_ref = %s,
                decided_by_subject = %s,
                decided_at = %s,
                version = %s
            WHERE request_ref = %s AND version = %s
            """,
            (
                None if request.decision_result is None else request.decision_result.value,
                request.external_decision_ref,
                request.decided_by_subject,
                request.decided_at,
                request.version,
                request.request_ref,
                expected_version,
            ),
        )
        if updated.rowcount != 1:
            raise AccessPolicyVersionConflict(str(request.request_ref))

    @classmethod
    def add_rule_in(cls, connection: psycopg.Connection[Any], rule: PolicyRule) -> None:
        subject = rule.access_subject
        created_at = rule.operational_history[0].changed_at
        connection.execute(
            """
            INSERT INTO access_policy.policy_rule
                (rule_ref, source_deployment_ref, destination_deployment_ref,
                 interaction_revision_ref, effect_state, effective_from,
                 effective_until, version, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                rule.rule_ref,
                subject.source_deployment_ref,
                subject.destination_deployment_ref,
                subject.interaction_revision_ref,
                rule.effect_state.value,
                rule.effective_window.effective_from,
                rule.effective_window.effective_until,
                rule.version,
                created_at,
            ),
        )
        cls._persist_rule_children(connection, rule)

    @classmethod
    def save_rule_in(
        cls,
        connection: psycopg.Connection[Any],
        rule: PolicyRule,
        *,
        expected_version: int,
    ) -> None:
        updated = connection.execute(
            """
            UPDATE access_policy.policy_rule
            SET effect_state = %s,
                effective_from = %s,
                effective_until = %s,
                version = %s
            WHERE rule_ref = %s AND version = %s
            """,
            (
                rule.effect_state.value,
                rule.effective_window.effective_from,
                rule.effective_window.effective_until,
                rule.version,
                rule.rule_ref,
                expected_version,
            ),
        )
        if updated.rowcount != 1:
            raise AccessPolicyVersionConflict(str(rule.rule_ref))
        cls._persist_rule_children(connection, rule)

    @classmethod
    def get_rule_in(
        cls,
        connection: psycopg.Connection[Any],
        rule_ref: UUID,
    ) -> PolicyRule | None:
        row = connection.execute(
            """
            SELECT rule_ref, source_deployment_ref, destination_deployment_ref,
                   interaction_revision_ref, effect_state, effective_from,
                   effective_until, version
            FROM access_policy.policy_rule
            WHERE rule_ref = %s
            """,
            (rule_ref,),
        ).fetchone()
        if row is None:
            return None
        auth_rows = connection.execute(
            """
            SELECT evidence_ref, access_request_ref, external_decision_ref,
                   decided_by_subject, decided_at
            FROM access_policy.policy_rule_authorization_evidence
            WHERE rule_ref = %s
            ORDER BY decided_at, evidence_ref
            """,
            (rule_ref,),
        ).fetchall()
        justification_rows = connection.execute(
            """
            SELECT association_ref, need_ref, attached_at,
                   attached_by_subject, source_access_request_ref
            FROM access_policy.policy_rule_justification
            WHERE rule_ref = %s
            ORDER BY attached_at, association_ref
            """,
            (rule_ref,),
        ).fetchall()
        history_rows = connection.execute(
            """
            SELECT history_ref, rule_version, effect_state,
                   effective_from, effective_until,
                   changed_by_subject, changed_at
            FROM access_policy.policy_rule_operational_history
            WHERE rule_ref = %s
            ORDER BY rule_version
            """,
            (rule_ref,),
        ).fetchall()
        return PolicyRule(
            rule_ref=row[0],
            access_subject=AccessSubject(
                source_deployment_ref=row[1],
                destination_deployment_ref=row[2],
                interaction_revision_ref=row[3],
            ),
            effect_state=RuleEffectState(row[4]),
            effective_window=EffectiveWindow(
                effective_from=row[5],
                effective_until=row[6],
            ),
            version=row[7],
            authorization_evidence=tuple(
                AuthorizationEvidence(
                    evidence_ref=evidence_ref,
                    access_request_ref=access_request_ref,
                    external_decision_ref=external_decision_ref,
                    decided_by_subject=decided_by_subject,
                    decided_at=decided_at,
                )
                for (
                    evidence_ref,
                    access_request_ref,
                    external_decision_ref,
                    decided_by_subject,
                    decided_at,
                ) in auth_rows
            ),
            justifications=tuple(
                JustificationAssociation(
                    association_ref=association_ref,
                    need_ref=need_ref,
                    attached_at=attached_at,
                    attached_by_subject=attached_by_subject,
                    source_access_request_ref=source_access_request_ref,
                )
                for (
                    association_ref,
                    need_ref,
                    attached_at,
                    attached_by_subject,
                    source_access_request_ref,
                ) in justification_rows
            ),
            operational_history=tuple(
                OperationalHistory(
                    history_ref=history_ref,
                    rule_version=rule_version,
                    effect_state=RuleEffectState(effect_state),
                    effective_window=EffectiveWindow(
                        effective_from=effective_from,
                        effective_until=effective_until,
                    ),
                    changed_by_subject=changed_by_subject,
                    changed_at=changed_at,
                )
                for (
                    history_ref,
                    rule_version,
                    effect_state,
                    effective_from,
                    effective_until,
                    changed_by_subject,
                    changed_at,
                ) in history_rows
            ),
        )

    @staticmethod
    def _persist_rule_children(
        connection: psycopg.Connection[Any],
        rule: PolicyRule,
    ) -> None:
        for evidence in rule.authorization_evidence:
            connection.execute(
                """
                INSERT INTO access_policy.policy_rule_authorization_evidence
                    (evidence_ref, rule_ref, access_request_ref,
                     external_decision_ref, decided_by_subject, decided_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (evidence_ref) DO NOTHING
                """,
                (
                    evidence.evidence_ref,
                    rule.rule_ref,
                    evidence.access_request_ref,
                    evidence.external_decision_ref,
                    evidence.decided_by_subject,
                    evidence.decided_at,
                ),
            )
        for association in rule.justifications:
            connection.execute(
                """
                INSERT INTO access_policy.policy_rule_justification
                    (association_ref, rule_ref, need_ref,
                     attached_at, attached_by_subject, source_access_request_ref)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (association_ref) DO NOTHING
                """,
                (
                    association.association_ref,
                    rule.rule_ref,
                    association.need_ref,
                    association.attached_at,
                    association.attached_by_subject,
                    association.source_access_request_ref,
                ),
            )
        for history in rule.operational_history:
            connection.execute(
                """
                INSERT INTO access_policy.policy_rule_operational_history
                    (history_ref, rule_ref, rule_version, effect_state,
                     effective_from, effective_until,
                     changed_by_subject, changed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (history_ref) DO NOTHING
                """,
                (
                    history.history_ref,
                    rule.rule_ref,
                    history.rule_version,
                    history.effect_state.value,
                    history.effective_window.effective_from,
                    history.effective_window.effective_until,
                    history.changed_by_subject,
                    history.changed_at,
                ),
            )
