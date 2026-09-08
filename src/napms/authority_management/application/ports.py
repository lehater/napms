from datetime import datetime
from typing import Protocol

from napms.authority_management.domain.model import AuthorityAssignment


class AuthorityPersistenceError(Exception):
    """Authority persistence failed without a trustworthy semantic result."""


class AuthorityAssignmentRepository(Protocol):
    def find_effective(
        self,
        *,
        actor_id: str,
        action: str,
        scope: str,
        effective_time: datetime,
    ) -> tuple[AuthorityAssignment, ...]: ...

    def find_effective_for_actor_action(
        self,
        *,
        actor_id: str,
        action: str,
        effective_time: datetime,
    ) -> tuple[AuthorityAssignment, ...]: ...
