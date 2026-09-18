#!/usr/bin/env python3
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "docs/canonical-graph.yaml"
PROJECTION = ROOT / "docs/harness-core.yaml"


class VerticalError(ValueError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise VerticalError(f"{path.relative_to(ROOT)} must be a mapping")
    return value


def evaluate(graph: dict[str, Any], projection: dict[str, Any]) -> dict[str, Any]:
    nodes = {item["id"]: item for item in graph.get("nodes", [])}
    authorities = {item.get("id") for item in projection.get("authorities", []) if isinstance(item, dict)}
    bindings = projection.get("bindings", [])
    provider_map: dict[str, list[str]] = {}
    artifact_authority: dict[str, str] = {}

    for binding in bindings:
        artifact = binding["artifact"]
        authority = binding["authority"]
        if artifact not in nodes:
            raise VerticalError(f"binding references unknown canonical artifact {artifact}")
        if authority not in authorities:
            raise VerticalError(f"binding {artifact} references unknown authority {authority}")
        artifact_authority[artifact] = authority
        for capability in binding.get("provides", []) or []:
            provider_map.setdefault(capability, []).append(artifact)

    for capability, providers in provider_map.items():
        owners = {artifact_authority[item] for item in providers}
        if len(owners) != 1:
            raise VerticalError(f"capability {capability} spans authorities {sorted(owners)}")

    unresolved_by_artifact: dict[str, list[str]] = {}
    for question in projection.get("questions", []) or []:
        if question.get("resolution") is not None:
            continue
        for artifact in question.get("blocks", []) or []:
            unresolved_by_artifact.setdefault(artifact, []).append(question["id"])

    result = {"satisfied": True, "contracts": []}
    contract_ids: set[str] = set()

    for contract in projection.get("contracts", []) or []:
        contract_id = contract.get("id")
        if not contract_id or contract_id in contract_ids:
            raise VerticalError("contract IDs must be present and unique")
        contract_ids.add(contract_id)
        consumer = contract.get("consumer")
        if consumer not in authorities:
            raise VerticalError(f"contract {contract_id}: unknown consumer authority {consumer}")

        requirement_ids: set[str] = set()
        contract_result = {"id": contract_id, "consumer": consumer, "satisfied": True, "requirements": []}
        for requirement in contract.get("requires", []) or []:
            requirement_id = requirement.get("id")
            capability = requirement.get("capability")
            expected_authority = requirement.get("authority")
            if not requirement_id or requirement_id in requirement_ids:
                raise VerticalError(f"contract {contract_id}: requirement IDs must be present and unique")
            requirement_ids.add(requirement_id)
            if expected_authority not in authorities:
                raise VerticalError(f"contract {contract_id}/{requirement_id}: unknown authority {expected_authority}")
            if not isinstance(capability, str) or not capability:
                raise VerticalError(f"contract {contract_id}/{requirement_id}: capability is required")

            providers = sorted(provider_map.get(capability, []))
            status = None
            evidence_capability = None

            if providers:
                owners = {artifact_authority[item] for item in providers}
                if owners != {expected_authority}:
                    raise VerticalError(
                        f"contract {contract_id}/{requirement_id}: capability {capability} "
                        f"is owned by {sorted(owners)}, expected {expected_authority}"
                    )
                blocked_by = sorted(
                    {q for provider in providers for q in unresolved_by_artifact.get(provider, [])}
                )
                status = "BLOCKED" if blocked_by else "PROVIDED"
            else:
                na = requirement.get("not_applicable")
                evidence_capability = na.get("evidence_capability") if isinstance(na, dict) else None
                evidence_providers = sorted(provider_map.get(evidence_capability, [])) if evidence_capability else []
                if evidence_providers:
                    owners = {artifact_authority[item] for item in evidence_providers}
                    if owners != {expected_authority}:
                        raise VerticalError(
                            f"contract {contract_id}/{requirement_id}: NOT_APPLICABLE evidence "
                            f"is owned by {sorted(owners)}, expected {expected_authority}"
                        )
                    blocked_by = sorted(
                        {q for provider in evidence_providers for q in unresolved_by_artifact.get(provider, [])}
                    )
                    providers = evidence_providers
                    status = "BLOCKED" if blocked_by else "NOT_APPLICABLE"
                else:
                    blocked_by = []
                    status = "DESIGN_GAP"

            if status in {"BLOCKED", "DESIGN_GAP"}:
                contract_result["satisfied"] = False
                result["satisfied"] = False

            item = {
                "id": requirement_id,
                "capability": capability,
                "authority": expected_authority,
                "status": status,
                "providers": providers,
                "blocked_by": blocked_by,
            }
            if evidence_capability:
                item["evidence_capability"] = evidence_capability
            if status == "DESIGN_GAP":
                item["question"] = {
                    "authority": expected_authority,
                    "text": f"Provide canonical capability {capability} required by {contract_id}/{requirement_id}.",
                }
            contract_result["requirements"].append(item)

        if not contract_result["requirements"]:
            raise VerticalError(f"contract {contract_id} requires at least one capability")
        result["contracts"].append(contract_result)

    if not result["contracts"]:
        raise VerticalError("at least one consumer contract is required")
    return result


def main() -> int:
    graph = load_yaml(GRAPH)
    projection = load_yaml(PROJECTION)
    result = evaluate(graph, projection)
    for contract in result["contracts"]:
        print(f"{contract['id']}: {'PASS' if contract['satisfied'] else 'FAIL'}")
        for item in contract["requirements"]:
            providers = ",".join(item["providers"]) or "-"
            print(f"  {item['id']}: {item['status']} [{providers}]")
    if not result["satisfied"]:
        raise SystemExit("Harness documentation vertical has unresolved DESIGN_GAP/BLOCKED requirements")
    print("Harness documentation vertical PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
