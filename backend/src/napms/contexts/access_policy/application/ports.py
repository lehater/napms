from __future__ import annotations

from typing import Protocol
from uuid import UUID

from napms.contexts.access_policy.domain.model import AccessRequest, AccessSubject, PolicyRule


class AccessPolicyNotFound(Exception):
    pass


class AccessPolicyVersionConflict(Exception):
    pass


class AccessRequestRepository(Protocol):
    def add_request(self, request: AccessRequest) -> None: ...

    def get_request(self, request_ref: UUID) -> AccessRequest | None: ...

    def save_request(self, request: AccessRequest, *, expected_version: int) -> None: ...


class PolicyRuleRepository(Protocol):
    def find_rule_by_subject(self, subject: AccessSubject) -> PolicyRule | None: ...

    def add_rule(self, rule: PolicyRule) -> None: ...

    def save_rule(self, rule: PolicyRule, *, expected_version: int) -> None: ...

    def get_rule(self, rule_ref: UUID) -> PolicyRule | None: ...
