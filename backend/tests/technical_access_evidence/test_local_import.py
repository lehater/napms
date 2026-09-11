import json

import pytest

from napms.contexts.technical_access_evidence.presentation.imports.local_json import (
    LocalEvidenceImportAdapter,
    LocalEvidenceImportError,
)
from napms.contexts.technical_access_evidence.domain.model import (
    EvidenceAction,
    EvidenceKind,
    EvidenceTime,
    PortConstraintKind,
    ProtocolSelectorKind,
)


def document(*, entries=None, evidence_time=None):
    return {
        "source_reference": "fixture-a",
        "source_scope_reference": "dataset-a",
        "source_capture_reference": "capture-a",
        "evidence_time": evidence_time or {"kind": "Unknown"},
        "entries": entries if entries is not None else [],
    }


def entry(**overrides):
    value = {
        "source_addresses": {
            "kind": "Ranges",
            "ranges": [
                {"first": "10.0.0.1", "last": "10.0.0.10"},
            ],
        },
        "destination_addresses": {"kind": "Any"},
        "protocol": "tcp",
        "source_ports": {"kind": "Any"},
        "destination_ports": {
            "kind": "Ranges",
            "ranges": [{"first": 443, "last": 443}],
        },
        "action": "Permit",
        "source_entry_reference": "rule-1",
        "source_position": 10,
    }
    value.update(overrides)
    return value


def test_local_import_normalizes_to_imported_source_qualified_command():
    command = LocalEvidenceImportAdapter().normalize(
        json.dumps(document(entries=[entry()]))
    )

    assert command.kind is EvidenceKind.IMPORTED
    assert command.source.namespace == "local-import"
    assert command.source.reference == "fixture-a"
    assert command.source_scope.value == "dataset-a"
    assert command.source_capture_reference.value == "capture-a"
    assert command.evidence_time == EvidenceTime.unknown()

    payload = command.entries[0]
    assert payload.predicate.protocol.kind is ProtocolSelectorKind.IP_PROTOCOL_NUMBER
    assert payload.predicate.protocol.number == 6
    assert payload.predicate.destination_ports.ranges[0].first == 443
    assert payload.action is EvidenceAction.PERMIT
    assert payload.source_entry_reference == "rule-1"
    assert payload.source_position == 10


def test_local_import_maps_explicit_window_and_udp():
    command = LocalEvidenceImportAdapter().normalize(
        json.dumps(
            document(
                evidence_time={
                    "kind": "Window",
                    "start": "2026-09-09T10:00:00Z",
                    "end": "2026-09-09T11:00:00+00:00",
                },
                entries=[
                    entry(
                        protocol="udp",
                        source_ports={"kind": "Any"},
                        destination_ports={"kind": "Any"},
                        action=None,
                    )
                ],
            )
        )
    )

    assert command.evidence_time.start.isoformat() == "2026-09-09T10:00:00+00:00"
    assert command.entries[0].predicate.protocol.number == 17
    assert (
        command.entries[0].predicate.source_ports.kind
        is PortConstraintKind.ANY
    )
    assert command.entries[0].action is None


def test_local_import_rejects_protocol_any_with_constrained_ports():
    with pytest.raises(LocalEvidenceImportError):
        LocalEvidenceImportAdapter().normalize(
            json.dumps(
                document(
                    entries=[
                        entry(
                            protocol="any",
                            destination_ports={
                                "kind": "Ranges",
                                "ranges": [{"first": 443, "last": 443}],
                            },
                        )
                    ]
                )
            )
        )


def test_local_import_rejects_unknown_service_semantics_instead_of_dropping_them():
    value = entry()
    value["service_object"] = "https-service"

    with pytest.raises(LocalEvidenceImportError, match="unsupported fields"):
        LocalEvidenceImportAdapter().normalize(
            json.dumps(document(entries=[value]))
        )


def test_local_import_rejects_one_invalid_entry_before_any_record_command_exists():
    valid = entry()
    invalid = entry(protocol="gre")
    with pytest.raises(LocalEvidenceImportError):
        LocalEvidenceImportAdapter().normalize(
            json.dumps(document(entries=[valid, invalid]))
        )


def test_local_import_rejects_malformed_or_naive_time():
    with pytest.raises(LocalEvidenceImportError):
        LocalEvidenceImportAdapter().normalize("{broken")

    with pytest.raises(LocalEvidenceImportError):
        LocalEvidenceImportAdapter().normalize(
            json.dumps(
                document(
                    evidence_time={
                        "kind": "Instant",
                        "at": "2026-09-09T10:00:00",
                    }
                )
            )
        )


def test_local_import_rejects_duplicate_json_fields():
    raw = json.dumps(document(entries=[entry()]))
    raw = raw.replace(
        '"protocol": "tcp"',
        '"protocol": "tcp", "protocol": "udp"',
    )

    with pytest.raises(LocalEvidenceImportError, match="duplicate JSON field"):
        LocalEvidenceImportAdapter().normalize(raw)
