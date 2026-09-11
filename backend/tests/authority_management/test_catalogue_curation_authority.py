from datetime import datetime, timezone

from napms.application_catalogue.application.ports import (
    APPLICATION_CATALOGUE_AUTHORITY_SCOPE,
    APPLICATION_CATALOGUE_CURATION_ACTION,
    ApplicationCatalogueAuthorityOutcome,
)
from napms.contexts.authority_management.infrastructure.integrations.catalogue_curation import (
    ApplicationCatalogueCurationAuthorityAdapter,
    ResourceCatalogueCurationAuthorityAdapter,
)
from napms.contexts.authority_management.application.check_authority import CheckAuthority
from napms.contexts.authority_management.domain.model import AuthorityAssignment
from napms.contexts.resource_catalogue.application.ports import (
    RESOURCE_CATALOGUE_AUTHORITY_SCOPE,
    RESOURCE_CATALOGUE_CURATION_ACTION,
    ResourceCatalogueAuthorityOutcome,
)


NOW = datetime(2026, 9, 10, 9, 0, tzinfo=timezone.utc)


class FakeAssignments:
    def __init__(self, assignments):
        self.assignments = tuple(assignments)
        self.calls = []

    def find_effective(self, **kwargs):
        self.calls.append(kwargs)
        return tuple(
            item
            for item in self.assignments
            if item.actor_id == kwargs["actor_id"]
            and item.action == kwargs["action"]
            and item.scope == kwargs["scope"]
            and item.is_effective_at(kwargs["effective_time"])
        )


def assignment(reference, *, action, scope):
    return AuthorityAssignment(
        reference_id=reference,
        actor_id="actor-1",
        action=action,
        scope=scope,
        valid_from=datetime(2026, 1, 1, tzinfo=timezone.utc),
        valid_to=None,
        provenance_reference=f"prov:{reference}",
    )


def test_application_catalogue_adapter_uses_fixed_action_and_scope():
    repo = FakeAssignments(
        [
            assignment(
                "acc-curator",
                action=APPLICATION_CATALOGUE_CURATION_ACTION,
                scope=APPLICATION_CATALOGUE_AUTHORITY_SCOPE,
            )
        ]
    )
    adapter = ApplicationCatalogueCurationAuthorityAdapter(
        checker=CheckAuthority(assignments=repo)
    )

    result = adapter.check_curation(actor_id="actor-1", effective_time=NOW)

    assert result.outcome is ApplicationCatalogueAuthorityOutcome.PERMITTED
    assert result.authority_reference == "acc-curator"
    assert repo.calls == [
        {
            "actor_id": "actor-1",
            "action": "CurateApplicationCatalogue",
            "scope": "application-catalogue",
            "effective_time": NOW,
        }
    ]


def test_resource_catalogue_adapter_uses_fixed_action_and_scope():
    repo = FakeAssignments(
        [
            assignment(
                "rc-curator",
                action=RESOURCE_CATALOGUE_CURATION_ACTION,
                scope=RESOURCE_CATALOGUE_AUTHORITY_SCOPE,
            )
        ]
    )
    adapter = ResourceCatalogueCurationAuthorityAdapter(
        checker=CheckAuthority(assignments=repo)
    )

    result = adapter.check_curation(actor_id="actor-1", effective_time=NOW)

    assert result.outcome is ResourceCatalogueAuthorityOutcome.PERMITTED
    assert result.authority_reference == "rc-curator"
    assert repo.calls[0]["scope"] == "resource-catalogue"


def test_application_permission_does_not_grant_resource_curation():
    repo = FakeAssignments(
        [
            assignment(
                "acc-curator",
                action=APPLICATION_CATALOGUE_CURATION_ACTION,
                scope=APPLICATION_CATALOGUE_AUTHORITY_SCOPE,
            )
        ]
    )

    result = ResourceCatalogueCurationAuthorityAdapter(
        checker=CheckAuthority(assignments=repo)
    ).check_curation(actor_id="actor-1", effective_time=NOW)

    assert result.outcome is ResourceCatalogueAuthorityOutcome.DENIED
    assert result.authority_reference is None


def test_responsibility_scope_assignment_cannot_substitute_catalogue_scope():
    repo = FakeAssignments(
        [
            assignment(
                "wrong-scope",
                action=APPLICATION_CATALOGUE_CURATION_ACTION,
                scope="payments-team",
            )
        ]
    )

    result = ApplicationCatalogueCurationAuthorityAdapter(
        checker=CheckAuthority(assignments=repo)
    ).check_curation(actor_id="actor-1", effective_time=NOW)

    assert result.outcome is ApplicationCatalogueAuthorityOutcome.DENIED
    assert result.authority_reference is None


def test_ambiguous_catalogue_authority_fails_closed_unknown():
    repo = FakeAssignments(
        [
            assignment(
                "acc-curator-1",
                action=APPLICATION_CATALOGUE_CURATION_ACTION,
                scope=APPLICATION_CATALOGUE_AUTHORITY_SCOPE,
            ),
            assignment(
                "acc-curator-2",
                action=APPLICATION_CATALOGUE_CURATION_ACTION,
                scope=APPLICATION_CATALOGUE_AUTHORITY_SCOPE,
            ),
        ]
    )

    result = ApplicationCatalogueCurationAuthorityAdapter(
        checker=CheckAuthority(assignments=repo)
    ).check_curation(actor_id="actor-1", effective_time=NOW)

    assert result.outcome is ApplicationCatalogueAuthorityOutcome.UNKNOWN
    assert result.authority_reference is None
