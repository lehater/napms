from typing import Any

from napms.policy_export.application.export_snapshot import SnapshotDiagnostic
from napms.policy_export.application.normalization_types import (
    NormalizedPolicyRow,
    PortConstraint,
    SuccessfulNormalizedPolicyExport,
)


def port_constraint_json(value: PortConstraint) -> dict[str, Any]:
    result: dict[str, Any] = {"kind": value.kind.value}
    if value.ranges:
        result["ranges"] = [
            {"first": range_.first, "last": range_.last}
            for range_ in value.ranges
        ]
    return result


def normalized_policy_row_json(row: NormalizedPolicyRow) -> dict[str, Any]:
    effective_window = None
    if row.rule_effective_window is not None:
        effective_window = {
            "start": row.rule_effective_window.start.isoformat(),
            "end": row.rule_effective_window.end.isoformat(),
        }

    return {
        "ruleId": str(row.rule_id),
        "semanticIdentity": {
            "sourceComponentDeploymentId": str(
                row.rule_semantic_identity.source_component_deployment_id
            ),
            "destinationComponentDeploymentId": str(
                row.rule_semantic_identity.destination_component_deployment_id
            ),
            "dcsContractRevisionId": str(
                row.rule_semantic_identity.dcs_contract_revision_id
            ),
        },
        "decisionReference": row.decision_reference,
        "governanceScope": row.rule_governance_scope,
        "operationalState": row.rule_operational_state.value,
        "effectiveWindow": effective_window,
        "snapshotAsOf": row.snapshot_as_of.isoformat(),
        "readAuthorityReference": row.read_authority_reference,
        "source": {
            "resourceReference": row.source_resource_reference.value,
            "endpointReference": row.source_endpoint_reference,
            "technicalAddress": row.source_technical_address,
            "factReference": row.source_fact_reference,
            "validityReference": row.source_validity_reference,
            "provenanceReference": row.source_provenance_reference,
        },
        "destination": {
            "resourceReference": row.destination_resource_reference.value,
            "endpointReference": row.destination_endpoint_reference,
            "technicalAddress": row.destination_technical_address,
            "factReference": row.destination_fact_reference,
            "validityReference": row.destination_validity_reference,
            "provenanceReference": row.destination_provenance_reference,
        },
        "traffic": {
            "protocol": row.protocol,
            "sourcePorts": port_constraint_json(row.source_ports),
            "destinationPorts": port_constraint_json(row.destination_ports),
            "serviceReference": row.service_reference,
        },
        "applicationCommunicationCatalogue": {
            "factReference": row.acc_fact_reference,
            "validityReference": row.acc_validity_reference,
            "provenanceReference": row.acc_provenance_reference,
        },
    }


def normalized_policy_export_json(
    value: SuccessfulNormalizedPolicyExport,
) -> dict[str, Any]:
    return {
        "scope": value.scope,
        "asOf": value.as_of.isoformat(),
        "authorityReference": value.authority_reference,
        "rows": [normalized_policy_row_json(row) for row in value.rows],
    }


def snapshot_diagnostic_json(value: SnapshotDiagnostic) -> dict[str, Any]:
    return {
        "ruleId": str(value.rule_id) if value.rule_id is not None else None,
        "source": value.source.value,
        "category": value.category.value,
        "reference": value.reference,
    }
