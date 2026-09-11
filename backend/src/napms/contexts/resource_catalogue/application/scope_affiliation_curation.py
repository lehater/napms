from dataclasses import dataclass
from datetime import datetime

from napms.contexts.resource_catalogue.application._temporal_curation import (
    TemporalCurationOutcome,
    fingerprint,
    instant,
    is_aware,
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
    ResourceScopeAffiliation,
)


_CREATE_SCOPE_AFFILIATION = "CreateResourceScopeAffiliation"
_END_SCOPE_AFFILIATION = "EndResourceScopeAffiliation"


@dataclass(frozen=True, slots=True)
class CreateScopeAffiliationCommand:
    resource_reference: str
    responsibility_scope: str
    valid_from: datetime
    valid_to: datetime | None
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class EndScopeAffiliationCommand:
    affiliation_reference: str
    valid_to: datetime
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ScopeAffiliationMutationResult:
    outcome: TemporalCurationOutcome
    affiliation: ResourceScopeAffiliation | None = None
    result_version: int | None = None


class CreateResourceScopeAffiliation:
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
    ) -> ScopeAffiliationMutationResult | None:
        receipt = self._catalogue.find_command_receipt(
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is None:
            return None
        if (
            receipt.command_kind != _CREATE_SCOPE_AFFILIATION
            or receipt.request_fingerprint != request_fingerprint
        ):
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.IDEMPOTENCY_CONFLICT
            )
        affiliation = self._catalogue.get_scope_affiliation(receipt.result_reference)
        if affiliation is None:
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )
        return ScopeAffiliationMutationResult(
            TemporalCurationOutcome.RESOLVED,
            affiliation=affiliation,
            result_version=receipt.result_version,
        )

    def execute(
        self,
        command: CreateScopeAffiliationCommand,
    ) -> ScopeAffiliationMutationResult:
        authority = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority.outcome is ResourceCatalogueAuthorityOutcome.DENIED:
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.AUTHORITY_DENIED
            )
        if (
            authority.outcome is not ResourceCatalogueAuthorityOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.AUTHORITY_UNKNOWN
            )

        resource_reference = required(command.resource_reference)
        responsibility_scope = required(command.responsibility_scope)
        idempotency_key = required(command.idempotency_key)
        if (
            resource_reference is None
            or responsibility_scope is None
            or idempotency_key is None
            or not valid_interval(command.valid_from, command.valid_to)
        ):
            return ScopeAffiliationMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        request_fingerprint = fingerprint(
            {
                "resourceReference": resource_reference,
                "responsibilityScope": responsibility_scope,
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
            return ScopeAffiliationMutationResult(TemporalCurationOutcome.NOT_FOUND)
        if resource.lifecycle_state is not ResourceLifecycleState.ACTIVE:
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.RESOURCE_INACTIVE
            )

        if self._catalogue.find_overlapping_scope_affiliations(
            resource_reference=resource_reference,
            responsibility_scope=responsibility_scope,
            valid_from=command.valid_from,
            valid_to=command.valid_to,
        ):
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.OVERLAP_CONFLICT
            )

        affiliation_reference = self._identities.new_scope_affiliation_reference()
        provenance_reference = self._provenance.for_scope_affiliation(
            affiliation_reference=affiliation_reference,
            actor_id=command.actor_id,
            authority_reference=authority.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            affiliation = ResourceScopeAffiliation(
                affiliation_reference=affiliation_reference,
                resource_reference=resource_reference,
                responsibility_scope=responsibility_scope,
                valid_from=command.valid_from,
                valid_to=command.valid_to,
                provenance_reference=provenance_reference,
            )
        except ResourceCatalogueInvariantError:
            return ScopeAffiliationMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        self._catalogue.add_scope_affiliation(affiliation)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ResourceCatalogueCommandReceipt(
                command_kind=_CREATE_SCOPE_AFFILIATION,
                request_fingerprint=request_fingerprint,
                result_reference=affiliation.affiliation_reference,
                result_version=affiliation.version,
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
            return replay or ScopeAffiliationMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )
        except ResourceCataloguePersistenceOutcomeUnknown:
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )

        return ScopeAffiliationMutationResult(
            TemporalCurationOutcome.CREATED,
            affiliation=affiliation,
            result_version=affiliation.version,
        )


class EndResourceScopeAffiliation:
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
    ) -> ScopeAffiliationMutationResult | None:
        receipt = self._catalogue.find_command_receipt(
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is None:
            return None
        if (
            receipt.command_kind != _END_SCOPE_AFFILIATION
            or receipt.request_fingerprint != request_fingerprint
        ):
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.IDEMPOTENCY_CONFLICT
            )
        affiliation = self._catalogue.get_scope_affiliation(receipt.result_reference)
        if affiliation is None:
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )
        return ScopeAffiliationMutationResult(
            TemporalCurationOutcome.RESOLVED,
            affiliation=affiliation,
            result_version=receipt.result_version,
        )

    def execute(
        self,
        command: EndScopeAffiliationCommand,
    ) -> ScopeAffiliationMutationResult:
        authority = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority.outcome is ResourceCatalogueAuthorityOutcome.DENIED:
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.AUTHORITY_DENIED
            )
        if (
            authority.outcome is not ResourceCatalogueAuthorityOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.AUTHORITY_UNKNOWN
            )

        affiliation_reference = required(command.affiliation_reference)
        idempotency_key = required(command.idempotency_key)
        if (
            affiliation_reference is None
            or idempotency_key is None
            or command.expected_version < 1
            or not is_aware(command.valid_to)
        ):
            return ScopeAffiliationMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        request_fingerprint = fingerprint(
            {
                "affiliationReference": affiliation_reference,
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

        current = self._catalogue.get_scope_affiliation(affiliation_reference)
        if current is None:
            return ScopeAffiliationMutationResult(TemporalCurationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.CONCURRENCY_CONFLICT
            )

        end_provenance = self._provenance.for_scope_affiliation_end(
            affiliation_reference=affiliation_reference,
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
            return ScopeAffiliationMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        try:
            self._catalogue.save_scope_affiliation(
                ended,
                expected_version=command.expected_version,
            )
        except ResourceCatalogueConcurrencyConflict:
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.CONCURRENCY_CONFLICT
            )

        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ResourceCatalogueCommandReceipt(
                command_kind=_END_SCOPE_AFFILIATION,
                request_fingerprint=request_fingerprint,
                result_reference=ended.affiliation_reference,
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
            return replay or ScopeAffiliationMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )
        except ResourceCataloguePersistenceOutcomeUnknown:
            return ScopeAffiliationMutationResult(
                TemporalCurationOutcome.PERSISTENCE_UNKNOWN
            )

        return ScopeAffiliationMutationResult(
            TemporalCurationOutcome.UPDATED,
            affiliation=ended,
            result_version=ended.version,
        )
