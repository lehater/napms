from dataclasses import replace

from napms.contexts.access_policy_realization.domain.model import (
    AccessCorrespondence,
    AddressConstraint,
    AddressConstraintKind,
    AddressRange,
    AmbiguityWitness,
    DomainAccessResolution,
    DomainCorrespondence,
    DomainInteractionIdentity,
    DomainInteractionRegion,
    DomainKnowledgeSnapshot,
    InputProvenance,
    KnowledgeGap,
    PortConstraint,
    PortConstraintKind,
    PortRegion,
    PortRegionKind,
    ProtocolSelectorKind,
    ResolutionStatus,
    TechnicalAccessPredicate,
    TechnicalRegionFragment,
    UnresolvedTechnicalRemainder,
    require_aware,
)


_IPV4_UNIVERSE = AddressRange(
    "0.0.0.0",
    "255.255.255.255",
)
_IPV6_UNIVERSE = AddressRange(
    "::",
    "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff",
)


def fragment_sort_key(
    value: TechnicalRegionFragment,
) -> tuple:
    return (
        value.source_address.version,
        value.source_address.first_int,
        value.source_address.last_int,
        value.destination_address.version,
        value.destination_address.first_int,
        value.destination_address.last_int,
        value.protocol_number,
        value.source_ports.kind.value,
        (
            value.source_ports.first
            if value.source_ports.first is not None
            else -1
        ),
        (
            value.source_ports.last
            if value.source_ports.last is not None
            else -1
        ),
        value.destination_ports.kind.value,
        (
            value.destination_ports.first
            if value.destination_ports.first is not None
            else -1
        ),
        (
            value.destination_ports.last
            if value.destination_ports.last is not None
            else -1
        ),
    )


def interaction_sort_key(
    value: DomainInteractionIdentity,
) -> tuple[str, str, str]:
    return (
        str(value.source_component_deployment_id),
        str(value.destination_component_deployment_id),
        str(value.dcs_contract_revision_id),
    )


def _address_regions(
    value: AddressConstraint,
) -> tuple[AddressRange, ...]:
    if value.kind is AddressConstraintKind.ANY:
        return (
            _IPV4_UNIVERSE,
            _IPV6_UNIVERSE,
        )
    return value.ranges


def _port_regions(
    value: PortConstraint,
) -> tuple[PortRegion, ...]:
    if value.kind is PortConstraintKind.NOT_APPLICABLE:
        return (PortRegion.not_applicable(),)
    if value.kind is PortConstraintKind.ANY:
        return (PortRegion.numeric(0, 65535),)
    return tuple(
        PortRegion.numeric(item.first, item.last)
        for item in value.ranges
    )


def expand_predicate(
    value: TechnicalAccessPredicate,
) -> tuple[TechnicalRegionFragment, ...]:
    if value.protocol.kind is ProtocolSelectorKind.ANY:
        return ()
    assert value.protocol.number is not None
    fragments = {
        TechnicalRegionFragment(
            source_address=source_address,
            destination_address=destination_address,
            protocol_number=value.protocol.number,
            source_ports=source_ports,
            destination_ports=destination_ports,
        )
        for source_address in _address_regions(
            value.source_addresses
        )
        for destination_address in _address_regions(
            value.destination_addresses
        )
        for source_ports in _port_regions(
            value.source_ports
        )
        for destination_ports in _port_regions(
            value.destination_ports
        )
    }
    return tuple(
        sorted(
            fragments,
            key=fragment_sort_key,
        )
    )


def _intersect_address(
    left: AddressRange,
    right: AddressRange,
) -> AddressRange | None:
    if left.version != right.version:
        return None
    first = max(
        left.first_int,
        right.first_int,
    )
    last = min(
        left.last_int,
        right.last_int,
    )
    if first > last:
        return None
    return AddressRange.from_ints(
        first,
        last,
        version=left.version,
    )


def _contains_address(
    container: AddressRange,
    content: AddressRange,
) -> bool:
    return (
        container.version == content.version
        and container.first_int <= content.first_int
        and content.last_int <= container.last_int
    )


def _intersect_port(
    left: PortRegion,
    right: PortRegion,
) -> PortRegion | None:
    if (
        left.kind is PortRegionKind.NOT_APPLICABLE
        or right.kind is PortRegionKind.NOT_APPLICABLE
    ):
        if left.kind is right.kind:
            return PortRegion.not_applicable()
        return None
    assert left.first is not None
    assert left.last is not None
    assert right.first is not None
    assert right.last is not None
    first = max(left.first, right.first)
    last = min(left.last, right.last)
    if first > last:
        return None
    return PortRegion.numeric(first, last)


def _contains_port(
    container: PortRegion,
    content: PortRegion,
) -> bool:
    if (
        container.kind is PortRegionKind.NOT_APPLICABLE
        or content.kind is PortRegionKind.NOT_APPLICABLE
    ):
        return container.kind is content.kind
    assert container.first is not None
    assert container.last is not None
    assert content.first is not None
    assert content.last is not None
    return (
        container.first <= content.first
        and content.last <= container.last
    )


def intersect_fragments(
    left: TechnicalRegionFragment,
    right: TechnicalRegionFragment,
) -> TechnicalRegionFragment | None:
    if left.protocol_number != right.protocol_number:
        return None
    source_address = _intersect_address(
        left.source_address,
        right.source_address,
    )
    destination_address = _intersect_address(
        left.destination_address,
        right.destination_address,
    )
    source_ports = _intersect_port(
        left.source_ports,
        right.source_ports,
    )
    destination_ports = _intersect_port(
        left.destination_ports,
        right.destination_ports,
    )
    if None in (
        source_address,
        destination_address,
        source_ports,
        destination_ports,
    ):
        return None
    assert source_address is not None
    assert destination_address is not None
    assert source_ports is not None
    assert destination_ports is not None
    return TechnicalRegionFragment(
        source_address=source_address,
        destination_address=destination_address,
        protocol_number=left.protocol_number,
        source_ports=source_ports,
        destination_ports=destination_ports,
    )


def fragment_contains(
    container: TechnicalRegionFragment,
    content: TechnicalRegionFragment,
) -> bool:
    return (
        container.protocol_number
        == content.protocol_number
        and _contains_address(
            container.source_address,
            content.source_address,
        )
        and _contains_address(
            container.destination_address,
            content.destination_address,
        )
        and _contains_port(
            container.source_ports,
            content.source_ports,
        )
        and _contains_port(
            container.destination_ports,
            content.destination_ports,
        )
    )


def correspondence(
    technical: TechnicalRegionFragment,
    domain: TechnicalRegionFragment,
) -> tuple[
    AccessCorrespondence,
    TechnicalRegionFragment | None,
]:
    overlap = intersect_fragments(
        technical,
        domain,
    )
    if overlap is None:
        return (
            AccessCorrespondence.NONE,
            None,
        )
    technical_contains_domain = fragment_contains(
        technical,
        domain,
    )
    domain_contains_technical = fragment_contains(
        domain,
        technical,
    )
    if (
        technical_contains_domain
        and domain_contains_technical
    ):
        return (
            AccessCorrespondence.EXACT,
            overlap,
        )
    if technical_contains_domain:
        return (
            AccessCorrespondence.COVERS,
            overlap,
        )
    if domain_contains_technical:
        return (
            AccessCorrespondence.COVERED_BY,
            overlap,
        )
    return (
        AccessCorrespondence.PARTIAL_OVERLAP,
        overlap,
    )


def _split_address(
    core: TechnicalRegionFragment,
    overlap: TechnicalRegionFragment,
    *,
    field: str,
) -> tuple[
    list[TechnicalRegionFragment],
    TechnicalRegionFragment,
]:
    base = getattr(core, field)
    cut = getattr(overlap, field)
    pieces: list[TechnicalRegionFragment] = []
    if base.first_int < cut.first_int:
        pieces.append(
            replace(
                core,
                **{
                    field: AddressRange.from_ints(
                        base.first_int,
                        cut.first_int - 1,
                        version=base.version,
                    )
                },
            )
        )
    if cut.last_int < base.last_int:
        pieces.append(
            replace(
                core,
                **{
                    field: AddressRange.from_ints(
                        cut.last_int + 1,
                        base.last_int,
                        version=base.version,
                    )
                },
            )
        )
    return (
        pieces,
        replace(
            core,
            **{field: cut},
        ),
    )


def _split_port(
    core: TechnicalRegionFragment,
    overlap: TechnicalRegionFragment,
    *,
    field: str,
) -> tuple[
    list[TechnicalRegionFragment],
    TechnicalRegionFragment,
]:
    base = getattr(core, field)
    cut = getattr(overlap, field)
    if base.kind is PortRegionKind.NOT_APPLICABLE:
        return ([], core)
    assert base.first is not None
    assert base.last is not None
    assert cut.first is not None
    assert cut.last is not None
    pieces: list[TechnicalRegionFragment] = []
    if base.first < cut.first:
        pieces.append(
            replace(
                core,
                **{
                    field: PortRegion.numeric(
                        base.first,
                        cut.first - 1,
                    )
                },
            )
        )
    if cut.last < base.last:
        pieces.append(
            replace(
                core,
                **{
                    field: PortRegion.numeric(
                        cut.last + 1,
                        base.last,
                    )
                },
            )
        )
    return (
        pieces,
        replace(
            core,
            **{field: cut},
        ),
    )


def subtract_fragment(
    base: TechnicalRegionFragment,
    cut: TechnicalRegionFragment,
) -> tuple[TechnicalRegionFragment, ...]:
    overlap = intersect_fragments(
        base,
        cut,
    )
    if overlap is None:
        return (base,)
    if overlap == base:
        return ()

    result: list[TechnicalRegionFragment] = []
    core = base
    for field in (
        "source_address",
        "destination_address",
    ):
        pieces, core = _split_address(
            core,
            overlap,
            field=field,
        )
        result.extend(pieces)
    for field in (
        "source_ports",
        "destination_ports",
    ):
        pieces, core = _split_port(
            core,
            overlap,
            field=field,
        )
        result.extend(pieces)
    return tuple(
        sorted(
            set(result),
            key=fragment_sort_key,
        )
    )


def subtract_many(
    bases: tuple[TechnicalRegionFragment, ...],
    cuts: tuple[TechnicalRegionFragment, ...],
) -> tuple[TechnicalRegionFragment, ...]:
    remaining = tuple(
        sorted(
            set(bases),
            key=fragment_sort_key,
        )
    )
    for cut in tuple(
        sorted(
            set(cuts),
            key=fragment_sort_key,
        )
    ):
        next_remaining: list[
            TechnicalRegionFragment
        ] = []
        for base in remaining:
            next_remaining.extend(
                subtract_fragment(
                    base,
                    cut,
                )
            )
        remaining = tuple(
            sorted(
                set(next_remaining),
                key=fragment_sort_key,
            )
        )
    return remaining


def _merge_correspondence(
    existing: DomainCorrespondence,
    region: DomainInteractionRegion,
) -> DomainCorrespondence:
    return replace(
        existing,
        provenance=existing.provenance.merged(
            region.provenance
        ),
    )


def _collect_correspondences(
    technical_fragments: tuple[
        TechnicalRegionFragment,
        ...,
    ],
    regions: tuple[
        DomainInteractionRegion,
        ...,
    ],
) -> tuple[DomainCorrespondence, ...]:
    collected: dict[
        tuple,
        DomainCorrespondence,
    ] = {}
    for technical in technical_fragments:
        for region in regions:
            relation, overlap = correspondence(
                technical,
                region.fragment,
            )
            if (
                relation
                is AccessCorrespondence.NONE
                or overlap is None
            ):
                continue
            key = (
                region.interaction,
                relation,
                overlap,
                region.fragment,
            )
            current = collected.get(key)
            if current is None:
                collected[key] = DomainCorrespondence(
                    interaction=region.interaction,
                    relation=relation,
                    overlap=overlap,
                    domain_region=region.fragment,
                    provenance=region.provenance,
                )
            else:
                collected[key] = _merge_correspondence(
                    current,
                    region,
                )
    return tuple(
        sorted(
            collected.values(),
            key=lambda item: (
                interaction_sort_key(
                    item.interaction
                ),
                item.relation.value,
                fragment_sort_key(
                    item.overlap
                ),
                fragment_sort_key(
                    item.domain_region
                ),
            ),
        )
    )


def _ambiguities(
    correspondences: tuple[
        DomainCorrespondence,
        ...,
    ],
) -> tuple[AmbiguityWitness, ...]:
    witnesses: dict[
        tuple[
            TechnicalRegionFragment,
            tuple[
                DomainInteractionIdentity,
                ...,
            ],
        ],
        AmbiguityWitness,
    ] = {}
    for index, left in enumerate(
        correspondences
    ):
        for right in correspondences[
            index + 1 :
        ]:
            if (
                left.interaction
                == right.interaction
            ):
                continue
            overlap = intersect_fragments(
                left.overlap,
                right.overlap,
            )
            if overlap is None:
                continue
            interactions = tuple(
                sorted(
                    {
                        left.interaction,
                        right.interaction,
                    },
                    key=interaction_sort_key,
                )
            )
            key = (
                overlap,
                interactions,
            )
            witnesses[key] = AmbiguityWitness(
                overlap=overlap,
                interactions=interactions,
            )
    return tuple(
        sorted(
            witnesses.values(),
            key=lambda item: (
                fragment_sort_key(
                    item.overlap
                ),
                tuple(
                    interaction_sort_key(
                        value
                    )
                    for value
                    in item.interactions
                ),
            ),
        )
    )


def _protocol_any_resolution(
    predicate: TechnicalAccessPredicate,
    *,
    as_of,
    input_provenance: InputProvenance,
) -> DomainAccessResolution:
    gap = KnowledgeGap(
        owner="Access Policy Realization",
        reason="ProtocolAnyAlgebraUnsupported",
    )
    return DomainAccessResolution(
        predicate=predicate,
        as_of=as_of,
        status=ResolutionStatus.UNKNOWN,
        correspondences=(),
        ambiguities=(),
        remainder=UnresolvedTechnicalRemainder(
            original_predicate=predicate,
            fragments=(),
            complete=False,
        ),
        knowledge_gaps=(gap,),
        input_provenance=input_provenance,
    )


def resolve_domain_access(
    predicate: TechnicalAccessPredicate,
    *,
    as_of,
    knowledge: DomainKnowledgeSnapshot | None,
    input_provenance: InputProvenance = (
        InputProvenance()
    ),
) -> DomainAccessResolution:
    require_aware(as_of)
    if (
        predicate.protocol.kind
        is ProtocolSelectorKind.ANY
    ):
        return _protocol_any_resolution(
            predicate,
            as_of=as_of,
            input_provenance=input_provenance,
        )
    if knowledge is None:
        raise ValueError(
            "knowledge is required for "
            "an exact protocol predicate"
        )

    technical_fragments = expand_predicate(
        predicate
    )
    correspondences = (
        _collect_correspondences(
            technical_fragments,
            knowledge.regions,
        )
    )
    overlap_fragments = tuple(
        item.overlap
        for item in correspondences
    )
    remainder_fragments = subtract_many(
        technical_fragments,
        overlap_fragments,
    )
    ambiguities = _ambiguities(
        correspondences
    )
    complete = (
        knowledge.complete_for_predicate
        and not knowledge.knowledge_gaps
    )

    if not complete:
        status = ResolutionStatus.UNKNOWN
    elif ambiguities:
        status = ResolutionStatus.AMBIGUOUS
    elif not correspondences:
        status = ResolutionStatus.UNRESOLVED
    elif not remainder_fragments:
        distinct_interactions = {
            item.interaction
            for item in correspondences
        }
        exact = (
            len(technical_fragments) == 1
            and len(distinct_interactions) == 1
            and any(
                item.relation
                is AccessCorrespondence.EXACT
                and item.overlap
                == technical_fragments[0]
                for item in correspondences
            )
        )
        status = (
            ResolutionStatus.EXACT
            if exact
            else ResolutionStatus.COVERED
        )
    else:
        status = ResolutionStatus.PARTIAL

    return DomainAccessResolution(
        predicate=predicate,
        as_of=as_of,
        status=status,
        correspondences=correspondences,
        ambiguities=ambiguities,
        remainder=UnresolvedTechnicalRemainder(
            original_predicate=predicate,
            fragments=remainder_fragments,
            complete=complete,
        ),
        knowledge_gaps=(
            knowledge.knowledge_gaps
        ),
        input_provenance=input_provenance,
    )
