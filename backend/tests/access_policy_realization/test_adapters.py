from datetime import datetime, timedelta, timezone
from uuid import UUID

from napms.contexts.access_policy_realization.infrastructure.integrations.catalogues import (
    CatalogueDomainKnowledgeAdapter,
)
from napms.contexts.access_policy_realization.infrastructure.integrations.technical_access_evidence import (
    TechnicalAccessEvidenceProjectionAdapter,
)
from napms.contexts.access_policy_realization.application.resolve import (
    ResolveTechnicalAccess,
)
from napms.contexts.access_policy_realization.domain.model import (
    AddressConstraint,
    AddressRange,
    PortConstraint,
    PortRange,
    ProtocolSelector,
    ResolutionStatus,
    TechnicalAccessPredicate,
)
from napms.contexts.application_catalogue.domain.model import (
    DcsRevision,
    DeploymentResourceBinding,
)
from napms.policy_export.application.normalization_ports import (
    DcsProjectionDecodeError,
)
from napms.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    PortConstraint as DcsPortConstraint,
    PortRange as DcsPortRange,
)
from napms.contexts.resource_catalogue.domain.model import (
    EndpointAddress,
    ResourceRealizationVersion,
)
from napms.contexts.technical_access_evidence.domain.model import (
    AddressConstraint as TaeAddressConstraint,
    AddressRange as TaeAddressRange,
    EvidenceAction,
    EvidenceKind,
    EvidenceSourceReference,
    EvidenceTime,
    PortConstraint as TaePortConstraint,
    PortRange as TaePortRange,
    ProtocolSelector as TaeProtocolSelector,
    SourceCaptureReference,
    SourceScopeReference,
    TechnicalAccessEntry,
    TechnicalAccessEntryPayload,
    TechnicalAccessEvidenceSet,
    TechnicalAccessPredicate as TaeTechnicalAccessPredicate,
)


NOW = datetime(
    2026,
    9,
    9,
    12,
    tzinfo=timezone.utc,
)
SOURCE_ID = UUID(int=1)
DESTINATION_ID = UUID(int=2)
DCS_ID = UUID(int=3)


class FakeApplicationCatalogue:
    def __init__(
        self,
        *,
        revisions,
        bindings,
    ):
        self.revisions = tuple(revisions)
        self.bindings = bindings

    def list_dcs_revisions(
        self,
        *,
        offset,
        limit,
        search=None,
    ):
        assert search is None
        return self.revisions[
            offset : offset + limit
        ]

    def find_effective_bindings(
        self,
        *,
        component_deployment_id,
        as_of,
    ):
        assert as_of == NOW
        return self.bindings.get(
            component_deployment_id,
            (),
        )


class FakeResourceCatalogue:
    def __init__(
        self,
        *,
        realizations,
        has_facts=(),
    ):
        self.realizations = realizations
        self.has_facts = set(has_facts)

    def find_effective_realizations(
        self,
        *,
        resource_reference,
        as_of,
    ):
        assert as_of == NOW
        return self.realizations.get(
            resource_reference,
            (),
        )

    def has_realization_facts(
        self,
        *,
        resource_reference,
    ):
        return (
            resource_reference
            in self.has_facts
        )


class FakeDecoder:
    def __init__(
        self,
        alternatives,
    ):
        self.alternatives = alternatives
        self.calls = 0

    def decode(self, payload):
        assert payload == b"dcs"
        self.calls += 1
        if isinstance(
            self.alternatives,
            Exception,
        ):
            raise self.alternatives
        return self.alternatives


def dcs():
    return DcsRevision(
        revision_id=DCS_ID,
        source_component_deployment_id=SOURCE_ID,
        destination_component_deployment_id=DESTINATION_ID,
        projection_payload=b"dcs",
        provenance_reference="acc:dcs",
    )


def binding(
    *,
    reference,
    component,
    resource,
):
    return DeploymentResourceBinding(
        reference_id=reference,
        component_deployment_id=component,
        resource_reference=resource,
        valid_from=NOW
        - timedelta(days=1),
        valid_to=None,
        provenance_reference=(
            "acc:" + reference
        ),
    )


def realization(
    *,
    reference,
    resource,
    address,
):
    return ResourceRealizationVersion(
        fact_reference=reference,
        resource_reference=resource,
        endpoint_realizations=(
            EndpointAddress(
                endpoint_reference=(
                    "endpoint:" + resource
                ),
                technical_address=address,
            ),
        ),
        valid_from=NOW
        - timedelta(days=1),
        valid_to=None,
        provenance_reference=(
            "rc:" + reference
        ),
    )


def predicate():
    return TechnicalAccessPredicate(
        source_addresses=(
            AddressConstraint.ranged(
                AddressRange(
                    "10.0.0.1",
                    "10.0.0.1",
                )
            )
        ),
        destination_addresses=(
            AddressConstraint.ranged(
                AddressRange(
                    "10.0.0.2",
                    "10.0.0.2",
                )
            )
        ),
        protocol=(
            ProtocolSelector.ip_protocol(6)
        ),
        source_ports=(
            PortConstraint.any()
        ),
        destination_ports=(
            PortConstraint.ranged(
                PortRange(443, 443)
            )
        ),
    )


def catalogues(
    *,
    source_address="10.0.0.1",
    destination_address="10.0.0.2",
    decoder=None,
    source_realizations=None,
    destination_realizations=None,
):
    source_binding = binding(
        reference="binding:source",
        component=SOURCE_ID,
        resource="resource:source",
    )
    destination_binding = binding(
        reference="binding:destination",
        component=DESTINATION_ID,
        resource="resource:destination",
    )
    application = FakeApplicationCatalogue(
        revisions=(dcs(),),
        bindings={
            SOURCE_ID: (source_binding,),
            DESTINATION_ID: (
                destination_binding,
            ),
        },
    )
    resource = FakeResourceCatalogue(
        realizations={
            "resource:source": (
                realization(
                    reference="fact:source",
                    resource="resource:source",
                    address=source_address,
                ),
            )
            if source_realizations
            is None
            else source_realizations,
            "resource:destination": (
                realization(
                    reference="fact:destination",
                    resource=(
                        "resource:destination"
                    ),
                    address=(
                        destination_address
                    ),
                ),
            )
            if destination_realizations
            is None
            else destination_realizations,
        },
    )
    decoder = decoder or FakeDecoder(
        (
            DcsTrafficAlternative(
                protocol="tcp",
                source_ports=(
                    DcsPortConstraint.any()
                ),
                destination_ports=(
                    DcsPortConstraint.ranged(
                        DcsPortRange(
                            443,
                            443,
                        )
                    )
                ),
            ),
        )
    )
    return (
        CatalogueDomainKnowledgeAdapter(
            application_catalogue=application,
            resource_catalogue=resource,
            dcs_decoder=decoder,
        ),
        decoder,
    )


def test_catalogue_adapter_drives_exact_core_resolution():
    adapter, decoder = catalogues()

    result = ResolveTechnicalAccess(
        domain_knowledge=adapter
    ).execute(
        predicate=predicate(),
        as_of=NOW,
    )

    assert (
        result.status
        is ResolutionStatus.EXACT
    )
    assert decoder.calls == 1
    assert (
        result.correspondences[
            0
        ].interaction.dcs_contract_revision_id
        == DCS_ID
    )
    assert any(
        value.startswith(
            "dcs-provenance:"
        )
        for value
        in result.correspondences[
            0
        ].provenance.acc_references
    )


def test_disjoint_unsupported_dcs_does_not_create_unknown():
    decoder = FakeDecoder(
        DcsProjectionDecodeError()
    )
    adapter, decoder = catalogues(
        source_address="192.0.2.1",
        destination_address="192.0.2.2",
        decoder=decoder,
    )

    result = ResolveTechnicalAccess(
        domain_knowledge=adapter
    ).execute(
        predicate=predicate(),
        as_of=NOW,
    )

    assert (
        result.status
        is ResolutionStatus.UNRESOLVED
    )
    assert decoder.calls == 0
    assert (
        result.knowledge_gaps
        == ()
    )


def test_relevant_unsupported_protocol_is_unknown():
    decoder = FakeDecoder(
        (
            DcsTrafficAlternative(
                protocol="protocol-x",
                source_ports=(
                    DcsPortConstraint.any()
                ),
                destination_ports=(
                    DcsPortConstraint.any()
                ),
            ),
        )
    )
    adapter, _ = catalogues(
        decoder=decoder
    )

    result = ResolveTechnicalAccess(
        domain_knowledge=adapter
    ).execute(
        predicate=predicate(),
        as_of=NOW,
    )

    assert (
        result.status
        is ResolutionStatus.UNKNOWN
    )
    assert any(
        value.reason
        == "UnsupportedDcsProtocol:protocol-x"
        for value
        in result.knowledge_gaps
    )


def test_effective_binding_without_resource_realization_is_unknown():
    adapter, _ = catalogues(
        destination_realizations=(),
    )

    result = ResolveTechnicalAccess(
        domain_knowledge=adapter
    ).execute(
        predicate=predicate(),
        as_of=NOW,
    )

    assert (
        result.status
        is ResolutionStatus.UNKNOWN
    )
    assert any(
        value.owner
        == "Resource Catalogue"
        for value
        in result.knowledge_gaps
    )


def test_missing_source_realization_is_ignored_when_destination_is_disjoint():
    adapter, decoder = catalogues(
        source_realizations=(),
        destination_address="192.0.2.2",
    )

    result = ResolveTechnicalAccess(
        domain_knowledge=adapter
    ).execute(
        predicate=predicate(),
        as_of=NOW,
    )

    assert (
        result.status
        is ResolutionStatus.UNRESOLVED
    )
    assert result.knowledge_gaps == ()
    assert decoder.calls == 0


def test_missing_destination_realization_is_ignored_when_source_is_disjoint():
    adapter, decoder = catalogues(
        source_address="192.0.2.1",
        destination_realizations=(),
    )

    result = ResolveTechnicalAccess(
        domain_knowledge=adapter
    ).execute(
        predicate=predicate(),
        as_of=NOW,
    )

    assert (
        result.status
        is ResolutionStatus.UNRESOLVED
    )
    assert result.knowledge_gaps == ()
    assert decoder.calls == 0


def test_tae_projection_preserves_source_qualified_provenance():
    entry_id = UUID(int=20)
    evidence = TechnicalAccessEvidenceSet(
        evidence_set_id=UUID(int=10),
        kind=EvidenceKind.IMPORTED,
        source=EvidenceSourceReference(
            "local-import",
            "fixture",
        ),
        source_scope=SourceScopeReference(
            "scope-a"
        ),
        source_capture_reference=(
            SourceCaptureReference(
                "capture-a"
            )
        ),
        evidence_time=EvidenceTime.unknown(),
        recorded_at=NOW,
        entries=(
            TechnicalAccessEntry(
                evidence_entry_id=entry_id,
                payload=(
                    TechnicalAccessEntryPayload(
                        predicate=(
                            TaeTechnicalAccessPredicate(
                                source_addresses=(
                                    TaeAddressConstraint.ranged(
                                        TaeAddressRange(
                                            "10.0.0.1",
                                            "10.0.0.1",
                                        )
                                    )
                                ),
                                destination_addresses=(
                                    TaeAddressConstraint.ranged(
                                        TaeAddressRange(
                                            "10.0.0.2",
                                            "10.0.0.2",
                                        )
                                    )
                                ),
                                protocol=(
                                    TaeProtocolSelector.ip_protocol(
                                        6
                                    )
                                ),
                                source_ports=(
                                    TaePortConstraint.any()
                                ),
                                destination_ports=(
                                    TaePortConstraint.ranged(
                                        TaePortRange(
                                            443,
                                            443,
                                        )
                                    )
                                ),
                            )
                        ),
                        action=(
                            EvidenceAction.BLOCK
                        ),
                        source_entry_reference=(
                            "rule-7"
                        ),
                        source_position=7,
                    )
                ),
            ),
        ),
    )

    projected = (
        TechnicalAccessEvidenceProjectionAdapter()
        .project_entry(
            evidence_set=evidence,
            evidence_entry_id=entry_id,
        )
    )

    assert (
        projected.predicate.protocol.number
        == 6
    )
    assert (
        projected.predicate.destination_ports.ranges[
            0
        ].first
        == 443
    )
    assert (
        "tae-action:Block"
        in projected.input_provenance.references
    )
    assert (
        "tae-evidence-time:Unknown"
        in projected.input_provenance.references
    )
    assert any(
        value.startswith(
            "tae-recorded-at:"
        )
        for value
        in projected.input_provenance.references
    )
