import json

from napms.policy_export.application.normalization_ports import (
    DcsProjectionDecodeError,
)
from napms.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    NormalizationInvariantError,
    PortConstraint,
    PortConstraintKind,
    PortRange,
)


_SCHEMA = "napms.dcs-projection"
_VERSION = 1


class DcsProjectionEncodeError(Exception):
    """The accepted traffic semantics cannot be encoded into the greenfield payload."""


class JsonDcsProjectionCodec:
    """Strict versioned ACC payload codec used only inside NAPMS greenfield integration."""

    def encode(
        self,
        alternatives: tuple[DcsTrafficAlternative, ...],
    ) -> bytes:
        if not alternatives:
            raise DcsProjectionEncodeError("at least one DCS traffic alternative is required")
        if len(set(alternatives)) != len(alternatives):
            raise DcsProjectionEncodeError("duplicate DCS traffic alternatives are not allowed")

        ordered = tuple(sorted(alternatives, key=_alternative_sort_key))
        document = {
            "schema": _SCHEMA,
            "version": _VERSION,
            "alternatives": [_encode_alternative(value) for value in ordered],
        }
        return json.dumps(
            document,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

    def decode(self, payload: bytes) -> tuple[DcsTrafficAlternative, ...]:
        if not isinstance(payload, bytes) or not payload:
            raise DcsProjectionDecodeError("payload must be non-empty bytes")

        try:
            document = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DcsProjectionDecodeError("payload is not valid UTF-8 JSON") from exc

        if not isinstance(document, dict) or set(document) != {
            "schema",
            "version",
            "alternatives",
        }:
            raise DcsProjectionDecodeError("unexpected DCS payload document shape")
        if document["schema"] != _SCHEMA or document["version"] != _VERSION:
            raise DcsProjectionDecodeError("unsupported DCS payload schema/version")
        if not isinstance(document["alternatives"], list) or not document["alternatives"]:
            raise DcsProjectionDecodeError("DCS payload requires alternatives")

        try:
            alternatives = tuple(
                _decode_alternative(value) for value in document["alternatives"]
            )
        except (KeyError, TypeError, ValueError, NormalizationInvariantError) as exc:
            raise DcsProjectionDecodeError("invalid DCS traffic alternative") from exc

        if len(set(alternatives)) != len(alternatives):
            raise DcsProjectionDecodeError("duplicate DCS traffic alternatives are not allowed")
        return alternatives


def _encode_alternative(value: DcsTrafficAlternative) -> dict:
    return {
        "protocol": value.protocol,
        "sourcePorts": _encode_constraint(value.source_ports),
        "destinationPorts": _encode_constraint(value.destination_ports),
        "serviceReference": value.service_reference,
    }


def _encode_constraint(value: PortConstraint) -> dict:
    if value.kind is PortConstraintKind.RANGES:
        return {
            "kind": value.kind.value,
            "ranges": [[range_.first, range_.last] for range_ in value.ranges],
        }
    return {"kind": value.kind.value}


def _decode_alternative(value) -> DcsTrafficAlternative:
    if not isinstance(value, dict) or set(value) != {
        "protocol",
        "sourcePorts",
        "destinationPorts",
        "serviceReference",
    }:
        raise ValueError("unexpected alternative shape")

    protocol = value["protocol"]
    service_reference = value["serviceReference"]
    if not isinstance(protocol, str):
        raise TypeError("protocol must be a string")
    if service_reference is not None and not isinstance(service_reference, str):
        raise TypeError("serviceReference must be a string or null")

    return DcsTrafficAlternative(
        protocol=protocol,
        source_ports=_decode_constraint(value["sourcePorts"]),
        destination_ports=_decode_constraint(value["destinationPorts"]),
        service_reference=service_reference,
    )


def _decode_constraint(value) -> PortConstraint:
    if not isinstance(value, dict) or "kind" not in value:
        raise ValueError("port constraint must be an object with kind")

    kind = value["kind"]
    if kind == PortConstraintKind.ANY.value:
        if set(value) != {"kind"}:
            raise ValueError("Any cannot carry extra fields")
        return PortConstraint.any()
    if kind == PortConstraintKind.NOT_APPLICABLE.value:
        if set(value) != {"kind"}:
            raise ValueError("NotApplicable cannot carry extra fields")
        return PortConstraint.not_applicable()
    if kind != PortConstraintKind.RANGES.value or set(value) != {"kind", "ranges"}:
        raise ValueError("unsupported port constraint kind")

    ranges = value["ranges"]
    if not isinstance(ranges, list) or not ranges:
        raise ValueError("Ranges requires a non-empty ranges list")

    decoded = []
    for item in ranges:
        if (
            not isinstance(item, list)
            or len(item) != 2
            or type(item[0]) is not int
            or type(item[1]) is not int
        ):
            raise ValueError("port range must be [integer, integer]")
        decoded.append(PortRange(item[0], item[1]))
    return PortConstraint.ranged(*decoded)


def _constraint_sort_key(value: PortConstraint):
    return (
        value.kind.value,
        tuple((range_.first, range_.last) for range_ in value.ranges),
    )


def _alternative_sort_key(value: DcsTrafficAlternative):
    return (
        value.protocol,
        _constraint_sort_key(value.source_ports),
        _constraint_sort_key(value.destination_ports),
        value.service_reference or "",
    )
