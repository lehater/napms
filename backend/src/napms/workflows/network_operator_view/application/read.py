from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID

from napms.contexts.access_policy_realization.application.ports import ManagedReconciliationScopeContract
from napms.contexts.access_policy_realization.domain.realization import DesiredDerivationStatus
from napms.contexts.access_policy_realization.domain.rendering import RenderStatus
from napms.contexts.network_environment_operations.domain.model import (
    NetworkOperationResult,
)


class Availability(str, Enum):
    AVAILABLE = "Available"
    NOT_AVAILABLE = "NotAvailable"
    UNKNOWN = "Unknown"


class ReadOutcome(str, Enum):
    AVAILABLE = "Available"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"


@dataclass(frozen=True, slots=True)
class AuthorityResult:
    permitted: bool | None
    authority_reference: str | None = None


class OperatorViewAuthorityPort(Protocol):
    def check(self, *, actor_id: str, scope: str, as_of: datetime) -> AuthorityResult: ...


@dataclass(frozen=True, slots=True)
class Stage:
    availability: Availability
    value: object | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class NetworkOperatorRealizationView:
    scope: str
    as_of: datetime
    authority_reference: str
    desired: Stage
    reconciliation: Stage
    rendering: Stage
    operation: Stage


@dataclass(frozen=True, slots=True)
class ReadNetworkOperatorRealizationResult:
    outcome: ReadOutcome
    view: NetworkOperatorRealizationView | None = None


class ReadNetworkOperatorRealization:
    def __init__(self, *, authority: OperatorViewAuthorityPort, derive_desired, build_configured, reconcile, render) -> None:
        self._authority = authority
        self._derive_desired = derive_desired
        self._build_configured = build_configured
        self._reconcile = reconcile
        self._render = render

    def execute(
        self,
        *,
        actor_id: str,
        scope: str,
        as_of: datetime,
        configured_evidence_set_id: UUID | None = None,
        reconciliation_contract: ManagedReconciliationScopeContract | None = None,
        operation_result: NetworkOperationResult | None = None,
    ) -> ReadNetworkOperatorRealizationResult:
        if not actor_id or not scope:
            raise ValueError("actor_id and scope must be non-empty")
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ValueError("as_of must be timezone-aware")

        admission = self._authority.check(actor_id=actor_id, scope=scope, as_of=as_of)
        if admission.permitted is False:
            return ReadNetworkOperatorRealizationResult(ReadOutcome.AUTHORITY_DENIED)
        if admission.permitted is not True or not admission.authority_reference:
            return ReadNetworkOperatorRealizationResult(ReadOutcome.AUTHORITY_UNKNOWN)

        desired_value = self._derive_desired.execute(governance_scope=scope, as_of=as_of)
        desired = (
            Stage(Availability.AVAILABLE, desired_value)
            if desired_value.status is DesiredDerivationStatus.DERIVED
            else Stage(Availability.UNKNOWN, desired_value, desired_value.status.value)
        )

        rendered_values = self._render.execute(desired_value)
        if rendered_values and all(item.status is RenderStatus.RENDERED for item in rendered_values):
            rendering = Stage(Availability.AVAILABLE, tuple(rendered_values))
        elif any(item.status is RenderStatus.UNKNOWN for item in rendered_values):
            rendering = Stage(Availability.UNKNOWN, tuple(rendered_values), "RenderUnknown")
        elif rendered_values:
            rendering = Stage(Availability.UNKNOWN, tuple(rendered_values), "RenderUnsupported")
        else:
            rendering = Stage(Availability.NOT_AVAILABLE, (), "NoRenderTarget")

        if configured_evidence_set_id is None or reconciliation_contract is None:
            reconciliation = Stage(Availability.NOT_AVAILABLE, reason="ConfiguredInputNotSelected")
        else:
            configured = self._build_configured.execute(
                evidence_set_id=configured_evidence_set_id,
                contract=reconciliation_contract,
                as_of=as_of,
            )
            result = self._reconcile.execute(desired=desired_value, configured=configured)
            reconciliation = Stage(Availability.AVAILABLE, result)
            if getattr(result.status, "value", None) == "Unknown":
                reconciliation = Stage(Availability.UNKNOWN, result, "ReconciliationUnknown")

        operation = (
            Stage(Availability.AVAILABLE, operation_result)
            if operation_result is not None
            else Stage(Availability.NOT_AVAILABLE, reason="OperationEvidenceNotSelected")
        )

        return ReadNetworkOperatorRealizationResult(
            ReadOutcome.AVAILABLE,
            NetworkOperatorRealizationView(
                scope=scope,
                as_of=as_of,
                authority_reference=admission.authority_reference,
                desired=desired,
                reconciliation=reconciliation,
                rendering=rendering,
                operation=operation,
            ),
        )
