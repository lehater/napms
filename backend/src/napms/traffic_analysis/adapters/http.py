from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from fastapi import APIRouter, HTTPException, Query, Request

from napms.runtime.auth import InMemorySessionStore
from napms.runtime.http_support import SESSION_COOKIE_NAME
from napms.traffic_analysis.application.model import (
    TrafficAnalysisInvariantError,
    TrafficAnalysisQuery,
)


def create_traffic_analysis_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager],
) -> APIRouter:
    router = APIRouter()

    @router.get("/api/v1/traffic-analysis", name="ReadTrafficAnalysis")
    def read_traffic_analysis(
        request: Request,
        source: str = Query(min_length=1, max_length=128),
        destination: str = Query(min_length=1, max_length=128),
        protocol: str = Query(min_length=1, max_length=32),
        port: str = Query(min_length=1, max_length=32),
        as_of: datetime = Query(alias="asOf"),
    ):
        actor = sessions.get(request.cookies.get(SESSION_COOKIE_NAME))
        if actor is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise HTTPException(status_code=422, detail="asOf must include timezone")

        try:
            first, last = _parse_port(port)
            query = TrafficAnalysisQuery(
                source_address=source,
                destination_address=destination,
                protocol=protocol,
                destination_port_first=first,
                destination_port_last=last,
                as_of=as_of,
            )
            with open_scope() as scope:
                result = scope.read.execute(actor_id=actor.actor_id, query=query)
        except (TrafficAnalysisInvariantError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        return _serialize(result)

    return router


def _parse_port(value: str) -> tuple[int, int]:
    parts = value.strip().split("-", 1)
    try:
        first = int(parts[0])
        last = int(parts[1]) if len(parts) == 2 else first
    except ValueError as exc:
        raise ValueError("port must be an integer or integer range") from exc
    if not 0 <= first <= last <= 65535:
        raise ValueError("port range must be within 0..65535")
    return first, last


def _serialize(result):
    return {
        "query": {
            "sourceAddress": result.query.source_address,
            "destinationAddress": result.query.destination_address,
            "protocol": result.query.protocol,
            "port": (
                str(result.query.destination_port_first)
                if result.query.destination_port_first
                == result.query.destination_port_last
                else (
                    f"{result.query.destination_port_first}-"
                    f"{result.query.destination_port_last}"
                )
            ),
            "asOf": result.query.as_of.isoformat(),
        },
        "source": _serialize_resolution(result.source),
        "destination": _serialize_resolution(result.destination),
        "policyMatches": [
            {
                "sourceComponent": item.source_component,
                "destinationComponent": item.destination_component,
                "dcsReference": item.dcs_reference,
                "dcsDisplayName": item.dcs_display_name,
                "accessSummary": item.access_summary,
                "requirement": item.requirement,
                "decision": item.decision,
                "rule": item.rule,
                "effective": item.effective,
                "scope": item.scope,
                "partial": item.partial,
            }
            for item in result.policy_matches
        ],
        "sourceResponsibilities": [
            _serialize_responsibility(item)
            for item in result.source_responsibilities
        ],
        "destinationResponsibilities": [
            _serialize_responsibility(item)
            for item in result.destination_responsibilities
        ],
        "networkContext": {
            "completeForPair": result.network_context.complete_for_pair,
            "knowledgeGaps": list(result.network_context.knowledge_gaps),
            "candidates": [
                {
                    "providerNamespace": item.provider_namespace,
                    "deviceReference": item.device_reference,
                    "logicalFirewallReference": item.logical_firewall_reference,
                    "enforcementAttachmentReference": (
                        item.enforcement_attachment_reference
                    ),
                    "pathAttachmentReference": item.path_attachment_reference,
                    "sourceRelevance": item.source_relevance,
                    "provenanceReferences": list(item.provenance_references),
                    "evidence": (
                        {
                            "evidenceSetReference": item.evidence.evidence_set_reference,
                            "sourceReference": item.evidence.source_reference,
                            "sourceScopeReference": item.evidence.source_scope_reference,
                            "capturedAt": (
                                item.evidence.captured_at.isoformat()
                                if item.evidence.captured_at is not None
                                else None
                            ),
                            "recordedAt": item.evidence.recorded_at.isoformat(),
                            "provenanceReferences": list(
                                item.evidence.provenance_references
                            ),
                            "matches": [
                                {
                                    "entryReference": match.entry_reference,
                                    "action": match.action,
                                    "normalized": match.normalized,
                                    "matchKind": match.match_kind.value,
                                }
                                for match in item.evidence.matches
                            ],
                        }
                        if item.evidence is not None
                        else None
                    ),
                }
                for item in result.network_context.candidates
            ],
        },
        "findings": list(result.findings),
    }


def _serialize_resolution(value):
    return {
        "state": value.state.value,
        "address": value.address,
        "resources": [
            {
                "resourceReference": item.resource_reference,
                "endpointReference": item.endpoint_reference,
                "technicalAddress": item.technical_address,
                "componentNames": list(item.component_names),
                "responsibilityScope": item.responsibility_scope,
                "provenanceReferences": list(item.provenance_references),
            }
            for item in value.resources
        ],
    }


def _serialize_responsibility(item):
    return {
        "resourceReference": item.resource_reference,
        "role": item.role,
        "partyReference": item.party_reference,
        "partyKind": item.party_kind,
        "displayName": item.display_name,
        "contact": item.contact,
        "provenanceReference": item.provenance_reference,
    }
