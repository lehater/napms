#!/usr/bin/env python3
from __future__ import annotations

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


def _ids(items: Any, label: str) -> set[str]:
    if not isinstance(items, list):
        raise VerticalError(f"{label} must be a list")
    result: set[str] = set()
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            raise VerticalError(f"{label} entries require non-empty id")
        if item["id"] in result:
            raise VerticalError(f"{label} id {item['id']} is duplicated")
        result.add(item["id"])
    return result


def _validate_authority_boundaries(projection: dict[str, Any]) -> set[str]:
    authorities = projection.get("authorities", [])
    authority_ids = _ids(authorities, "authorities")
    for authority in authorities:
        boundary = authority.get("boundary")
        if not isinstance(boundary, dict):
            raise VerticalError(f"authority {authority['id']}: boundary evidence is required")
        for key in ("semantic_cohesion", "independent_change", "public_contract"):
            if not isinstance(boundary.get(key), str) or not boundary[key].strip():
                raise VerticalError(f"authority {authority['id']}: boundary.{key} is required")
        if boundary.get("atomic") is not True:
            raise VerticalError(f"authority {authority['id']}: boundary must explicitly conclude atomic: true")

    for cluster in projection.get("decomposed_clusters", []) or []:
        if not isinstance(cluster, dict) or not cluster.get("id"):
            raise VerticalError("decomposed cluster requires id")
        if cluster["id"] in authority_ids:
            raise VerticalError(f"decomposed cluster {cluster['id']} may not remain an Authority")
        replacements = cluster.get("replaced_by", [])
        if not isinstance(replacements, list) or not replacements:
            raise VerticalError(f"decomposed cluster {cluster['id']}: replacements are required")
        missing = sorted(set(replacements) - authority_ids)
        if missing:
            raise VerticalError(f"decomposed cluster {cluster['id']}: unknown replacements {missing}")
    return authority_ids


def _blocked_questions(
    graph: dict[str, Any], projection: dict[str, Any], authority_ids: set[str], artifact_authority: dict[str, str]
) -> dict[str, list[str]]:
    nodes = {item["id"]: item for item in graph.get("nodes", [])}
    reverse = {node_id: set() for node_id in nodes}
    for node_id, node in nodes.items():
        for dep in node.get("depends_on", []) or []:
            reverse[dep].add(node_id)

    def closure(seed: str) -> set[str]:
        if seed not in nodes:
            raise VerticalError(f"Question blocks unknown canonical artifact {seed}")
        result = {seed}
        stack = [seed]
        while stack:
            current = stack.pop()
            for downstream in reverse[current]:
                if downstream not in result:
                    result.add(downstream)
                    stack.append(downstream)
        return result

    blocked: dict[str, set[str]] = {}
    question_ids: set[str] = set()
    for question in projection.get("questions", []) or []:
        if not isinstance(question, dict) or not question.get("id") or question["id"] in question_ids:
            raise VerticalError("Question IDs must be present and unique")
        question_ids.add(question["id"])
        authority = question.get("authority")
        if authority not in authority_ids:
            raise VerticalError(f"Question {question['id']}: unknown authority {authority}")
        if not isinstance(question.get("text"), str) or not question["text"].strip():
            raise VerticalError(f"Question {question['id']}: text is required")
        resolution = question.get("resolution")
        if resolution is not None:
            if resolution not in artifact_authority:
                raise VerticalError(f"Question {question['id']}: unknown resolution artifact {resolution}")
            if artifact_authority[resolution] != authority:
                raise VerticalError(f"Question {question['id']}: resolution authority mismatch")
            continue
        for seed in question.get("blocks", []) or []:
            for artifact in closure(seed):
                blocked.setdefault(artifact, set()).add(question["id"])
    return {artifact: sorted(question_ids) for artifact, question_ids in blocked.items()}


def evaluate(graph: dict[str, Any], projection: dict[str, Any]) -> dict[str, Any]:
    nodes = {item["id"]: item for item in graph.get("nodes", [])}
    authority_ids = _validate_authority_boundaries(projection)
    consumer_ids = _ids(projection.get("consumers", []) or [], "consumers")
    if authority_ids & consumer_ids:
        raise VerticalError(f"consumer-only IDs overlap Authorities: {sorted(authority_ids & consumer_ids)}")

    bindings = projection.get("bindings", [])
    provider_map: dict[str, list[str]] = {}
    artifact_authority: dict[str, str] = {}

    for binding in bindings:
        if not isinstance(binding, dict):
            raise VerticalError("binding must be a mapping")
        artifact = binding.get("artifact")
        authority = binding.get("authority")
        if artifact not in nodes:
            raise VerticalError(f"binding references unknown canonical artifact {artifact}")
        if artifact in artifact_authority:
            raise VerticalError(f"artifact {artifact} has multiple Authority bindings")
        if authority not in authority_ids:
            raise VerticalError(f"binding {artifact} references unknown authority {authority}")
        artifact_authority[artifact] = authority
        for capability in binding.get("provides", []) or []:
            if not isinstance(capability, str) or not capability:
                raise VerticalError(f"binding {artifact}: invalid capability")
            provider_map.setdefault(capability, []).append(artifact)

    for capability, providers in provider_map.items():
        owners = {artifact_authority[item] for item in providers}
        if len(owners) != 1:
            raise VerticalError(f"capability {capability} spans authorities {sorted(owners)}")

    unbound_artifacts = sorted(set(nodes) - set(artifact_authority))
    if unbound_artifacts:
        raise VerticalError(f"Canonical artifacts without Authority binding: {unbound_artifacts}")

    bound_authorities = set(artifact_authority.values())
    unbound = sorted(authority_ids - bound_authorities)
    if unbound:
        raise VerticalError(f"Authorities without canonical artifacts: {unbound}")

    blocked_by_artifact = _blocked_questions(graph, projection, authority_ids, artifact_authority)

    result = {"satisfied": True, "contracts": []}
    contract_ids: set[str] = set()

    for contract in projection.get("contracts", []) or []:
        contract_id = contract.get("id")
        if not contract_id or contract_id in contract_ids:
            raise VerticalError("contract IDs must be present and unique")
        contract_ids.add(contract_id)
        consumer = contract.get("consumer")
        if consumer not in authority_ids and consumer not in consumer_ids:
            raise VerticalError(f"contract {contract_id}: unknown consumer {consumer}")

        requirement_ids: set[str] = set()
        contract_result = {"id": contract_id, "consumer": consumer, "satisfied": True, "requirements": []}
        for requirement in contract.get("requires", []) or []:
            requirement_id = requirement.get("id")
            capability = requirement.get("capability")
            expected_authority = requirement.get("authority")
            if not requirement_id or requirement_id in requirement_ids:
                raise VerticalError(f"contract {contract_id}: requirement IDs must be present and unique")
            requirement_ids.add(requirement_id)
            if expected_authority not in authority_ids:
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
                    {q for provider in providers for q in blocked_by_artifact.get(provider, [])}
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
                        {q for provider in evidence_providers for q in blocked_by_artifact.get(provider, [])}
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
