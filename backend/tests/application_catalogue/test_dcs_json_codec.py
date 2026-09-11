import json

import pytest

from napms.contexts.application_catalogue.infrastructure.integrations.dcs_json_codec import (
    DcsProjectionEncodeError,
    JsonDcsProjectionCodec,
)
from napms.policy_export.application.normalization_ports import (
    DcsProjectionDecodeError,
)
from napms.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    PortConstraint,
    PortRange,
)


def alternative(
    protocol="tcp",
    source=None,
    destination=None,
    service="https",
):
    return DcsTrafficAlternative(
        protocol=protocol,
        source_ports=source or PortConstraint.any(),
        destination_ports=destination
        or PortConstraint.ranged(PortRange(443, 443)),
        service_reference=service,
    )


def test_codec_round_trip_is_deterministic_and_preserves_semantics():
    codec = JsonDcsProjectionCodec()
    udp = alternative(
        protocol="udp",
        destination=PortConstraint.ranged(PortRange(53, 53)),
        service="dns",
    )
    tcp = alternative(
        destination=PortConstraint.ranged(
            PortRange(1000, 1005),
            PortRange(443, 443),
            PortRange(1006, 1010),
        )
    )

    first = codec.encode((udp, tcp))
    second = codec.encode((tcp, udp))

    assert first == second
    decoded = codec.decode(first)
    assert tuple(value.protocol for value in decoded) == ("tcp", "udp")
    assert decoded[0].destination_ports.ranges == (
        PortRange(443, 443),
        PortRange(1000, 1010),
    )


def test_not_applicable_and_any_remain_distinct():
    codec = JsonDcsProjectionCodec()
    value = DcsTrafficAlternative(
        protocol="protocol-x",
        source_ports=PortConstraint.not_applicable(),
        destination_ports=PortConstraint.any(),
    )

    decoded = codec.decode(codec.encode((value,)))[0]

    assert decoded.source_ports == PortConstraint.not_applicable()
    assert decoded.destination_ports == PortConstraint.any()
    assert decoded.source_ports != decoded.destination_ports


@pytest.mark.parametrize(
    "document",
    [
        {},
        {"schema": "other", "version": 1, "alternatives": []},
        {"schema": "napms.dcs-projection", "version": 2, "alternatives": []},
        {"schema": "napms.dcs-projection", "version": 1, "alternatives": []},
        {
            "schema": "napms.dcs-projection",
            "version": 1,
            "alternatives": [],
            "extra": True,
        },
    ],
)
def test_decoder_rejects_wrong_document_contract(document):
    payload = json.dumps(document).encode("utf-8")
    with pytest.raises(DcsProjectionDecodeError):
        JsonDcsProjectionCodec().decode(payload)


@pytest.mark.parametrize(
    "constraint",
    [
        {"kind": "Any", "ranges": []},
        {"kind": "NotApplicable", "extra": 1},
        {"kind": "Ranges", "ranges": []},
        {"kind": "Ranges", "ranges": [[443]]},
        {"kind": "Ranges", "ranges": [[True, 443]]},
        {"kind": "Other"},
    ],
)
def test_decoder_rejects_malformed_port_constraints(constraint):
    document = {
        "schema": "napms.dcs-projection",
        "version": 1,
        "alternatives": [
            {
                "protocol": "tcp",
                "sourcePorts": {"kind": "Any"},
                "destinationPorts": constraint,
                "serviceReference": None,
            }
        ],
    }
    with pytest.raises(DcsProjectionDecodeError):
        JsonDcsProjectionCodec().decode(
            json.dumps(document).encode("utf-8")
        )


def test_decoder_rejects_unknown_alternative_fields():
    document = {
        "schema": "napms.dcs-projection",
        "version": 1,
        "alternatives": [
            {
                "protocol": "tcp",
                "sourcePorts": {"kind": "Any"},
                "destinationPorts": {"kind": "Any"},
                "serviceReference": None,
                "vendorField": "x",
            }
        ],
    }
    with pytest.raises(DcsProjectionDecodeError):
        JsonDcsProjectionCodec().decode(json.dumps(document).encode("utf-8"))


def test_duplicate_alternatives_are_rejected_on_encode_and_decode():
    codec = JsonDcsProjectionCodec()
    value = alternative()

    with pytest.raises(DcsProjectionEncodeError):
        codec.encode((value, value))

    single = json.loads(codec.encode((value,)).decode("utf-8"))
    single["alternatives"].append(single["alternatives"][0])
    with pytest.raises(DcsProjectionDecodeError):
        codec.decode(json.dumps(single).encode("utf-8"))


@pytest.mark.parametrize("payload", [b"", b"\xff", b"not-json"])
def test_decoder_rejects_non_payload_bytes(payload):
    with pytest.raises(DcsProjectionDecodeError):
        JsonDcsProjectionCodec().decode(payload)
