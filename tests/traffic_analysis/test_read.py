from datetime import datetime, timezone

from napms.traffic_analysis.application.model import (
    EndpointResolution,
    EvidenceSnapshot,
    NetworkCandidateView,
    NetworkContextView,
    PolicyMatch,
    ResolvedResource,
    ResolutionState,
    ResponsibilityItem,
    RuleMatchKind,
    TechnicalRuleMatch,
    TrafficAnalysisQuery,
)
from napms.traffic_analysis.application.read import ReadTrafficAnalysis


NOW = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)
QUERY = TrafficAnalysisQuery(
    source_address="10.10.10.10",
    destination_address="10.20.20.20",
    protocol="TCP",
    destination_port_first=443,
    destination_port_last=443,
    as_of=NOW,
)


class Endpoints:
    def resolve(self, *, address, as_of):
        resource = "source" if address == "10.10.10.10" else "destination"
        return EndpointResolution(
            state=ResolutionState.RESOLVED,
            address=address,
            resources=(
                ResolvedResource(
                    resource_reference=resource,
                    endpoint_reference=f"{resource}:endpoint",
                    technical_address=address,
                ),
            ),
        )


class Policy:
    def find_matches(self, **kwargs):
        return (
            PolicyMatch(
                source_component="Web",
                destination_component="Orders",
                dcs_reference="dcs-1",
                dcs_display_name="HTTPS",
                access_summary="TCP/443",
                requirement="Required",
                decision="Allowed",
                rule="Active",
                effective="Yes",
                scope="payments",
            ),
        )


class Network:
    def read(self, *, query):
        return NetworkContextView(
            candidates=(
                NetworkCandidateView(
                    provider_namespace="device",
                    device_reference="fw-1",
                    logical_firewall_reference=None,
                    enforcement_attachment_reference=None,
                    path_attachment_reference=None,
                    source_relevance="Possible",
                    provenance_references=("network-source",),
                ),
                NetworkCandidateView(
                    provider_namespace="device",
                    device_reference="fw-2",
                    logical_firewall_reference=None,
                    enforcement_attachment_reference=None,
                    path_attachment_reference=None,
                    source_relevance=None,
                    provenance_references=("network-source",),
                ),
            ),
            complete_for_pair=False,
            knowledge_gaps=("candidate set may contain false positives",),
        )


class Evidence:
    def latest_applicable(self, *, query, provider_namespace, device_reference):
        if device_reference == "fw-2":
            return None
        return EvidenceSnapshot(
            evidence_set_reference="snapshot-1",
            source_reference="import:fw-1",
            source_scope_reference="fw-1",
            captured_at=NOW,
            recorded_at=NOW,
            provenance_references=("capture-1",),
            matches=(
                TechnicalRuleMatch(
                    entry_reference="ACL-100",
                    action="Permit",
                    normalized="10.10.0.0-10.10.255.255 → 10.20.0.0-10.20.255.255 TCP 443",
                    match_kind=RuleMatchKind.COVERS_QUERY,
                ),
            ),
        )


class Responsibilities:
    def list_for_resources(self, *, resource_references, as_of):
        if not resource_references:
            return ()
        ref = resource_references[0]
        return (
            ResponsibilityItem(
                resource_reference=ref,
                role="ServiceOwner",
                party_reference=f"team:{ref}",
                party_kind="Team",
                display_name=f"{ref.title()} Team",
                contact=f"{ref}-ops",
                provenance_reference="catalogue",
            ),
        )


def test_composes_policy_candidates_evidence_and_contacts_without_path_claim() -> None:
    result = ReadTrafficAnalysis(
        endpoints=Endpoints(),
        policy=Policy(),
        network_context=Network(),
        evidence=Evidence(),
        responsibilities=Responsibilities(),
    ).execute(actor_id="operator", query=QUERY)

    assert result.source.state is ResolutionState.RESOLVED
    assert result.policy_matches[0].decision == "Allowed"
    assert [item.device_reference for item in result.network_context.candidates] == [
        "fw-1",
        "fw-2",
    ]
    assert result.network_context.candidates[0].evidence is not None
    assert result.network_context.candidates[1].evidence is None
    assert result.source_responsibilities[0].contact == "source-ops"
    assert "fw-2: no applicable stored configured-evidence snapshot" in result.findings
    assert "Network Context candidate knowledge is incomplete" in result.findings
