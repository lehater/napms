from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

import psycopg

from napms.contexts.access_policy.domain.model import PolicyRule
from napms.contexts.access_policy.infrastructure.persistence.postgres.repository import (
    PostgresAccessPolicyRepository,
)
from napms.contexts.application_communication_catalogue.infrastructure.persistence.postgres.repository import (
    PostgresApplicationCommunicationRepository,
)
from napms.contexts.application_deployment.infrastructure.persistence.postgres.repository import (
    PostgresApplicationDeploymentRepository,
)
from napms.contexts.authority_management.application.service import (
    Principal,
    RequireScopedAuthority,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.repository import (
    PostgresResourceRepository,
)


@dataclass(frozen=True)
class MaterializationIssue:
    rule_ref: UUID
    reason: str


@dataclass(frozen=True)
class MaterializationResult:
    status: str
    evaluation_at: datetime
    selection: dict[str, object]
    export_authority_evidence: tuple[dict[str, object], ...]
    rule_provenance: tuple[dict[str, object], ...]
    non_effective: tuple[dict[str, object], ...]
    rows: tuple[dict[str, object], ...]
    issues: tuple[MaterializationIssue, ...]

    def as_http(self) -> dict[str, object]:
        return {
            "status": self.status,
            "evaluationAt": self.evaluation_at.isoformat(),
            "selection": self.selection,
            "exportAuthorityEvidence": list(self.export_authority_evidence),
            "ruleProvenance": list(self.rule_provenance),
            "nonEffective": list(self.non_effective),
            "rows": list(self.rows),
            "issues": [
                {"policyRuleRef": str(item.rule_ref), "reason": item.reason}
                for item in self.issues
            ],
        }


class PostgresPolicyMaterialization:
    def __init__(self, *, dsn: str) -> None:
        self._dsn = dsn

    def materialize(
        self,
        *,
        principal: Principal,
        rule_refs: tuple[UUID, ...] | None,
    ) -> MaterializationResult:
        with psycopg.connect(self._dsn) as connection:
            connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            evaluation_at = self._evaluation_at(connection)
            rules, missing = self._select_rules(connection, rule_refs)
            selection = {
                "mode": "ALL" if rule_refs is None else "EXPLICIT",
                "policyRuleRefs": [str(rule.rule_ref) for rule in rules],
            }
            issues = [
                MaterializationIssue(rule_ref, "selected policy rule unresolved")
                for rule_ref in missing
            ]
            non_effective: list[dict[str, object]] = []
            provenance = [self._provenance(rule) for rule in rules]
            realization: dict[UUID, tuple[Any, Any, Any, Any, Any]] = {}
            scopes: set[str] = set()

            for rule in rules:
                if not rule.is_effective(evaluation_at):
                    non_effective.append(
                        {
                            "policyRuleRef": str(rule.rule_ref),
                            "effectState": rule.effect_state.value,
                        }
                    )
                    continue
                subject = rule.access_subject
                source = PostgresApplicationDeploymentRepository.resolve_deployment_in(
                    connection, subject.source_deployment_ref
                )
                destination = PostgresApplicationDeploymentRepository.resolve_deployment_in(
                    connection, subject.destination_deployment_ref
                )
                revision = PostgresApplicationCommunicationRepository.resolve_revision_in(
                    connection, subject.interaction_revision_ref
                )
                if source is None or destination is None or revision is None:
                    issues.append(
                        MaterializationIssue(rule.rule_ref, "technical reference unresolved")
                    )
                    continue
                source_resource = PostgresResourceRepository.resolve_resource_in(
                    connection, source.resource_ref
                )
                destination_resource = PostgresResourceRepository.resolve_resource_in(
                    connection, destination.resource_ref
                )
                if source_resource is None or destination_resource is None:
                    issues.append(MaterializationIssue(rule.rule_ref, "resource unresolved"))
                    continue
                if not self._addresses(source_resource) or not self._addresses(
                    destination_resource
                ):
                    issues.append(
                        MaterializationIssue(rule.rule_ref, "address realization unresolved")
                    )
                    continue
                scopes.update(
                    (
                        source_resource.authority_scope_ref,
                        destination_resource.authority_scope_ref,
                    )
                )
                realization[rule.rule_ref] = (
                    source,
                    destination,
                    revision,
                    source_resource,
                    destination_resource,
                )

            authority_evidence = tuple(
                self._authority_evidence(
                    principal,
                    scope=scope,
                    evaluation_at=evaluation_at,
                )
                for scope in sorted(scopes)
            )
            rows: list[dict[str, object]] = []
            if not issues:
                for rule in rules:
                    facts = realization.get(rule.rule_ref)
                    if facts is None:
                        continue
                    source, destination, revision, source_resource, destination_resource = facts
                    for source_address in self._addresses(source_resource):
                        for destination_address in self._addresses(destination_resource):
                            for clause in revision.revision.traffic_clauses:
                                rows.append(
                                    {
                                        "policyRuleRef": str(rule.rule_ref),
                                        "sourceDeploymentRef": str(source.deployment_ref),
                                        "destinationDeploymentRef": str(
                                            destination.deployment_ref
                                        ),
                                        "interactionRevisionRef": str(
                                            rule.access_subject.interaction_revision_ref
                                        ),
                                        "sourceAddress": source_address,
                                        "destinationAddress": destination_address,
                                        "ipProtocol": clause.ip_protocol,
                                        "sourcePorts": [
                                            {"start": item.start, "end": item.end}
                                            for item in clause.source_ports
                                        ],
                                        "destinationPorts": [
                                            {"start": item.start, "end": item.end}
                                            for item in clause.destination_ports
                                        ],
                                    }
                                )

            return MaterializationResult(
                status="UNRESOLVED" if issues else "COMPLETE",
                evaluation_at=evaluation_at,
                selection=selection,
                export_authority_evidence=authority_evidence,
                rule_provenance=tuple(provenance),
                non_effective=tuple(non_effective),
                rows=tuple(rows),
                issues=tuple(issues),
            )

    @staticmethod
    def _evaluation_at(connection: psycopg.Connection[Any]) -> datetime:
        row = connection.execute("SELECT transaction_timestamp()").fetchone()
        assert row is not None
        return row[0]

    @staticmethod
    def _select_rules(
        connection: psycopg.Connection[Any],
        rule_refs: tuple[UUID, ...] | None,
    ) -> tuple[tuple[PolicyRule, ...], tuple[UUID, ...]]:
        if rule_refs is None:
            return PostgresAccessPolicyRepository.list_rules_in(connection), ()
        rules: list[PolicyRule] = []
        missing: list[UUID] = []
        for rule_ref in rule_refs:
            rule = PostgresAccessPolicyRepository.get_rule_in(connection, rule_ref)
            if rule is None:
                missing.append(rule_ref)
            else:
                rules.append(rule)
        return tuple(rules), tuple(missing)

    @staticmethod
    def _addresses(resource: Any) -> tuple[str, ...]:
        return tuple(
            endpoint.current_address.address.value
            for endpoint in resource.endpoints
            if endpoint.current_address is not None
        )

    @staticmethod
    def _authority_evidence(
        principal: Principal,
        *,
        scope: str,
        evaluation_at: datetime,
    ) -> dict[str, object]:
        grant = RequireScopedAuthority("policy.export").require(
            principal,
            scope_ref=scope,
            evaluated_at=evaluation_at,
        )
        return {
            "actorSubject": principal.subject,
            "action": grant.action,
            "scopeRef": grant.scope_ref,
            "effectiveFrom": (
                None if grant.effective_from is None else grant.effective_from.isoformat()
            ),
            "effectiveUntil": (
                None if grant.effective_until is None else grant.effective_until.isoformat()
            ),
            "evaluatedAt": evaluation_at.isoformat(),
        }

    @staticmethod
    def _provenance(rule: PolicyRule) -> dict[str, object]:
        return {
            "policyRuleRef": str(rule.rule_ref),
            "version": rule.version,
            "authorizationEvidence": [
                {
                    "accessRequestRef": str(item.access_request_ref),
                    "externalDecisionRef": item.external_decision_ref,
                    "decidedBySubject": item.decided_by_subject,
                    "decidedAt": item.decided_at.isoformat(),
                }
                for item in rule.authorization_evidence
            ],
            "justifications": [
                {
                    "needRef": str(item.need_ref),
                    "attachedBySubject": item.attached_by_subject,
                    "attachedAt": item.attached_at.isoformat(),
                }
                for item in rule.justifications
            ],
        }
