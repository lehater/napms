from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict

from napms.contexts.access_policy.application.ports import (
    AccessPolicyNotFound,
    AccessPolicyVersionConflict,
)
from napms.contexts.access_policy.application.ports import (
    AccessPolicyNotFound,
    AccessPolicyVersionConflict,
)
from napms.contexts.access_policy.application.submission import AccessRequestSubmissionRejected
from napms.contexts.access_policy.domain.model import (
    EffectiveWindow,
    PermissionDecision,
    PolicyRule,
    RuleEffectState,
)
from napms.platform.database.policy_materialization import MaterializationResult
from napms.platform.database.policy_rule_justification import JustificationRejected
from napms.contexts.access_policy.domain.model import AccessRequest, PermissionDecision, PolicyRule
from napms.contexts.authority_management.application.service import AuthorityForbidden
from napms.contexts.authority_management.domain.model import Principal
from napms.platform.security.oidc import (
    AuthenticationRejected,
    IdentityDependencyUnavailable,
    OidcIdentityValidator,
)


class AccessRequestSubmitter(Protocol):
    def submit(
        self,
        *,
        principal: Principal,
        source_deployment_ref: UUID,
        destination_deployment_ref: UUID,
        interaction_revision_ref: UUID,
        need_ref: UUID,
    ) -> AccessRequest: ...


class AccessRequestDecider(Protocol):
    def decide(
        self,
        *,
        request_ref: UUID,
        result: PermissionDecision,
        decided_by_subject: str,
        expected_version: int,
        external_decision_ref: str | None = None,
    ) -> tuple[AccessRequest, PolicyRule | None]: ...


class AccessRequestDecider(Protocol):
    def decide(
        self,
        *,
        request_ref: UUID,
        result: PermissionDecision,
        decided_by_subject: str,
        expected_version: int,
        external_decision_ref: str | None = None,
    ): ...


class PolicyRuleJustifier(Protocol):
    def attach(
        self,
        *,
        rule_ref: UUID,
        need_ref: UUID,
        attached_by_subject: str,
        expected_version: int,
    ) -> PolicyRule: ...


class PolicyRuleOperator(Protocol):
    def set_state(
        self,
        *,
        rule_ref: UUID,
        effect_state: RuleEffectState,
        effective_window: EffectiveWindow,
        changed_by_subject: str,
        expected_version: int,
    ) -> PolicyRule: ...


class PolicyMaterializer(Protocol):
    def materialize(
        self,
        *,
        principal: Principal,
        rule_refs: tuple[UUID, ...] | None,
    ) -> MaterializationResult: ...


class SubmitAccessRequestBody(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    source_deployment_ref: UUID
    destination_deployment_ref: UUID
    interaction_revision_ref: UUID
    need_ref: UUID


class DecideAccessRequestBody(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    result: PermissionDecision
    external_decision_ref: str | None = None


@dataclass(frozen=True)
class HttpDependencies:
    identity: OidcIdentityValidator
    access_requests: AccessRequestSubmitter
    access_request_decisions: AccessRequestDecider | None = None
    policy_rule_justifications: PolicyRuleJustifier | None = None
    policy_rule_operations: PolicyRuleOperator | None = None
    policy_materialization: PolicyMaterializer | None = None
    access_request_decisions: AccessRequestDecider | None = None


def create_app(dependencies: HttpDependencies) -> FastAPI:
    app = FastAPI(title="NAPMS", version="1.0")

    def principal(authorization: str | None = Header(default=None)) -> Principal:
        if authorization is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        scheme, separator, token = authorization.partition(" ")
        if separator != " " or scheme.lower() != "bearer" or not token.strip():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        try:
            return dependencies.identity.validate_bearer(token)
        except AuthenticationRejected as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc
        except IdentityDependencyUnavailable as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE) from exc

    def require_permission(caller: Principal, permission: str) -> None:
        if permission not in caller.instance_permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    def expected_version(if_match: str) -> int:
        value = if_match.strip()
        if value.startswith("W/"):
            value = value[2:]
        value = value.strip('"')
        try:
            version = int(value)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
        if version < 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        return version

    @app.post("/v1/access-requests", status_code=status.HTTP_201_CREATED)
    def submit_access_request(
        body: SubmitAccessRequestBody,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1),
        caller: Principal = Depends(principal),
    ) -> dict[str, object]:
        del idempotency_key
        try:
            request = dependencies.access_requests.submit(
                principal=caller,
                source_deployment_ref=body.source_deployment_ref,
                destination_deployment_ref=body.destination_deployment_ref,
                interaction_revision_ref=body.interaction_revision_ref,
                need_ref=body.need_ref,
            )
        except AuthorityForbidden as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN) from exc
        except AccessRequestSubmissionRejected as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc
        return {"requestRef": str(request.request_ref), "version": request.version}

    @app.post("/v1/access-requests/{request_ref}/decision")
    def decide_access_request(
        request_ref: UUID,
        body: DecideAccessRequestBody,
        if_match: str = Header(alias="If-Match"),
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1),
        caller: Principal = Depends(principal),
    ) -> dict[str, object]:
        del idempotency_key
        if "access.decide" not in caller.instance_permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        if dependencies.access_request_decisions is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            expected_version = int(if_match.strip('"'))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
        try:
            request, rule = dependencies.access_request_decisions.decide(
                request_ref=request_ref,
                result=body.result,
                decided_by_subject=caller.subject,
                expected_version=expected_version,
                external_decision_ref=body.external_decision_ref,
            )
        except AccessPolicyVersionConflict as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
        except AccessPolicyNotFound as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
        return {
            "requestRef": str(request.request_ref),
            "version": request.version,
            "result": request.decision_result.value,
            "policyRuleRef": None if rule is None else str(rule.rule_ref),
        }

    class DecideAccessRequestBody(BaseModel):
        model_config = ConfigDict(extra="forbid", populate_by_name=True)
        result: PermissionDecision
        external_decision_ref: str | None = None

    @app.post("/v1/access-requests/{request_ref}/decision")
    def decide_access_request(
        request_ref: UUID,
        body: DecideAccessRequestBody,
        if_match: str = Header(alias="If-Match"),
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1),
        caller: Principal = Depends(principal),
    ) -> dict[str, object]:
        del idempotency_key
        require_permission(caller, "access.decide")
        if dependencies.access_request_decisions is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            decided, rule = dependencies.access_request_decisions.decide(
                request_ref=request_ref,
                result=body.result,
                decided_by_subject=caller.subject,
                expected_version=expected_version(if_match),
                external_decision_ref=body.external_decision_ref,
            )
        except AccessPolicyVersionConflict as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
        except AccessPolicyNotFound as exc:
            # The canonical decision operation has no 404 response; inability to
            # establish its outcome is represented as unavailable.
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE) from exc
        return {
            "requestRef": str(decided.request_ref),
            "version": decided.version,
            "result": decided.decision_result.value if decided.decision_result else None,
            "policyRuleRef": None if rule is None else str(rule.rule_ref),
        }

    class AttachJustificationBody(BaseModel):
        model_config = ConfigDict(extra="forbid", populate_by_name=True)
        need_ref: UUID

    @app.post("/v1/policy-rules/{rule_ref}/justifications")
    def attach_justification(
        rule_ref: UUID,
        body: AttachJustificationBody,
        if_match: str = Header(alias="If-Match"),
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1),
        caller: Principal = Depends(principal),
    ) -> dict[str, object]:
        del idempotency_key
        require_permission(caller, "access.manage")
        if dependencies.policy_rule_justifications is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            rule = dependencies.policy_rule_justifications.attach(
                rule_ref=rule_ref,
                need_ref=body.need_ref,
                attached_by_subject=caller.subject,
                expected_version=expected_version(if_match),
            )
        except AccessPolicyVersionConflict as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
        except JustificationRejected as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc
        except AccessPolicyNotFound as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc
        return {"policyRuleRef": str(rule.rule_ref), "version": rule.version}

    class EffectiveWindowBody(BaseModel):
        model_config = ConfigDict(extra="forbid", populate_by_name=True)
        effective_from: datetime | None = None
        effective_until: datetime | None = None

    class SetOperationalStateBody(BaseModel):
        model_config = ConfigDict(extra="forbid", populate_by_name=True)
        effect_state: RuleEffectState
        effective_window: EffectiveWindowBody | None = None

    @app.put("/v1/policy-rules/{rule_ref}/operational-state")
    def set_operational_state(
        rule_ref: UUID,
        body: SetOperationalStateBody,
        if_match: str = Header(alias="If-Match"),
        caller: Principal = Depends(principal),
    ) -> dict[str, object]:
        require_permission(caller, "access.manage")
        if dependencies.policy_rule_operations is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        window = body.effective_window
        try:
            rule = dependencies.policy_rule_operations.set_state(
                rule_ref=rule_ref,
                effect_state=body.effect_state,
                effective_window=EffectiveWindow(
                    effective_from=None if window is None else window.effective_from,
                    effective_until=None if window is None else window.effective_until,
                ),
                changed_by_subject=caller.subject,
                expected_version=expected_version(if_match),
            )
        except AccessPolicyVersionConflict as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
        except AccessPolicyNotFound as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc
        return {"policyRuleRef": str(rule.rule_ref), "version": rule.version}

    class PolicyMaterializationBody(BaseModel):
        model_config = ConfigDict(extra="forbid", populate_by_name=True)
        policy_rule_refs: tuple[UUID, ...] | None = None

    @app.post("/v1/policy-materializations")
    def materialize_policy(
        body: PolicyMaterializationBody,
        caller: Principal = Depends(principal),
    ) -> dict[str, object]:
        if dependencies.policy_materialization is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            result = dependencies.policy_materialization.materialize(
                principal=caller,
                rule_refs=body.policy_rule_refs,
            )
        except AuthorityForbidden as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN) from exc
        return result.as_http()

    return app
