from datetime import datetime, timedelta, timezone
from uuid import UUID

from napms.contexts.access_policy.domain.model import (
    EffectiveWindow,
    OperationalState,
    RuleSemanticIdentity,
)
from napms.workflows.policy_export.application.normalization_types import (
    NormalizedPolicyRow,
    PortConstraint,
    PortRange,
    SuccessfulNormalizedPolicyExport,
)
from napms.workflows.policy_export.application.ports import ResourceReference
from napms.workflows.policy_export.presentation.http.json import normalized_policy_export_json


AS_OF = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)


def test_normalized_policy_json_preserves_complete_row_semantics_and_provenance():
    identity = RuleSemanticIdentity(UUID(int=1), UUID(int=2), UUID(int=3))
    row = NormalizedPolicyRow(
        rule_id=UUID(int=4),
        rule_semantic_identity=identity,
        decision_reference="decision-1",
        rule_governance_scope="scope-a",
        rule_operational_state=OperationalState.ACTIVE,
        rule_effective_window=EffectiveWindow(
            AS_OF - timedelta(hours=1),
            AS_OF + timedelta(hours=1),
        ),
        snapshot_as_of=AS_OF,
        read_authority_reference="read-auth-1",
        source_resource_reference=ResourceReference("src-resource"),
        source_endpoint_reference="src-endpoint",
        source_technical_address="198.51.100.10",
        source_fact_reference="src-fact",
        source_validity_reference="src-validity",
        source_provenance_reference="src-provenance",
        destination_resource_reference=ResourceReference("dst-resource"),
        destination_endpoint_reference="dst-endpoint",
        destination_technical_address="203.0.113.20",
        destination_fact_reference="dst-fact",
        destination_validity_reference="dst-validity",
        destination_provenance_reference="dst-provenance",
        protocol="tcp",
        source_ports=PortConstraint.any(),
        destination_ports=PortConstraint.ranged(
            PortRange(443, 443),
            PortRange(1000, 1005),
        ),
        service_reference="https",
        acc_fact_reference="acc-fact",
        acc_validity_reference="acc-validity",
        acc_provenance_reference="acc-provenance",
    )
    export = SuccessfulNormalizedPolicyExport(
        scope="scope-a",
        as_of=AS_OF,
        authority_reference="read-auth-1",
        rows=(row,),
    )

    payload = normalized_policy_export_json(export)

    assert payload["scope"] == "scope-a"
    assert payload["asOf"] == AS_OF.isoformat()
    assert payload["authorityReference"] == "read-auth-1"

    encoded = payload["rows"][0]
    assert encoded["ruleId"] == str(UUID(int=4))
    assert encoded["semanticIdentity"] == {
        "sourceComponentDeploymentId": str(UUID(int=1)),
        "destinationComponentDeploymentId": str(UUID(int=2)),
        "dcsContractRevisionId": str(UUID(int=3)),
    }
    assert encoded["decisionReference"] == "decision-1"
    assert encoded["governanceScope"] == "scope-a"
    assert encoded["operationalState"] == "Active"
    assert encoded["effectiveWindow"] == {
        "start": (AS_OF - timedelta(hours=1)).isoformat(),
        "end": (AS_OF + timedelta(hours=1)).isoformat(),
    }
    assert encoded["snapshotAsOf"] == AS_OF.isoformat()
    assert encoded["readAuthorityReference"] == "read-auth-1"

    assert encoded["source"] == {
        "resourceReference": "src-resource",
        "endpointReference": "src-endpoint",
        "technicalAddress": "198.51.100.10",
        "factReference": "src-fact",
        "validityReference": "src-validity",
        "provenanceReference": "src-provenance",
    }
    assert encoded["destination"] == {
        "resourceReference": "dst-resource",
        "endpointReference": "dst-endpoint",
        "technicalAddress": "203.0.113.20",
        "factReference": "dst-fact",
        "validityReference": "dst-validity",
        "provenanceReference": "dst-provenance",
    }

    assert encoded["traffic"]["protocol"] == "tcp"
    assert encoded["traffic"]["sourcePorts"] == {"kind": "Any"}
    assert encoded["traffic"]["destinationPorts"] == {
        "kind": "Ranges",
        "ranges": [
            {"first": 443, "last": 443},
            {"first": 1000, "last": 1005},
        ],
    }
    assert encoded["traffic"]["serviceReference"] == "https"
    assert encoded["applicationCommunicationCatalogue"] == {
        "factReference": "acc-fact",
        "validityReference": "acc-validity",
        "provenanceReference": "acc-provenance",
    }


def test_not_applicable_remains_distinct_from_any_in_json():
    identity = RuleSemanticIdentity(UUID(int=1), UUID(int=2), UUID(int=3))
    row = NormalizedPolicyRow(
        rule_id=UUID(int=4),
        rule_semantic_identity=identity,
        decision_reference=None,
        rule_governance_scope="scope-a",
        rule_operational_state=OperationalState.ACTIVE,
        rule_effective_window=None,
        snapshot_as_of=AS_OF,
        read_authority_reference="read-auth-1",
        source_resource_reference=ResourceReference("src"),
        source_endpoint_reference="src-endpoint",
        source_technical_address="198.51.100.10",
        source_fact_reference="src-fact",
        source_validity_reference="src-validity",
        source_provenance_reference="src-provenance",
        destination_resource_reference=ResourceReference("dst"),
        destination_endpoint_reference="dst-endpoint",
        destination_technical_address="203.0.113.20",
        destination_fact_reference="dst-fact",
        destination_validity_reference="dst-validity",
        destination_provenance_reference="dst-provenance",
        protocol="ip-protocol-x",
        source_ports=PortConstraint.not_applicable(),
        destination_ports=PortConstraint.any(),
        service_reference=None,
        acc_fact_reference="acc-fact",
        acc_validity_reference="acc-validity",
        acc_provenance_reference="acc-provenance",
    )

    payload = normalized_policy_export_json(
        SuccessfulNormalizedPolicyExport(
            scope="scope-a",
            as_of=AS_OF,
            authority_reference="read-auth-1",
            rows=(row,),
        )
    )

    traffic = payload["rows"][0]["traffic"]
    assert traffic["sourcePorts"] == {"kind": "NotApplicable"}
    assert traffic["destinationPorts"] == {"kind": "Any"}
