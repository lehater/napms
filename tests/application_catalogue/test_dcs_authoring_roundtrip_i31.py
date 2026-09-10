from napms.application_catalogue.adapters.dcs_authoring import (
    JsonDcsAuthoringProjectionEncoder,
)
from napms.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortRange,
)


def test_authored_dcs_projection_roundtrip_preserves_canonical_traffic() -> None:
    alternatives = (
        AuthoredDcsTrafficAlternative(
            protocol="udp",
            source_ports=DcsPortConstraint.any(),
            destination_ports=DcsPortConstraint.ranged(DcsPortRange(53, 53)),
            service_reference="dns",
        ),
        AuthoredDcsTrafficAlternative(
            protocol="tcp",
            source_ports=DcsPortConstraint.any(),
            destination_ports=DcsPortConstraint.ranged(
                DcsPortRange(443, 443),
                DcsPortRange(8000, 8010),
            ),
            service_reference="https",
        ),
    )
    codec = JsonDcsAuthoringProjectionEncoder()

    decoded = codec.decode(codec.encode(alternatives))

    assert set(decoded) == set(alternatives)
