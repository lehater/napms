from __future__ import annotations

from datetime import datetime

from napms.contexts.authority_management.domain.model import (
    AuthorityEvidence,
    Principal,
)


class AuthorityForbidden(Exception):
    pass


class RequireScopedAuthority:
    def require(
        self,
        *,
        principal: Principal,
        action: str,
        scopes: tuple[str, ...],
        evaluated_at: datetime,
    ) -> tuple[AuthorityEvidence, ...]:
        if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
            raise ValueError("evaluated_at must be timezone-aware")
        if not action.strip() or any(not scope.strip() for scope in scopes):
            raise ValueError("action and scopes must be explicit")
        required_scopes = tuple(dict.fromkeys(scope.strip() for scope in scopes))

        evidence: list[AuthorityEvidence] = []
        for scope in required_scopes:
            grant = next(
                (
                    candidate
                    for candidate in principal.authority_grants
                    if candidate.is_effective(
                        action=action,
                        scope=scope,
                        evaluated_at=evaluated_at,
                    )
                ),
                None,
            )
            if grant is None:
                raise AuthorityForbidden(f"{action}@{scope}")
            evidence.append(
                AuthorityEvidence(
                    action=action,
                    scope=scope,
                    evaluated_at=evaluated_at,
                    effective_from=grant.effective_from,
                    effective_until=grant.effective_until,
                )
            )
        return tuple(evidence)
