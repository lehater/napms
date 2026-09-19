#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from check_harness_vertical import GRAPH, PROJECTION, VerticalError, evaluate, load_yaml


def _index_projection(
    graph: dict[str, Any], projection: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, list[str]]]:
    nodes = {item["id"]: item for item in graph.get("nodes", [])}
    bindings: dict[str, dict[str, Any]] = {}
    capability_providers: dict[str, list[str]] = {}

    for binding in projection.get("bindings", []) or []:
        artifact = binding["artifact"]
        bindings[artifact] = binding
        for capability in binding.get("provides", []) or []:
            capability_providers.setdefault(capability, []).append(artifact)

    return nodes, bindings, capability_providers


def _same_authority_dependency_closure(
    artifact_id: str,
    nodes: dict[str, dict[str, Any]],
    bindings: dict[str, dict[str, Any]],
) -> set[str]:
    owner = bindings[artifact_id]["authority"]
    result: set[str] = set()
    stack = [artifact_id]
    while stack:
        current = stack.pop()
        for dependency in nodes[current].get("depends_on", []) or []:
            if dependency not in bindings:
                raise VerticalError(
                    f"canonical dependency {dependency} of {current} has no Authority binding"
                )
            if bindings[dependency]["authority"] != owner:
                continue
            if dependency not in result:
                result.add(dependency)
                stack.append(dependency)
    return result


def build_execution_context(
    authority_id: str,
    graph: dict[str, Any],
    projection: dict[str, Any],
) -> dict[str, Any]:
    evaluation = evaluate(graph, projection)
    authorities = {item["id"]: item for item in projection.get("authorities", [])}
    if authority_id not in authorities:
        raise VerticalError(f"unknown engineering Authority {authority_id}")

    nodes, bindings, capability_providers = _index_projection(graph, projection)
    root_ids = {item["id"] for item in projection.get("root_authorities", []) or []}

    owned_artifacts: list[dict[str, Any]] = []
    public_outputs: set[str] = set()
    for artifact_id, binding in bindings.items():
        if binding["authority"] != authority_id:
            continue
        node = nodes[artifact_id]
        provides = sorted(binding.get("provides", []) or [])
        public_outputs.update(provides)
        owned_artifacts.append(
            {
                "id": artifact_id,
                "kind": node.get("kind"),
                "path": node.get("path"),
                "provides": provides,
            }
        )
    owned_artifacts.sort(key=lambda item: item["id"])

    contract_results = {
        item["id"]: item
        for item in evaluation.get("contracts", [])
        if item.get("consumer") == authority_id
    }
    contract_specs = [
        item for item in projection.get("contracts", []) or []
        if item.get("consumer") == authority_id
    ]

    if authority_id not in root_ids and not contract_specs:
        raise VerticalError(f"Authority {authority_id} has no input contract")

    requirements: list[dict[str, Any]] = []
    input_artifact_ids: set[str] = set()
    supporting_artifact_ids: set[str] = set()
    blockers: list[dict[str, Any]] = []

    for spec in contract_specs:
        result = contract_results[spec["id"]]
        result_requirements = {item["id"]: item for item in result["requirements"]}
        for requirement_spec in spec.get("requires", []) or []:
            requirement_result = result_requirements[requirement_spec["id"]]
            provider_artifacts: list[dict[str, Any]] = []
            for artifact_id in requirement_result.get("providers", []) or []:
                provider = bindings[artifact_id]
                node = nodes[artifact_id]
                input_artifact_ids.add(artifact_id)
                supporting_artifact_ids.update(
                    _same_authority_dependency_closure(artifact_id, nodes, bindings)
                )
                provider_artifacts.append(
                    {
                        "id": artifact_id,
                        "authority": provider["authority"],
                        "kind": node.get("kind"),
                        "path": node.get("path"),
                    }
                )

            requirement = {
                "contract": spec["id"],
                "id": requirement_spec["id"],
                "capability": requirement_spec["capability"],
                "authority": requirement_spec["authority"],
                "status": requirement_result["status"],
                "providers": provider_artifacts,
            }
            if requirement_result.get("evidence_capability"):
                requirement["evidence_capability"] = requirement_result["evidence_capability"]
            if requirement_result.get("blocked_by"):
                requirement["blocked_by"] = requirement_result["blocked_by"]
            if requirement_result.get("question"):
                requirement["question"] = requirement_result["question"]
            requirements.append(requirement)

            if requirement_result["status"] in {"BLOCKED", "DESIGN_GAP"}:
                blockers.append(
                    {
                        "contract": spec["id"],
                        "requirement": requirement_spec["id"],
                        "status": requirement_result["status"],
                        "owner": requirement_spec["authority"],
                        "capability": requirement_spec["capability"],
                        "blocked_by": requirement_result.get("blocked_by", []),
                        "question": requirement_result.get("question"),
                    }
                )

    downstream: list[dict[str, Any]] = []
    for contract in projection.get("contracts", []) or []:
        consumed: list[str] = []
        for requirement in contract.get("requires", []) or []:
            capability = requirement.get("capability")
            evidence = (requirement.get("not_applicable") or {}).get("evidence_capability")
            if capability in public_outputs:
                consumed.append(capability)
            if evidence in public_outputs:
                consumed.append(evidence)
        if consumed:
            downstream.append(
                {
                    "contract": contract["id"],
                    "consumer": contract["consumer"],
                    "capabilities": sorted(set(consumed)),
                }
            )
    downstream.sort(key=lambda item: (item["consumer"], item["contract"]))

    input_artifacts = [
        {
            "id": artifact_id,
            "authority": bindings[artifact_id]["authority"],
            "kind": nodes[artifact_id].get("kind"),
            "path": nodes[artifact_id].get("path"),
        }
        for artifact_id in sorted(input_artifact_ids)
    ]

    supporting_artifact_ids.difference_update(input_artifact_ids)
    supporting_input_artifacts = [
        {
            "id": artifact_id,
            "authority": bindings[artifact_id]["authority"],
            "kind": nodes[artifact_id].get("kind"),
            "path": nodes[artifact_id].get("path"),
        }
        for artifact_id in sorted(supporting_artifact_ids)
    ]

    status = "ROOT" if authority_id in root_ids else ("BLOCKED" if blockers else "READY")
    allowed_reads = sorted(
        {
            item["path"]
            for item in input_artifacts + supporting_input_artifacts + owned_artifacts
            if item.get("path")
        }
    )
    allowed_writes = sorted(
        item["path"] for item in owned_artifacts if item.get("path")
    )

    return {
        "kind": "authority-execution-context",
        "authority": authority_id,
        "status": status,
        "responsibility": authorities[authority_id].get("responsibility"),
        "input_contracts": [item["id"] for item in contract_specs],
        "requirements": requirements,
        "input_artifacts": input_artifacts,
        "supporting_input_artifacts": supporting_input_artifacts,
        "owned_artifacts": owned_artifacts,
        "public_outputs": sorted(public_outputs),
        "downstream_consumers": downstream,
        "blockers": blockers,
        "access": {
            "read": allowed_reads,
            "write": allowed_writes,
        },
        "execution_rules": [
            "Use only declared input capability providers, their same-Authority internal dependency closure, and the selected Authority's own current artifacts as engineering context.",
            "Write only artifacts owned by this Authority.",
            "Do not invent missing upstream semantics; a BLOCKED or DESIGN_GAP input stops artifact production.",
            "After edits, run design validation so public capabilities and downstream contracts are re-evaluated.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a bounded engineering context for one Harness Authority."
    )
    parser.add_argument("authority", help="Engineering Authority ID")
    parser.add_argument(
        "--format",
        choices=("yaml", "json"),
        default="yaml",
        help="Output format (default: yaml)",
    )
    parser.add_argument(
        "--allow-blocked",
        action="store_true",
        help="Return zero even when the Authority is blocked; useful for inspection.",
    )
    args = parser.parse_args()

    graph = load_yaml(GRAPH)
    projection = load_yaml(PROJECTION)
    context = build_execution_context(args.authority, graph, projection)

    if args.format == "json":
        import json
        print(json.dumps(context, indent=2, sort_keys=False))
    else:
        print(yaml.safe_dump(context, sort_keys=False, allow_unicode=True), end="")

    if context["status"] == "BLOCKED" and not args.allow_blocked:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
