from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from napms.contexts.access_policy.domain.model import (
    AccessRequest,
    PermissionDecision,
    PolicyRule,
    RuleEffectState,
)


class AccessRequestSortField(str, Enum):
    SUBMITTED_AT = "submittedAt"
    REQUEST_REF = "requestRef"
    DECISION_RESULT = "decisionResult"


class PolicyRuleSortField(str, Enum):
    POLICY_RULE_REF = "policyRuleRef"
    EFFECT_STATE = "effectState"


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True)
class AccessRequestCatalogueQuery:
    search: str | None = None
    source_deployment_ref: UUID | None = None
    destination_deployment_ref: UUID | None = None
    decision_result: PermissionDecision | None = None
    sort_by: AccessRequestSortField = AccessRequestSortField.SUBMITTED_AT
    sort_direction: SortDirection = SortDirection.ASC
    page: int = 1
    page_size: int = 25

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if not 1 <= self.page_size <= 100:
            raise ValueError("page_size must be between 1 and 100")


@dataclass(frozen=True)
class AccessRequestCataloguePage:
    items: tuple[AccessRequest, ...]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True)
class PolicyRuleCatalogueQuery:
    search: str | None = None
    source_deployment_ref: UUID | None = None
    destination_deployment_ref: UUID | None = None
    effect_state: RuleEffectState | None = None
    sort_by: PolicyRuleSortField = PolicyRuleSortField.POLICY_RULE_REF
    sort_direction: SortDirection = SortDirection.ASC
    page: int = 1
    page_size: int = 25

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if not 1 <= self.page_size <= 100:
            raise ValueError("page_size must be between 1 and 100")


@dataclass(frozen=True)
class PolicyRuleCataloguePage:
    items: tuple[PolicyRule, ...]
    total: int
    page: int
    page_size: int
