from napms.contexts.application_catalogue.infrastructure.integrations.dcs_json_codec import JsonDcsProjectionCodec
from napms.contexts.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortConstraintKind,
    DcsPortRange,
)
from napms.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    PortConstraint,
    PortConstraintKind,
    PortRange,
)


class JsonDcsAuthoringProjectionEncoder:
    """Translate ACC-owned authoring semantics to/from the existing versioned DCS codec."""

    def __init__(self, codec: JsonDcsProjectionCodec | None = None) -> None:
        self._codec = codec or JsonDcsProjectionCodec()

    def encode(
        self,
        alternatives: tuple[AuthoredDcsTrafficAlternative, ...],
    ) -> bytes:
        return self._codec.encode(tuple(_translate(value) for value in alternatives))

    def decode(
        self,
        payload: bytes,
    ) -> tuple[AuthoredDcsTrafficAlternative, ...]:
        return tuple(_translate_back(value) for value in self._codec.decode(payload))


def _translate(value: AuthoredDcsTrafficAlternative) -> DcsTrafficAlternative:
    return DcsTrafficAlternative(
        protocol=value.protocol,
        source_ports=_translate_constraint(value.source_ports),
        destination_ports=_translate_constraint(value.destination_ports),
        service_reference=value.service_reference,
    )


def _translate_constraint(value: DcsPortConstraint) -> PortConstraint:
    if value.kind is DcsPortConstraintKind.ANY:
        return PortConstraint.any()
    if value.kind is DcsPortConstraintKind.NOT_APPLICABLE:
        return PortConstraint.not_applicable()
    return PortConstraint.ranged(
        *(PortRange(item.first, item.last) for item in value.ranges)
    )


def _translate_back(value: DcsTrafficAlternative) -> AuthoredDcsTrafficAlternative:
    return AuthoredDcsTrafficAlternative(
        protocol=value.protocol,
        source_ports=_translate_constraint_back(value.source_ports),
        destination_ports=_translate_constraint_back(value.destination_ports),
        service_reference=value.service_reference,
    )


def _translate_constraint_back(value: PortConstraint) -> DcsPortConstraint:
    if value.kind is PortConstraintKind.ANY:
        return DcsPortConstraint.any()
    if value.kind is PortConstraintKind.NOT_APPLICABLE:
        return DcsPortConstraint.not_applicable()
    return DcsPortConstraint.ranged(
        *(DcsPortRange(item.first, item.last) for item in value.ranges)
    )
