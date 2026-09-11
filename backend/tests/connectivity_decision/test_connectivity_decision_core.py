from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from napms.contexts.connectivity_decision.application.options import (
    DecisionInteractionDiscoveryOutcome,
    DiscoverDecisionInteractions,
    DiscoverDecisionScopes,
)
from napms.contexts.connectivity_decision.application.ports import (
    DecisionAuthorityCheck,
    DecisionCommitOutcomeUnknown,
    DecisionCurrentConflict,
    DecisionInteractionPage,
    DecisionScopeOptions,
    DecisionSubjectCheck,
    SubjectOutcome,
    TernaryOutcome,
)
from napms.contexts.connectivity_decision.application.read import (
    DecisionDetailOutcome,
    GetConnectivityDecision,
    ListConnectivityDecisions,
)
from napms.contexts.connectivity_decision.application.record import (
    RecordConnectivityDecision,
    RecordDecision,
    RecordDecisionOutcome,
)
from napms.contexts.connectivity_decision.application.select import (
    SelectEffectiveConnectivityDecision,
    SelectionOutcome,
)
from napms.contexts.connectivity_decision.domain.model import (
    ConnectivityDecision,
    DecisionEvidenceReference,
    DecisionInvariantError,
    DecisionOutcome,
    DecisionProvenance,
    DecisionSubject,
    DecisionValidity,
)


NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
SOURCE = UUID(int=101)
DESTINATION = UUID(int=102)
DCS = UUID(int=201)
SUBJECT = DecisionSubject(SOURCE, DESTINATION, DCS)
DECISION_ID = UUID(int=301)
OTHER_DECISION_ID = UUID(int=302)


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
        return DecisionAuthorityCheck(
            self.outcome,
            self.reference if self.outcome is TernaryOutcome.PERMITTED else None,
        )


class FakeCatalogue:
    def __init__(self, outcome=SubjectOutcome.VALID, subject=SUBJECT):
        self.outcome = outcome
        self.subject = subject
        self.calls = []

    def validate_decision_subject(self, **kwargs):
        self.calls.append(kwargs)
        return DecisionSubjectCheck(
            outcome=self.outcome,
            subject=self.subject if self.outcome is SubjectOutcome.VALID else None,
            provenance_reference=(
                "catalogue-1" if self.outcome is SubjectOutcome.VALID else None
            ),
        )


class FakeScopes:
    def __init__(self, permitted=("scope-a",), ambiguous=()):
        self.options = DecisionScopeOptions(permitted, ambiguous)
        self.calls = []

    def list_effective_decision_scopes(self, **kwargs):
        self.calls.append(kwargs)
        return self.options

    def list_effective_decision_read_scopes(self, **kwargs):
        self.calls.append(kwargs)
        return self.options


class FakeInteractionDiscovery:
    def __init__(self):
        self.calls = []

    def list_decision_subjects(self, *, page, page_size, search=None):
        self.calls.append((page, page_size, search))
        return DecisionInteractionPage(
            subjects=(SUBJECT,),
            page=page,
            page_size=page_size,
            has_more=False,
        )


class MemoryDecisions:
    def __init__(self, values=()):
        self.values = {value.decision_id: value for value in values}
        self.added = []
        self.commits = 0

    def get_by_id(self, decision_id):
        return self.values.get(decision_id)

    def find_current(self, *, subject, governance_scope, as_of):
        matching = [
            value
            for value in self.values.values()
            if (
                value.subject == subject
                and value.governance_scope == governance_scope
                and value.is_effective_at(as_of)
            )
        ]
        current = []
        for value in matching:
            superseded = any(
                successor.subject == subject
                and successor.governance_scope == governance_scope
                and successor.supersedes_decision_id == value.decision_id
                and successor.validity.valid_from <= as_of
                for successor in self.values.values()
            )
            if not superseded:
                current.append(value)
        return tuple(sorted(current, key=lambda value: value.decision_id))

    def list_by_governance_scopes(self, scopes, *, offset, limit):
        rows = tuple(
            sorted(
                (
                    value
                    for value in self.values.values()
                    if value.governance_scope in scopes
                ),
                key=lambda value: value.decision_id,
            )
        )
        return rows[offset : offset + limit]

    def add(self, decision):
        self.values[decision.decision_id] = decision
        self.added.append(decision)

    def commit(self):
        self.commits += 1


class ConflictDecisions(MemoryDecisions):
    def __init__(self, winner):
        super().__init__((winner,))
        self.first_lookup = True

    def find_current(self, *, subject, governance_scope, as_of):
        if self.first_lookup:
            self.first_lookup = False
            return ()
        return super().find_current(
            subject=subject,
            governance_scope=governance_scope,
            as_of=as_of,
        )

    def add(self, decision):
        raise DecisionCurrentConflict()


class UnknownCommitDecisions(MemoryDecisions):
    def commit(self):
        raise DecisionCommitOutcomeUnknown()


def validity(start=NOW, end=None):
    return DecisionValidity(start, end)


def evidence():
    return (
        DecisionEvidenceReference(
            "ConnectivityRequirement",
            "requirement-1",
        ),
    )


def decision(
    *,
    decision_id=DECISION_ID,
    scope="scope-a",
    outcome=DecisionOutcome.ALLOWED,
    valid=None,
    reason_code="BUSINESS_NEED",
    reason_text="Required application interaction",
    supersedes=None,
):
    return ConnectivityDecision(
        decision_id=decision_id,
        subject=SUBJECT,
        governance_scope=scope,
        outcome=outcome,
        validity=valid or validity(),
        reason_code=reason_code,
        reason_text=reason_text,
        evidence_references=evidence(),
        provenance=DecisionProvenance(
            actor_id="decider",
            decided_at=NOW,
            authority_reference="authority-1",
        ),
        supersedes_decision_id=supersedes,
    )


def command(
    *,
    scope="scope-a",
    outcome=DecisionOutcome.ALLOWED,
    valid=None,
    reason_code="BUSINESS_NEED",
    reason_text="Required application interaction",
    supersedes=None,
):
    return RecordDecision(
        subject=SUBJECT,
        governance_scope=scope,
        outcome=outcome,
        validity=valid or validity(),
        reason_code=reason_code,
        reason_text=reason_text,
        evidence_references=evidence(),
        actor_id="decider",
        effective_time=NOW,
        supersedes_decision_id=supersedes,
    )


def service(*, authority=None, catalogue=None, decisions=None, id_factory=None):
    kwargs = dict(
        authority=authority or FakeAuthority(),
        catalogue=catalogue or FakeCatalogue(),
        decisions=decisions or MemoryDecisions(),
    )
    if id_factory is not None:
        kwargs["id_factory"] = id_factory
    return RecordConnectivityDecision(**kwargs)


def test_decision_validity_is_half_open_and_offset_aware():
    end = NOW + timedelta(hours=1)
    value = DecisionValidity(NOW, end)

    assert value.contains(NOW)
    assert value.contains(end - timedelta(microseconds=1))
    assert not value.contains(end)

    with pytest.raises(DecisionInvariantError):
        DecisionValidity(
            datetime(2026, 9, 9, 12, 0),
            end,
        )
    with pytest.raises(DecisionInvariantError):
        DecisionValidity(NOW, NOW)


def test_decision_requires_reason_and_provenance():
    with pytest.raises(DecisionInvariantError):
        decision(reason_code=" ")
    with pytest.raises(DecisionInvariantError):
        ConnectivityDecision(
            decision_id=DECISION_ID,
            subject=SUBJECT,
            governance_scope="scope-a",
            outcome=DecisionOutcome.ALLOWED,
            validity=validity(),
            reason_code="OK",
            reason_text=" ",
            evidence_references=(),
            provenance=DecisionProvenance("actor", NOW, "authority"),
        )


def test_authorized_record_creates_immutable_final_decision():
    authority = FakeAuthority()
    repo = MemoryDecisions()
    result = service(
        authority=authority,
        decisions=repo,
        id_factory=lambda: DECISION_ID,
    ).execute(command())

    assert result.outcome is RecordDecisionOutcome.RECORDED
    assert result.decision.decision_id == DECISION_ID
    assert result.decision.outcome is DecisionOutcome.ALLOWED
    assert result.decision.provenance.authority_reference == "authority-1"
    assert authority.calls[0]["action"].value == "DecideConnectivity"
    assert repo.commits == 1


def test_decision_is_authority_first():
    authority = FakeAuthority(TernaryOutcome.DENIED)
    catalogue = FakeCatalogue()
    repo = MemoryDecisions()

    result = service(
        authority=authority,
        catalogue=catalogue,
        decisions=repo,
    ).execute(command())

    assert result.outcome is RecordDecisionOutcome.AUTHORITY_DENIED
    assert catalogue.calls == []
    assert repo.values == {}


def test_permitted_without_authority_reference_fails_closed():
    result = service(
        authority=FakeAuthority(TernaryOutcome.PERMITTED, reference=None)
    ).execute(command())

    assert result.outcome is RecordDecisionOutcome.AUTHORITY_UNKNOWN


def test_invalid_and_unknown_subjects_do_not_create_decisions():
    for actual, expected in (
        (SubjectOutcome.INVALID, RecordDecisionOutcome.SUBJECT_INVALID),
        (SubjectOutcome.UNKNOWN, RecordDecisionOutcome.SUBJECT_UNKNOWN),
    ):
        repo = MemoryDecisions()
        result = service(
            catalogue=FakeCatalogue(actual),
            decisions=repo,
        ).execute(command())
        assert result.outcome is expected
        assert repo.values == {}


def test_repeated_same_intent_resolves_existing_decision():
    existing = decision()
    repo = MemoryDecisions((existing,))

    result = service(decisions=repo).execute(command())

    assert result.outcome is RecordDecisionOutcome.RESOLVED
    assert result.decision == existing
    assert repo.commits == 0


def test_changed_current_decision_requires_explicit_supersession():
    existing = decision()
    result = service(decisions=MemoryDecisions((existing,))).execute(
        command(
            outcome=DecisionOutcome.NOT_ALLOWED,
            reason_code="RISK",
            reason_text="Risk not accepted",
        )
    )

    assert result.outcome is RecordDecisionOutcome.SUPERSESSION_REQUIRED


def test_supersession_creates_new_decision_and_preserves_history():
    existing = decision()
    repo = MemoryDecisions((existing,))
    result = service(
        decisions=repo,
        id_factory=lambda: OTHER_DECISION_ID,
    ).execute(
        command(
            outcome=DecisionOutcome.NOT_ALLOWED,
            reason_code="RISK",
            reason_text="Risk not accepted",
            supersedes=existing.decision_id,
        )
    )

    assert result.outcome is RecordDecisionOutcome.RECORDED
    assert result.decision.supersedes_decision_id == existing.decision_id
    assert repo.get_by_id(existing.decision_id) == existing
    assert repo.find_current(
        subject=SUBJECT,
        governance_scope="scope-a",
        as_of=NOW,
    ) == (result.decision,)


def test_non_current_or_cross_scope_supersession_is_invalid():
    expired = decision(
        valid=DecisionValidity(
            NOW - timedelta(hours=2),
            NOW - timedelta(hours=1),
        )
    )
    repo = MemoryDecisions((expired,))

    result = service(decisions=repo).execute(
        command(supersedes=expired.decision_id)
    )

    assert result.outcome is RecordDecisionOutcome.SUPERSESSION_INVALID


def test_selection_distinguishes_found_not_found_and_ambiguous():
    repo = MemoryDecisions((decision(),))
    selector = SelectEffectiveConnectivityDecision(decisions=repo)

    found = selector.execute(
        subject=SUBJECT,
        governance_scope="scope-a",
        as_of=NOW,
    )
    missing = selector.execute(
        subject=SUBJECT,
        governance_scope="other",
        as_of=NOW,
    )

    assert found.outcome is SelectionOutcome.FOUND
    assert found.decision.decision_id == DECISION_ID
    assert missing.outcome is SelectionOutcome.NOT_FOUND

    second = decision(
        decision_id=OTHER_DECISION_ID,
        reason_code="OTHER",
        reason_text="Other independent record",
    )
    ambiguous_repo = MemoryDecisions((decision(), second))
    ambiguous = SelectEffectiveConnectivityDecision(
        decisions=ambiguous_repo
    ).execute(
        subject=SUBJECT,
        governance_scope="scope-a",
        as_of=NOW,
    )
    assert ambiguous.outcome is SelectionOutcome.AMBIGUOUS


def test_detail_uses_stored_scope_and_read_authority():
    existing = decision(scope="scope-a")
    authority = FakeAuthority()
    result = GetConnectivityDecision(
        authority=authority,
        decisions=MemoryDecisions((existing,)),
    ).execute(
        decision_id=existing.decision_id,
        actor_id="reader",
        effective_time=NOW,
    )

    assert result.outcome is DecisionDetailOutcome.FOUND
    assert authority.calls[0]["action"].value == "ReadConnectivityDecision"
    assert authority.calls[0]["scope"] == "scope-a"


def test_denied_detail_exposes_no_decision():
    existing = decision()
    result = GetConnectivityDecision(
        authority=FakeAuthority(TernaryOutcome.DENIED),
        decisions=MemoryDecisions((existing,)),
    ).execute(
        decision_id=existing.decision_id,
        actor_id="reader",
        effective_time=NOW,
    )

    assert result.outcome is DecisionDetailOutcome.AUTHORITY_DENIED
    assert result.decision is None


def test_list_uses_only_permitted_read_scopes():
    scope_a = decision(decision_id=UUID(int=401), scope="scope-a")
    scope_b = decision(decision_id=UUID(int=402), scope="scope-b")
    page = ListConnectivityDecisions(
        read_scopes=FakeScopes(
            permitted=("scope-a",),
            ambiguous=("scope-b",),
        ),
        decisions=MemoryDecisions((scope_a, scope_b)),
    ).execute(actor_id="reader", effective_time=NOW)

    assert tuple(item.decision_id for item in page.decisions) == (
        scope_a.decision_id,
    )
    assert page.ambiguous_scopes == ("scope-b",)


def test_decision_interaction_discovery_is_authority_first():
    catalogue = FakeInteractionDiscovery()
    denied = DiscoverDecisionInteractions(
        authority=FakeAuthority(TernaryOutcome.DENIED),
        catalogue=catalogue,
    ).execute(
        actor_id="decider",
        scope="scope-a",
        effective_time=NOW,
        search="orders",
    )

    assert denied.outcome is DecisionInteractionDiscoveryOutcome.AUTHORITY_DENIED
    assert catalogue.calls == []

    allowed = DiscoverDecisionInteractions(
        authority=FakeAuthority(),
        catalogue=catalogue,
    ).execute(
        actor_id="decider",
        scope="scope-a",
        effective_time=NOW,
        search="orders",
    )
    assert allowed.outcome is DecisionInteractionDiscoveryOutcome.AVAILABLE
    assert allowed.page.subjects == (SUBJECT,)


def test_decision_scope_discovery_delegates_to_authority():
    scopes = FakeScopes(
        permitted=("scope-a", "scope-b"),
        ambiguous=("scope-c",),
    )
    result = DiscoverDecisionScopes(discovery=scopes).execute(
        actor_id="decider",
        effective_time=NOW,
    )
    assert result.permitted_scopes == ("scope-a", "scope-b")
    assert result.ambiguous_scopes == ("scope-c",)


def test_concurrent_same_intent_resolves_winner():
    winner = decision()
    result = service(
        decisions=ConflictDecisions(winner),
        id_factory=lambda: OTHER_DECISION_ID,
    ).execute(command())

    assert result.outcome is RecordDecisionOutcome.RESOLVED
    assert result.decision == winner


def test_unknown_commit_is_never_converted_to_success():
    with pytest.raises(DecisionCommitOutcomeUnknown):
        service(
            decisions=UnknownCommitDecisions(),
            id_factory=lambda: DECISION_ID,
        ).execute(command())
