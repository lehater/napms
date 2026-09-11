from datetime import datetime, timezone
from uuid import UUID

from napms.contexts.access_policy_realization.infrastructure.rendering.cisco_asa import CiscoAsaAclRenderer
from napms.contexts.access_policy_realization.infrastructure.rendering.cisco_asa_semantics import (
    project_asa_permit_regions,
)
from napms.contexts.access_policy_realization.application.render import RenderConfiguration
from napms.contexts.access_policy_realization.domain.model import (
    AddressRange,
    DomainInteractionIdentity,
    PortRegion,
    TechnicalRegionFragment,
)
from napms.contexts.access_policy_realization.domain.realization import (
    DesiredDerivationStatus,
    DesiredEnforcementIntent,
    DesiredEnforcementPolicy,
    EnforcementTarget,
)
from napms.contexts.access_policy_realization.domain.rendering import RenderStatus


def _policy(fragment: TechnicalRegionFragment) -> DesiredEnforcementPolicy:
    interaction = DomainInteractionIdentity(
        source_component_deployment_id=UUID("00000000-0000-0000-0000-000000000001"),
        destination_component_deployment_id=UUID("00000000-0000-0000-0000-000000000002"),
        dcs_contract_revision_id=UUID("00000000-0000-0000-0000-000000000003"),
    )
    target = EnforcementTarget(
        logical_firewall_id=UUID("00000000-0000-0000-0000-000000000010"),
        enforcement_attachment_id=UUID("00000000-0000-0000-0000-000000000011"),
    )
    return DesiredEnforcementPolicy(
        governance_scope="scope-a",
        as_of=datetime(2026, 9, 10, tzinfo=timezone.utc),
        desired_interactions=(interaction,),
        status=DesiredDerivationStatus.DERIVED,
        intents=(
            DesiredEnforcementIntent(
                target=target,
                fragment=fragment,
                rule_references=("rule-1",),
                interactions=(interaction,),
                placement_provenance_references=("placement-1",),
            ),
        ),
    )


def test_cisco_asa_renderer_preserves_supported_region_exactly() -> None:
    fragment = TechnicalRegionFragment(
        source_address=AddressRange("10.0.0.0", "10.0.0.255"),
        destination_address=AddressRange("192.0.2.10", "192.0.2.10"),
        protocol_number=6,
        source_ports=PortRegion.numeric(0, 65535),
        destination_ports=PortRegion.numeric(443, 443),
    )
    policy = _policy(fragment)

    (result,) = RenderConfiguration(CiscoAsaAclRenderer()).execute(policy)

    assert result.status is RenderStatus.RENDERED
    assert result.content == (
        "access-list NAPMS extended permit tcp "
        "10.0.0.0 255.255.255.0 host 192.0.2.10 eq 443\n"
    )
    assert project_asa_permit_regions(result.content) == (fragment,)
    assert result.statements[0].rule_references == ("rule-1",)


def test_semantic_projector_detects_broadening() -> None:
    fragment = TechnicalRegionFragment(
        source_address=AddressRange("10.0.0.1", "10.0.0.1"),
        destination_address=AddressRange("192.0.2.10", "192.0.2.10"),
        protocol_number=6,
        source_ports=PortRegion.numeric(0, 65535),
        destination_ports=PortRegion.numeric(443, 443),
    )
    policy = _policy(fragment)
    (result,) = RenderConfiguration(CiscoAsaAclRenderer()).execute(policy)
    assert result.content is not None

    broadened = result.content.replace("host 10.0.0.1", "10.0.0.0 255.255.255.0")

    assert project_asa_permit_regions(broadened) != (fragment,)


def test_cisco_asa_renderer_fails_closed_for_unsupported_protocol() -> None:
    policy = _policy(
        TechnicalRegionFragment(
            source_address=AddressRange("10.0.0.1", "10.0.0.1"),
            destination_address=AddressRange("192.0.2.10", "192.0.2.10"),
            protocol_number=1,
            source_ports=PortRegion.not_applicable(),
            destination_ports=PortRegion.not_applicable(),
        )
    )

    (result,) = RenderConfiguration(CiscoAsaAclRenderer()).execute(policy)

    assert result.status is RenderStatus.UNSUPPORTED
    assert result.content is None
    assert result.statements == ()
