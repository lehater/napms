from datetime import datetime, timedelta, timezone
from uuid import UUID

from napms.contexts.technical_access_evidence.domain.model import (
    AddressConstraint,
    AddressRange,
    EvidenceAction,
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
from napms.traffic_analysis.adapters.technical_evidence import (
    TechnicalAccessEvidenceTrafficAnalysisAdapter,
)
from napms.traffic_analysis.application.model import RuleMatchKind, TrafficAnalysisQuery


NOW = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)


def _set(set_id: int, captured_at: datetime, recorded_at: datetime):
    return TechnicalAccessEvidenceSet(
        evidence_set_id=UUID(int=set_id),
        kind=EvidenceKind.CONFIGURED,
        source=EvidenceSourceReference("import", "firewall"),
        source_scope=SourceScopeReference("fw-1"),
        source_capture_reference=SourceCaptureReference(f"capture-{set_id}"),
        evidence_time=EvidenceTime.instant(captured_at),
        recorded_at=recorded_at,
        entries=(
            TechnicalAccessEntry(
                evidence_entry_id=UUID(int=set_id + 100),
                payload=TechnicalAccessEntryPayload(
                    predicate=TechnicalAccessPredicate(
                        source_addresses=AddressConstraint.ranged(
                            AddressRange("10.10.10.0", "10.10.10.255")
                        ),
                        destination_addresses=AddressConstraint.ranged(
                            AddressRange("10.20.20.0", "10.20.20.255")
                        ),
                        protocol=ProtocolSelector.ip_protocol(6),
                        source_ports=PortConstraint.any(),
                        destination_ports=PortConstraint.ranged(PortRange(443, 443)),
                    ),
                    action=EvidenceAction.PERMIT,
                    source_entry_reference=f"ACL-{set_id}",
                ),
            ),
        ),
    )


class Repo:
    def __init__(self, rows):
        self.rows = tuple(rows)

    def list(self, *, filters, offset, limit):
        assert filters.source_scope == SourceScopeReference("fw-1")
        assert filters.kind is EvidenceKind.CONFIGURED
        return self.rows[offset : offset + limit]


def test_uses_latest_snapshot_available_at_as_of_not_future_capture() -> None:
    old = _set(1, NOW - timedelta(hours=2), NOW - timedelta(hours=1, minutes=50))
    future = _set(2, NOW + timedelta(hours=1), NOW - timedelta(minutes=5))
    adapter = TechnicalAccessEvidenceTrafficAnalysisAdapter(
        evidence_sets=Repo((future, old))
    )

    result = adapter.latest_applicable(
        query=TrafficAnalysisQuery(
            source_address="10.10.10.10",
            destination_address="10.20.20.20",
            protocol="TCP",
            destination_port_first=443,
            destination_port_last=443,
            as_of=NOW,
        ),
        provider_namespace="device",
        device_reference="fw-1",
    )

    assert result is not None
    assert result.evidence_set_reference == str(UUID(int=1))
    assert result.captured_at == NOW - timedelta(hours=2)
    assert result.matches[0].entry_reference == "ACL-1"
    assert result.matches[0].match_kind is RuleMatchKind.COVERS_QUERY


def test_does_not_treat_absent_snapshot_as_current_device_state() -> None:
    adapter = TechnicalAccessEvidenceTrafficAnalysisAdapter(evidence_sets=Repo(()))
    result = adapter.latest_applicable(
        query=TrafficAnalysisQuery(
            source_address="10.10.10.10",
            destination_address="10.20.20.20",
            protocol="TCP",
            destination_port_first=443,
            destination_port_last=443,
            as_of=NOW,
        ),
        provider_namespace="device",
        device_reference="fw-1",
    )
    assert result is None
