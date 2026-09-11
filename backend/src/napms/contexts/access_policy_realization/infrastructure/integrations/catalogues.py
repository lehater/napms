from dataclasses import dataclass
from ipaddress import ip_address
from itertools import product

from napms.contexts.access_policy_realization.domain.model import (
    AddressConstraint,
    AddressConstraintKind,
    AddressRange,
    DomainInteractionIdentity,
    DomainInteractionRegion,
    DomainKnowledgeSnapshot,
    DomainRegionProvenance,
    KnowledgeGap,
    PortRegion,
    ProtocolSelectorKind,
    TechnicalAccessPredicate,
    TechnicalRegionFragment,
    require_aware,
)
from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueRepository,
)
from napms.contexts.application_catalogue.domain.model import (
    DcsRevision,
    DeploymentResourceBinding,
)
from napms.policy_export.application.normalization_ports import (
    DcsProjectionDecodeError,
    DcsProjectionDecoder,
)
from napms.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    PortConstraint,
    PortConstraintKind,
)
from napms.contexts.resource_catalogue.application.ports import (
    ResourceCatalogueRepository,
)
from napms.contexts.resource_catalogue.domain.model import (
    ResourceRealizationVersion,
)


_PROTOCOL_NUMBERS = {
    "tcp": 6,
    "udp": 17,
}


@dataclass(frozen=True, slots=True)
class _ResolvedEndpoint:
    binding: DeploymentResourceBinding
    realization: ResourceRealizationVersion
    endpoint_reference: str
    technical_address: str


class CatalogueDomainKnowledgeAdapter:
    def __init__(
        self,
        *,
        application_catalogue: ApplicationCatalogueRepository,
        resource_catalogue: ResourceCatalogueRepository,
        dcs_decoder: DcsProjectionDecoder,
        page_size: int = 200,
    ) -> None:
        if page_size < 1:
            raise ValueError("page_size must be positive")
        self._application_catalogue = application_catalogue
        self._resource_catalogue = resource_catalogue
        self._dcs_decoder = dcs_decoder
        self._page_size = page_size

    def load_for(
        self,
        *,
        predicate: TechnicalAccessPredicate,
        as_of,
    ) -> DomainKnowledgeSnapshot:
        require_aware(as_of)
        if (
            predicate.protocol.kind
            is ProtocolSelectorKind.ANY
        ):
            return DomainKnowledgeSnapshot(
                (),
                (
                    KnowledgeGap(
                        owner="Access Policy Realization",
                        reason="ProtocolAnyAlgebraUnsupported",
                    ),
                ),
                False,
            )

        regions: list[DomainInteractionRegion] = []
        gaps: list[KnowledgeGap] = []

        for dcs in self._list_dcs_revisions():
            (
                relevant_sources,
                source_gaps,
            ) = self._resolve_relevant_side(
                dcs=dcs,
                component_deployment_id=(
                    dcs.source_component_deployment_id
                ),
                constraint=predicate.source_addresses,
                as_of=as_of,
                side="source",
            )
            (
                relevant_destinations,
                destination_gaps,
            ) = self._resolve_relevant_side(
                dcs=dcs,
                component_deployment_id=(
                    dcs.destination_component_deployment_id
                ),
                constraint=predicate.destination_addresses,
                as_of=as_of,
                side="destination",
            )

            # A completely known disjoint side proves the whole
            # directed candidate disjoint, so uncertainty on the
            # opposite side is predicate-irrelevant.
            if relevant_sources == () or relevant_destinations == ():
                continue

            if (
                relevant_sources is None
                or relevant_destinations is None
            ):
                gaps.extend(source_gaps)
                gaps.extend(destination_gaps)
                continue

            try:
                alternatives = self._dcs_decoder.decode(
                    dcs.projection_payload
                )
            except DcsProjectionDecodeError:
                gaps.append(
                    self._gap(
                        dcs,
                        "UntranslatableDcsProjection",
                    )
                )
                continue

            if (
                not alternatives
                or any(
                    not isinstance(
                        alternative,
                        DcsTrafficAlternative,
                    )
                    for alternative in alternatives
                )
            ):
                gaps.append(
                    self._gap(
                        dcs,
                        "InvalidDcsProjection",
                    )
                )
                continue

            for alternative in alternatives:
                protocol_number = _PROTOCOL_NUMBERS.get(
                    alternative.protocol
                )
                if protocol_number is None:
                    gaps.append(
                        self._gap(
                            dcs,
                            (
                                "UnsupportedDcsProtocol:"
                                + alternative.protocol
                            ),
                        )
                    )
                    continue
                assert predicate.protocol.number is not None
                if (
                    protocol_number
                    != predicate.protocol.number
                ):
                    continue

                source_ports = _port_regions(
                    alternative.source_ports
                )
                destination_ports = _port_regions(
                    alternative.destination_ports
                )

                for (
                    source,
                    destination,
                    source_port,
                    destination_port,
                ) in product(
                    relevant_sources,
                    relevant_destinations,
                    source_ports,
                    destination_ports,
                ):
                    regions.append(
                        DomainInteractionRegion(
                            interaction=(
                                DomainInteractionIdentity(
                                    (
                                        dcs.source_component_deployment_id
                                    ),
                                    (
                                        dcs.destination_component_deployment_id
                                    ),
                                    dcs.revision_id,
                                )
                            ),
                            fragment=TechnicalRegionFragment(
                                source_address=_single_address(
                                    source.technical_address
                                ),
                                destination_address=_single_address(
                                    destination.technical_address
                                ),
                                protocol_number=protocol_number,
                                source_ports=source_port,
                                destination_ports=destination_port,
                            ),
                            provenance=_provenance(
                                dcs=dcs,
                                source=source,
                                destination=destination,
                                service_reference=(
                                    alternative.service_reference
                                ),
                            ),
                        )
                    )

        canonical_gaps = tuple(
            sorted(
                set(gaps),
                key=lambda value: (
                    value.owner,
                    value.reason,
                    value.references,
                ),
            )
        )
        return DomainKnowledgeSnapshot(
            regions=tuple(regions),
            knowledge_gaps=canonical_gaps,
            complete_for_predicate=not canonical_gaps,
        )

    def _list_dcs_revisions(
        self,
    ) -> tuple[DcsRevision, ...]:
        offset = 0
        result: list[DcsRevision] = []
        while True:
            page = (
                self._application_catalogue.list_dcs_revisions(
                    offset=offset,
                    limit=self._page_size,
                )
            )
            result.extend(page)
            if len(page) < self._page_size:
                return tuple(result)
            offset += len(page)

    def _resolve_relevant_side(
        self,
        *,
        dcs: DcsRevision,
        component_deployment_id,
        constraint: AddressConstraint,
        as_of,
        side: str,
    ) -> tuple[
        tuple[_ResolvedEndpoint, ...] | None,
        tuple[KnowledgeGap, ...],
    ]:
        local_gaps: list[KnowledgeGap] = []
        bindings = self._load_bindings(
            dcs=dcs,
            component_deployment_id=component_deployment_id,
            as_of=as_of,
            side=side,
            gaps=local_gaps,
        )
        if bindings is None:
            return None, tuple(local_gaps)
        if not bindings:
            return (), ()

        endpoints = self._resolve_bindings(
            dcs=dcs,
            bindings=bindings,
            as_of=as_of,
            side=side,
            gaps=local_gaps,
        )
        if endpoints is None:
            return None, tuple(local_gaps)

        relevant = self._relevant_endpoints(
            constraint,
            endpoints,
            dcs=dcs,
            side=side,
            gaps=local_gaps,
        )
        if relevant is None:
            return None, tuple(local_gaps)
        return relevant, ()

    def _load_bindings(
        self,
        *,
        dcs: DcsRevision,
        component_deployment_id,
        as_of,
        side: str,
        gaps: list[KnowledgeGap],
    ) -> tuple[DeploymentResourceBinding, ...] | None:
        bindings = (
            self._application_catalogue.find_effective_bindings(
                component_deployment_id=(
                    component_deployment_id
                ),
                as_of=as_of,
            )
        )
        seen_resources: set[str] = set()
        for binding in bindings:
            if (
                binding.component_deployment_id
                != component_deployment_id
                or not binding.is_effective_at(as_of)
                or binding.resource_reference
                in seen_resources
            ):
                gaps.append(
                    self._gap(
                        dcs,
                        (
                            "InvalidEffective"
                            + side.title()
                            + "Binding"
                        ),
                        references=(
                            binding.reference_id,
                        ),
                    )
                )
                return None
            seen_resources.add(
                binding.resource_reference
            )
        return tuple(bindings)

    def _resolve_bindings(
        self,
        *,
        dcs: DcsRevision,
        bindings: tuple[
            DeploymentResourceBinding,
            ...,
        ],
        as_of,
        side: str,
        gaps: list[KnowledgeGap],
    ) -> tuple[_ResolvedEndpoint, ...] | None:
        endpoints: list[_ResolvedEndpoint] = []
        for binding in bindings:
            matches = (
                self._resource_catalogue.find_effective_realizations(
                    resource_reference=(
                        binding.resource_reference
                    ),
                    as_of=as_of,
                )
            )
            if len(matches) != 1:
                reason = (
                    "MissingResourceRealization"
                    if not matches
                    and not self._resource_catalogue.has_realization_facts(
                        resource_reference=(
                            binding.resource_reference
                        )
                    )
                    else (
                        "StaleResourceRealization"
                        if not matches
                        else "NonUniqueResourceRealization"
                    )
                )
                gaps.append(
                    self._gap(
                        dcs,
                        (
                            side.title()
                            + reason
                        ),
                        references=(
                            binding.reference_id,
                            binding.resource_reference,
                        ),
                        owner="Resource Catalogue",
                    )
                )
                return None

            realization = matches[0]
            if (
                realization.resource_reference
                != binding.resource_reference
                or not realization.is_effective_at(
                    as_of
                )
            ):
                gaps.append(
                    self._gap(
                        dcs,
                        (
                            side.title()
                            + "InvalidResourceRealization"
                        ),
                        references=(
                            binding.reference_id,
                            binding.resource_reference,
                            realization.fact_reference,
                        ),
                        owner="Resource Catalogue",
                    )
                )
                return None

            for endpoint in (
                realization.endpoint_realizations
            ):
                endpoints.append(
                    _ResolvedEndpoint(
                        binding=binding,
                        realization=realization,
                        endpoint_reference=(
                            endpoint.endpoint_reference
                        ),
                        technical_address=(
                            endpoint.technical_address
                        ),
                    )
                )
        return tuple(endpoints)

    def _relevant_endpoints(
        self,
        constraint: AddressConstraint,
        endpoints: tuple[
            _ResolvedEndpoint,
            ...,
        ],
        *,
        dcs: DcsRevision,
        side: str,
        gaps: list[KnowledgeGap],
    ) -> tuple[_ResolvedEndpoint, ...] | None:
        result: list[_ResolvedEndpoint] = []
        for endpoint in endpoints:
            try:
                address = ip_address(
                    endpoint.technical_address
                )
            except ValueError:
                gaps.append(
                    self._gap(
                        dcs,
                        (
                            side.title()
                            + "InvalidTechnicalAddress"
                        ),
                        references=(
                            endpoint.endpoint_reference,
                            endpoint.technical_address,
                        ),
                        owner="Resource Catalogue",
                    )
                )
                return None
            if _address_matches(
                constraint,
                address,
            ):
                result.append(endpoint)
        return tuple(result)

    @staticmethod
    def _gap(
        dcs: DcsRevision,
        reason: str,
        *,
        references: tuple[str, ...] = (),
        owner: str = "Application Communication Catalogue",
    ) -> KnowledgeGap:
        return KnowledgeGap(
            owner=owner,
            reason=reason,
            references=(
                f"dcs:{dcs.revision_id}",
                *references,
            ),
        )


def _address_matches(
    constraint: AddressConstraint,
    address,
) -> bool:
    if (
        constraint.kind
        is AddressConstraintKind.ANY
    ):
        return True
    value = int(address)
    return any(
        region.version == address.version
        and region.first_int
        <= value
        <= region.last_int
        for region in constraint.ranges
    )


def _single_address(
    value: str,
) -> AddressRange:
    address = ip_address(value)
    canonical = str(address)
    return AddressRange(
        canonical,
        canonical,
    )


def _port_regions(
    constraint: PortConstraint,
) -> tuple[PortRegion, ...]:
    if (
        constraint.kind
        is PortConstraintKind.NOT_APPLICABLE
    ):
        return (
            PortRegion.not_applicable(),
        )
    if (
        constraint.kind
        is PortConstraintKind.ANY
    ):
        return (
            PortRegion.numeric(
                0,
                65535,
            ),
        )
    return tuple(
        PortRegion.numeric(
            value.first,
            value.last,
        )
        for value in constraint.ranges
    )


def _provenance(
    *,
    dcs: DcsRevision,
    source: _ResolvedEndpoint,
    destination: _ResolvedEndpoint,
    service_reference: str | None,
) -> DomainRegionProvenance:
    acc_references = [
        f"dcs:{dcs.revision_id}",
        (
            "dcs-provenance:"
            + dcs.provenance_reference
        ),
        (
            "source-binding:"
            + source.binding.reference_id
        ),
        (
            "source-binding-provenance:"
            + source.binding.provenance_reference
        ),
        (
            "destination-binding:"
            + destination.binding.reference_id
        ),
        (
            "destination-binding-provenance:"
            + destination.binding.provenance_reference
        ),
    ]
    if service_reference is not None:
        acc_references.append(
            "service-reference:"
            + service_reference
        )
    return DomainRegionProvenance(
        acc_references=tuple(acc_references),
        source_rc_references=(
            (
                "resource:"
                + source.realization.resource_reference
            ),
            (
                "endpoint:"
                + source.endpoint_reference
            ),
            (
                "fact:"
                + source.realization.fact_reference
            ),
            (
                "provenance:"
                + source.realization.provenance_reference
            ),
        ),
        destination_rc_references=(
            (
                "resource:"
                + destination.realization.resource_reference
            ),
            (
                "endpoint:"
                + destination.endpoint_reference
            ),
            (
                "fact:"
                + destination.realization.fact_reference
            ),
            (
                "provenance:"
                + destination.realization.provenance_reference
            ),
        ),
    )
