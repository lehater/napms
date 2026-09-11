from dataclasses import dataclass
from datetime import datetime

from napms.contexts.resource_catalogue.application._temporal_curation import (
    TemporalCurationOutcome,
    fingerprint,
    instant,
    required,
    valid_interval,
)
from napms.contexts.resource_catalogue.application.ports import (
    ResourceCatalogueAuthorityOutcome,
    ResourceCatalogueCommandReceipt,
    ResourceCatalogueConcurrencyConflict,
    ResourceCatalogueCurationAuthorityPort,
    ResourceCatalogueCurationRepository,
    ResourceCatalogueIdempotencyConflict,
    ResourceCatalogueIdentityFactory,
    ResourceCataloguePersistenceOutcomeUnknown,
    ResourceCatalogueProvenanceFactory,
)
from napms.contexts.resource_catalogue.domain.model import (
    EndpointAddress,
    ResourceCatalogueInvariantError,
    ResourceLifecycleState,
    ResourceRealizationVersion,
)


_CREATE_REALIZATION = "CreateResourceRealization"
_REPLACE_REALIZATION = "ReplaceResourceRealization"


@dataclass(frozen=True, slots=True)
class CreateResourceRealizationCommand:
    resource_reference: str
    technical_addresses: tuple[str, ...]
    valid_from: datetime
    valid_to: datetime | None
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ReplaceResourceRealizationCommand:
    current_fact_reference: str
    technical_addresses: tuple[str, ...]
    valid_from: datetime
    valid_to: datetime | None
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RealizationMutationResult:
    outcome: TemporalCurationOutcome
    realization: ResourceRealizationVersion | None = None
    replaced_fact_reference: str | None = None
    result_version: int | None = None


def _normalize_addresses(values: tuple[str, ...]) -> tuple[str, ...] | None:
    normalized = tuple(value.strip() for value in values if value and value.strip())
    if len(normalized) != len(values) or not normalized:
        return None
    if len(set(normalized)) != len(normalized):
        return None
    return tuple(sorted(normalized))


class _RealizationCommandBase:
    def __init__(
        self,
        *,
        authority: ResourceCatalogueCurationAuthorityPort,
        catalogue: ResourceCatalogueCurationRepository,
        identities: ResourceCatalogueIdentityFactory,
        provenance: ResourceCatalogueProvenanceFactory,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._identities = identities
        self._provenance = provenance

    def _resolve(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
        command_kind: str,
        request_fingerprint: str,
    ) -> RealizationMutationResult | None:
        receipt = self._catalogue.find_command_receipt(
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is None:
            return None
        if (
            receipt.command_kind != command_kind
            or receipt.request_fingerprint != request_fingerprint
        ):
            return RealizationMutationResult(
                TemporalCurationOutcome.IDEMPOTENCY_CONFLICT
            )
        realization = self._catalogue.get_realization(receipt.result_reference)
        if realization is None:
            return RealizationMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )
        return RealizationMutationResult(
            TemporalCurationOutcome.RESOLVED,
            realization=realization,
            result_version=receipt.result_version,
        )

    def _new_realization(
        self,
        *,
        resource_reference: str,
        technical_addresses: tuple[str, ...],
        valid_from: datetime,
        valid_to: datetime | None,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> ResourceRealizationVersion:
        fact_reference = self._identities.new_realization_reference()
        endpoints = tuple(
            EndpointAddress(
                endpoint_reference=self._identities.new_endpoint_reference(),
                technical_address=address,
            )
            for address in technical_addresses
        )
        provenance_reference = self._provenance.for_realization(
            fact_reference=fact_reference,
            actor_id=actor_id,
            authority_reference=authority_reference,
            effective_time=effective_time,
        )
        return ResourceRealizationVersion(
            fact_reference=fact_reference,
            resource_reference=resource_reference,
            endpoint_realizations=endpoints,
            valid_from=valid_from,
            valid_to=valid_to,
            provenance_reference=provenance_reference,
        )


class CreateResourceRealization(_RealizationCommandBase):
    def execute(
        self,
        command: CreateResourceRealizationCommand,
    ) -> RealizationMutationResult:
        authority = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority.outcome is ResourceCatalogueAuthorityOutcome.DENIED:
            return RealizationMutationResult(TemporalCurationOutcome.AUTHORITY_DENIED)
        if (
            authority.outcome is not ResourceCatalogueAuthorityOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return RealizationMutationResult(TemporalCurationOutcome.AUTHORITY_UNKNOWN)

        resource_reference = required(command.resource_reference)
        idempotency_key = required(command.idempotency_key)
        addresses = _normalize_addresses(command.technical_addresses)
        if (
            resource_reference is None
            or idempotency_key is None
            or addresses is None
            or not valid_interval(command.valid_from, command.valid_to)
        ):
            return RealizationMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        request_fingerprint = fingerprint(
            {
                "resourceReference": resource_reference,
                "technicalAddresses": addresses,
                "validFrom": instant(command.valid_from),
                "validTo": instant(command.valid_to),
            }
        )
        replay = self._resolve(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_CREATE_REALIZATION,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        resource = self._catalogue.get_resource(resource_reference)
        if resource is None:
            return RealizationMutationResult(TemporalCurationOutcome.NOT_FOUND)
        if resource.lifecycle_state is not ResourceLifecycleState.ACTIVE:
            return RealizationMutationResult(TemporalCurationOutcome.RESOURCE_INACTIVE)

        if self._catalogue.find_overlapping_realizations(
            resource_reference=resource_reference,
            valid_from=command.valid_from,
            valid_to=command.valid_to,
        ):
            return RealizationMutationResult(TemporalCurationOutcome.OVERLAP_CONFLICT)

        try:
            realization = self._new_realization(
                resource_reference=resource_reference,
                technical_addresses=addresses,
                valid_from=command.valid_from,
                valid_to=command.valid_to,
                actor_id=command.actor_id,
                authority_reference=authority.authority_reference,
                effective_time=command.effective_time,
            )
        except ResourceCatalogueInvariantError:
            return RealizationMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        self._catalogue.add_realization(realization)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ResourceCatalogueCommandReceipt(
                command_kind=_CREATE_REALIZATION,
                request_fingerprint=request_fingerprint,
                result_reference=realization.fact_reference,
                result_version=realization.version,
            ),
        )
        try:
            self._catalogue.commit()
        except ResourceCatalogueIdempotencyConflict:
            replay = self._resolve(
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_CREATE_REALIZATION,
                request_fingerprint=request_fingerprint,
            )
            return replay or RealizationMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )
        except ResourceCataloguePersistenceOutcomeUnknown:
            return RealizationMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )

        return RealizationMutationResult(
            TemporalCurationOutcome.CREATED,
            realization=realization,
            result_version=realization.version,
        )


class ReplaceResourceRealization(_RealizationCommandBase):
    def execute(
        self,
        command: ReplaceResourceRealizationCommand,
    ) -> RealizationMutationResult:
        authority = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority.outcome is ResourceCatalogueAuthorityOutcome.DENIED:
            return RealizationMutationResult(TemporalCurationOutcome.AUTHORITY_DENIED)
        if (
            authority.outcome is not ResourceCatalogueAuthorityOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return RealizationMutationResult(TemporalCurationOutcome.AUTHORITY_UNKNOWN)

        current_fact_reference = required(command.current_fact_reference)
        idempotency_key = required(command.idempotency_key)
        addresses = _normalize_addresses(command.technical_addresses)
        if (
            current_fact_reference is None
            or idempotency_key is None
            or addresses is None
            or command.expected_version < 1
            or not valid_interval(command.valid_from, command.valid_to)
        ):
            return RealizationMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        request_fingerprint = fingerprint(
            {
                "currentFactReference": current_fact_reference,
                "technicalAddresses": addresses,
                "validFrom": instant(command.valid_from),
                "validTo": instant(command.valid_to),
                "expectedVersion": command.expected_version,
            }
        )
        replay = self._resolve(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_REPLACE_REALIZATION,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        current = self._catalogue.get_realization(current_fact_reference)
        if current is None:
            return RealizationMutationResult(TemporalCurationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return RealizationMutationResult(
                TemporalCurationOutcome.CONCURRENCY_CONFLICT
            )
        if current.valid_to is not None or command.valid_from <= current.valid_from:
            return RealizationMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        resource = self._catalogue.get_resource(current.resource_reference)
        if resource is None:
            return RealizationMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )
        if resource.lifecycle_state is not ResourceLifecycleState.ACTIVE:
            return RealizationMutationResult(TemporalCurationOutcome.RESOURCE_INACTIVE)

        overlaps = self._catalogue.find_overlapping_realizations(
            resource_reference=current.resource_reference,
            valid_from=command.valid_from,
            valid_to=command.valid_to,
        )
        if any(item.fact_reference != current_fact_reference for item in overlaps):
            return RealizationMutationResult(TemporalCurationOutcome.OVERLAP_CONFLICT)

        end_provenance = self._provenance.for_realization_end(
            fact_reference=current_fact_reference,
            actor_id=command.actor_id,
            authority_reference=authority.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            ended = current.ended(
                valid_to=command.valid_from,
                end_provenance_reference=end_provenance,
            )
            successor = self._new_realization(
                resource_reference=current.resource_reference,
                technical_addresses=addresses,
                valid_from=command.valid_from,
                valid_to=command.valid_to,
                actor_id=command.actor_id,
                authority_reference=authority.authority_reference,
                effective_time=command.effective_time,
            )
        except ResourceCatalogueInvariantError:
            return RealizationMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        try:
            self._catalogue.save_realization(
                ended,
                expected_version=command.expected_version,
            )
        except ResourceCatalogueConcurrencyConflict:
            return RealizationMutationResult(
                TemporalCurationOutcome.CONCURRENCY_CONFLICT
            )
        self._catalogue.add_realization(successor)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ResourceCatalogueCommandReceipt(
                command_kind=_REPLACE_REALIZATION,
                request_fingerprint=request_fingerprint,
                result_reference=successor.fact_reference,
                result_version=successor.version,
            ),
        )
        try:
            self._catalogue.commit()
        except ResourceCatalogueIdempotencyConflict:
            replay = self._resolve(
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_REPLACE_REALIZATION,
                request_fingerprint=request_fingerprint,
            )
            return replay or RealizationMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )
        except ResourceCataloguePersistenceOutcomeUnknown:
            return RealizationMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )

        return RealizationMutationResult(
            TemporalCurationOutcome.UPDATED,
            realization=successor,
            replaced_fact_reference=ended.fact_reference,
            result_version=successor.version,
        )
