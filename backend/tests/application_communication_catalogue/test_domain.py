from uuid import UUID

import pytest

from napms.contexts.application_communication_catalogue.domain.model import (
    Application,
    Interaction,
    PortRange,
    TrafficClause,
)


def test_component_lifetime_is_owned_by_one_application() -> None:
    application = Application.create(application_ref=UUID(int=1), name="Orders")
    updated = application.add_component(component_ref=UUID(int=2), name="API")

    assert updated.application_ref == application.application_ref
    assert updated.components[0].component_ref == UUID(int=2)
    assert updated.components[0].application_ref == application.application_ref
    assert updated.version == 2


def test_same_directed_pair_may_have_multiple_independent_interactions() -> None:
    first = Interaction.create(
        interaction_ref=UUID(int=10),
        source_component_ref=UUID(int=2),
        destination_component_ref=UUID(int=3),
        purpose="submit orders",
    )
    second = Interaction.create(
        interaction_ref=UUID(int=11),
        source_component_ref=UUID(int=2),
        destination_component_ref=UUID(int=3),
        purpose="query status",
    )

    assert first.interaction_ref != second.interaction_ref
    assert first.source_component_ref == second.source_component_ref
    assert first.destination_component_ref == second.destination_component_ref


def test_revision_is_immutable_history_and_traffic_ranges_are_canonical() -> None:
    interaction = Interaction.create(
        interaction_ref=UUID(int=20),
        source_component_ref=UUID(int=2),
        destination_component_ref=UUID(int=3),
        purpose="submit orders",
    )
    first = interaction.publish_revision(
        revision_ref=UUID(int=21),
        traffic_clauses=(
            TrafficClause(
                ip_protocol=6,
                destination_ports=(PortRange(443, 443),),
            ),
        ),
        subject="subject:alice",
    )
    second = first.publish_revision(
        revision_ref=UUID(int=22),
        traffic_clauses=(
            TrafficClause(
                ip_protocol=6,
                destination_ports=(PortRange(8443, 8443),),
            ),
        ),
        subject="subject:bob",
    )

    assert [item.revision_no for item in second.revisions] == [1, 2]
    assert second.revisions[0].traffic_clauses[0].destination_ports[0].start == 443

    with pytest.raises(ValueError):
        TrafficClause(
            ip_protocol=6,
            destination_ports=(PortRange(443, 443), PortRange(444, 444)),
        )


def test_non_tcp_udp_protocol_cannot_carry_ports() -> None:
    with pytest.raises(ValueError):
        TrafficClause(ip_protocol=1, destination_ports=(PortRange(80, 80),))
