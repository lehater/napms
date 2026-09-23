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
    PostgresApplicationCommunicationCatalogue,
)
from napms.contexts.application_deployment.infrastructure.persistence.postgres.repository import (
    PostgresComponentDeploymentRepository,
)
from napms.contexts.authority_management.application.service import (
    Principal,
    RequireScopedAuthority,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.repository import (
    PostgresResourceCatalogueRepository,
)


class PolicyMaterializationRejected(ValueError):
    pass


class PolicyMaterializationIntegrityError(RuntimeError):
    pass


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
                {"policyRuleRef": str(item.rule_ref), "reason": item.reason} for item in self.issues
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
            if missing:
                raise PolicyMaterializationRejected(
                    "selected policy rule does not exist: "
                    + ", ".join(str(value) for value in missing)
                )

            selection: dict[str, object] = {
                "mode": "ALL" if rule_refs is None else "EXPLICIT",
                "policyRuleRefs": [str(rule.rule_ref) for rule in rules],
            }
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
                source = PostgresComponentDeploymentRepository.resolve_deployment_in(
                    connection, subject.source_deployment_ref
                )
                destination = PostgresComponentDeploymentRepository.resolve_deployment_in(
                    connection, subject.destination_deployment_ref
                )
                revision = PostgresApplicationCommunicationCatalogue.resolve_revision_in(
                    connection, subject.interaction_revision_ref
                )
                if source is None or destination is None or revision is None:
                    raise PolicyMaterializationIntegrityError(
                        f"policy rule {rule.rule_ref} references missing deployment/revision truth"
                    )

                source_resource = PostgresResourceCatalogueRepository.resolve_resource_in(
                    connection, source.resource_ref
                )
                destination_resource = PostgresResourceCatalogueRepository.resolve_resource_in(
                    connection, destination.resource_ref
                )
                if source_resource is None or destination_resource is None:
                    raise PolicyMaterializationIntegrityError(
                        f"policy rule {rule.rule_ref} references missing Resource truth"
                    )

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
            incomplete_rules: set[UUID] = set()
            for rule in rules:
                facts = realization.get(rule.rule_ref)
                if facts is None:
                    continue
                source, destination, revision, source_resource, destination_resource = facts

                for source_endpoint_ref, source_address in self._endpoint_realizations(
                    source_resource
                ):
                    for (
                        destination_endpoint_ref,
                        destination_address,
                    ) in self._endpoint_realizations(destination_resource):
                        ready = source_address is not None and destination_address is not None
                        if not ready:
                            incomplete_rules.add(rule.rule_ref)

                        for clause in revision.revision.traffic_clauses:
                            rows.append(
                                {
                                    "policyRuleRef": str(rule.rule_ref),
                                    "technicalStatus": "READY" if ready else "INCOMPLETE",
                                    "sourceDeploymentRef": str(source.deployment_ref),
                                    "destinationDeploymentRef": str(destination.deployment_ref),
                                    "interactionRevisionRef": str(
                                        rule.access_subject.interaction_revision_ref
                                    ),
                                    "sourceResourceRef": str(source_resource.resource_ref),
                                    "sourceResourceName": source_resource.display_name,
                                    "sourceEndpointRef": (
                                        None
                                        if source_endpoint_ref is None
                                        else str(source_endpoint_ref)
                                    ),
                                    "sourceAddress": source_address,
                                    "destinationResourceRef": str(
                                        destination_resource.resource_ref
                                    ),
                                    "destinationResourceName": (destination_resource.display_name),
                                    "destinationEndpointRef": (
                                        None
                                        if destination_endpoint_ref is None
                                        else str(destination_endpoint_ref)
                                    ),
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

            issues = tuple(
                MaterializationIssue(
                    rule_ref,
                    "current address realization incomplete",
                )
                for rule_ref in sorted(incomplete_rules, key=str)
            )
            return MaterializationResult(
                status="COMPLETE",
                evaluation_at=evaluation_at,
                selection=selection,
                export_authority_evidence=authority_evidence,
                rule_provenance=tuple(provenance),
                non_effective=tuple(non_effective),
                rows=tuple(rows),
                issues=issues,
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
    def _endpoint_realizations(resource: Any) -> tuple[tuple[UUID | None, str | None], ...]:
        if not resource.endpoints:
            return ((None, None),)
        return tuple(
            (
                endpoint.endpoint_ref,
                (
                    None
                    if endpoint.current_address is None
                    else endpoint.current_address.address.value
                ),
            )
            for endpoint in resource.endpoints
        )

    @staticmethod
    def _authority_evidence(
        principal: Principal,
        *,
        scope: str,
        evaluation_at: datetime,
    ) -> dict[str, object]:
        evidence = RequireScopedAuthority().require(
            principal=principal,
            action="policy.export",
            scopes=(scope,),
            evaluated_at=evaluation_at,
        )[0]
        return {
            "actorSubject": principal.subject,
            "action": evidence.action,
            "scopeRef": evidence.scope,
            "effectiveFrom": (
                None if evidence.effective_from is None else evidence.effective_from.isoformat()
            ),
            "effectiveUntil": (
                None if evidence.effective_until is None else evidence.effective_until.isoformat()
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
