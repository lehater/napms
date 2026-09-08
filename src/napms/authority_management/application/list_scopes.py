from dataclasses import dataclass
from datetime import datetime

from napms.authority_management.application.ports import AuthorityAssignmentRepository


@dataclass(frozen=True, slots=True)
class AuthorityScopeDiscovery:
    permitted_scopes: tuple[str, ...]
    ambiguous_scopes: tuple[str, ...]


class ListEffectiveAuthorityScopes:
    def __init__(self, *, assignments: AuthorityAssignmentRepository) -> None:
        self._assignments = assignments

    def execute(
        self,
        *,
        actor_id: str,
        action: str,
        effective_time: datetime,
    ) -> AuthorityScopeDiscovery:
        assignments = self._assignments.find_effective_for_actor_action(
            actor_id=actor_id,
            action=action,
            effective_time=effective_time,
        )

        by_scope: dict[str, list] = {}
        for assignment in assignments:
            if assignment.is_effective_at(effective_time):
                by_scope.setdefault(assignment.scope, []).append(assignment)

        permitted = tuple(sorted(scope for scope, matches in by_scope.items() if len(matches) == 1))
        ambiguous = tuple(sorted(scope for scope, matches in by_scope.items() if len(matches) != 1))
        return AuthorityScopeDiscovery(
            permitted_scopes=permitted,
            ambiguous_scopes=ambiguous,
        )
