from dataclasses import dataclass
from datetime import datetime

from napms.contexts.resource_catalogue.application._temporal_curation import (
    TemporalCurationOutcome,
    fingerprint,
    instant,
    is_aware,
    optional,
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
    ResourceCatalogueInvariantError,
    ResourceLifecycleState,
)
from napms.contexts.resource_catalogue.domain.responsibility import (
    ResponsiblePartyKind,
    ResourceResponsibility,
    ResourceResponsibilityRole,
)


_CREATE_RESPONSIBILITY = "CreateResourceResponsibility"
_END_RESPONSIBILITY = "EndResourceResponsibility"


@dataclass(frozen=True, slots=True)
class CreateResponsibilityCommand:
    resource_reference: str
    party_reference: str
    party_kind: ResponsiblePartyKind
    role: ResourceResponsibilityRole
    display_name: str
    contact: str | None
    valid_from: datetime
    valid_to: datetime | None
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class EndResponsibilityCommand:
    assignment_reference: str
    valid_to: datetime
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ResponsibilityMutationResult:
    outcome: TemporalCurationOutcome
    responsibility: ResourceResponsibility | None = None
    result_version: int | None = None


class CreateResourceResponsibility:
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
        request_fingerprint: str,
    ) -> ResponsibilityMutationResult | None:
        receipt = self._catalogue.find_command_receipt(
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is None:
            return None
        if (
            receipt.command_kind != _CREATE_RESPONSIBILITY
            or receipt.request_fingerprint != request_fingerprint
        ):
            return ResponsibilityMutationResult(
                TemporalCurationOutcome.IDEMPOTENCY_CONFLICT
            )
        responsibility = self._catalogue.get_responsibility(receipt.result_reference)
        if responsibility is None:
            return ResponsibilityMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )
        return ResponsibilityMutationResult(
            TemporalCurationOutcome.RESOLVED,
            responsibility=responsibility,
            result_version=receipt.result_version,
        )

    def execute(
        self,
        command: CreateResponsibilityCommand,
    ) -> ResponsibilityMutationResult:
        authority = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority.outcome is ResourceCatalogueAuthorityOutcome.DENIED:
            return ResponsibilityMutationResult(TemporalCurationOutcome.AUTHORITY_DENIED)
        if (
            authority.outcome is not ResourceCatalogueAuthorityOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return ResponsibilityMutationResult(TemporalCurationOutcome.AUTHORITY_UNKNOWN)

        resource_reference = required(command.resource_reference)
        party_reference = required(command.party_reference)
        display_name = required(command.display_name)
        idempotency_key = required(command.idempotency_key)
        contact = optional(command.contact)
        if (
            resource_reference is None
            or party_reference is None
            or display_name is None
            or idempotency_key is None
            or (command.contact is not None and contact is None)
            or not valid_interval(command.valid_from, command.valid_to)
        ):
            return ResponsibilityMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        request_fingerprint = fingerprint(
            {
                "resourceReference": resource_reference,
                "partyReference": party_reference,
                "partyKind": command.party_kind.value,
                "role": command.role.value,
                "displayName": display_name,
                "contact": contact,
                "validFrom": instant(command.valid_from),
                "validTo": instant(command.valid_to),
            }
        )
        replay = self._resolve(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        resource = self._catalogue.get_resource(resource_reference)
        if resource is None:
            return ResponsibilityMutationResult(TemporalCurationOutcome.NOT_FOUND)
        if resource.lifecycle_state is not ResourceLifecycleState.ACTIVE:
            return ResponsibilityMutationResult(TemporalCurationOutcome.RESOURCE_INACTIVE)

        assignment_reference = self._identities.new_responsibility_reference()
        provenance_reference = self._provenance.for_responsibility(
            assignment_reference=assignment_reference,
            actor_id=command.actor_id,
            authority_reference=authority.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            responsibility = ResourceResponsibility(
                assignment_reference=assignment_reference,
                resource_reference=resource_reference,
                party_reference=party_reference,
                party_kind=command.party_kind,
                role=command.role,
                display_name=display_name,
                contact=contact,
                valid_from=command.valid_from,
                valid_to=command.valid_to,
                provenance_reference=provenance_reference,
            )
        except ResourceCatalogueInvariantError:
            return ResponsibilityMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        self._catalogue.add_responsibility(responsibility)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ResourceCatalogueCommandReceipt(
                command_kind=_CREATE_RESPONSIBILITY,
                request_fingerprint=request_fingerprint,
                result_reference=responsibility.assignment_reference,
                result_version=responsibility.version,
            ),
        )
        try:
            self._catalogue.commit()
        except ResourceCatalogueIdempotencyConflict:
            replay = self._resolve(
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                request_fingerprint=request_fingerprint,
            )
            return replay or ResponsibilityMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )
        except ResourceCataloguePersistenceOutcomeUnknown:
            return ResponsibilityMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )

        return ResponsibilityMutationResult(
            TemporalCurationOutcome.CREATED,
            responsibility=responsibility,
            result_version=responsibility.version,
        )


class EndResourceResponsibility:
    def __init__(
        self,
        *,
        authority: ResourceCatalogueCurationAuthorityPort,
        catalogue: ResourceCatalogueCurationRepository,
        provenance: ResourceCatalogueProvenanceFactory,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._provenance = provenance

    def _resolve(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
        request_fingerprint: str,
    ) -> ResponsibilityMutationResult | None:
        receipt = self._catalogue.find_command_receipt(
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is None:
            return None
        if (
            receipt.command_kind != _END_RESPONSIBILITY
            or receipt.request_fingerprint != request_fingerprint
        ):
            return ResponsibilityMutationResult(
                TemporalCurationOutcome.IDEMPOTENCY_CONFLICT
            )
        responsibility = self._catalogue.get_responsibility(receipt.result_reference)
        if responsibility is None:
            return ResponsibilityMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )
        return ResponsibilityMutationResult(
            TemporalCurationOutcome.RESOLVED,
            responsibility=responsibility,
            result_version=receipt.result_version,
        )

    def execute(
        self,
        command: EndResponsibilityCommand,
    ) -> ResponsibilityMutationResult:
        authority = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority.outcome is ResourceCatalogueAuthorityOutcome.DENIED:
            return ResponsibilityMutationResult(TemporalCurationOutcome.AUTHORITY_DENIED)
        if (
            authority.outcome is not ResourceCatalogueAuthorityOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return ResponsibilityMutationResult(TemporalCurationOutcome.AUTHORITY_UNKNOWN)

        assignment_reference = required(command.assignment_reference)
        idempotency_key = required(command.idempotency_key)
        if (
            assignment_reference is None
            or idempotency_key is None
            or command.expected_version < 1
            or not is_aware(command.valid_to)
        ):
            return ResponsibilityMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        request_fingerprint = fingerprint(
            {
                "assignmentReference": assignment_reference,
                "validTo": instant(command.valid_to),
                "expectedVersion": command.expected_version,
            }
        )
        replay = self._resolve(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        current = self._catalogue.get_responsibility(assignment_reference)
        if current is None:
            return ResponsibilityMutationResult(TemporalCurationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return ResponsibilityMutationResult(
                TemporalCurationOutcome.CONCURRENCY_CONFLICT
            )

        end_provenance = self._provenance.for_responsibility_end(
            assignment_reference=assignment_reference,
            actor_id=command.actor_id,
            authority_reference=authority.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            ended = current.ended(
                valid_to=command.valid_to,
                end_provenance_reference=end_provenance,
            )
        except ResourceCatalogueInvariantError:
            return ResponsibilityMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        try:
            self._catalogue.save_responsibility(
                ended,
                expected_version=command.expected_version,
            )
        except ResourceCatalogueConcurrencyConflict:
            return ResponsibilityMutationResult(
                TemporalCurationOutcome.CONCURRENCY_CONFLICT
            )

        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ResourceCatalogueCommandReceipt(
                command_kind=_END_RESPONSIBILITY,
                request_fingerprint=request_fingerprint,
                result_reference=ended.assignment_reference,
                result_version=ended.version,
            ),
        )
        try:
            self._catalogue.commit()
        except ResourceCatalogueIdempotencyConflict:
            replay = self._resolve(
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                request_fingerprint=request_fingerprint,
            )
            return replay or ResponsibilityMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )
        except ResourceCataloguePersistenceOutcomeUnknown:
            return ResponsibilityMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )

        return ResponsibilityMutationResult(
            TemporalCurationOutcome.UPDATED,
            responsibility=ended,
            result_version=ended.version,
        )
