from napms.access_policy_realization.adapters.technical_access_evidence import (
    TechnicalAccessEvidenceProjectionAdapter,
)
from napms.access_policy_realization.application.ports import (
    ConfiguredEvidenceProjection,
    ConfiguredPermitProjection,
    ConfiguredPolicySemantics,
    ManagedReconciliationScopeContract,
)
from napms.access_policy_realization.domain.model import (
    KnowledgeGap,
)
from napms.technical_access_evidence.application.read import (
    EvidenceSetDetailOutcome,
)
from napms.technical_access_evidence.domain.model import (
    EvidenceAction,
    EvidenceKind,
    EvidenceTimeKind,
)


def _gap(
    reason: str,
    *references: str,
) -> KnowledgeGap:
    return KnowledgeGap(
        owner="Access Policy Realization",
        reason=reason,
        references=tuple(
            value
            for value in references
            if value
        ),
    )


class ConfiguredEvidenceProjectionAdapter:
    def __init__(
        self,
        *,
        get_evidence_set,
        entry_projection: (
            TechnicalAccessEvidenceProjectionAdapter
            | None
        ) = None,
    ) -> None:
        self._get_evidence_set = (
            get_evidence_set
        )
        self._entry_projection = (
            entry_projection
            or TechnicalAccessEvidenceProjectionAdapter()
        )

    def load_configured(
        self,
        *,
        evidence_set_id,
        contract: ManagedReconciliationScopeContract,
        as_of,
    ) -> ConfiguredEvidenceProjection:
        requested_reference = (
            "tae-evidence-set:"
            + str(evidence_set_id)
        )
        contract_reference = (
            "managed-scope-contract:"
            + contract.managed_scope.source_contract_reference
        )
        base_references = (
            requested_reference,
            contract_reference,
            (
                "managed-scope-contract-provenance:"
                + contract.provenance_reference
            ),
        )

        detail = self._get_evidence_set.execute(
            evidence_set_id
        )
        if (
            detail.outcome
            is not EvidenceSetDetailOutcome.FOUND
            or detail.evidence_set is None
        ):
            return ConfiguredEvidenceProjection(
                managed_scope=(
                    contract.managed_scope
                ),
                as_of=as_of,
                permits=(),
                evidence_references=(
                    base_references
                ),
                complete_for_managed_scope=False,
                knowledge_gaps=(
                    _gap(
                        "ConfiguredEvidenceSetNotFound",
                        requested_reference,
                    ),
                ),
            )

        evidence_set = detail.evidence_set
        references = list(
            base_references
        )
        references.extend(
            (
                (
                    "tae-source:"
                    + evidence_set.source.namespace
                    + ":"
                    + evidence_set.source.reference
                ),
                (
                    "tae-source-scope:"
                    + evidence_set.source_scope.value
                ),
                (
                    "tae-source-capture:"
                    + evidence_set.source_capture_reference.value
                ),
                (
                    "tae-kind:"
                    + evidence_set.kind.value
                ),
            )
        )
        gaps: list[KnowledgeGap] = []

        if (
            contract.semantics
            is not ConfiguredPolicySemantics.EFFECTIVE_PERMIT_SET
        ):
            gaps.append(
                _gap(
                    "ConfiguredPolicySemanticsUnsupported",
                    contract_reference,
                )
            )
        if not (
            contract.complete_for_managed_scope
        ):
            gaps.append(
                _gap(
                    "ConfiguredManagedScopeIncomplete",
                    contract_reference,
                )
            )
        if (
            evidence_set.kind
            is not EvidenceKind.CONFIGURED
        ):
            gaps.append(
                _gap(
                    "EvidenceKindNotConfigured",
                    requested_reference,
                )
            )
        if (
            evidence_set.source.namespace
            != contract.evidence_source_namespace
            or evidence_set.source.reference
            != contract.evidence_source_reference
        ):
            gaps.append(
                _gap(
                    "ConfiguredEvidenceSourceMismatch",
                    requested_reference,
                    contract_reference,
                )
            )
        if (
            evidence_set.source_scope.value
            != contract.evidence_source_scope_reference
        ):
            gaps.append(
                _gap(
                    "ConfiguredEvidenceScopeMismatch",
                    requested_reference,
                    contract_reference,
                )
            )
        if (
            evidence_set.evidence_time.kind
            is not EvidenceTimeKind.INSTANT
            or evidence_set.evidence_time.at
            != as_of
        ):
            gaps.append(
                _gap(
                    "ConfiguredEvidenceTimeMismatch",
                    requested_reference,
                )
            )

        permits: list[
            ConfiguredPermitProjection
        ] = []
        if (
            evidence_set.kind
            is EvidenceKind.CONFIGURED
        ):
            for entry in evidence_set.entries:
                if (
                    entry.payload.action
                    is not EvidenceAction.PERMIT
                ):
                    gaps.append(
                        _gap(
                            "ConfiguredSourceNotEffectivePermitSet",
                            (
                                "tae-evidence-entry:"
                                + str(
                                    entry.evidence_entry_id
                                )
                            ),
                        )
                    )
                    continue
                projected = (
                    self._entry_projection.project_entry(
                        evidence_set=(
                            evidence_set
                        ),
                        evidence_entry_id=(
                            entry.evidence_entry_id
                        ),
                    )
                )
                permits.append(
                    ConfiguredPermitProjection(
                        predicate=(
                            projected.predicate
                        ),
                        input_provenance=(
                            projected.input_provenance
                        ),
                    )
                )

        return ConfiguredEvidenceProjection(
            managed_scope=contract.managed_scope,
            as_of=as_of,
            permits=tuple(permits),
            evidence_references=tuple(
                references
            ),
            complete_for_managed_scope=(
                contract.complete_for_managed_scope
                and not gaps
            ),
            knowledge_gaps=tuple(gaps),
        )
