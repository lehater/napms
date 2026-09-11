from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from napms.contexts.connectivity_requirements.application.declare import (
    DeclarationOutcome,
    DeclareConnectivityRequirement,
    DeclareRequirement,
)
from napms.contexts.connectivity_requirements.application.options import (
    DiscoverRequiredInteractions,
    DiscoverRequirementScopes,
    RequiredInteractionDiscoveryOutcome,
)
from napms.contexts.connectivity_requirements.application.ports import (
    ActiveRequirementSemanticConflict,
    InteractionOutcome,
    RequirementAuthorityCheck,
    RequirementInteractionCheck,
    RequirementInteractionPage,
    RequirementScopeOptions,
    TernaryOutcome,
)
from napms.contexts.connectivity_requirements.application.read import (
    GetConnectivityRequirement,
    ListConnectivityRequirements,
    RequirementDetailOutcome,
)
from napms.contexts.connectivity_requirements.application.retire import (
    RetireConnectivityRequirement,
    RetireRequirement,
    RetirementOutcome,
)
from napms.contexts.connectivity_requirements.application.set_applicability import (
    ApplicabilityMutationOutcome,
    SetConnectivityRequirementApplicability,
    SetRequirementApplicability,
)
from napms.contexts.connectivity_requirements.application.set_justification import (
    JustificationMutationOutcome,
    SetConnectivityRequirementJustification,
    SetRequirementJustification,
)
from napms.contexts.connectivity_requirements.domain.model import (
    ConnectivityRequirement,
    RequiredSemanticInteraction,
    RequirementApplicability,
    RequirementDeclarationProvenance,
    RequirementInvariantError,
    RequirementLifecycleState,
    RequirementSemanticKey,
)


NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
SOURCE = UUID(int=101)
DESTINATION = UUID(int=102)
OTHER = UUID(int=103)
DCS = UUID(int=201)
INTERACTION = RequiredSemanticInteraction(SOURCE, DESTINATION, DCS)
REQUIREMENT_ID = UUID(int=301)


class FakeAuthority:
    def __init__(
        self,
        outcome=TernaryOutcome.PERMITTED,
        reference="authority-1",
    ):
        self.outcome = outcome
        self.reference = reference
        self.calls = []

    def check(self, **kwargs):
        self.calls.append(kwargs)
        return RequirementAuthorityCheck(
            self.outcome,
            self.reference if self.outcome is TernaryOutcome.PERMITTED else None,
        )


class FakeCatalogue:
    def __init__(
        self,
        outcome=InteractionOutcome.VALID,
        identity=INTERACTION,
    ):
        self.outcome = outcome
        self.identity = identity
        self.calls = []

    def validate_required_interaction(self, **kwargs):
        self.calls.append(kwargs)
        return RequirementInteractionCheck(
            outcome=self.outcome,
            identity=(
                self.identity
                if self.outcome is InteractionOutcome.VALID
                else None
            ),
            provenance_reference=(
                "catalogue-1"
                if self.outcome is InteractionOutcome.VALID
                else None
            ),
        )


class MemoryRequirements:
    def __init__(self, values=()):
        self.values = {value.requirement_id: value for value in values}
        self.added = []
        self.saved = []
        self.commits = 0

    def find_active_by_semantic_key(self, key):
        for value in self.values.values():
            if (
                value.lifecycle_state is RequirementLifecycleState.ACTIVE
                and value.semantic_key == key
            ):
                return value
        return None

    def get_by_id(self, requirement_id):
        return self.values.get(requirement_id)

    def list_by_governance_scopes(self, scopes, *, offset, limit):
        rows = tuple(
            sorted(
                (
                    value
                    for value in self.values.values()
                    if value.governance_scope in scopes
                ),
                key=lambda value: value.requirement_id,
            )
        )
        return rows[offset : offset + limit]

    def add(self, requirement):
        if self.find_active_by_semantic_key(requirement.semantic_key) is not None:
            raise ActiveRequirementSemanticConflict()
        self.values[requirement.requirement_id] = requirement
        self.added.append(requirement)

    def save(self, requirement, *, expected_version):
        current = self.values[requirement.requirement_id]
        assert current.version == expected_version
        self.values[requirement.requirement_id] = requirement
        self.saved.append((requirement, expected_version))

    def commit(self):
        self.commits += 1


class ConflictThenWinnerRequirements(MemoryRequirements):
    def __init__(self, winner):
        super().__init__()
        self.winner = winner
        self.lookup_count = 0

    def find_active_by_semantic_key(self, key):
        self.lookup_count += 1
        if self.lookup_count == 1:
            return None
        return self.winner

    def add(self, requirement):
        raise ActiveRequirementSemanticConflict()


class FakeScopes:
    def __init__(self, permitted=("scope-a",), ambiguous=()):
        self.options = RequirementScopeOptions(permitted, ambiguous)
        self.calls = []

    def list_effective_declaration_scopes(self, **kwargs):
        self.calls.append(kwargs)
        return self.options

    def list_effective_read_scopes(self, **kwargs):
        self.calls.append(kwargs)
        return self.options


class FakeInteractionDiscovery:
    def __init__(self):
        self.calls = []

    def list_required_interactions(
        self,
        *,
        page,
        page_size,
        search=None,
    ):
        self.calls.append((page, page_size, search))
        return RequirementInteractionPage(
            interactions=(INTERACTION,),
            page=page,
            page_size=page_size,
            has_more=False,
        )


def semantic_key(scope="scope-a", dependent=SOURCE, interaction=INTERACTION):
    return RequirementSemanticKey(
        governance_scope=scope,
        dependent_component_deployment_id=dependent,
        required_interaction=interaction,
    )


def requirement(
    *,
    requirement_id=REQUIREMENT_ID,
    scope="scope-a",
    applicability=None,
    justification="Business dependency",
):
    applicability = applicability or RequirementApplicability.ongoing()
    return ConnectivityRequirement.declared(
        requirement_id=requirement_id,
        semantic_key=semantic_key(scope=scope),
        applicability=applicability,
        justification=justification,
        provenance=RequirementDeclarationProvenance(
            actor_id="actor-1",
            effective_time=NOW,
            governance_scope=scope,
            authority_reference="declare-authority",
            catalogue_reference="catalogue-1",
        ),
    )


def declare_command(
    *,
    scope="scope-a",
    dependent=SOURCE,
    interaction=INTERACTION,
    applicability=None,
    justification="Business dependency",
):
    return DeclareRequirement(
        governance_scope=scope,
        dependent_component_deployment_id=dependent,
        required_interaction=interaction,
        applicability=applicability or RequirementApplicability.ongoing(),
        justification=justification,
        actor_id="actor-1",
        effective_time=NOW,
    )


def test_absolute_applicability_is_half_open():
    start = NOW
    end = NOW + timedelta(hours=2)
    value = RequirementApplicability.absolute_window(start=start, end=end)

    assert value.applies_at(start)
    assert value.applies_at(start + timedelta(hours=1))
    assert not value.applies_at(end)
    assert not value.applies_at(start - timedelta(seconds=1))


def test_absolute_applicability_requires_aware_start_before_end():
    with pytest.raises(RequirementInvariantError):
        RequirementApplicability.absolute_window(
            start=datetime(2026, 9, 9, 12, 0),
            end=datetime(2026, 9, 9, 13, 0),
        )
    with pytest.raises(RequirementInvariantError):
        RequirementApplicability.absolute_window(
            start=NOW,
            end=NOW,
        )


def test_semantic_key_requires_dependent_to_participate():
    with pytest.raises(RequirementInvariantError):
        semantic_key(dependent=OTHER)


def test_requirement_mutations_preserve_identity_increment_version_and_audit():
    original = requirement()
    window = RequirementApplicability.absolute_window(
        start=NOW,
        end=NOW + timedelta(hours=4),
    )

    changed_window = original.with_applicability(
        applicability=window,
        actor_id="actor-2",
        effective_time=NOW + timedelta(minutes=1),
        authority_reference="window-authority",
    )
    changed_justification = changed_window.with_justification(
        justification="Updated reason",
        actor_id="actor-3",
        effective_time=NOW + timedelta(minutes=2),
        authority_reference="justification-authority",
    )
    retired = changed_justification.retired(
        actor_id="actor-4",
        effective_time=NOW + timedelta(minutes=3),
        authority_reference="retire-authority",
    )

    assert retired.requirement_id == original.requirement_id
    assert retired.semantic_key == original.semantic_key
    assert retired.version == 4
    assert len(retired.applicability_history) == 1
    assert len(retired.justification_history) == 1
    assert len(retired.lifecycle_history) == 1
    assert retired.lifecycle_state is RequirementLifecycleState.RETIRED


def test_retired_requirement_is_terminal():
    retired = requirement().retired(
        actor_id="actor-2",
        effective_time=NOW,
        authority_reference="retire-authority",
    )

    with pytest.raises(RequirementInvariantError):
        retired.with_justification(
            justification="Cannot change",
            actor_id="actor-2",
            effective_time=NOW,
            authority_reference="justify-authority",
        )


def test_business_audit_requires_aware_effective_time():
    with pytest.raises(RequirementInvariantError):
        requirement().with_justification(
            justification="Changed",
            actor_id="actor-2",
            effective_time=datetime(2026, 9, 9, 12, 0),
            authority_reference="justify-authority",
        )


def test_authorized_declaration_creates_requirement_only():
    authority = FakeAuthority()
    catalogue = FakeCatalogue()
    repo = MemoryRequirements()
    service = DeclareConnectivityRequirement(
        authority=authority,
        catalogue=catalogue,
        requirements=repo,
        id_factory=lambda: REQUIREMENT_ID,
    )

    result = service.execute(declare_command())

    assert result.outcome is DeclarationOutcome.DECLARED
    assert result.requirement.requirement_id == REQUIREMENT_ID
    assert result.requirement.lifecycle_state is RequirementLifecycleState.ACTIVE
    assert result.requirement.governance_scope == "scope-a"
    assert repo.commits == 1
    assert authority.calls[0]["scope"] == "scope-a"
    assert catalogue.calls[0]["identity"] == INTERACTION


def test_declaration_is_authority_first_and_denied_creates_nothing():
    authority = FakeAuthority(TernaryOutcome.DENIED)
    catalogue = FakeCatalogue()
    repo = MemoryRequirements()

    result = DeclareConnectivityRequirement(
        authority=authority,
        catalogue=catalogue,
        requirements=repo,
    ).execute(declare_command())

    assert result.outcome is DeclarationOutcome.AUTHORITY_DENIED
    assert catalogue.calls == []
    assert repo.values == {}


def test_permitted_without_authority_reference_fails_closed():
    authority = FakeAuthority(TernaryOutcome.PERMITTED, reference=None)
    repo = MemoryRequirements()

    result = DeclareConnectivityRequirement(
        authority=authority,
        catalogue=FakeCatalogue(),
        requirements=repo,
    ).execute(declare_command())

    assert result.outcome is DeclarationOutcome.AUTHORITY_UNKNOWN
    assert repo.values == {}


def test_invalid_or_unknown_interaction_creates_nothing():
    for outcome, expected in (
        (InteractionOutcome.INVALID, DeclarationOutcome.INTERACTION_INVALID),
        (InteractionOutcome.UNKNOWN, DeclarationOutcome.INTERACTION_UNKNOWN),
    ):
        repo = MemoryRequirements()
        result = DeclareConnectivityRequirement(
            authority=FakeAuthority(),
            catalogue=FakeCatalogue(outcome),
            requirements=repo,
        ).execute(declare_command())

        assert result.outcome is expected
        assert repo.values == {}


def test_dependent_outside_interaction_is_rejected():
    repo = MemoryRequirements()
    result = DeclareConnectivityRequirement(
        authority=FakeAuthority(),
        catalogue=FakeCatalogue(),
        requirements=repo,
    ).execute(declare_command(dependent=OTHER))

    assert result.outcome is DeclarationOutcome.DEPENDENT_INVALID
    assert repo.values == {}


def test_blank_justification_is_rejected_after_authority_and_catalogue():
    authority = FakeAuthority()
    catalogue = FakeCatalogue()
    repo = MemoryRequirements()

    result = DeclareConnectivityRequirement(
        authority=authority,
        catalogue=catalogue,
        requirements=repo,
    ).execute(declare_command(justification="   "))

    assert result.outcome is DeclarationOutcome.INPUT_INVALID
    assert authority.calls
    assert catalogue.calls
    assert repo.values == {}


def test_repeated_active_declaration_resolves_without_overwriting_properties():
    existing = requirement(
        applicability=RequirementApplicability.ongoing(),
        justification="Original",
    )
    repo = MemoryRequirements((existing,))
    requested_window = RequirementApplicability.absolute_window(
        start=NOW,
        end=NOW + timedelta(hours=1),
    )

    result = DeclareConnectivityRequirement(
        authority=FakeAuthority(),
        catalogue=FakeCatalogue(),
        requirements=repo,
    ).execute(
        declare_command(
            applicability=requested_window,
            justification="Different",
        )
    )

    assert result.outcome is DeclarationOutcome.RESOLVED
    assert result.requirement == existing
    assert result.requirement.justification == "Original"
    assert result.requirement.applicability == RequirementApplicability.ongoing()
    assert repo.commits == 0


def test_concurrent_declaration_resolves_winning_active_requirement():
    winner = requirement()
    repo = ConflictThenWinnerRequirements(winner)

    result = DeclareConnectivityRequirement(
        authority=FakeAuthority(),
        catalogue=FakeCatalogue(),
        requirements=repo,
        id_factory=lambda: UUID(int=999),
    ).execute(declare_command())

    assert result.outcome is DeclarationOutcome.RESOLVED
    assert result.requirement.requirement_id == winner.requirement_id


def test_applicability_mutation_uses_stored_scope_and_expected_version():
    original = requirement(scope="scope-a")
    repo = MemoryRequirements((original,))
    authority = FakeAuthority()
    target = RequirementApplicability.absolute_window(
        start=NOW,
        end=NOW + timedelta(hours=1),
    )

    result = SetConnectivityRequirementApplicability(
        authority=authority,
        requirements=repo,
    ).execute(
        SetRequirementApplicability(
            requirement_id=original.requirement_id,
            applicability=target,
            actor_id="actor-2",
            effective_time=NOW,
        )
    )

    assert result.outcome is ApplicabilityMutationOutcome.UPDATED
    assert result.requirement.version == 2
    assert authority.calls[0]["scope"] == "scope-a"
    assert repo.saved[0][1] == 1
    assert result.requirement.applicability_history[-1].authority_reference == "authority-1"


def test_same_applicability_is_noop_without_save_or_audit():
    original = requirement()
    repo = MemoryRequirements((original,))

    result = SetConnectivityRequirementApplicability(
        authority=FakeAuthority(),
        requirements=repo,
    ).execute(
        SetRequirementApplicability(
            original.requirement_id,
            original.applicability,
            "actor-2",
            NOW,
        )
    )

    assert result.outcome is ApplicabilityMutationOutcome.ALREADY_IN_REQUESTED_VALUE
    assert repo.saved == []
    assert result.requirement.applicability_history == ()


def test_retired_requirement_rejects_property_mutations():
    retired = requirement().retired(
        actor_id="actor-2",
        effective_time=NOW,
        authority_reference="retire-authority",
    )
    repo = MemoryRequirements((retired,))

    applicability = SetConnectivityRequirementApplicability(
        authority=FakeAuthority(),
        requirements=repo,
    ).execute(
        SetRequirementApplicability(
            retired.requirement_id,
            RequirementApplicability.ongoing(),
            "actor-3",
            NOW,
        )
    )
    justification = SetConnectivityRequirementJustification(
        authority=FakeAuthority(),
        requirements=repo,
    ).execute(
        SetRequirementJustification(
            retired.requirement_id,
            "New",
            "actor-3",
            NOW,
        )
    )

    assert applicability.outcome is ApplicabilityMutationOutcome.REQUIREMENT_RETIRED
    assert justification.outcome is JustificationMutationOutcome.REQUIREMENT_RETIRED
    assert repo.saved == []


def test_justification_update_and_blank_validation():
    original = requirement(justification="Original")
    repo = MemoryRequirements((original,))
    service = SetConnectivityRequirementJustification(
        authority=FakeAuthority(),
        requirements=repo,
    )

    updated = service.execute(
        SetRequirementJustification(
            original.requirement_id,
            "  Updated  ",
            "actor-2",
            NOW,
        )
    )
    invalid = service.execute(
        SetRequirementJustification(
            original.requirement_id,
            "   ",
            "actor-2",
            NOW,
        )
    )

    assert updated.outcome is JustificationMutationOutcome.UPDATED
    assert updated.requirement.justification == "Updated"
    assert invalid.outcome is JustificationMutationOutcome.INPUT_INVALID


def test_retirement_is_terminal_and_repeat_is_noop():
    original = requirement()
    repo = MemoryRequirements((original,))
    service = RetireConnectivityRequirement(
        authority=FakeAuthority(),
        requirements=repo,
    )

    first = service.execute(RetireRequirement(original.requirement_id, "actor-2", NOW))
    second = service.execute(RetireRequirement(original.requirement_id, "actor-2", NOW))

    assert first.outcome is RetirementOutcome.RETIRED
    assert first.requirement.lifecycle_state is RequirementLifecycleState.RETIRED
    assert second.outcome is RetirementOutcome.ALREADY_RETIRED
    assert len(second.requirement.lifecycle_history) == 1


def test_denied_mutation_changes_nothing():
    original = requirement()
    repo = MemoryRequirements((original,))

    result = RetireConnectivityRequirement(
        authority=FakeAuthority(TernaryOutcome.DENIED),
        requirements=repo,
    ).execute(RetireRequirement(original.requirement_id, "actor-2", NOW))

    assert result.outcome is RetirementOutcome.AUTHORITY_DENIED
    assert repo.get_by_id(original.requirement_id) == original
    assert repo.saved == []


def test_list_returns_only_permitted_scopes_and_reports_ambiguous_scopes():
    scope_a = requirement(requirement_id=UUID(int=401), scope="scope-a")
    scope_b = requirement(requirement_id=UUID(int=402), scope="scope-b")
    repo = MemoryRequirements((scope_a, scope_b))

    page = ListConnectivityRequirements(
        read_scopes=FakeScopes(
            permitted=("scope-a",),
            ambiguous=("scope-b",),
        ),
        requirements=repo,
    ).execute(
        actor_id="reader",
        effective_time=NOW,
    )

    assert tuple(item.requirement_id for item in page.requirements) == (
        scope_a.requirement_id,
    )
    assert page.ambiguous_scopes == ("scope-b",)


def test_detail_checks_read_authority_against_stored_scope():
    original = requirement(scope="scope-a")
    authority = FakeAuthority()
    result = GetConnectivityRequirement(
        authority=authority,
        requirements=MemoryRequirements((original,)),
    ).execute(
        requirement_id=original.requirement_id,
        actor_id="reader",
        effective_time=NOW,
    )

    assert result.outcome is RequirementDetailOutcome.FOUND
    assert authority.calls[0]["scope"] == "scope-a"
    assert result.read_authority_reference == "authority-1"


def test_denied_detail_returns_no_requirement_data():
    original = requirement()
    result = GetConnectivityRequirement(
        authority=FakeAuthority(TernaryOutcome.DENIED),
        requirements=MemoryRequirements((original,)),
    ).execute(
        requirement_id=original.requirement_id,
        actor_id="reader",
        effective_time=NOW,
    )

    assert result.outcome is RequirementDetailOutcome.AUTHORITY_DENIED
    assert result.requirement is None


def test_required_interaction_discovery_is_authority_first():
    catalogue = FakeInteractionDiscovery()
    denied = DiscoverRequiredInteractions(
        authority=FakeAuthority(TernaryOutcome.DENIED),
        catalogue=catalogue,
    ).execute(
        actor_id="actor-1",
        scope="scope-a",
        effective_time=NOW,
        search="orders",
    )

    assert denied.outcome is RequiredInteractionDiscoveryOutcome.AUTHORITY_DENIED
    assert catalogue.calls == []

    permitted = DiscoverRequiredInteractions(
        authority=FakeAuthority(),
        catalogue=catalogue,
    ).execute(
        actor_id="actor-1",
        scope="scope-a",
        effective_time=NOW,
        search="orders",
    )
    assert permitted.outcome is RequiredInteractionDiscoveryOutcome.AVAILABLE
    assert permitted.page.interactions == (INTERACTION,)
    assert catalogue.calls == [(1, 50, "orders")]


def test_declaration_scope_discovery_delegates_to_authority_port():
    scopes = FakeScopes(
        permitted=("scope-a", "scope-b"),
        ambiguous=("scope-c",),
    )
    result = DiscoverRequirementScopes(discovery=scopes).execute(
        actor_id="actor-1",
        effective_time=NOW,
    )

    assert result.permitted_scopes == ("scope-a", "scope-b")
    assert result.ambiguous_scopes == ("scope-c",)
