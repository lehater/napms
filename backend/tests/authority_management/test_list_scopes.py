from datetime import datetime, timezone

from napms.contexts.authority_management.application.list_scopes import ListEffectiveAuthorityScopes
from napms.contexts.authority_management.domain.model import AuthorityAssignment


NOW = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)


class FakeAssignments:
    def __init__(self, assignments):
        self.assignments = tuple(assignments)

    def find_effective_for_actor_action(self, **kwargs):
        return self.assignments


def _assignment(reference_id, scope):
    return AuthorityAssignment(
        reference_id=reference_id,
        actor_id="actor-1",
        action="ProposeConnectivity",
        scope=scope,
        valid_from=NOW,
        valid_to=None,
        provenance_reference=f"prov:{reference_id}",
    )


def test_scope_discovery_returns_only_unambiguous_effective_scopes():
    query = ListEffectiveAuthorityScopes(
        assignments=FakeAssignments(
            (
                _assignment("a1", "scope-a"),
                _assignment("b1", "scope-b"),
                _assignment("b2", "scope-b"),
            )
        )
    )

    result = query.execute(
        actor_id="actor-1",
        action="ProposeConnectivity",
        effective_time=NOW,
    )

    assert result.permitted_scopes == ("scope-a",)
    assert result.ambiguous_scopes == ("scope-b",)
