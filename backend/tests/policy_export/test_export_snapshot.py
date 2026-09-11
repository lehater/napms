from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from napms.access_policy.application.select_effective_policy import (
    EffectivePolicySelectionOutcome,
    EffectivePolicySelectionResult,
)
from napms.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    EffectiveWindow,
    OperationalState,
    ProposalProvenance,
    RuleSemanticIdentity,
)
from napms.policy_export.application.export_snapshot import (
    AssembleExportSnapshot,
    SnapshotAssemblyOutcome,
    SnapshotFactSource,
    SnapshotFailureCategory,
)
from napms.policy_export.application.ports import (
    ApplicationProjectionFact,
    ApplicationProjectionOutcome,
    EndpointRealization,
    ResourceRealizationFact,
    ResourceRealizationOutcome,
    ResourceReference,
)


AS_OF = datetime(2026, 9, 12, 12, 0, tzinfo=timezone.utc)
NOW = datetime(2026, 9, 8, 18, 0, tzinfo=timezone.utc)


def active_rule(*, rule_id=1, scope="scope-1"):
    identity = RuleSemanticIdentity(
        UUID(int=rule_id),
        UUID(int=rule_id + 100),
        UUID(int=rule_id + 200),
    )
    return AccessRule.materialized_from_allowed_decision(
        rule_id=UUID(int=rule_id),
        semantic_identity=identity,
        decision=DecisionReference(
            subject=identity,
            result=ConnectivityDecisionResult.ALLOWED,
            decision_id=f"decision-{rule_id}",
        ),
        proposal_provenance=ProposalProvenance(
            actor_id="proposer",
            authority_scope=scope,
            effective_time=NOW,
            authority_reference="proposal-auth",
            catalogue_reference="proposal-catalogue",
        ),
    )


def inactive(rule):
    return rule.with_operational_state(
        target_state=OperationalState.INACTIVE,
        actor_id="state-admin",
        effective_time=NOW,
        authority_reference="state-auth",
    )


def out_of_window(rule):
    return rule.with_effective_window(
        window=EffectiveWindow(
            AS_OF - timedelta(hours=2),
            AS_OF - timedelta(hours=1),
        ),
        actor_id="window-admin",
        effective_time=NOW,
        authority_reference="window-auth",
    )


def selected(
    rules=(),
    *,
    outcome=EffectivePolicySelectionOutcome.SELECTED,
    scope="scope-1",
    as_of=AS_OF,
    authority_reference="read-auth",
):
    return EffectivePolicySelectionResult(
        outcome=outcome,
        scope=scope,
        as_of=as_of,
        rules=tuple(rules),
        authority_reference=authority_reference,
    )


def ref(value):
    return ResourceReference(value)


def application_fact(
    rule,
    *,
    outcome=ApplicationProjectionOutcome.RESOLVED,
    subject=None,
    as_of=AS_OF,
    source=("src-1",),
    destination=("dst-1",),
    payload=b"opaque-dcs-projection",
    fact_reference="acc-fact-1",
    validity_reference="acc-validity-1",
    provenance_reference="acc-provenance-1",
):
    return ApplicationProjectionFact(
        outcome=outcome,
        subject=rule.semantic_identity if subject is None else subject,
        as_of=as_of,
        source_resource_references=tuple(ref(value) for value in source),
        destination_resource_references=tuple(ref(value) for value in destination),
        dcs_projection_payload=payload,
        fact_reference=fact_reference,
        validity_reference=validity_reference,
        provenance_reference=provenance_reference,
    )


def resource_fact(
    reference,
    *,
    outcome=ResourceRealizationOutcome.RESOLVED,
    returned_reference=None,
    as_of=AS_OF,
    endpoints=None,
    fact_reference="rc-fact-1",
    validity_reference="rc-validity-1",
    provenance_reference="rc-provenance-1",
):
    resource_reference = ref(reference)
    if endpoints is None:
        endpoints = (
            EndpointRealization(
                endpoint_reference=f"endpoint-{reference}",
                technical_address=f"198.51.100.{len(reference)}",
            ),
        )
    return ResourceRealizationFact(
        outcome=outcome,
        resource_reference=(
            resource_reference
            if returned_reference is None
            else ref(returned_reference)
        ),
        as_of=as_of,
        endpoint_realizations=tuple(endpoints),
        fact_reference=fact_reference,
        validity_reference=validity_reference,
        provenance_reference=provenance_reference,
    )


class FakeApplicationCatalogue:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def resolve_projection(self, *, subject, as_of):
        self.calls.append((subject, as_of))
        return self.responses[subject]


class FakeResourceCatalogue:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def resolve_realization(self, *, resource_reference, as_of):
        self.calls.append((resource_reference, as_of))
        return self.responses[resource_reference]


def assembler(application_responses, resource_responses):
    application = FakeApplicationCatalogue(application_responses)
    resources = FakeResourceCatalogue(resource_responses)
    return (
        AssembleExportSnapshot(
            application_catalogue=application,
            resource_catalogue=resources,
        ),
        application,
        resources,
    )


def test_complete_snapshot_is_immutable_and_preserves_correlations():
    rule = active_rule()
    app = application_fact(
        rule,
        source=("src-a", "src-b"),
        destination=("dst-a",),
        payload=b"complete-opaque-dcs-payload",
    )
    service, application, resources = assembler(
        {rule.semantic_identity: app},
        {
            ref("src-a"): resource_fact("src-a"),
            ref("src-b"): resource_fact("src-b"),
            ref("dst-a"): resource_fact("dst-a"),
        },
    )

    result = service.execute(selected([rule]))

    assert result.outcome is SnapshotAssemblyOutcome.SUCCESS
    assert result.diagnostics == ()
    assert result.snapshot.scope == "scope-1"
    assert result.snapshot.as_of == AS_OF
    assert result.snapshot.authority_reference == "read-auth"
    assert len(result.snapshot.items) == 1

    item = result.snapshot.items[0]
    assert item.rule is rule
    assert item.rule.decision.decision_id == "decision-1"
    assert item.rule.governance_scope == "scope-1"
    assert item.application_projection == app
    assert item.application_projection.dcs_projection_payload == (
        b"complete-opaque-dcs-payload"
    )
    assert tuple(x.resource_reference for x in item.source_realizations) == (
        ref("src-a"),
        ref("src-b"),
    )
    assert tuple(x.resource_reference for x in item.destination_realizations) == (
        ref("dst-a"),
    )
    assert application.calls == [(rule.semantic_identity, AS_OF)]
    assert resources.calls == [
        (ref("src-a"), AS_OF),
        (ref("src-b"), AS_OF),
        (ref("dst-a"), AS_OF),
    ]

    with pytest.raises(FrozenInstanceError):
        result.snapshot.scope = "other"
    with pytest.raises(FrozenInstanceError):
        item.source_realizations[0].fact_reference = "other"


def test_empty_selection_is_successful_without_catalogue_calls():
    service, application, resources = assembler({}, {})

    result = service.execute(selected([]))

    assert result.outcome is SnapshotAssemblyOutcome.SUCCESS
    assert result.snapshot.items == ()
    assert application.calls == []
    assert resources.calls == []


@pytest.mark.parametrize(
    "outcome",
    [
        EffectivePolicySelectionOutcome.AUTHORITY_DENIED,
        EffectivePolicySelectionOutcome.AUTHORITY_UNKNOWN,
    ],
)
def test_unavailable_selection_never_calls_catalogues(outcome):
    service, application, resources = assembler({}, {})

    result = service.execute(
        selected(
            [active_rule()],
            outcome=outcome,
            authority_reference=None,
        )
    )

    assert result.outcome is SnapshotAssemblyOutcome.SELECTION_UNAVAILABLE
    assert result.snapshot is None
    assert result.diagnostics[0].source is SnapshotFactSource.EFFECTIVE_SELECTION
    assert application.calls == []
    assert resources.calls == []


@pytest.mark.parametrize("authority_reference", [None, ""])
def test_selected_without_authority_provenance_is_unavailable(authority_reference):
    service, application, resources = assembler({}, {})

    result = service.execute(
        selected([active_rule()], authority_reference=authority_reference)
    )

    assert result.outcome is SnapshotAssemblyOutcome.SELECTION_UNAVAILABLE
    assert result.snapshot is None
    assert application.calls == []
    assert resources.calls == []


def test_scope_drift_fails_before_catalogue_access():
    rule = active_rule(scope="scope-2")
    service, application, resources = assembler({}, {})

    result = service.execute(selected([rule], scope="scope-1"))

    assert result.outcome is SnapshotAssemblyOutcome.INCOMPLETE
    diagnostic = result.diagnostics[0]
    assert diagnostic.rule_id == rule.rule_id
    assert diagnostic.source is SnapshotFactSource.EFFECTIVE_SELECTION
    assert diagnostic.category is SnapshotFailureCategory.CORRELATION_MISMATCH
    assert application.calls == []
    assert resources.calls == []


@pytest.mark.parametrize(
    "rule",
    [
        inactive(active_rule(rule_id=2)),
        out_of_window(active_rule(rule_id=3)),
    ],
)
def test_non_effective_rule_cannot_be_reintroduced(rule):
    service, application, resources = assembler({}, {})

    result = service.execute(selected([rule]))

    assert result.outcome is SnapshotAssemblyOutcome.INCOMPLETE
    assert result.snapshot is None
    assert result.diagnostics[0].category is (
        SnapshotFailureCategory.NON_EFFECTIVE_SELECTION
    )
    assert application.calls == []
    assert resources.calls == []


def test_naive_as_of_fails_before_catalogue_access():
    service, application, resources = assembler({}, {})

    result = service.execute(
        selected([active_rule()], as_of=AS_OF.replace(tzinfo=None))
    )

    assert result.outcome is SnapshotAssemblyOutcome.INCOMPLETE
    assert result.diagnostics[0].category is SnapshotFailureCategory.INVALID
    assert application.calls == []
    assert resources.calls == []


def test_duplicate_rule_fails_before_catalogue_access():
    rule = active_rule()
    service, application, resources = assembler({}, {})

    result = service.execute(selected([rule, rule]))

    assert result.outcome is SnapshotAssemblyOutcome.INCOMPLETE
    assert result.diagnostics[0].category is SnapshotFailureCategory.INVALID
    assert application.calls == []
    assert resources.calls == []


@pytest.mark.parametrize(
    "outcome,category",
    [
        (ApplicationProjectionOutcome.MISSING, SnapshotFailureCategory.MISSING),
        (ApplicationProjectionOutcome.INVALID, SnapshotFailureCategory.INVALID),
        (ApplicationProjectionOutcome.UNKNOWN, SnapshotFailureCategory.UNKNOWN),
    ],
)
def test_application_projection_failure_short_circuits_resource_lookup(
    outcome, category
):
    rule = active_rule()
    service, application, resources = assembler(
        {rule.semantic_identity: ApplicationProjectionFact(outcome=outcome)},
        {},
    )

    result = service.execute(selected([rule]))

    assert result.outcome is SnapshotAssemblyOutcome.INCOMPLETE
    diagnostic = result.diagnostics[0]
    assert diagnostic.rule_id == rule.rule_id
    assert diagnostic.source is (
        SnapshotFactSource.APPLICATION_COMMUNICATION_CATALOGUE
    )
    assert diagnostic.category is category
    assert len(application.calls) == 1
    assert resources.calls == []


@pytest.mark.parametrize(
    "fact_factory",
    [
        lambda rule: application_fact(
            rule,
            subject=RuleSemanticIdentity(UUID(int=9), UUID(int=10), UUID(int=11)),
        ),
        lambda rule: application_fact(rule, as_of=AS_OF + timedelta(seconds=1)),
    ],
)
def test_application_projection_exact_correlation_is_required(fact_factory):
    rule = active_rule()
    service, _, resources = assembler(
        {rule.semantic_identity: fact_factory(rule)},
        {},
    )

    result = service.execute(selected([rule]))

    assert result.outcome is SnapshotAssemblyOutcome.INCOMPLETE
    assert any(
        d.category is SnapshotFailureCategory.CORRELATION_MISMATCH
        for d in result.diagnostics
    )
    assert resources.calls == []


@pytest.mark.parametrize(
    "fact_factory",
    [
        lambda rule: application_fact(rule, source=()),
        lambda rule: application_fact(rule, destination=()),
        lambda rule: application_fact(rule, source=("same", "same")),
        lambda rule: application_fact(rule, destination=("same", "same")),
        lambda rule: application_fact(rule, payload=b""),
        lambda rule: application_fact(rule, fact_reference=None),
        lambda rule: application_fact(rule, validity_reference=None),
        lambda rule: application_fact(rule, provenance_reference=None),
    ],
)
def test_resolved_application_fact_requires_complete_evidence(fact_factory):
    rule = active_rule()
    service, _, resources = assembler(
        {rule.semantic_identity: fact_factory(rule)},
        {},
    )

    result = service.execute(selected([rule]))

    assert result.outcome is SnapshotAssemblyOutcome.INCOMPLETE
    assert any(
        d.category is SnapshotFailureCategory.INVALID
        for d in result.diagnostics
    )
    assert resources.calls == []


@pytest.mark.parametrize(
    "outcome,category",
    [
        (ResourceRealizationOutcome.MISSING, SnapshotFailureCategory.MISSING),
        (ResourceRealizationOutcome.STALE, SnapshotFailureCategory.STALE),
        (ResourceRealizationOutcome.UNKNOWN, SnapshotFailureCategory.UNKNOWN),
    ],
)
def test_resource_failure_prevents_success(outcome, category):
    rule = active_rule()
    service, _, _ = assembler(
        {rule.semantic_identity: application_fact(rule)},
        {
            ref("src-1"): resource_fact("src-1", outcome=outcome),
            ref("dst-1"): resource_fact("dst-1"),
        },
    )

    result = service.execute(selected([rule]))

    assert result.outcome is SnapshotAssemblyOutcome.INCOMPLETE
    diagnostic = next(d for d in result.diagnostics if d.reference == "src-1")
    assert diagnostic.rule_id == rule.rule_id
    assert diagnostic.source is SnapshotFactSource.RESOURCE_CATALOGUE
    assert diagnostic.category is category


@pytest.mark.parametrize(
    "fact_factory",
    [
        lambda: resource_fact("src-1", returned_reference="other"),
        lambda: resource_fact("src-1", as_of=AS_OF + timedelta(seconds=1)),
    ],
)
def test_resource_exact_correlation_is_required(fact_factory):
    rule = active_rule()
    service, _, _ = assembler(
        {rule.semantic_identity: application_fact(rule)},
        {
            ref("src-1"): fact_factory(),
            ref("dst-1"): resource_fact("dst-1"),
        },
    )

    result = service.execute(selected([rule]))

    assert result.outcome is SnapshotAssemblyOutcome.INCOMPLETE
    diagnostic = next(d for d in result.diagnostics if d.reference == "src-1")
    assert diagnostic.category is SnapshotFailureCategory.CORRELATION_MISMATCH


@pytest.mark.parametrize(
    "fact_factory",
    [
        lambda: resource_fact("src-1", endpoints=()),
        lambda: resource_fact(
            "src-1",
            endpoints=(EndpointRealization("", "198.51.100.1"),),
        ),
        lambda: resource_fact(
            "src-1",
            endpoints=(EndpointRealization("endpoint-1", ""),),
        ),
        lambda: resource_fact("src-1", fact_reference=None),
        lambda: resource_fact("src-1", validity_reference=None),
        lambda: resource_fact("src-1", provenance_reference=None),
    ],
)
def test_resolved_resource_fact_requires_complete_evidence(fact_factory):
    rule = active_rule()
    service, _, _ = assembler(
        {rule.semantic_identity: application_fact(rule)},
        {
            ref("src-1"): fact_factory(),
            ref("dst-1"): resource_fact("dst-1"),
        },
    )

    result = service.execute(selected([rule]))

    assert result.outcome is SnapshotAssemblyOutcome.INCOMPLETE
    diagnostic = next(d for d in result.diagnostics if d.reference == "src-1")
    assert diagnostic.category is SnapshotFailureCategory.INVALID


def test_one_incomplete_rule_prevents_success_without_silent_drop():
    first = active_rule(rule_id=1)
    second = active_rule(rule_id=2)
    service, application, resources = assembler(
        {
            first.semantic_identity: application_fact(
                first,
                source=("src-first",),
                destination=("dst-first",),
            ),
            second.semantic_identity: ApplicationProjectionFact(
                outcome=ApplicationProjectionOutcome.MISSING
            ),
        },
        {
            ref("src-first"): resource_fact("src-first"),
            ref("dst-first"): resource_fact("dst-first"),
        },
    )

    result = service.execute(selected([first, second]))

    assert result.outcome is SnapshotAssemblyOutcome.INCOMPLETE
    assert result.snapshot is None
    assert {call[0] for call in application.calls} == {
        first.semantic_identity,
        second.semantic_identity,
    }
    assert any(
        d.rule_id == second.rule_id
        and d.category is SnapshotFailureCategory.MISSING
        for d in result.diagnostics
    )
    assert resources.calls


def test_shared_resource_is_resolved_once_per_snapshot_attempt():
    first = active_rule(rule_id=1)
    second = active_rule(rule_id=2)
    shared = ref("shared")
    service, _, resources = assembler(
        {
            first.semantic_identity: application_fact(
                first,
                source=("shared",),
                destination=("dst-first",),
            ),
            second.semantic_identity: application_fact(
                second,
                source=("shared",),
                destination=("dst-second",),
            ),
        },
        {
            shared: resource_fact("shared"),
            ref("dst-first"): resource_fact("dst-first"),
            ref("dst-second"): resource_fact("dst-second"),
        },
    )

    result = service.execute(selected([first, second]))

    assert result.outcome is SnapshotAssemblyOutcome.SUCCESS
    assert len(result.snapshot.items) == 2
    assert resources.calls.count((shared, AS_OF)) == 1
    assert (
        result.snapshot.items[0].source_realizations[0]
        == result.snapshot.items[1].source_realizations[0]
    )


def test_port_exception_propagates_and_cannot_become_success():
    rule = active_rule()

    class FailingApplicationCatalogue:
        def resolve_projection(self, **_):
            raise RuntimeError("catalogue unavailable")

    service = AssembleExportSnapshot(
        application_catalogue=FailingApplicationCatalogue(),
        resource_catalogue=FakeResourceCatalogue({}),
    )

    with pytest.raises(RuntimeError, match="catalogue unavailable"):
        service.execute(selected([rule]))
