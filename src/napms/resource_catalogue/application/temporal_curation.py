from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json

from napms.resource_catalogue.application.ports import (
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
from napms.resource_catalogue.domain.model import (
    ResourceCatalogueInvariantError,
    ResourceLifecycleState,
    ResourceScopeAffiliation,
)
from napms.resource_catalogue.domain.responsibility import (
    ResponsiblePartyKind,
    ResourceResponsibility,
    ResourceResponsibilityRole,
)


_CREATE_SCOPE_AFFILIATION = "CreateResourceScopeAffiliation"
_END_SCOPE_AFFILIATION = "EndResourceScopeAffiliation"
_CREATE_RESPONSIBILITY = "CreateResourceResponsibility"
_END_RESPONSIBILITY = "EndResourceResponsibility"


class TemporalCurationOutcome(str, Enum):
    CREATED = "Created"
    UPDATED = "Updated"
    RESOLVED = "Resolved"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    NOT_FOUND = "NotFound"
    RESOURCE_INACTIVE = "ResourceInactive"
    INPUT_INVALID = "InputInvalid"
    OVERLAP_CONFLICT = "OverlapConflict"
    CONCURRENCY_CONFLICT = "ConcurrencyConflict"
    IDEMPOTENCY_CONFLICT = "IdempotencyConflict"
    PERSISTENCE_UNKNOWN = "PersistenceUnknown"


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


def _required(value: str) -> str | None:
    normalized = value.strip() if value else ""
    return normalized or None


def _optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _instant(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


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
        fingerprint: str,
    ) -> ScopeAffiliationMutationResult | None:
        receipt = self._catalogue.find_command_receipt(
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is None:
            return None
        if (
            receipt.command_kind != _CREATE_SCOPE_AFFILIATION
            or receipt.request_fingerprint != fingerprint
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

        resource_reference = _required(command.resource_reference)
        responsibility_scope = _required(command.responsibility_scope)
        idempotency_key = _required(command.idempotency_key)
        if (
            resource_reference is None
            or responsibility_scope is None
            or idempotency_key is None
        ):
            return ScopeAffiliationMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        fingerprint = _fingerprint(
            {
                "resourceReference": resource_reference,
                "responsibilityScope": responsibility_scope,
                "validFrom": _instant(command.valid_from),
                "validTo": _instant(command.valid_to),
            }
        )
        replay = self._resolve(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
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
                request_fingerprint=fingerprint,
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
                fingerprint=fingerprint,
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
        fingerprint: str,
    ) -> ScopeAffiliationMutationResult | None:
        receipt = self._catalogue.find_command_receipt(
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is None:
            return None
        if (
            receipt.command_kind != _END_SCOPE_AFFILIATION
            or receipt.request_fingerprint != fingerprint
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

        affiliation_reference = _required(command.affiliation_reference)
        idempotency_key = _required(command.idempotency_key)
        if (
            affiliation_reference is None
            or idempotency_key is None
            or command.expected_version < 1
        ):
            return ScopeAffiliationMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        fingerprint = _fingerprint(
            {
                "affiliationReference": affiliation_reference,
                "validTo": _instant(command.valid_to),
                "expectedVersion": command.expected_version,
            }
        )
        replay = self._resolve(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
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
                request_fingerprint=fingerprint,
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
                fingerprint=fingerprint,
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
        fingerprint: str,
    ) -> ResponsibilityMutationResult | None:
        receipt = self._catalogue.find_command_receipt(
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is None:
            return None
        if (
            receipt.command_kind != _CREATE_RESPONSIBILITY
            or receipt.request_fingerprint != fingerprint
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

        resource_reference = _required(command.resource_reference)
        party_reference = _required(command.party_reference)
        display_name = _required(command.display_name)
        idempotency_key = _required(command.idempotency_key)
        contact = _optional(command.contact)
        if (
            resource_reference is None
            or party_reference is None
            or display_name is None
            or idempotency_key is None
            or (command.contact is not None and contact is None)
        ):
            return ResponsibilityMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        fingerprint = _fingerprint(
            {
                "resourceReference": resource_reference,
                "partyReference": party_reference,
                "partyKind": command.party_kind.value,
                "role": command.role.value,
                "displayName": display_name,
                "contact": contact,
                "validFrom": _instant(command.valid_from),
                "validTo": _instant(command.valid_to),
            }
        )
        replay = self._resolve(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
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
                request_fingerprint=fingerprint,
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
                fingerprint=fingerprint,
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
        fingerprint: str,
    ) -> ResponsibilityMutationResult | None:
        receipt = self._catalogue.find_command_receipt(
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is None:
            return None
        if (
            receipt.command_kind != _END_RESPONSIBILITY
            or receipt.request_fingerprint != fingerprint
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

        assignment_reference = _required(command.assignment_reference)
        idempotency_key = _required(command.idempotency_key)
        if (
            assignment_reference is None
            or idempotency_key is None
            or command.expected_version < 1
        ):
            return ResponsibilityMutationResult(TemporalCurationOutcome.INPUT_INVALID)

        fingerprint = _fingerprint(
            {
                "assignmentReference": assignment_reference,
                "validTo": _instant(command.valid_to),
                "expectedVersion": command.expected_version,
            }
        )
        replay = self._resolve(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
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
                request_fingerprint=fingerprint,
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
                fingerprint=fingerprint,
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
