from datetime import datetime, timedelta, timezone
from uuid import UUID

from napms.contexts.access_policy.infrastructure.integrations.requirement_policy_alignment import (
    AccessPolicyAlignmentAdapter,
)
from napms.contexts.access_policy.application.ports import AccessRulePersistenceError
from napms.contexts.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    EffectiveWindow,
    OperationalState,
    ProposalProvenance,
    RuleSemanticIdentity,
)
from napms.contexts.connectivity_requirements.infrastructure.integrations.requirement_policy_alignment import (
    ConnectivityRequirementsAlignmentAdapter,
)
from napms.contexts.connectivity_requirements.application.ports import (
    RequirementAuthorityCheck,
    RequirementAuthorityAction,
    RequirementPersistenceError,
    RequirementScopeOptions,
    TernaryOutcome,
)
from napms.contexts.connectivity_requirements.application.read import (
    GetAuthorizedRequirement,
    ListConnectivityRequirements,
)
from napms.contexts.connectivity_requirements.domain.model import (
    ConnectivityRequirement,
    RequiredSemanticInteraction,
    RequirementApplicability,
    RequirementDeclarationProvenance,
    RequirementSemanticKey,
)
from napms.workflows.requirement_policy_alignment.application.model import (
    AlignmentApplicabilityKind,
    AlignmentRequirementLifecycle,
    AlignmentSemanticIdentity,
)
from napms.workflows.requirement_policy_alignment.application.ports import (
    PolicyCoverageOutcome,
    RequirementAlignmentListOutcome,
    RequirementAlignmentReadOutcome,
)


NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
SOURCE = UUID(int=101)
DESTINATION = UUID(int=102)
DCS = UUID(int=103)
REQ_ID = UUID(int=104)
RULE_ID = UUID(int=105)
ALIGNMENT_IDENTITY = AlignmentSemanticIdentity(SOURCE, DESTINATION, DCS)


class FakeReadScopes:
    def __init__(self, permitted=("requirements-scope",), ambiguous=()):
        self.permitted = permitted
        self.ambiguous = ambiguous

    def list_effective_read_scopes(self, **kwargs):
        return RequirementScopeOptions(
            permitted_scopes=self.permitted,
            ambiguous_scopes=self.ambiguous,
        )


class FakeRequirementAuthority:
    def __init__(
        self,
        outcome=TernaryOutcome.PERMITTED,
        reference="requirement-read-authority",
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


class RequirementRepository:
    def __init__(self, value=None, *, fail=False, values=None):
        self.value = value
        self.values = tuple(values or (() if value is None else (value,)))
        self.fail = fail

    def get_by_id(self, requirement_id):
        if self.fail:
            raise RequirementPersistenceError()
        return next(
            (item for item in self.values if item.requirement_id == requirement_id),
            None,
        )

    def list_by_governance_scopes(self, scopes, *, offset, limit):
        if self.fail:
            raise RequirementPersistenceError()
        rows = tuple(
            item for item in self.values if item.governance_scope in scopes
        )
        return rows[offset : offset + limit]


class RuleRepository:
    def __init__(self, rule=None, *, fail=False, mismatched=None):
        self.rule = rule
        self.fail = fail
        self.mismatched = mismatched
        self.calls = []

    def find_by_identity(self, identity):
        self.calls.append(identity)
        if self.fail:
            raise AccessRulePersistenceError()
        if self.mismatched is not None:
            return self.mismatched
        if self.rule and self.rule.semantic_identity == identity:
            return self.rule
        return None


def requirement(*, applicability=None):
    interaction = RequiredSemanticInteraction(SOURCE, DESTINATION, DCS)
    key = RequirementSemanticKey(
        governance_scope="requirements-scope",
        dependent_component_deployment_id=SOURCE,
        required_interaction=interaction,
    )
    return ConnectivityRequirement.declared(
        requirement_id=REQ_ID,
        semantic_key=key,
        applicability=applicability or RequirementApplicability.ongoing(),
        justification="Business need",
        provenance=RequirementDeclarationProvenance(
            actor_id="declarer",
            effective_time=NOW,
            governance_scope="requirements-scope",
            authority_reference="declare-authority",
            catalogue_reference="catalogue-1",
        ),
    )


def rule(*, scope="policy-scope", window=None, inactive=False, identity=None):
    semantic_identity = identity or RuleSemanticIdentity(SOURCE, DESTINATION, DCS)
    value = AccessRule.materialized_from_allowed_decision(
        rule_id=RULE_ID,
        semantic_identity=semantic_identity,
        decision=DecisionReference(
            semantic_identity,
            ConnectivityDecisionResult.ALLOWED,
            "decision-1",
        ),
        proposal_provenance=ProposalProvenance(
            actor_id="proposer",
            authority_scope=scope,
            effective_time=NOW,
            authority_reference="proposal-authority",
            catalogue_reference="catalogue-1",
        ),
    )
    if window is not None:
        value = value.with_effective_window(
            window=window,
            actor_id="window-admin",
            effective_time=NOW,
            authority_reference="window-authority",
        )
    if inactive:
        value = value.with_operational_state(
            target_state=OperationalState.INACTIVE,
            actor_id="state-admin",
            effective_time=NOW,
            authority_reference="state-authority",
        )
    return value


def cr_adapter(repository, authority=None, read_scopes=None):
    authority = authority or FakeRequirementAuthority()
    read_scopes = read_scopes or FakeReadScopes()
    return (
        ConnectivityRequirementsAlignmentAdapter(
            reader=GetAuthorizedRequirement(
                authority=authority,
                requirements=repository,
            ),
            lister=ListConnectivityRequirements(
                read_scopes=read_scopes,
                requirements=repository,
            ),
        ),
        authority,
    )


def test_requirement_adapter_maps_authorized_requirement_and_checks_only_read():
    value = requirement(
        applicability=RequirementApplicability.absolute_window(
            start=NOW,
            end=NOW + timedelta(hours=2),
        )
    )
    adapter, authority = cr_adapter(RequirementRepository(value))

    result = adapter.get_for_alignment(
        requirement_id=REQ_ID,
        actor_id="owner",
        as_of=NOW,
    )

    assert result.outcome is RequirementAlignmentReadOutcome.FOUND
    assert result.read_authority_reference == "requirement-read-authority"
    assert result.snapshot.requirement_id == REQ_ID
    assert result.snapshot.semantic_identity == ALIGNMENT_IDENTITY
    assert result.snapshot.lifecycle is AlignmentRequirementLifecycle.ACTIVE
    assert result.snapshot.applicability.kind is AlignmentApplicabilityKind.ABSOLUTE_WINDOW
    assert authority.calls == [
        {
            "actor_id": "owner",
            "action": RequirementAuthorityAction.READ,
            "scope": "requirements-scope",
            "effective_time": NOW,
        }
    ]


def test_requirement_adapter_denied_returns_no_snapshot():
    adapter, _ = cr_adapter(
        RequirementRepository(requirement()),
        FakeRequirementAuthority(TernaryOutcome.DENIED),
    )

    result = adapter.get_for_alignment(
        requirement_id=REQ_ID,
        actor_id="owner",
        as_of=NOW,
    )

    assert result.outcome is RequirementAlignmentReadOutcome.AUTHORITY_DENIED
    assert result.snapshot is None


def test_requirement_adapter_persistence_failure_is_unavailable():
    adapter, _ = cr_adapter(RequirementRepository(fail=True))

    result = adapter.get_for_alignment(
        requirement_id=REQ_ID,
        actor_id="owner",
        as_of=NOW,
    )

    assert result.outcome is RequirementAlignmentReadOutcome.UNAVAILABLE


def test_policy_adapter_ignores_governance_scope_for_exact_semantic_match():
    value = rule(scope="different-policy-scope")
    adapter = AccessPolicyAlignmentAdapter(rules=RuleRepository(value))

    result = adapter.check_exact_coverage(
        semantic_identity=ALIGNMENT_IDENTITY,
        as_of=NOW,
    )

    assert result is PolicyCoverageOutcome.COVERED


def test_policy_adapter_missing_rule_is_uncovered():
    result = AccessPolicyAlignmentAdapter(
        rules=RuleRepository()
    ).check_exact_coverage(
        semantic_identity=ALIGNMENT_IDENTITY,
        as_of=NOW,
    )

    assert result is PolicyCoverageOutcome.UNCOVERED


def test_policy_adapter_inactive_or_outside_window_is_uncovered():
    ended = EffectiveWindow(
        NOW - timedelta(hours=2),
        NOW,
    )
    for value in (rule(inactive=True), rule(window=ended)):
        result = AccessPolicyAlignmentAdapter(
            rules=RuleRepository(value)
        ).check_exact_coverage(
            semantic_identity=ALIGNMENT_IDENTITY,
            as_of=NOW,
        )
        assert result is PolicyCoverageOutcome.UNCOVERED


def test_policy_adapter_effective_window_is_half_open():
    window = EffectiveWindow(NOW, NOW + timedelta(hours=1))
    adapter = AccessPolicyAlignmentAdapter(rules=RuleRepository(rule(window=window)))

    assert adapter.check_exact_coverage(
        semantic_identity=ALIGNMENT_IDENTITY,
        as_of=NOW,
    ) is PolicyCoverageOutcome.COVERED
    assert adapter.check_exact_coverage(
        semantic_identity=ALIGNMENT_IDENTITY,
        as_of=NOW + timedelta(hours=1),
    ) is PolicyCoverageOutcome.UNCOVERED


def test_policy_adapter_persistence_failure_is_unknown():
    result = AccessPolicyAlignmentAdapter(
        rules=RuleRepository(fail=True)
    ).check_exact_coverage(
        semantic_identity=ALIGNMENT_IDENTITY,
        as_of=NOW,
    )

    assert result is PolicyCoverageOutcome.UNKNOWN


def test_policy_adapter_contract_violation_is_unknown():
    wrong = rule(
        identity=RuleSemanticIdentity(UUID(int=999), DESTINATION, DCS)
    )
    result = AccessPolicyAlignmentAdapter(
        rules=RuleRepository(mismatched=wrong)
    ).check_exact_coverage(
        semantic_identity=ALIGNMENT_IDENTITY,
        as_of=NOW,
    )

    assert result is PolicyCoverageOutcome.UNKNOWN



def test_requirement_adapter_lists_only_authorized_scopes_for_alignment():
    visible = requirement()
    hidden_interaction = RequiredSemanticInteraction(
        UUID(int=201),
        UUID(int=202),
        UUID(int=203),
    )
    hidden = ConnectivityRequirement.declared(
        requirement_id=UUID(int=204),
        semantic_key=RequirementSemanticKey(
            governance_scope="hidden-scope",
            dependent_component_deployment_id=UUID(int=201),
            required_interaction=hidden_interaction,
        ),
        applicability=RequirementApplicability.ongoing(),
        justification="Hidden need",
        provenance=RequirementDeclarationProvenance(
            actor_id="declarer",
            effective_time=NOW,
            governance_scope="hidden-scope",
            authority_reference="declare-hidden",
            catalogue_reference="catalogue-hidden",
        ),
    )
    adapter, _ = cr_adapter(
        RequirementRepository(values=(visible, hidden)),
        read_scopes=FakeReadScopes(
            permitted=("requirements-scope",),
            ambiguous=("hidden-scope",),
        ),
    )

    result = adapter.list_for_alignment(
        actor_id="owner",
        as_of=NOW,
        page=1,
        page_size=50,
    )

    assert result.outcome is RequirementAlignmentListOutcome.AVAILABLE
    assert tuple(
        item.requirement_id for item in result.page.snapshots
    ) == (REQ_ID,)
    assert result.page.ambiguous_scopes == ("hidden-scope",)
