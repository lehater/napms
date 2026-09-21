from datetime import datetime, timedelta, timezone

import pytest

from napms.contexts.authority_management.application.service import (
    AuthorityForbidden,
    RequireScopedAuthority,
)
from napms.contexts.authority_management.domain.model import AuthorityGrant, Principal


NOW = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)


def test_every_distinct_scope_requires_effective_exact_grant() -> None:
    principal = Principal(
        subject="subject:alice",
        authority_grants=(
            AuthorityGrant(action="access.request", scope="scope:a"),
            AuthorityGrant(
                action="access.request",
                scope="scope:b",
                effective_from=NOW - timedelta(minutes=1),
                effective_until=NOW + timedelta(minutes=1),
            ),
        ),
    )

    evidence = RequireScopedAuthority().require(
        principal=principal,
        action="access.request",
        scopes=("scope:a", "scope:b"),
        evaluated_at=NOW,
    )

    assert [item.scope for item in evidence] == ["scope:a", "scope:b"]
    assert all(item.evaluated_at == NOW for item in evidence)


def test_partial_or_out_of_window_coverage_fails_closed() -> None:
    principal = Principal(
        subject="subject:alice",
        authority_grants=(
            AuthorityGrant(
                action="policy.export",
                scope="scope:a",
                effective_until=NOW,
            ),
        ),
    )

    with pytest.raises(AuthorityForbidden):
        RequireScopedAuthority().require(
            principal=principal,
            action="policy.export",
            scopes=("scope:a",),
            evaluated_at=NOW,
        )


def test_exact_action_and_scope_prevent_cross_grant() -> None:
    principal = Principal(
        subject="subject:alice",
        authority_grants=(
            AuthorityGrant(action="CurateApplicationCatalogue", scope="application-catalogue"),
        ),
    )

    with pytest.raises(AuthorityForbidden):
        RequireScopedAuthority().require(
            principal=principal,
            action="CurateResourceCatalogue",
            scopes=("resource-catalogue",),
            evaluated_at=NOW,
        )
