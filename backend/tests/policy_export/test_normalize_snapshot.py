from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from napms.contexts.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    EffectiveWindow,
    OperationalState,
    ProposalProvenance,
    RuleSemanticIdentity,
)
from napms.policy_export.application.export_snapshot import (
    CapturedResourceRealization,
    ExportSnapshotItem,
    SuccessfulExportSnapshot,
)
from napms.policy_export.application.normalize_snapshot import NormalizeExportSnapshot
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
from napms.policy_export.application.ports import (
    ApplicationProjectionFact,
    ApplicationProjectionOutcome,
    EndpointRealization,
    ResourceReference,
)


AS_OF = datetime(2026, 9, 12, 12, 0, tzinfo=timezone.utc)
NOW = datetime(2026, 9, 8, 18, 0, tzinfo=timezone.utc)


def active_rule(*, rule_id=1, scope="scope-1", window=None):
    identity = RuleSemanticIdentity(
        UUID(int=rule_id),
        UUID(int=rule_id + 100),
        UUID(int=rule_id + 200),
    )
    rule = AccessRule.materialized_from_allowed_decision(
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
    if window is not None:
        rule = rule.with_effective_window(
            window=window,
            actor_id="window-admin",
            effective_time=NOW,
            authority_reference="window-auth",
        )
    return rule


def ref(value):
    return ResourceReference(value)


def captured(resource, *endpoints):
    return CapturedResourceRealization(
        resource_reference=ref(resource),
        endpoint_realizations=tuple(
            EndpointRealization(endpoint, address)
            for endpoint, address in endpoints
        ),
        fact_reference=f"{resource}-fact",
        validity_reference=f"{resource}-validity",
        provenance_reference=f"{resource}-provenance",
    )


def item(
    rule,
    *,
    payload=b"dcs-a",
    sources=None,
    destinations=None,
):
    sources = sources or (
        captured("src", ("src-endpoint", "198.51.100.10")),
    )
    destinations = destinations or (
        captured("dst", ("dst-endpoint", "203.0.113.20")),
    )
    application = ApplicationProjectionFact(
        outcome=ApplicationProjectionOutcome.RESOLVED,
        subject=rule.semantic_identity,
        as_of=AS_OF,
        source_resource_references=tuple(
            value.resource_reference for value in sources
        ),
        destination_resource_references=tuple(
            value.resource_reference for value in destinations
        ),
        dcs_projection_payload=payload,
        fact_reference=f"acc-fact-{rule.rule_id.int}",
        validity_reference=f"acc-validity-{rule.rule_id.int}",
        provenance_reference=f"acc-provenance-{rule.rule_id.int}",
    )
    return ExportSnapshotItem(
        rule=rule,
        application_projection=application,
        source_realizations=tuple(sources),
        destination_realizations=tuple(destinations),
    )


def snapshot(*items, scope="scope-1", as_of=AS_OF, authority="read-auth"):
    return SuccessfulExportSnapshot(
        scope=scope,
        as_of=as_of,
        authority_reference=authority,
        items=tuple(items),
    )


class FakeDecoder:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def decode(self, payload):
        self.calls.append(payload)
        return self.responses[payload]


class FailingDecoder:
    def decode(self, payload):
        raise DcsProjectionDecodeError("unsupported payload")


def any_ports():
    return PortConstraint.any()


def na_ports():
    return PortConstraint.not_applicable()


def alt(
    protocol="tcp",
    source_ports=None,
    destination_ports=None,
    service_reference=None,
):
    return DcsTrafficAlternative(
        protocol=protocol,
        source_ports=source_ports or any_ports(),
        destination_ports=destination_ports or PortConstraint.ranged(
            PortRange(443, 443)
        ),
        service_reference=service_reference,
    )


@pytest.mark.parametrize(
    "first,last",
    [
        (-1, 1),
        (0, 65536),
        (100, 99),
    ],
)
def test_port_range_rejects_invalid_boundaries(first, last):
    with pytest.raises(NormalizationInvariantError):
        PortRange(first, last)


def test_port_range_set_is_canonicalized_without_enumerating_ports():
    constraint = PortConstraint.ranged(
        PortRange(200, 210),
        PortRange(80, 90),
        PortRange(91, 100),
        PortRange(205, 220),
        PortRange(150, 160),
    )

    assert constraint.kind is PortConstraintKind.RANGES
    assert constraint.ranges == (
        PortRange(80, 100),
        PortRange(150, 160),
        PortRange(200, 220),
    )


@pytest.mark.parametrize(
    "kind",
    [PortConstraintKind.ANY, PortConstraintKind.NOT_APPLICABLE],
)
def test_any_and_not_applicable_cannot_carry_ranges(kind):
    with pytest.raises(NormalizationInvariantError):
        PortConstraint(kind, (PortRange(80, 80),))


def test_any_and_not_applicable_are_distinct_semantics():
    assert any_ports() != na_ports()
    assert any_ports().kind is PortConstraintKind.ANY
    assert na_ports().kind is PortConstraintKind.NOT_APPLICABLE


@pytest.mark.parametrize("protocol", ["", " tcp", "tcp "])
def test_protocol_token_must_be_non_empty_and_already_canonical(protocol):
    with pytest.raises(NormalizationInvariantError):
        alt(protocol=protocol)


def test_empty_service_reference_is_rejected():
    with pytest.raises(NormalizationInvariantError):
        alt(service_reference="")


def test_single_snapshot_item_normalizes_to_complete_explainable_row():
    rule = active_rule(
        window=EffectiveWindow(
            AS_OF - timedelta(hours=1),
            AS_OF + timedelta(hours=1),
        )
    )
    traffic = DcsTrafficAlternative(
        protocol="tcp",
        source_ports=PortConstraint.ranged(PortRange(1024, 65535)),
        destination_ports=PortConstraint.ranged(PortRange(443, 443)),
        service_reference="https-service",
    )
    decoder = FakeDecoder({b"dcs-a": (traffic,)})

    result = NormalizeExportSnapshot(decoder=decoder).execute(
        snapshot(item(rule))
    )

    assert result.scope == "scope-1"
    assert result.as_of == AS_OF
    assert result.authority_reference == "read-auth"
    assert decoder.calls == [b"dcs-a"]
    assert len(result.rows) == 1

    row = result.rows[0]
    assert row.rule_id == rule.rule_id
    assert row.rule_semantic_identity == rule.semantic_identity
    assert row.decision_reference == "decision-1"
    assert row.rule_governance_scope == "scope-1"
    assert row.rule_operational_state is OperationalState.ACTIVE
    assert row.rule_effective_window == rule.effective_window
    assert row.snapshot_as_of == AS_OF
    assert row.read_authority_reference == "read-auth"

    assert row.source_resource_reference == ref("src")
    assert row.source_endpoint_reference == "src-endpoint"
    assert row.source_technical_address == "198.51.100.10"
    assert row.source_fact_reference == "src-fact"
    assert row.source_validity_reference == "src-validity"
    assert row.source_provenance_reference == "src-provenance"

    assert row.destination_resource_reference == ref("dst")
    assert row.destination_endpoint_reference == "dst-endpoint"
    assert row.destination_technical_address == "203.0.113.20"
    assert row.destination_fact_reference == "dst-fact"
    assert row.destination_validity_reference == "dst-validity"
    assert row.destination_provenance_reference == "dst-provenance"

    assert row.protocol == "tcp"
    assert row.source_ports == PortConstraint.ranged(PortRange(1024, 65535))
    assert row.destination_ports == PortConstraint.ranged(PortRange(443, 443))
    assert row.service_reference == "https-service"
    assert row.acc_fact_reference == "acc-fact-1"
    assert row.acc_validity_reference == "acc-validity-1"
    assert row.acc_provenance_reference == "acc-provenance-1"

    with pytest.raises(FrozenInstanceError):
        row.protocol = "udp"
    with pytest.raises(FrozenInstanceError):
        result.scope = "other"


def test_non_port_protocol_preserves_not_applicable_distinct_from_any():
    rule = active_rule()
    traffic = DcsTrafficAlternative(
        protocol="ip-protocol-x",
        source_ports=na_ports(),
        destination_ports=na_ports(),
    )
    result = NormalizeExportSnapshot(
        decoder=FakeDecoder({b"dcs-a": (traffic,)})
    ).execute(snapshot(item(rule)))

    assert result.rows[0].source_ports is traffic.source_ports
    assert result.rows[0].destination_ports is traffic.destination_ports
    assert result.rows[0].source_ports != any_ports()


def test_expansion_is_exact_source_x_destination_x_dcs_product():
    rule = active_rule()
    sources = (
        captured(
            "src-b",
            ("src-b-2", "198.51.100.22"),
            ("src-b-1", "198.51.100.21"),
        ),
        captured("src-a", ("src-a-1", "198.51.100.11")),
    )
    destinations = (
        captured("dst-b", ("dst-b-1", "203.0.113.22")),
        captured("dst-a", ("dst-a-1", "203.0.113.11")),
    )
    alternatives = (
        alt(
            protocol="udp",
            source_ports=any_ports(),
            destination_ports=PortConstraint.ranged(PortRange(53, 53)),
            service_reference="dns",
        ),
        alt(
            protocol="tcp",
            source_ports=PortConstraint.ranged(
                PortRange(2000, 2010),
                PortRange(1000, 1005),
            ),
            destination_ports=PortConstraint.ranged(PortRange(443, 443)),
            service_reference="https",
        ),
    )

    result = NormalizeExportSnapshot(
        decoder=FakeDecoder({b"dcs-a": alternatives})
    ).execute(
        snapshot(
            item(
                rule,
                sources=sources,
                destinations=destinations,
            )
        )
    )

    assert len(result.rows) == 3 * 2 * 2
    keys = [
        (
            row.source_resource_reference.value,
            row.source_endpoint_reference,
            row.source_technical_address,
            row.destination_resource_reference.value,
            row.destination_endpoint_reference,
            row.destination_technical_address,
            row.protocol,
            row.service_reference,
        )
        for row in result.rows
    ]
    assert keys == sorted(keys)
    assert {row.protocol for row in result.rows} == {"tcp", "udp"}
    assert all(row.rule_id == rule.rule_id for row in result.rows)


def test_range_semantics_remain_ranges_in_every_expanded_row():
    rule = active_rule()
    ports = PortConstraint.ranged(
        PortRange(1000, 1999),
        PortRange(443, 443),
    )
    traffic = alt(destination_ports=ports)

    result = NormalizeExportSnapshot(
        decoder=FakeDecoder({b"dcs-a": (traffic,)})
    ).execute(snapshot(item(rule)))

    assert result.rows[0].destination_ports.ranges == (
        PortRange(443, 443),
        PortRange(1000, 1999),
    )


def test_independent_rules_with_equivalent_technical_effects_remain_independent():
    first = active_rule(rule_id=1)
    second = active_rule(rule_id=2)
    traffic = alt()
    decoder = FakeDecoder(
        {
            b"dcs-first": (traffic,),
            b"dcs-second": (traffic,),
        }
    )
    shared_source = (
        captured("src", ("src-endpoint", "198.51.100.10")),
    )
    shared_destination = (
        captured("dst", ("dst-endpoint", "203.0.113.20")),
    )

    result = NormalizeExportSnapshot(decoder=decoder).execute(
        snapshot(
            item(
                second,
                payload=b"dcs-second",
                sources=shared_source,
                destinations=shared_destination,
            ),
            item(
                first,
                payload=b"dcs-first",
                sources=shared_source,
                destinations=shared_destination,
            ),
        )
    )

    assert len(result.rows) == 2
    assert tuple(row.rule_id for row in result.rows) == (
        UUID(int=1),
        UUID(int=2),
    )
    assert result.rows[0].decision_reference == "decision-1"
    assert result.rows[1].decision_reference == "decision-2"


def test_empty_snapshot_normalizes_to_empty_success_without_decoder_call():
    decoder = FakeDecoder({})

    result = NormalizeExportSnapshot(decoder=decoder).execute(snapshot())

    assert result.rows == ()
    assert decoder.calls == []


def test_decoder_failure_prevents_success():
    with pytest.raises(
        NormalizationInvariantError,
        match="cannot be normalized",
    ):
        NormalizeExportSnapshot(decoder=FailingDecoder()).execute(
            snapshot(item(active_rule()))
        )


@pytest.mark.parametrize("decoded", [(), ("wrong-type",)])
def test_decoder_must_return_one_or_more_valid_alternatives(decoded):
    with pytest.raises(
        NormalizationInvariantError,
        match="one-or-more",
    ):
        NormalizeExportSnapshot(
            decoder=FakeDecoder({b"dcs-a": decoded})
        ).execute(snapshot(item(active_rule())))


@pytest.mark.parametrize(
    "bad_snapshot",
    [
        lambda value: replace(value, scope=""),
        lambda value: replace(value, authority_reference=""),
        lambda value: replace(value, as_of=AS_OF.replace(tzinfo=None)),
    ],
)
def test_invalid_snapshot_metadata_fails_closed(bad_snapshot):
    value = snapshot(item(active_rule()))

    with pytest.raises(NormalizationInvariantError):
        NormalizeExportSnapshot(
            decoder=FakeDecoder({b"dcs-a": (alt(),)})
        ).execute(bad_snapshot(value))


def test_duplicate_rule_in_snapshot_fails_closed():
    rule = active_rule()
    value = snapshot(item(rule), item(rule))

    with pytest.raises(
        NormalizationInvariantError,
        match="same authoritative Rule twice",
    ):
        NormalizeExportSnapshot(
            decoder=FakeDecoder({b"dcs-a": (alt(),)})
        ).execute(value)


def test_rule_outside_snapshot_scope_fails_closed():
    value = snapshot(item(active_rule(scope="scope-2")), scope="scope-1")

    with pytest.raises(
        NormalizationInvariantError,
        match="outside its effective authorized selection",
    ):
        NormalizeExportSnapshot(
            decoder=FakeDecoder({b"dcs-a": (alt(),)})
        ).execute(value)


def test_non_effective_rule_in_snapshot_fails_closed():
    rule = active_rule().with_operational_state(
        target_state=OperationalState.INACTIVE,
        actor_id="state-admin",
        effective_time=NOW,
        authority_reference="state-auth",
    )

    with pytest.raises(
        NormalizationInvariantError,
        match="outside its effective authorized selection",
    ):
        NormalizeExportSnapshot(
            decoder=FakeDecoder({b"dcs-a": (alt(),)})
        ).execute(snapshot(item(rule)))


def test_acc_subject_correlation_is_rechecked():
    rule = active_rule()
    snapshot_item = item(rule)
    wrong_identity = RuleSemanticIdentity(UUID(int=99), UUID(int=100), UUID(int=101))
    wrong_application = replace(
        snapshot_item.application_projection,
        subject=wrong_identity,
    )
    value = snapshot(replace(snapshot_item, application_projection=wrong_application))

    with pytest.raises(
        NormalizationInvariantError,
        match="application projection",
    ):
        NormalizeExportSnapshot(
            decoder=FakeDecoder({b"dcs-a": (alt(),)})
        ).execute(value)


def test_captured_resource_references_must_match_acc_binding_exactly():
    rule = active_rule()
    snapshot_item = item(rule)
    wrong_source = (
        captured("other-src", ("endpoint", "198.51.100.99")),
    )
    value = snapshot(replace(snapshot_item, source_realizations=wrong_source))

    with pytest.raises(
        NormalizationInvariantError,
        match="source realization set",
    ):
        NormalizeExportSnapshot(
            decoder=FakeDecoder({b"dcs-a": (alt(),)})
        ).execute(value)


def test_incomplete_captured_endpoint_fails_closed():
    rule = active_rule()
    broken_source = (
        captured("src", ("", "198.51.100.10")),
    )

    with pytest.raises(
        NormalizationInvariantError,
        match="endpoint realization",
    ):
        NormalizeExportSnapshot(
            decoder=FakeDecoder({b"dcs-a": (alt(),)})
        ).execute(snapshot(item(rule, sources=broken_source)))
