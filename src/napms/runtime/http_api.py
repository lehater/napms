import json
import logging
import re
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable, ContextManager
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from napms.access_policy.application.materialize_rule import (
    MaterializationOutcome,
    MaterializeAllowedAccessRule,
    SubmitAccessRuleProposal,
)
from napms.access_policy.application.ports import (
    AccessRuleCommitOutcomeUnknown,
    AccessRulePersistenceError,
    ConnectivityDecisionPort,
)
from napms.access_policy.application.read_rules import (
    AccessRuleDetailOutcome,
    GetAuthorizedAccessRule,
    ListAuthorizedAccessRules,
)
from napms.access_policy.application.proposal_options import (
    DiscoverProposalInteractions,
    DiscoverProposalScopes,
    ProposalInteractionDiscoveryOutcome,
)
from napms.access_policy.application.set_effective_window import (
    EffectiveWindowMutationOutcome,
    SetAccessRuleEffectiveWindow,
    SetRuleEffectiveWindow,
)
from napms.access_policy.application.set_operational_state import (
    OperationalStateMutationOutcome,
    SetAccessRuleOperationalState,
    SetRuleOperationalState,
)
from napms.access_policy.application.select_effective_policy import (
    DiscoverEffectivePolicyScopes,
    EffectivePolicySelectionOutcome,
    SelectAccessPolicyEffectiveDesiredPolicy,
    SelectEffectiveDesiredPolicy,
)
from napms.access_policy.domain.model import AccessRule, EffectiveWindow, OperationalState
from napms.application_catalogue.application.ports import CataloguePersistenceError
from napms.authority_management.application.ports import AuthorityPersistenceError
from napms.policy_export.application.export_snapshot import (
    AssembleExportSnapshot,
    SnapshotAssemblyOutcome,
)
from napms.policy_export.application.normalize_snapshot import NormalizeExportSnapshot
from napms.policy_export.application.normalization_types import (
    NormalizationInvariantError,
)
from napms.runtime.auth import (
    AuthenticatedActor,
    InMemorySessionStore,
    LocalPasswordAuthenticator,
)
from napms.runtime.normalized_policy_json import (
    normalized_policy_export_json,
    snapshot_diagnostic_json,
)


SESSION_COOKIE_NAME = "napms_session"
CORRELATION_HEADER = "X-Correlation-ID"
_CORRELATION_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_LOGGER = logging.getLogger("napms.runtime.http")
_ERROR_DEPENDENCIES = {
    "AuthorityDenied": "AuthorityManagement",
    "AuthorityUnknown": "AuthorityManagement",
    "AuthorityUnavailable": "AuthorityManagement",
    "InteractionInvalid": "ApplicationCommunicationCatalogue",
    "InteractionUnknown": "ApplicationCommunicationCatalogue",
    "CatalogueUnavailable": "ApplicationCommunicationCatalogue",
    "DecisionUnknown": "ConnectivityDecision",
    "DecisionSubjectMismatch": "ConnectivityDecision",
    "PersistenceUnavailable": "AccessPolicyPersistence",
    "PersistenceOutcomeUnknown": "AccessPolicyPersistence",
    "SnapshotIncomplete": "PolicyExportSnapshot",
    "NormalizationFailed": "PolicyExportNormalization",
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class HttpApiDependencies:
    authenticator: LocalPasswordAuthenticator
    sessions: InMemorySessionStore
    open_scope: Callable[[], ContextManager[Any]]
    decisions: ConnectivityDecisionPort
    readiness: Callable[[], bool]
    clock: Callable[[], datetime] = _utc_now
    secure_cookie: bool = False


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    login: str = Field(min_length=1, max_length=256)
    password: str = Field(min_length=1, max_length=4096)


class SubmitProposalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    authority_scope: str = Field(alias="authorityScope", min_length=1, max_length=512)
    source_component_deployment_id: UUID = Field(alias="sourceComponentDeploymentId")
    destination_component_deployment_id: UUID = Field(
        alias="destinationComponentDeploymentId"
    )
    dcs_contract_revision_id: UUID = Field(alias="dcsContractRevisionId")


class SetOperationalStateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    target_state: OperationalState = Field(alias="targetState")


class EffectiveWindowValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: datetime
    end: datetime


class SetEffectiveWindowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    window: EffectiveWindowValue | None


class PublicApiError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def configure_json_logging(*, level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    _LOGGER.handlers.clear()
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(level)
    _LOGGER.propagate = False


def _safe_correlation_id(raw: str | None) -> str:
    if raw and _CORRELATION_PATTERN.fullmatch(raw):
        return raw
    return str(uuid4())


def _correlation_id(request: Request) -> str:
    return getattr(request.state, "correlation_id", str(uuid4()))


def _set_outcome(request: Request, outcome: str) -> None:
    request.state.semantic_outcome = outcome


def _set_dependency(request: Request, dependency: str) -> None:
    request.state.dependency = dependency


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    _set_outcome(request, code)
    dependency = _ERROR_DEPENDENCIES.get(code)
    if dependency is not None and not getattr(request.state, "dependency", None):
        _set_dependency(request, dependency)
    error = {
        "code": code,
        "message": message,
        "correlationId": _correlation_id(request),
    }
    if details is not None:
        error["details"] = details
    return JSONResponse(
        status_code=status_code,
        content={"error": error},
    )


def _actor_dto(actor: AuthenticatedActor) -> dict[str, str]:
    return {"actorId": actor.actor_id, "login": actor.login}


def _rule_dto(rule: AccessRule) -> dict[str, Any]:
    window = None
    if rule.effective_window is not None:
        window = {
            "start": rule.effective_window.start.isoformat(),
            "end": rule.effective_window.end.isoformat(),
        }
    return {
        "ruleId": str(rule.rule_id),
        "semanticIdentity": {
            "sourceComponentDeploymentId": str(
                rule.semantic_identity.source_component_deployment_id
            ),
            "destinationComponentDeploymentId": str(
                rule.semantic_identity.destination_component_deployment_id
            ),
            "dcsContractRevisionId": str(
                rule.semantic_identity.dcs_contract_revision_id
            ),
        },
        "governanceScope": rule.governance_scope,
        "operationalState": rule.operational_state.value,
        "effectiveWindow": window,
        "decisionReference": rule.decision.decision_id,
    }


def _rule_detail_dto(rule: AccessRule) -> dict[str, Any]:
    payload = _rule_dto(rule)
    payload["proposalProvenance"] = {
        "actorId": rule.proposal_provenance.actor_id,
        "effectiveTime": rule.proposal_provenance.effective_time.isoformat(),
        "authorityReference": rule.proposal_provenance.authority_reference,
        "catalogueReference": rule.proposal_provenance.catalogue_reference,
    }
    payload["stateHistory"] = [
        {
            "fromState": transition.from_state.value,
            "toState": transition.to_state.value,
            "actorId": transition.actor_id,
            "effectiveTime": transition.effective_time.isoformat(),
            "governanceScope": transition.governance_scope,
            "authorityReference": transition.authority_reference,
        }
        for transition in rule.operational_state_history
    ]
    payload["effectiveWindowHistory"] = [
        {
            "previousWindow": (
                {
                    "start": change.previous_window.start.isoformat(),
                    "end": change.previous_window.end.isoformat(),
                }
                if change.previous_window is not None
                else None
            ),
            "newWindow": (
                {
                    "start": change.new_window.start.isoformat(),
                    "end": change.new_window.end.isoformat(),
                }
                if change.new_window is not None
                else None
            ),
            "actorId": change.actor_id,
            "effectiveTime": change.effective_time.isoformat(),
            "governanceScope": change.governance_scope,
            "authorityReference": change.authority_reference,
        }
        for change in rule.effective_window_history
    ]
    return payload


def create_http_api(dependencies: HttpApiDependencies) -> FastAPI:
    app = FastAPI(title="NAPMS API", version="1")

    @app.middleware("http")
    async def runtime_boundary(request: Request, call_next):
        request.state.correlation_id = _safe_correlation_id(
            request.headers.get(CORRELATION_HEADER)
        )
        request.state.operation = request.url.path
        request.state.semantic_outcome = "HttpCompleted"
        started = perf_counter()
        error: Exception | None = None
        try:
            response = await call_next(request)
        except Exception as exc:  # boundary owns generic failure/logging
            error = exc
            request.state.semantic_outcome = "InternalError"
            response = _error_response(
                request,
                status_code=500,
                code="InternalError",
                message="The operation could not be completed.",
            )

        response.headers[CORRELATION_HEADER] = request.state.correlation_id
        duration_ms = round((perf_counter() - started) * 1000, 3)
        event = {
            "event": "operation_completed",
            "operation": request.state.operation,
            "correlationId": request.state.correlation_id,
            "outcome": request.state.semantic_outcome,
            "httpStatus": response.status_code,
            "durationMs": duration_ms,
        }
        actor_id = getattr(request.state, "actor_id", None)
        if actor_id:
            event["actorId"] = actor_id
        for state_name, event_name in (
            ("rule_id", "ruleId"),
            ("authority_reference", "authorityReference"),
            ("decision_reference", "decisionReference"),
            ("dependency", "dependency"),
        ):
            value = getattr(request.state, state_name, None)
            if value:
                event[event_name] = value

        if error is not None:
            event["exception"] = {
                "class": type(error).__name__,
                "stack": [
                    frame.rstrip()
                    for frame in traceback.format_list(
                        traceback.extract_tb(error.__traceback__)
                    )
                ],
            }

        level = logging.INFO
        if response.status_code >= 500:
            level = logging.ERROR if error is not None else logging.WARNING
        elif response.status_code >= 400:
            level = logging.WARNING
        _LOGGER.log(
            level,
            json.dumps(event, separators=(",", ":"), sort_keys=True),
        )
        return response

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_error_handler(
        request: Request,
        exc: StarletteHTTPException,
    ):
        if exc.status_code == 404:
            return _error_response(
                request,
                status_code=404,
                code="NotFound",
                message="The requested resource was not found.",
            )
        if exc.status_code == 405:
            return _error_response(
                request,
                status_code=405,
                code="MethodNotAllowed",
                message="The requested method is not allowed.",
            )
        return _error_response(
            request,
            status_code=exc.status_code,
            code="HttpError",
            message="The request could not be completed.",
        )

    @app.exception_handler(PublicApiError)
    async def public_api_error_handler(request: Request, exc: PublicApiError):
        return _error_response(
            request,
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        return _error_response(
            request,
            status_code=422,
            code="ValidationError",
            message="The request is invalid.",
        )

    @app.exception_handler(AccessRuleCommitOutcomeUnknown)
    async def uncertain_commit_handler(
        request: Request,
        exc: AccessRuleCommitOutcomeUnknown,
    ):
        return _error_response(
            request,
            status_code=503,
            code="PersistenceOutcomeUnknown",
            message="The authoritative persistence outcome is currently unknown.",
        )

    @app.exception_handler(AccessRulePersistenceError)
    async def access_rule_persistence_handler(
        request: Request,
        exc: AccessRulePersistenceError,
    ):
        return _error_response(
            request,
            status_code=503,
            code="PersistenceUnavailable",
            message="The authoritative persistence service is unavailable.",
        )

    @app.exception_handler(AuthorityPersistenceError)
    async def authority_persistence_handler(
        request: Request,
        exc: AuthorityPersistenceError,
    ):
        return _error_response(
            request,
            status_code=503,
            code="AuthorityUnavailable",
            message="Authority information is unavailable.",
        )

    @app.exception_handler(NormalizationInvariantError)
    async def normalization_error_handler(
        request: Request,
        exc: NormalizationInvariantError,
    ):
        return _error_response(
            request,
            status_code=500,
            code="NormalizationFailed",
            message="The normalized policy could not be produced safely.",
        )

    @app.exception_handler(CataloguePersistenceError)
    async def catalogue_persistence_handler(
        request: Request,
        exc: CataloguePersistenceError,
    ):
        return _error_response(
            request,
            status_code=503,
            code="CatalogueUnavailable",
            message="Catalogue information is unavailable.",
        )

    def require_actor(request: Request) -> AuthenticatedActor:
        actor = dependencies.sessions.get(request.cookies.get(SESSION_COOKIE_NAME))
        if actor is None:
            raise PublicApiError(
                status_code=401,
                code="AuthenticationRequired",
                message="Authentication is required.",
            )
        request.state.actor_id = actor.actor_id
        return actor

    @app.post("/api/v1/session", name="CreateSession")
    def create_session(payload: LoginRequest, request: Request):
        request.state.operation = "CreateSession"
        actor = dependencies.authenticator.authenticate(
            login=payload.login,
            password=payload.password,
        )
        if actor is None:
            raise PublicApiError(
                status_code=401,
                code="AuthenticationFailed",
                message="Authentication failed.",
            )

        session_id = dependencies.sessions.create(actor)
        request.state.actor_id = actor.actor_id
        _set_outcome(request, "Authenticated")
        response = JSONResponse(status_code=200, content={"actor": _actor_dto(actor)})
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_id,
            httponly=True,
            secure=dependencies.secure_cookie,
            samesite="strict",
            path="/",
        )
        return response

    @app.get("/api/v1/session", name="GetSession")
    def get_session(
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetSession"
        _set_outcome(request, "Authenticated")
        return {"actor": _actor_dto(actor)}

    @app.delete("/api/v1/session", status_code=204, name="DeleteSession")
    def delete_session(
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DeleteSession"
        dependencies.sessions.delete(request.cookies.get(SESSION_COOKIE_NAME))
        _set_outcome(request, "LoggedOut")
        response = Response(status_code=204)
        response.delete_cookie(
            key=SESSION_COOKIE_NAME,
            path="/",
            secure=dependencies.secure_cookie,
            httponly=True,
            samesite="strict",
        )
        return response

    @app.get("/api/v1/access-rule-proposals/scopes", name="DiscoverProposalScopes")
    def discover_proposal_scopes(
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverProposalScopes"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as scope:
            result = DiscoverProposalScopes(
                authority=scope.proposal_scope_discovery
            ).execute(
                actor_id=actor.actor_id,
                effective_time=effective_time,
            )
        _set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "scopes": [{"scope": value} for value in result.permitted_scopes],
            "ambiguousScopes": [
                {"scope": value} for value in result.ambiguous_scopes
            ],
        }

    @app.get(
        "/api/v1/access-rule-proposals/interactions",
        name="DiscoverProposalInteractions",
    )
    def discover_proposal_interactions(
        request: Request,
        scope: str,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=100),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverProposalInteractions"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = DiscoverProposalInteractions(
                authority=runtime_scope.authority,
                catalogue=runtime_scope.proposal_interaction_catalogue,
            ).execute(
                actor_id=actor.actor_id,
                scope=scope,
                effective_time=effective_time,
                page=page,
                page_size=pageSize,
            )

        if result.outcome is ProposalInteractionDiscoveryOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is ProposalInteractionDiscoveryOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )
        assert result.page is not None
        _set_outcome(request, "Available")
        return {
            "items": [
                {
                    "sourceComponentDeploymentId": str(
                        identity.source_component_deployment_id
                    ),
                    "destinationComponentDeploymentId": str(
                        identity.destination_component_deployment_id
                    ),
                    "dcsContractRevisionId": str(
                        identity.dcs_contract_revision_id
                    ),
                }
                for identity in result.page.identities
            ],
            "page": result.page.page,
            "pageSize": result.page.page_size,
            "hasMore": result.page.has_more,
        }

    @app.post("/api/v1/access-rule-proposals", name="SubmitAccessRuleProposal")
    def submit_access_rule_proposal(
        payload: SubmitProposalRequest,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "SubmitAccessRuleProposal"
        effective_time = dependencies.clock()
        command = SubmitAccessRuleProposal(
            actor_id=actor.actor_id,
            authority_scope=payload.authority_scope,
            effective_time=effective_time,
            source_component_deployment_id=payload.source_component_deployment_id,
            destination_component_deployment_id=payload.destination_component_deployment_id,
            dcs_contract_revision_id=payload.dcs_contract_revision_id,
        )
        with dependencies.open_scope() as scope:
            result = MaterializeAllowedAccessRule(
                authority=scope.authority,
                catalogue=scope.proposal_catalogue,
                decisions=dependencies.decisions,
                rules=scope.access_rules,
            ).execute(command)

        if result.outcome in {
            MaterializationOutcome.MATERIALIZED,
            MaterializationOutcome.RESOLVED,
        }:
            assert result.rule is not None
            request.state.rule_id = str(result.rule.rule_id)
            request.state.authority_reference = (
                result.rule.proposal_provenance.authority_reference
            )
            if result.rule.decision.decision_id:
                request.state.decision_reference = result.rule.decision.decision_id
            _set_outcome(request, result.outcome.value)
            return JSONResponse(
                status_code=(
                    201
                    if result.outcome is MaterializationOutcome.MATERIALIZED
                    else 200
                ),
                content={
                    "outcome": result.outcome.value,
                    "rule": _rule_dto(result.rule),
                },
            )

        if result.outcome is MaterializationOutcome.NOT_ALLOWED:
            _set_outcome(request, result.outcome.value)
            return {"outcome": "NotAllowed", "rule": None}

        mapping = {
            MaterializationOutcome.AUTHORITY_DENIED: (
                403,
                "AuthorityDenied",
                "The requested operation is not permitted.",
            ),
            MaterializationOutcome.AUTHORITY_UNKNOWN: (
                409,
                "AuthorityUnknown",
                "Authority for the requested operation is ambiguous or unavailable.",
            ),
            MaterializationOutcome.INTERACTION_INVALID: (
                422,
                "InteractionInvalid",
                "The selected interaction is invalid.",
            ),
            MaterializationOutcome.INTERACTION_UNKNOWN: (
                409,
                "InteractionUnknown",
                "The selected interaction cannot currently be established.",
            ),
            MaterializationOutcome.DECISION_UNKNOWN: (
                503,
                "DecisionUnknown",
                "The connectivity decision is currently unavailable.",
            ),
            MaterializationOutcome.DECISION_SUBJECT_MISMATCH: (
                502,
                "DecisionSubjectMismatch",
                "The connectivity decision could not be correlated safely.",
            ),
        }
        status_code, code, message = mapping[result.outcome]
        raise PublicApiError(
            status_code=status_code,
            code=code,
            message=message,
        )

    @app.get("/api/v1/access-rules", name="ListAccessRules")
    def list_access_rules(
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=100),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "ListAccessRules"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = ListAuthorizedAccessRules(
                read_authority=runtime_scope.rule_read_scope_discovery,
                rules=runtime_scope.access_rules,
            ).execute(
                actor_id=actor.actor_id,
                effective_time=effective_time,
                page=page,
                page_size=pageSize,
            )

        _set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "items": [_rule_dto(rule) for rule in result.rules],
            "page": result.page,
            "pageSize": result.page_size,
            "hasMore": result.has_more,
            "ambiguousScopes": [
                {"scope": scope} for scope in result.ambiguous_scopes
            ],
        }

    @app.get("/api/v1/access-rules/{rule_id}", name="GetAccessRule")
    def get_access_rule(
        rule_id: UUID,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetAccessRule"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = GetAuthorizedAccessRule(
                authority=runtime_scope.authority,
                rules=runtime_scope.access_rules,
            ).execute(
                rule_id=rule_id,
                actor_id=actor.actor_id,
                effective_time=effective_time,
            )

        if result.outcome is AccessRuleDetailOutcome.RULE_NOT_FOUND:
            raise PublicApiError(
                status_code=404,
                code="RuleNotFound",
                message="The Access Rule was not found.",
            )
        if result.outcome is AccessRuleDetailOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is AccessRuleDetailOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.rule is not None
        assert result.state_mutation_admission is not None
        assert result.effective_window_mutation_admission is not None
        request.state.rule_id = str(result.rule.rule_id)
        request.state.authority_reference = result.read_authority_reference
        _set_outcome(request, "Found")
        return {
            "rule": _rule_detail_dto(result.rule),
            "capabilities": {
                "setOperationalState": result.state_mutation_admission.value,
                "setEffectiveWindow": result.effective_window_mutation_admission.value,
            },
        }

    @app.patch(
        "/api/v1/access-rules/{rule_id}/operational-state",
        name="SetAccessRuleOperationalState",
    )
    def set_access_rule_operational_state(
        rule_id: UUID,
        payload: SetOperationalStateRequest,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "SetAccessRuleOperationalState"
        effective_time = dependencies.clock()
        with dependencies.open_scope() as runtime_scope:
            result = SetAccessRuleOperationalState(
                authority=runtime_scope.authority,
                rules=runtime_scope.access_rules,
            ).execute(
                SetRuleOperationalState(
                    rule_id=rule_id,
                    target_state=payload.target_state,
                    actor_id=actor.actor_id,
                    effective_time=effective_time,
                )
            )

        if result.outcome is OperationalStateMutationOutcome.RULE_NOT_FOUND:
            raise PublicApiError(
                status_code=404,
                code="RuleNotFound",
                message="The Access Rule was not found.",
            )
        if result.outcome is OperationalStateMutationOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is OperationalStateMutationOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.rule is not None
        request.state.rule_id = str(result.rule.rule_id)
        if (
            result.outcome is OperationalStateMutationOutcome.UPDATED
            and result.rule.operational_state_history
        ):
            request.state.authority_reference = (
                result.rule.operational_state_history[-1].authority_reference
            )
        _set_outcome(request, result.outcome.value)
        return {
            "outcome": result.outcome.value,
            "rule": _rule_dto(result.rule),
        }

    @app.patch(
        "/api/v1/access-rules/{rule_id}/effective-window",
        name="SetAccessRuleEffectiveWindow",
    )
    def set_access_rule_effective_window(
        rule_id: UUID,
        payload: SetEffectiveWindowRequest,
        request: Request,
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "SetAccessRuleEffectiveWindow"
        effective_time = dependencies.clock()

        window = None
        if payload.window is not None:
            start = payload.window.start
            end = payload.window.end
            if (
                start.tzinfo is None
                or start.utcoffset() is None
                or end.tzinfo is None
                or end.utcoffset() is None
                or start >= end
            ):
                raise PublicApiError(
                    status_code=422,
                    code="InvalidEffectiveWindow",
                    message="EffectiveWindow requires offset-aware start < end.",
                )
            window = EffectiveWindow(start=start, end=end)

        with dependencies.open_scope() as runtime_scope:
            result = SetAccessRuleEffectiveWindow(
                authority=runtime_scope.authority,
                rules=runtime_scope.access_rules,
            ).execute(
                SetRuleEffectiveWindow(
                    rule_id=rule_id,
                    window=window,
                    actor_id=actor.actor_id,
                    effective_time=effective_time,
                )
            )

        if result.outcome is EffectiveWindowMutationOutcome.RULE_NOT_FOUND:
            raise PublicApiError(
                status_code=404,
                code="RuleNotFound",
                message="The Access Rule was not found.",
            )
        if result.outcome is EffectiveWindowMutationOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if result.outcome is EffectiveWindowMutationOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        assert result.rule is not None
        request.state.rule_id = str(result.rule.rule_id)
        if (
            result.outcome is EffectiveWindowMutationOutcome.UPDATED
            and result.rule.effective_window_history
        ):
            request.state.authority_reference = (
                result.rule.effective_window_history[-1].authority_reference
            )
        _set_outcome(request, result.outcome.value)
        return {
            "outcome": result.outcome.value,
            "rule": _rule_dto(result.rule),
        }

    @app.get("/api/v1/policy-views/scopes", name="DiscoverPolicyViewScopes")
    def discover_policy_view_scopes(
        request: Request,
        as_of: datetime = Query(alias="asOf"),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "DiscoverPolicyViewScopes"
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise PublicApiError(
                status_code=422,
                code="InvalidAsOf",
                message="asOf must include an explicit timezone offset.",
            )
        with dependencies.open_scope() as runtime_scope:
            result = DiscoverEffectivePolicyScopes(
                authority=runtime_scope.effective_policy_scope_discovery,
            ).execute(
                actor_id=actor.actor_id,
                effective_time=as_of,
            )
        _set_outcome(
            request,
            "AuthorityUnknown" if result.ambiguous_scopes else "Available",
        )
        return {
            "scopes": [{"scope": scope} for scope in result.permitted_scopes],
            "ambiguousScopes": [
                {"scope": scope} for scope in result.ambiguous_scopes
            ],
        }

    @app.get("/api/v1/effective-desired-policy", name="GetEffectiveDesiredPolicy")
    def get_effective_desired_policy(
        request: Request,
        scope: str,
        as_of: datetime = Query(alias="asOf"),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetEffectiveDesiredPolicy"
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise PublicApiError(
                status_code=422,
                code="InvalidAsOf",
                message="asOf must include an explicit timezone offset.",
            )

        with dependencies.open_scope() as runtime_scope:
            selection = SelectAccessPolicyEffectiveDesiredPolicy(
                authority=runtime_scope.authority,
                rules=runtime_scope.access_rules,
            ).execute(
                SelectEffectiveDesiredPolicy(
                    scope=scope,
                    as_of=as_of,
                    actor_id=actor.actor_id,
                )
            )

        if selection.outcome is EffectivePolicySelectionOutcome.AUTHORITY_DENIED:
            raise PublicApiError(
                status_code=403,
                code="AuthorityDenied",
                message="The requested operation is not permitted.",
            )
        if selection.outcome is EffectivePolicySelectionOutcome.AUTHORITY_UNKNOWN:
            raise PublicApiError(
                status_code=409,
                code="AuthorityUnknown",
                message="Authority for the requested operation is ambiguous or unavailable.",
            )

        request.state.authority_reference = selection.authority_reference
        _set_outcome(request, "Selected")
        return {
            "scope": selection.scope,
            "asOf": selection.as_of.isoformat(),
            "authorityReference": selection.authority_reference,
            "rules": [_rule_dto(rule) for rule in selection.rules],
        }

    @app.get("/api/v1/normalized-policy", name="GetNormalizedPolicy")
    def get_normalized_policy(
        request: Request,
        scope: str,
        as_of: datetime = Query(alias="asOf"),
        actor: AuthenticatedActor = Depends(require_actor),
    ):
        request.state.operation = "GetNormalizedPolicy"
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise PublicApiError(
                status_code=422,
                code="InvalidAsOf",
                message="asOf must include an explicit timezone offset.",
            )

        with dependencies.open_scope() as runtime_scope:
            selection = SelectAccessPolicyEffectiveDesiredPolicy(
                authority=runtime_scope.authority,
                rules=runtime_scope.access_rules,
            ).execute(
                SelectEffectiveDesiredPolicy(
                    scope=scope,
                    as_of=as_of,
                    actor_id=actor.actor_id,
                )
            )

            if selection.outcome is EffectivePolicySelectionOutcome.AUTHORITY_DENIED:
                raise PublicApiError(
                    status_code=403,
                    code="AuthorityDenied",
                    message="The requested operation is not permitted.",
                )
            if selection.outcome is EffectivePolicySelectionOutcome.AUTHORITY_UNKNOWN:
                raise PublicApiError(
                    status_code=409,
                    code="AuthorityUnknown",
                    message="Authority for the requested operation is ambiguous or unavailable.",
                )

            assembly = AssembleExportSnapshot(
                application_catalogue=runtime_scope.application_projection,
                resource_catalogue=runtime_scope.resource_projection,
            ).execute(selection)

            if assembly.outcome is not SnapshotAssemblyOutcome.SUCCESS:
                raise PublicApiError(
                    status_code=409,
                    code="SnapshotIncomplete",
                    message="A coherent normalized-policy snapshot cannot currently be produced.",
                    details={
                        "diagnostics": [
                            snapshot_diagnostic_json(value)
                            for value in assembly.diagnostics
                        ]
                    },
                )

            assert assembly.snapshot is not None
            normalized = NormalizeExportSnapshot(
                decoder=runtime_scope.dcs_decoder
            ).execute(assembly.snapshot)

        request.state.authority_reference = normalized.authority_reference
        _set_outcome(request, "NormalizedPolicyExported")
        return normalized_policy_export_json(normalized)

    @app.get("/health/live", name="Liveness")
    def liveness(request: Request):
        request.state.operation = "Liveness"
        _set_outcome(request, "Alive")
        return {"status": "alive"}

    @app.get("/health/ready", name="Readiness")
    def readiness(request: Request):
        request.state.operation = "Readiness"
        try:
            ready = dependencies.readiness()
        except Exception:
            ready = False
        if not ready:
            _set_dependency(request, "PostgreSQL")
            _set_outcome(request, "NotReady")
            return JSONResponse(status_code=503, content={"status": "not-ready"})
        _set_outcome(request, "Ready")
        return {"status": "ready"}

    return app
