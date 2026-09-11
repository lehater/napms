from itertools import product

from napms.policy_export.application.export_snapshot import (
    CapturedResourceRealization,
    ExportSnapshotItem,
    SuccessfulExportSnapshot,
)
from napms.policy_export.application.normalization_ports import (
    DcsProjectionDecodeError,
    DcsProjectionDecoder,
)
from napms.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    NormalizationInvariantError,
    NormalizedPolicyRow,
    PortConstraint,
    SuccessfulNormalizedPolicyExport,
)
from napms.policy_export.application.ports import ApplicationProjectionOutcome


class NormalizeExportSnapshot:
    def __init__(self, *, decoder: DcsProjectionDecoder) -> None:
        self._decoder = decoder

    def execute(
        self,
        snapshot: SuccessfulExportSnapshot,
    ) -> SuccessfulNormalizedPolicyExport:
        self._validate_snapshot(snapshot)

        rows: list[NormalizedPolicyRow] = []
        for item in sorted(snapshot.items, key=lambda value: value.rule.rule_id.int):
            payload = item.application_projection.dcs_projection_payload
            if not isinstance(payload, bytes) or not payload:
                raise NormalizationInvariantError(
                    "successful snapshot item requires non-empty DCS payload"
                )

            try:
                alternatives = self._decoder.decode(payload)
            except DcsProjectionDecodeError as exc:
                raise NormalizationInvariantError(
                    "DCS projection payload cannot be normalized"
                ) from exc

            if (
                not alternatives
                or any(
                    not isinstance(alternative, DcsTrafficAlternative)
                    for alternative in alternatives
                )
            ):
                raise NormalizationInvariantError(
                    "decoder must return one-or-more DcsTrafficAlternative values"
                )

            source_endpoints = _flatten_realizations(item.source_realizations)
            destination_endpoints = _flatten_realizations(
                item.destination_realizations
            )
            if not source_endpoints or not destination_endpoints:
                raise NormalizationInvariantError(
                    "successful snapshot item requires source and destination realizations"
                )

            ordered_alternatives = sorted(alternatives, key=_alternative_sort_key)
            for source, destination, alternative in product(
                source_endpoints,
                destination_endpoints,
                ordered_alternatives,
            ):
                source_capture, source_endpoint = source
                destination_capture, destination_endpoint = destination
                rule = item.rule
                application = item.application_projection

                rows.append(
                    NormalizedPolicyRow(
                        rule_id=rule.rule_id,
                        rule_semantic_identity=rule.semantic_identity,
                        decision_reference=rule.decision.decision_id,
                        rule_governance_scope=rule.governance_scope,
                        rule_operational_state=rule.operational_state,
                        rule_effective_window=rule.effective_window,
                        snapshot_as_of=snapshot.as_of,
                        read_authority_reference=snapshot.authority_reference,
                        source_resource_reference=source_capture.resource_reference,
                        source_endpoint_reference=source_endpoint.endpoint_reference,
                        source_technical_address=source_endpoint.technical_address,
                        source_fact_reference=source_capture.fact_reference,
                        source_validity_reference=source_capture.validity_reference,
                        source_provenance_reference=source_capture.provenance_reference,
                        destination_resource_reference=(
                            destination_capture.resource_reference
                        ),
                        destination_endpoint_reference=(
                            destination_endpoint.endpoint_reference
                        ),
                        destination_technical_address=(
                            destination_endpoint.technical_address
                        ),
                        destination_fact_reference=destination_capture.fact_reference,
                        destination_validity_reference=(
                            destination_capture.validity_reference
                        ),
                        destination_provenance_reference=(
                            destination_capture.provenance_reference
                        ),
                        protocol=alternative.protocol,
                        source_ports=alternative.source_ports,
                        destination_ports=alternative.destination_ports,
                        service_reference=alternative.service_reference,
                        acc_fact_reference=application.fact_reference,
                        acc_validity_reference=application.validity_reference,
                        acc_provenance_reference=application.provenance_reference,
                    )
                )

        return SuccessfulNormalizedPolicyExport(
            scope=snapshot.scope,
            as_of=snapshot.as_of,
            authority_reference=snapshot.authority_reference,
            rows=tuple(rows),
        )

    def _validate_snapshot(self, snapshot: SuccessfulExportSnapshot) -> None:
        if (
            not snapshot.scope
            or not snapshot.authority_reference
            or snapshot.as_of.tzinfo is None
            or snapshot.as_of.utcoffset() is None
        ):
            raise NormalizationInvariantError(
                "snapshot requires scope, authority provenance and aware as-of"
            )

        rule_ids = [item.rule.rule_id for item in snapshot.items]
        if len(set(rule_ids)) != len(rule_ids):
            raise NormalizationInvariantError(
                "snapshot cannot contain the same authoritative Rule twice"
            )

        for item in snapshot.items:
            rule = item.rule
            application = item.application_projection
            if (
                rule.governance_scope != snapshot.scope
                or not rule.contributes_effect_at(snapshot.as_of)
            ):
                raise NormalizationInvariantError(
                    "snapshot contains Rule outside its effective authorized selection"
                )

            if (
                application.outcome is not ApplicationProjectionOutcome.RESOLVED
                or application.subject != rule.semantic_identity
                or application.as_of != snapshot.as_of
                or not application.fact_reference
                or not application.validity_reference
                or not application.provenance_reference
            ):
                raise NormalizationInvariantError(
                    "snapshot application projection correlation/provenance is invalid"
                )

            if tuple(
                value.resource_reference for value in item.source_realizations
            ) != application.source_resource_references:
                raise NormalizationInvariantError(
                    "source realization set does not match ACC Resource references"
                )
            if tuple(
                value.resource_reference for value in item.destination_realizations
            ) != application.destination_resource_references:
                raise NormalizationInvariantError(
                    "destination realization set does not match ACC Resource references"
                )

            _validate_realizations(item)


def _validate_realizations(item: ExportSnapshotItem) -> None:
    for capture in item.source_realizations + item.destination_realizations:
        if (
            not capture.resource_reference.value
            or not capture.fact_reference
            or not capture.validity_reference
            or not capture.provenance_reference
            or not capture.endpoint_realizations
        ):
            raise NormalizationInvariantError(
                "captured Resource realization is incomplete"
            )
        if any(
            not endpoint.endpoint_reference or not endpoint.technical_address
            for endpoint in capture.endpoint_realizations
        ):
            raise NormalizationInvariantError(
                "captured endpoint realization is incomplete"
            )


def _flatten_realizations(realizations):
    flattened = []
    for capture in realizations:
        for endpoint in capture.endpoint_realizations:
            flattened.append((capture, endpoint))
    return tuple(
        sorted(
            flattened,
            key=lambda item: (
                item[0].resource_reference.value,
                item[1].endpoint_reference,
                item[1].technical_address,
            ),
        )
    )


def _constraint_sort_key(constraint: PortConstraint):
    return (
        constraint.kind.value,
        tuple((range_.first, range_.last) for range_ in constraint.ranges),
    )


def _alternative_sort_key(alternative: DcsTrafficAlternative):
    return (
        alternative.protocol,
        _constraint_sort_key(alternative.source_ports),
        _constraint_sort_key(alternative.destination_ports),
        alternative.service_reference or "",
    )
