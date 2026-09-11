from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from napms.contexts.technical_access_evidence.application.ports import (
    EvidenceCaptureConflict,
    EvidenceCommitOutcomeUnknown,
    EvidenceSetFilters,
)
from napms.contexts.technical_access_evidence.application.read import (
    EvidenceSetDetailOutcome,
    GetTechnicalAccessEvidenceSet,
    ListTechnicalAccessEvidenceSets,
)
from napms.contexts.technical_access_evidence.application.record import (
    RecordEvidenceOutcome,
    RecordEvidenceSet,
    RecordTechnicalAccessEvidenceSet,
)
from napms.contexts.technical_access_evidence.domain.model import (
    AddressConstraint,
    AddressRange,
    EvidenceAction,
    EvidenceInvariantError,
    EvidenceKind,
    EvidenceSourceReference,
    EvidenceTime,
    PortConstraint,
    PortRange,
    ProtocolSelector,
    SourceCaptureReference,
    SourceScopeReference,
    TechnicalAccessEntry,
    TechnicalAccessEntryPayload,
    TechnicalAccessEvidenceSet,
    TechnicalAccessPredicate,
)


NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
SOURCE = EvidenceSourceReference("controller", "fw-a")
SCOPE = SourceScopeReference("policy-package-a")
CAPTURE = SourceCaptureReference("capture-1")


def predicate(*, destination_port=443):
    return TechnicalAccessPredicate(
        source_addresses=AddressConstraint.ranged(
            AddressRange("10.0.0.1", "10.0.0.10"),
        ),
        destination_addresses=AddressConstraint.any(),
        protocol=ProtocolSelector.ip_protocol(6),
        source_ports=PortConstraint.any(),
        destination_ports=PortConstraint.ranged(
            PortRange(destination_port, destination_port),
        ),
    )


def entry_payload(
    *,
    reference="rule-1",
    position=10,
    destination_port=443,
):
    return TechnicalAccessEntryPayload(
        predicate=predicate(destination_port=destination_port),
        action=EvidenceAction.PERMIT,
        source_entry_reference=reference,
        source_position=position,
    )


def evidence_set(*, entries=None, recorded_at=NOW):
    payloads = entries or (entry_payload(),)
    return TechnicalAccessEvidenceSet(
        evidence_set_id=UUID(int=1),
        kind=EvidenceKind.CONFIGURED,
        source=SOURCE,
        source_scope=SCOPE,
        source_capture_reference=CAPTURE,
        evidence_time=EvidenceTime.instant(NOW - timedelta(minutes=5)),
        recorded_at=recorded_at,
        entries=tuple(
            TechnicalAccessEntry(UUID(int=index + 10), payload)
            for index, payload in enumerate(payloads)
        ),
    )


class MemoryEvidenceSets:
    def __init__(self, values=()):
        self.values = {
            value.evidence_set_id: value
            for value in values
        }
        self.pending = None

    def get_by_id(self, evidence_set_id):
        return self.values.get(evidence_set_id)

    def find_by_capture(
        self,
        *,
        source,
        source_capture_reference,
    ):
        for value in self.values.values():
            if (
                value.source == source
                and value.source_capture_reference
                == source_capture_reference
            ):
                return value
        return None

    def list(self, *, filters, offset, limit):
        values = list(self.values.values())
        if filters.source is not None:
            values = [
                value
                for value in values
                if value.source == filters.source
            ]
        if filters.source_scope is not None:
            values = [
                value
                for value in values
                if value.source_scope == filters.source_scope
            ]
        if filters.kind is not None:
            values = [
                value
                for value in values
                if value.kind is filters.kind
            ]
        if filters.recorded_from is not None:
            values = [
                value
                for value in values
                if value.recorded_at >= filters.recorded_from
            ]
        if filters.recorded_until is not None:
            values = [
                value
                for value in values
                if value.recorded_at < filters.recorded_until
            ]
        values.sort(
            key=lambda value: value.recorded_at,
            reverse=True,
        )
        return tuple(values[offset : offset + limit])

    def add(self, value):
        self.pending = value

    def commit(self):
        if self.pending is not None:
            self.values[self.pending.evidence_set_id] = self.pending
            self.pending = None


def test_evidence_time_keeps_unknown_and_recorded_time_distinct():
    assert EvidenceTime.unknown().at is None
    with pytest.raises(EvidenceInvariantError):
        EvidenceTime.window(NOW, NOW)
    with pytest.raises(EvidenceInvariantError):
        EvidenceTime.instant(datetime(2026, 9, 9, 12, 0))


def test_address_and_port_ranges_are_canonicalized_without_broadening():
    addresses = AddressConstraint.ranged(
        AddressRange("10.0.0.2", "10.0.0.3"),
        AddressRange("10.0.0.1", "10.0.0.1"),
        AddressRange("2001:db8::1", "2001:db8::2"),
    )
    assert addresses.ranges == (
        AddressRange("10.0.0.1", "10.0.0.3"),
        AddressRange("2001:db8::1", "2001:db8::2"),
    )
    ports = PortConstraint.ranged(
        PortRange(443, 443),
        PortRange(440, 442),
    )
    assert ports.ranges == (PortRange(440, 443),)


def test_protocol_selector_uses_exact_ip_protocol_number():
    assert ProtocolSelector.ip_protocol(6).number == 6
    with pytest.raises(EvidenceInvariantError):
        ProtocolSelector.ip_protocol(256)


def test_protocol_any_requires_unconstrained_ports():
    with pytest.raises(EvidenceInvariantError):
        TechnicalAccessPredicate(
            source_addresses=AddressConstraint.any(),
            destination_addresses=AddressConstraint.any(),
            protocol=ProtocolSelector.any(),
            source_ports=PortConstraint.any(),
            destination_ports=PortConstraint.ranged(
                PortRange(443, 443),
            ),
        )


def test_configured_block_and_traffic_derived_action_absence_are_preserved():
    configured_payload = TechnicalAccessEntryPayload(
        predicate=predicate(),
        action=EvidenceAction.BLOCK,
        source_entry_reference="configured-block",
        source_position=1,
    )
    traffic_payload = TechnicalAccessEntryPayload(
        predicate=predicate(),
        action=None,
        source_entry_reference="flow-observation",
        source_position=None,
    )

    configured = TechnicalAccessEvidenceSet(
        evidence_set_id=UUID(int=101),
        kind=EvidenceKind.CONFIGURED,
        source=SOURCE,
        source_scope=SCOPE,
        source_capture_reference=SourceCaptureReference("configured-capture"),
        evidence_time=EvidenceTime.instant(NOW),
        recorded_at=NOW,
        entries=(TechnicalAccessEntry(UUID(int=201), configured_payload),),
    )
    traffic = TechnicalAccessEvidenceSet(
        evidence_set_id=UUID(int=102),
        kind=EvidenceKind.TRAFFIC_DERIVED,
        source=EvidenceSourceReference("flow", "sensor-a"),
        source_scope=SourceScopeReference("observation-a"),
        source_capture_reference=SourceCaptureReference("traffic-capture"),
        evidence_time=EvidenceTime.window(
            NOW - timedelta(minutes=5),
            NOW,
        ),
        recorded_at=NOW,
        entries=(TechnicalAccessEntry(UUID(int=202), traffic_payload),),
    )

    assert configured.kind is EvidenceKind.CONFIGURED
    assert configured.entries[0].payload.action is EvidenceAction.BLOCK
    assert traffic.kind is EvidenceKind.TRAFFIC_DERIVED
    assert traffic.entries[0].payload.action is None


def test_duplicate_entry_payloads_are_preserved():
    duplicate = entry_payload(reference=None, position=None)
    value = evidence_set(entries=(duplicate, duplicate))
    assert len(value.entries) == 2
    assert value.entries[0].payload == value.entries[1].payload
    assert (
        value.entries[0].evidence_entry_id
        != value.entries[1].evidence_entry_id
    )


def test_capture_payload_equality_is_order_insensitive_but_multiplicity_sensitive():
    first = entry_payload(reference="a", position=10)
    second = entry_payload(reference="b", position=20)
    stored = evidence_set(entries=(first, second, first))

    equivalent = stored.capture_payload.__class__(
        kind=stored.kind,
        source_scope=stored.source_scope,
        evidence_time=stored.evidence_time,
        entries=(second, first, first),
    )
    missing_duplicate = stored.capture_payload.__class__(
        kind=stored.kind,
        source_scope=stored.source_scope,
        evidence_time=stored.evidence_time,
        entries=(second, first),
    )

    assert stored.capture_payload.is_equivalent_to(equivalent)
    assert not stored.capture_payload.is_equivalent_to(
        missing_duplicate
    )


def test_identical_retry_returns_existing_ids_and_recorded_at():
    stored = evidence_set()
    repository = MemoryEvidenceSets((stored,))
    generated = []

    def id_factory():
        generated.append(True)
        return UUID(int=99)

    use_case = RecordTechnicalAccessEvidenceSet(
        evidence_sets=repository,
        set_id_factory=id_factory,
        entry_id_factory=id_factory,
        clock=lambda: NOW + timedelta(hours=1),
    )
    result = use_case.execute(
        RecordEvidenceSet(
            kind=stored.kind,
            source=stored.source,
            source_scope=stored.source_scope,
            source_capture_reference=stored.source_capture_reference,
            evidence_time=stored.evidence_time,
            entries=tuple(
                entry.payload
                for entry in reversed(stored.entries)
            ),
        )
    )

    assert result.outcome is RecordEvidenceOutcome.RESOLVED
    assert result.evidence_set is stored
    assert result.evidence_set.recorded_at == NOW
    assert generated == []


def test_same_capture_with_different_payload_is_conflict():
    stored = evidence_set()
    repository = MemoryEvidenceSets((stored,))
    use_case = RecordTechnicalAccessEvidenceSet(
        evidence_sets=repository
    )

    result = use_case.execute(
        RecordEvidenceSet(
            kind=stored.kind,
            source=stored.source,
            source_scope=stored.source_scope,
            source_capture_reference=stored.source_capture_reference,
            evidence_time=stored.evidence_time,
            entries=(entry_payload(destination_port=8443),),
        )
    )

    assert result.outcome is RecordEvidenceOutcome.CAPTURE_CONFLICT
    assert result.evidence_set is None


def test_new_capture_records_generated_set_and_entry_ids():
    repository = MemoryEvidenceSets()
    ids = iter(
        (
            UUID(int=100),
            UUID(int=101),
            UUID(int=102),
        )
    )
    use_case = RecordTechnicalAccessEvidenceSet(
        evidence_sets=repository,
        set_id_factory=lambda: next(ids),
        entry_id_factory=lambda: next(ids),
        clock=lambda: NOW,
    )

    result = use_case.execute(
        RecordEvidenceSet(
            kind=EvidenceKind.IMPORTED,
            source=SOURCE,
            source_scope=SCOPE,
            source_capture_reference=CAPTURE,
            evidence_time=EvidenceTime.unknown(),
            entries=(
                entry_payload(reference="a"),
                entry_payload(reference="b"),
            ),
        )
    )

    assert result.outcome is RecordEvidenceOutcome.RECORDED
    assert result.evidence_set.evidence_set_id == UUID(int=100)
    assert [
        entry.evidence_entry_id
        for entry in result.evidence_set.entries
    ] == [
        UUID(int=101),
        UUID(int=102),
    ]
    assert result.evidence_set.recorded_at == NOW


def test_concurrent_capture_conflict_resolves_identical_winner():
    winner = evidence_set()

    class RacingRepository(MemoryEvidenceSets):
        def __init__(self):
            super().__init__()
            self.raced = False

        def find_by_capture(
            self,
            *,
            source,
            source_capture_reference,
        ):
            if self.raced:
                return winner
            return None

        def add(self, value):
            self.raced = True
            raise EvidenceCaptureConflict("race")

    repository = RacingRepository()
    use_case = RecordTechnicalAccessEvidenceSet(
        evidence_sets=repository
    )
    result = use_case.execute(
        RecordEvidenceSet(
            kind=winner.kind,
            source=winner.source,
            source_scope=winner.source_scope,
            source_capture_reference=winner.source_capture_reference,
            evidence_time=winner.evidence_time,
            entries=tuple(
                entry.payload
                for entry in winner.entries
            ),
        )
    )

    assert result.outcome is RecordEvidenceOutcome.RESOLVED
    assert result.evidence_set is winner


def test_commit_outcome_unknown_is_not_reported_as_success():
    class UnknownCommitRepository(MemoryEvidenceSets):
        def commit(self):
            raise EvidenceCommitOutcomeUnknown("unknown")

    repository = UnknownCommitRepository()
    use_case = RecordTechnicalAccessEvidenceSet(
        evidence_sets=repository,
        set_id_factory=lambda: UUID(int=100),
        entry_id_factory=lambda: UUID(int=101),
        clock=lambda: NOW,
    )

    with pytest.raises(EvidenceCommitOutcomeUnknown):
        use_case.execute(
            RecordEvidenceSet(
                kind=EvidenceKind.CONFIGURED,
                source=SOURCE,
                source_scope=SCOPE,
                source_capture_reference=CAPTURE,
                evidence_time=EvidenceTime.instant(NOW),
                entries=(entry_payload(),),
            )
        )


def test_list_keeps_multiple_captures_without_selecting_current_truth():
    first = evidence_set(recorded_at=NOW)
    second = TechnicalAccessEvidenceSet(
        evidence_set_id=UUID(int=2),
        kind=EvidenceKind.CONFIGURED,
        source=SOURCE,
        source_scope=SCOPE,
        source_capture_reference=SourceCaptureReference("capture-2"),
        evidence_time=EvidenceTime.instant(NOW + timedelta(minutes=1)),
        recorded_at=NOW + timedelta(minutes=1),
        entries=(),
    )
    repository = MemoryEvidenceSets((first, second))

    page = ListTechnicalAccessEvidenceSets(
        evidence_sets=repository
    ).execute(
        filters=EvidenceSetFilters(
            source=SOURCE,
            source_scope=SCOPE,
            kind=EvidenceKind.CONFIGURED,
        ),
        page=1,
        page_size=10,
    )

    assert page.evidence_sets == (second, first)
    assert page.has_more is False


def test_get_and_list_return_only_evidence_facts():
    first = evidence_set(recorded_at=NOW)
    second = TechnicalAccessEvidenceSet(
        evidence_set_id=UUID(int=2),
        kind=EvidenceKind.TRAFFIC_DERIVED,
        source=EvidenceSourceReference("flow", "sensor-a"),
        source_scope=SourceScopeReference("query-a"),
        source_capture_reference=SourceCaptureReference(
            "capture-2"
        ),
        evidence_time=EvidenceTime.window(
            NOW - timedelta(hours=1),
            NOW,
        ),
        recorded_at=NOW + timedelta(minutes=1),
        entries=(),
    )
    repository = MemoryEvidenceSets((first, second))

    detail = GetTechnicalAccessEvidenceSet(
        evidence_sets=repository
    ).execute(first.evidence_set_id)
    assert detail.outcome is EvidenceSetDetailOutcome.FOUND
    assert detail.evidence_set is first

    page = ListTechnicalAccessEvidenceSets(
        evidence_sets=repository
    ).execute(
        filters=EvidenceSetFilters(
            kind=EvidenceKind.TRAFFIC_DERIVED
        ),
        page=1,
        page_size=1,
    )
    assert page.evidence_sets == (second,)
    assert page.has_more is False
