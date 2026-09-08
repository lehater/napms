from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256

from napms.access_policy.domain.model import RuleSemanticIdentity
from napms.application_catalogue.application.ports import (
    ApplicationCatalogueRepository,
)
from napms.application_catalogue.domain.model import (
    CatalogueInvariantError,
    DeploymentResourceBinding,
)


class CatalogueResolutionOutcome(str, Enum):
    RESOLVED = "Resolved"
    MISSING = "Missing"
    INVALID = "Invalid"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class DirectedInteractionResolution:
    outcome: CatalogueResolutionOutcome
    identity: RuleSemanticIdentity | None = None
    provenance_reference: str | None = None


@dataclass(frozen=True, slots=True)
class ApplicationProjectionResolution:
    outcome: CatalogueResolutionOutcome
    subject: RuleSemanticIdentity | None = None
    as_of: datetime | None = None
    source_resource_references: tuple[str, ...] = ()
    destination_resource_references: tuple[str, ...] = ()
    projection_payload: bytes | None = None
    fact_reference: str | None = None
    validity_reference: str | None = None
    provenance_reference: str | None = None


def _require_aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise CatalogueInvariantError("effective time must be offset-aware")


class ValidateDirectedInteraction:
    def __init__(self, *, catalogue: ApplicationCatalogueRepository) -> None:
        self._catalogue = catalogue

    def execute(
        self,
        *,
        identity: RuleSemanticIdentity,
        effective_time: datetime,
    ) -> DirectedInteractionResolution:
        _require_aware(effective_time)
        dcs = self._catalogue.get_dcs_revision(identity.dcs_contract_revision_id)
        if dcs is None:
            return DirectedInteractionResolution(CatalogueResolutionOutcome.MISSING)
        if (
            dcs.source_component_deployment_id
            != identity.source_component_deployment_id
            or dcs.destination_component_deployment_id
            != identity.destination_component_deployment_id
        ):
            return DirectedInteractionResolution(CatalogueResolutionOutcome.INVALID)

        return DirectedInteractionResolution(
            CatalogueResolutionOutcome.RESOLVED,
            identity=identity,
            provenance_reference=dcs.provenance_reference,
        )


class ResolveApplicationProjection:
    def __init__(self, *, catalogue: ApplicationCatalogueRepository) -> None:
        self._catalogue = catalogue

    def execute(
        self,
        *,
        subject: RuleSemanticIdentity,
        as_of: datetime,
    ) -> ApplicationProjectionResolution:
        _require_aware(as_of)
        dcs = self._catalogue.get_dcs_revision(subject.dcs_contract_revision_id)
        if dcs is None:
            return ApplicationProjectionResolution(CatalogueResolutionOutcome.MISSING)
        if (
            dcs.source_component_deployment_id
            != subject.source_component_deployment_id
            or dcs.destination_component_deployment_id
            != subject.destination_component_deployment_id
        ):
            return ApplicationProjectionResolution(CatalogueResolutionOutcome.INVALID)

        source_bindings = self._catalogue.find_effective_bindings(
            component_deployment_id=subject.source_component_deployment_id,
            as_of=as_of,
        )
        destination_bindings = self._catalogue.find_effective_bindings(
            component_deployment_id=subject.destination_component_deployment_id,
            as_of=as_of,
        )
        if not source_bindings or not destination_bindings:
            return ApplicationProjectionResolution(CatalogueResolutionOutcome.MISSING)

        source_refs = _validated_resource_references(source_bindings, as_of)
        destination_refs = _validated_resource_references(destination_bindings, as_of)
        if source_refs is None or destination_refs is None:
            return ApplicationProjectionResolution(CatalogueResolutionOutcome.UNKNOWN)

        all_bindings = tuple(
            sorted(
                source_bindings + destination_bindings,
                key=lambda binding: binding.reference_id,
            )
        )
        binding_ids = ",".join(binding.reference_id for binding in all_bindings)
        validity_reference = f"acc-bindings:{binding_ids}"
        fact_material = (
            f"{dcs.revision_id}|{subject.source_component_deployment_id}|"
            f"{subject.destination_component_deployment_id}|{binding_ids}"
        ).encode("utf-8")
        provenance_material = (
            dcs.provenance_reference
            + "|"
            + "|".join(binding.provenance_reference for binding in all_bindings)
        ).encode("utf-8")

        return ApplicationProjectionResolution(
            CatalogueResolutionOutcome.RESOLVED,
            subject=subject,
            as_of=as_of,
            source_resource_references=source_refs,
            destination_resource_references=destination_refs,
            projection_payload=dcs.projection_payload,
            fact_reference=f"acc-projection:{sha256(fact_material).hexdigest()}",
            validity_reference=validity_reference,
            provenance_reference=(
                f"acc-provenance:{sha256(provenance_material).hexdigest()}"
            ),
        )


def _validated_resource_references(
    bindings: tuple[DeploymentResourceBinding, ...],
    as_of: datetime,
) -> tuple[str, ...] | None:
    seen: set[str] = set()
    result: list[str] = []
    for binding in sorted(bindings, key=lambda value: (value.resource_reference, value.reference_id)):
        if not binding.is_effective_at(as_of):
            return None
        if binding.resource_reference in seen:
            return None
        seen.add(binding.resource_reference)
        result.append(binding.resource_reference)
    return tuple(result)
