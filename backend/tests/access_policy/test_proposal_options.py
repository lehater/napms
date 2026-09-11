from datetime import datetime, timezone
from uuid import UUID

from napms.contexts.access_policy.application.ports import (
    AuthorityCheck,
    ProposalInteractionPage,
    ProposalScopeOptions,
    RuleSemanticIdentity,
    TernaryOutcome,
)
from napms.contexts.access_policy.application.proposal_options import (
    DiscoverProposalInteractions,
    DiscoverProposalScopes,
    ProposalInteractionDiscoveryOutcome,
)


NOW = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)


class FakeScopeDiscovery:
    def list_effective_proposal_scopes(self, **kwargs):
        return ProposalScopeOptions(("scope-a",), ("scope-b",))


class FakeAuthority:
    def __init__(self, outcome, reference="authority-1"):
        self.outcome = outcome
        self.reference = reference

    def check(self, **kwargs):
        return AuthorityCheck(self.outcome, self.reference)


class FakeCatalogue:
    def __init__(self):
        self.called = False
        self.search = None

    def list_directed_interactions(self, *, page, page_size, search=None):
        self.called = True
        self.search = search
        return ProposalInteractionPage(
            identities=(
                RuleSemanticIdentity(UUID(int=1), UUID(int=2), UUID(int=3)),
            ),
            page=page,
            page_size=page_size,
            has_more=False,
        )


def test_scope_use_case_returns_actor_specific_discovery():
    result = DiscoverProposalScopes(authority=FakeScopeDiscovery()).execute(
        actor_id="actor-1",
        effective_time=NOW,
    )
    assert result.permitted_scopes == ("scope-a",)
    assert result.ambiguous_scopes == ("scope-b",)


def test_interaction_discovery_checks_authority_before_catalogue_data():
    catalogue = FakeCatalogue()
    result = DiscoverProposalInteractions(
        authority=FakeAuthority(TernaryOutcome.DENIED, None),
        catalogue=catalogue,
    ).execute(
        actor_id="actor-1",
        scope="scope-a",
        effective_time=NOW,
    )

    assert result.outcome is ProposalInteractionDiscoveryOutcome.AUTHORITY_DENIED
    assert result.page is None
    assert catalogue.called is False


def test_permitted_interaction_discovery_returns_candidate_page():
    catalogue = FakeCatalogue()
    result = DiscoverProposalInteractions(
        authority=FakeAuthority(TernaryOutcome.PERMITTED),
        catalogue=catalogue,
    ).execute(
        actor_id="actor-1",
        scope="scope-a",
        effective_time=NOW,
        page=1,
        page_size=50,
    )

    assert result.outcome is ProposalInteractionDiscoveryOutcome.AVAILABLE
    assert result.page is not None
    assert result.page.identities[0].dcs_contract_revision_id == UUID(int=3)



def test_permitted_interaction_discovery_forwards_search_after_authority():
    catalogue = FakeCatalogue()
    result = DiscoverProposalInteractions(
        authority=FakeAuthority(TernaryOutcome.PERMITTED),
        catalogue=catalogue,
    ).execute(
        actor_id="actor-1",
        scope="scope-a",
        effective_time=NOW,
        search="orders",
    )

    assert result.outcome is ProposalInteractionDiscoveryOutcome.AVAILABLE
    assert catalogue.search == "orders"
