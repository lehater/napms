from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from napms.contexts.access_policy.application.select_effective_policy import (
    EffectivePolicySelectionOutcome,
    EffectivePolicySelectionResult,
)
from napms.contexts.access_policy.domain.model import AccessRule
from napms.policy_export.application.ports import (
    ApplicationCommunicationProjectionPort,
    ApplicationProjectionFact,
    ApplicationProjectionOutcome,
    EndpointRealization,
    ResourceCatalogueProjectionPort,
    ResourceRealizationFact,
    ResourceRealizationOutcome,
    ResourceReference,
)


class SnapshotAssemblyOutcome(str, Enum):
    SUCCESS = "Success"
    SELECTION_UNAVAILABLE = "SelectionUnavailable"
    INCOMPLETE = "Incomplete"


class SnapshotFactSource(str, Enum):
    EFFECTIVE_SELECTION = "EffectiveSelection"
    APPLICATION_COMMUNICATION_CATALOGUE = "ApplicationCommunicationCatalogue"
    RESOURCE_CATALOGUE = "ResourceCatalogue"


class SnapshotFailureCategory(str, Enum):
    MISSING = "Missing"
    INVALID = "Invalid"
    STALE = "Stale"
    UNKNOWN = "Unknown"
    CORRELATION_MISMATCH = "CorrelationMismatch"
    NON_EFFECTIVE_SELECTION = "NonEffectiveSelection"


@dataclass(frozen=True, slots=True)
class SnapshotDiagnostic:
    rule_id: UUID | None
    source: SnapshotFactSource
    category: SnapshotFailureCategory
    reference: str | None = None


@dataclass(frozen=True, slots=True)
class CapturedResourceRealization:
    resource_reference: ResourceReference
    endpoint_realizations: tuple[EndpointRealization, ...]
    fact_reference: str
    validity_reference: str
    provenance_reference: str


@dataclass(frozen=True, slots=True)
class ExportSnapshotItem:
    rule: AccessRule
    application_projection: ApplicationProjectionFact
    source_realizations: tuple[CapturedResourceRealization, ...]
    destination_realizations: tuple[CapturedResourceRealization, ...]


@dataclass(frozen=True, slots=True)
class SuccessfulExportSnapshot:
    scope: str
    as_of: datetime
    authority_reference: str
    items: tuple[ExportSnapshotItem, ...]


@dataclass(frozen=True, slots=True)
class ExportSnapshotAssemblyResult:
    outcome: SnapshotAssemblyOutcome
    snapshot: SuccessfulExportSnapshot | None = None
    diagnostics: tuple[SnapshotDiagnostic, ...] = ()


class AssembleExportSnapshot:
    def __init__(
        self,
        *,
        application_catalogue: ApplicationCommunicationProjectionPort,
        resource_catalogue: ResourceCatalogueProjectionPort,
    ) -> None:
        self._application_catalogue = application_catalogue
        self._resource_catalogue = resource_catalogue

    def execute(
        self,
        selection: EffectivePolicySelectionResult,
    ) -> ExportSnapshotAssemblyResult:
        selection_diagnostics = self._validate_selection(selection)
        if selection_diagnostics:
            outcome = (
                SnapshotAssemblyOutcome.SELECTION_UNAVAILABLE
                if selection.outcome is not EffectivePolicySelectionOutcome.SELECTED
                or not selection.authority_reference
                else SnapshotAssemblyOutcome.INCOMPLETE
            )
            return ExportSnapshotAssemblyResult(
                outcome=outcome,
                diagnostics=tuple(selection_diagnostics),
            )

        realization_cache: dict[ResourceReference, ResourceRealizationFact] = {}
        items: list[ExportSnapshotItem] = []
        diagnostics: list[SnapshotDiagnostic] = []

        for rule in selection.rules:
            application_fact = self._application_catalogue.resolve_projection(
                subject=rule.semantic_identity,
                as_of=selection.as_of,
            )
            application_diagnostics = self._validate_application_fact(
                rule=rule,
                selection=selection,
                fact=application_fact,
            )
            if application_diagnostics:
                diagnostics.extend(application_diagnostics)
                continue

            source_realizations, source_diagnostics = self._capture_realizations(
                rule=rule,
                references=application_fact.source_resource_references,
                as_of=selection.as_of,
                cache=realization_cache,
            )
            destination_realizations, destination_diagnostics = (
                self._capture_realizations(
                    rule=rule,
                    references=application_fact.destination_resource_references,
                    as_of=selection.as_of,
                    cache=realization_cache,
                )
            )
            diagnostics.extend(source_diagnostics)
            diagnostics.extend(destination_diagnostics)
            if source_diagnostics or destination_diagnostics:
                continue

            items.append(
                ExportSnapshotItem(
                    rule=rule,
                    application_projection=application_fact,
                    source_realizations=source_realizations,
                    destination_realizations=destination_realizations,
                )
            )

        if diagnostics:
            return ExportSnapshotAssemblyResult(
                outcome=SnapshotAssemblyOutcome.INCOMPLETE,
                diagnostics=tuple(diagnostics),
            )

        return ExportSnapshotAssemblyResult(
            outcome=SnapshotAssemblyOutcome.SUCCESS,
            snapshot=SuccessfulExportSnapshot(
                scope=selection.scope,
                as_of=selection.as_of,
                authority_reference=selection.authority_reference,
                items=tuple(items),
            ),
        )

    def _validate_selection(
        self,
        selection: EffectivePolicySelectionResult,
    ) -> list[SnapshotDiagnostic]:
        if (
            selection.outcome is not EffectivePolicySelectionOutcome.SELECTED
            or not selection.authority_reference
        ):
            return [
                SnapshotDiagnostic(
                    rule_id=None,
                    source=SnapshotFactSource.EFFECTIVE_SELECTION,
                    category=SnapshotFailureCategory.UNKNOWN,
                )
            ]

        if selection.as_of.tzinfo is None or selection.as_of.utcoffset() is None:
            return [
                SnapshotDiagnostic(
                    rule_id=None,
                    source=SnapshotFactSource.EFFECTIVE_SELECTION,
                    category=SnapshotFailureCategory.INVALID,
                )
            ]

        rule_ids = [rule.rule_id for rule in selection.rules]
        if len(set(rule_ids)) != len(rule_ids):
            return [
                SnapshotDiagnostic(
                    rule_id=None,
                    source=SnapshotFactSource.EFFECTIVE_SELECTION,
                    category=SnapshotFailureCategory.INVALID,
                )
            ]

        diagnostics: list[SnapshotDiagnostic] = []
        for rule in selection.rules:
            if rule.governance_scope != selection.scope:
                diagnostics.append(
                    SnapshotDiagnostic(
                        rule_id=rule.rule_id,
                        source=SnapshotFactSource.EFFECTIVE_SELECTION,
                        category=SnapshotFailureCategory.CORRELATION_MISMATCH,
                        reference=rule.governance_scope,
                    )
                )
            elif not rule.contributes_effect_at(selection.as_of):
                diagnostics.append(
                    SnapshotDiagnostic(
                        rule_id=rule.rule_id,
                        source=SnapshotFactSource.EFFECTIVE_SELECTION,
                        category=SnapshotFailureCategory.NON_EFFECTIVE_SELECTION,
                    )
                )
        return diagnostics

    def _validate_application_fact(
        self,
        *,
        rule: AccessRule,
        selection: EffectivePolicySelectionResult,
        fact: ApplicationProjectionFact,
    ) -> list[SnapshotDiagnostic]:
        if fact.outcome is not ApplicationProjectionOutcome.RESOLVED:
            category = {
                ApplicationProjectionOutcome.MISSING: SnapshotFailureCategory.MISSING,
                ApplicationProjectionOutcome.INVALID: SnapshotFailureCategory.INVALID,
                ApplicationProjectionOutcome.UNKNOWN: SnapshotFailureCategory.UNKNOWN,
            }[fact.outcome]
            return [
                SnapshotDiagnostic(
                    rule_id=rule.rule_id,
                    source=SnapshotFactSource.APPLICATION_COMMUNICATION_CATALOGUE,
                    category=category,
                )
            ]

        diagnostics: list[SnapshotDiagnostic] = []
        if fact.subject != rule.semantic_identity or fact.as_of != selection.as_of:
            diagnostics.append(
                SnapshotDiagnostic(
                    rule_id=rule.rule_id,
                    source=SnapshotFactSource.APPLICATION_COMMUNICATION_CATALOGUE,
                    category=SnapshotFailureCategory.CORRELATION_MISMATCH,
                )
            )

        if (
            not fact.source_resource_references
            or not fact.destination_resource_references
            or len(set(fact.source_resource_references))
            != len(fact.source_resource_references)
            or len(set(fact.destination_resource_references))
            != len(fact.destination_resource_references)
            or any(
                not reference.value
                for reference in fact.source_resource_references
            )
            or any(
                not reference.value
                for reference in fact.destination_resource_references
            )
            or not fact.dcs_projection_payload
            or not fact.fact_reference
            or not fact.validity_reference
            or not fact.provenance_reference
        ):
            diagnostics.append(
                SnapshotDiagnostic(
                    rule_id=rule.rule_id,
                    source=SnapshotFactSource.APPLICATION_COMMUNICATION_CATALOGUE,
                    category=SnapshotFailureCategory.INVALID,
                )
            )

        return diagnostics

    def _capture_realizations(
        self,
        *,
        rule: AccessRule,
        references: tuple[ResourceReference, ...],
        as_of: datetime,
        cache: dict[ResourceReference, ResourceRealizationFact],
    ) -> tuple[
        tuple[CapturedResourceRealization, ...],
        list[SnapshotDiagnostic],
    ]:
        captured: list[CapturedResourceRealization] = []
        diagnostics: list[SnapshotDiagnostic] = []

        for reference in references:
            fact = cache.get(reference)
            if fact is None:
                fact = self._resource_catalogue.resolve_realization(
                    resource_reference=reference,
                    as_of=as_of,
                )
                cache[reference] = fact

            diagnostic = self._validate_resource_fact(
                rule=rule,
                requested_reference=reference,
                as_of=as_of,
                fact=fact,
            )
            if diagnostic is not None:
                diagnostics.append(diagnostic)
                continue

            captured.append(
                CapturedResourceRealization(
                    resource_reference=reference,
                    endpoint_realizations=fact.endpoint_realizations,
                    fact_reference=fact.fact_reference,
                    validity_reference=fact.validity_reference,
                    provenance_reference=fact.provenance_reference,
                )
            )

        return tuple(captured), diagnostics

    def _validate_resource_fact(
        self,
        *,
        rule: AccessRule,
        requested_reference: ResourceReference,
        as_of: datetime,
        fact: ResourceRealizationFact,
    ) -> SnapshotDiagnostic | None:
        if fact.outcome is not ResourceRealizationOutcome.RESOLVED:
            category = {
                ResourceRealizationOutcome.MISSING: SnapshotFailureCategory.MISSING,
                ResourceRealizationOutcome.STALE: SnapshotFailureCategory.STALE,
                ResourceRealizationOutcome.UNKNOWN: SnapshotFailureCategory.UNKNOWN,
            }[fact.outcome]
            return SnapshotDiagnostic(
                rule_id=rule.rule_id,
                source=SnapshotFactSource.RESOURCE_CATALOGUE,
                category=category,
                reference=requested_reference.value,
            )

        if fact.resource_reference != requested_reference or fact.as_of != as_of:
            return SnapshotDiagnostic(
                rule_id=rule.rule_id,
                source=SnapshotFactSource.RESOURCE_CATALOGUE,
                category=SnapshotFailureCategory.CORRELATION_MISMATCH,
                reference=requested_reference.value,
            )

        if (
            not fact.endpoint_realizations
            or any(
                not endpoint.endpoint_reference or not endpoint.technical_address
                for endpoint in fact.endpoint_realizations
            )
            or not fact.fact_reference
            or not fact.validity_reference
            or not fact.provenance_reference
        ):
            return SnapshotDiagnostic(
                rule_id=rule.rule_id,
                source=SnapshotFactSource.RESOURCE_CATALOGUE,
                category=SnapshotFailureCategory.INVALID,
                reference=requested_reference.value,
            )

        return None
