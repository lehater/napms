from dataclasses import replace

from napms.workflows.traffic_analysis.application.model import (
    NetworkCandidateView,
    NetworkContextView,
    ResolutionState,
    TrafficAnalysisQuery,
    TrafficAnalysisResult,
)
from napms.workflows.traffic_analysis.application.ports import (
    ConfiguredEvidenceProjectionPort,
    NetworkContextProjectionPort,
    ResourceResponsibilityProjectionPort,
    TechnicalEndpointResolutionPort,
    TrafficPolicyProjectionPort,
)


class ReadTrafficAnalysis:
    def __init__(
        self,
        *,
        endpoints: TechnicalEndpointResolutionPort,
        policy: TrafficPolicyProjectionPort,
        network_context: NetworkContextProjectionPort,
        evidence: ConfiguredEvidenceProjectionPort,
        responsibilities: ResourceResponsibilityProjectionPort,
    ) -> None:
        self._endpoints = endpoints
        self._policy = policy
        self._network_context = network_context
        self._evidence = evidence
        self._responsibilities = responsibilities

    def execute(
        self,
        *,
        actor_id: str,
        query: TrafficAnalysisQuery,
    ) -> TrafficAnalysisResult:
        if not actor_id or not actor_id.strip():
            raise ValueError("actor_id must be non-empty")

        source = self._endpoints.resolve(
            address=query.source_address,
            as_of=query.as_of,
        )
        destination = self._endpoints.resolve(
            address=query.destination_address,
            as_of=query.as_of,
        )

        source_refs = tuple(
            dict.fromkeys(item.resource_reference for item in source.resources)
        )
        destination_refs = tuple(
            dict.fromkeys(item.resource_reference for item in destination.resources)
        )
        source_responsibilities = self._responsibilities.list_for_resources(
            resource_references=source_refs,
            as_of=query.as_of,
        )
        destination_responsibilities = self._responsibilities.list_for_resources(
            resource_references=destination_refs,
            as_of=query.as_of,
        )

        policy_matches = self._policy.find_matches(
            actor_id=actor_id,
            query=query,
            source=source,
            destination=destination,
        )
        network = self._network_context.read(query=query)

        enriched_candidates: list[NetworkCandidateView] = []
        findings: list[str] = []
        for candidate in network.candidates:
            snapshot = self._evidence.latest_applicable(
                query=query,
                provider_namespace=candidate.provider_namespace,
                device_reference=candidate.device_reference,
            )
            enriched_candidates.append(replace(candidate, evidence=snapshot))
            if snapshot is None:
                findings.append(
                    f"{candidate.device_reference}: no applicable stored configured-evidence snapshot"
                )

        if source.state is not ResolutionState.RESOLVED:
            findings.append(f"source resolution is {source.state.value}")
        if destination.state is not ResolutionState.RESOLVED:
            findings.append(f"destination resolution is {destination.state.value}")
        if not network.complete_for_pair:
            findings.append("Network Context candidate knowledge is incomplete")
        if not policy_matches:
            findings.append("no matching policy/governance projection is available")

        return TrafficAnalysisResult(
            query=query,
            source=source,
            destination=destination,
            policy_matches=policy_matches,
            source_responsibilities=source_responsibilities,
            destination_responsibilities=destination_responsibilities,
            network_context=NetworkContextView(
                candidates=tuple(enriched_candidates),
                complete_for_pair=network.complete_for_pair,
                knowledge_gaps=network.knowledge_gaps,
            ),
            findings=tuple(dict.fromkeys(findings)),
        )
