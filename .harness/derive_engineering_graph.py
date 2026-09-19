#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _normalized_requirement(requirement: dict[str, Any]) -> dict[str, str]:
    capability = requirement.get("capability")
    not_applicable = requirement.get("not_applicable")
    if isinstance(not_applicable, dict):
        capability = not_applicable.get("evidence_capability")
    if not isinstance(capability, str) or not capability:
        raise ValueError(f"invalid capability requirement: {requirement!r}")
    return {"capability": capability}


def _contract_requirements(
    contracts_by_consumer: dict[str, dict[str, Any]],
    consumer: str,
) -> list[dict[str, str]]:
    contract = contracts_by_consumer.get(consumer)
    if contract is None:
        return []
    return [
        _normalized_requirement(item)
        for item in contract.get("requires", []) or []
    ]


def _scoped_capability(subject: str, knowledge: str) -> str:
    return f"napms.coverage.{knowledge}.{subject}"


def derive(
    *,
    harness_root: Path,
    projection_path: Path = Path("docs/harness-core.yaml"),
    completeness_path: Path = Path("docs/engineering-knowledge-completeness.yaml"),
) -> tuple[dict[str, Any], dict[str, Any]]:
    sys.path.insert(0, str(ROOT / "tools"))
    sys.path.insert(0, str(harness_root))

    from adapters.canonical_graph import load_projection
    from check_knowledge_completeness import coverage_for_node

    projection = _load(ROOT / projection_path)
    completeness = _load(ROOT / completeness_path)
    canonical_graph = _load(ROOT / completeness["sources"]["canonical_graph"])
    journey = _load(ROOT / completeness["sources"]["journey"])
    strategic = _load(ROOT / completeness["sources"]["strategic_contexts"])

    core_model = load_projection(ROOT / projection_path)
    model_artifacts = {item["id"]: item for item in core_model["artifacts"]}

    contracts = projection.get("contracts", []) or []
    contracts_by_consumer = {
        item["consumer"]: item
        for item in contracts
    }

    bindings = projection.get("bindings", []) or []
    bindings_by_authority: dict[str, list[dict[str, Any]]] = {}
    binding_by_artifact: dict[str, dict[str, Any]] = {}
    for binding in bindings:
        bindings_by_authority.setdefault(binding["authority"], []).append(binding)
        binding_by_artifact[binding["artifact"]] = binding

    authorities: list[dict[str, Any]] = []
    production_by_capability: dict[str, dict[str, Any]] = {}

    for authority in projection.get("authorities", []) or []:
        authority_id = authority["id"]
        boundary = authority.get("boundary", {})
        productions: list[dict[str, Any]] = []
        common_requirements = _contract_requirements(
            contracts_by_consumer,
            authority_id,
        )
        for binding in bindings_by_authority.get(authority_id, []):
            for capability in binding.get("provides", []) or []:
                production = {
                    "capability": capability,
                    "requires": deepcopy(common_requirements),
                }
                productions.append(production)
                production_by_capability[capability] = production

        authorities.append(
            {
                "id": authority_id,
                "responsibility": authority.get(
                    "responsibility",
                    f"Own {authority_id} engineering decisions.",
                ),
                "boundary": {
                    "semantic_cohesion": boundary.get(
                        "semantic_cohesion",
                        f"One coherent class of {authority_id} engineering knowledge.",
                    ),
                    "independent_change": boundary.get(
                        "independent_change",
                        f"{authority_id} knowledge changes independently at its contract boundary.",
                    ),
                    "public_contract": boundary.get(
                        "public_contract",
                        f"Produces accepted {authority_id} capabilities for downstream consumers.",
                    ),
                },
                "produces": productions,
            }
        )

    authority_by_id = {item["id"]: item for item in authorities}

    # Project-owned subject coverage becomes scoped capability production + Core evidence.
    coverage_index: dict[tuple[str, str], list[str]] = {}
    knowledge_authorities: dict[str, set[str]] = {}
    for node in canonical_graph.get("nodes", []) or []:
        for subject, knowledge in coverage_for_node(node):
            coverage_index.setdefault((subject, knowledge), []).append(node["id"])
            binding = binding_by_artifact.get(node["id"])
            if binding is not None:
                knowledge_authorities.setdefault(knowledge, set()).add(binding["authority"])
                scoped = _scoped_capability(subject, knowledge)
                artifact = model_artifacts[node["id"]]
                if scoped not in artifact["provides"]:
                    artifact["provides"].append(scoped)
                    artifact["provides"].sort()

    broad_by_knowledge = {
        "tactical-domain-model": "engineering.domain.tactical-model",
        "domain-use-case": "engineering.domain.use-case-model",
    }
    context_ids = {
        item["name"]: item["context_id"]
        for item in strategic.get("contexts", []) or []
    }

    scoped_requirements: list[dict[str, str]] = []
    seen_scoped: set[str] = set()
    for rule in completeness.get("expectation_rules", []) or []:
        if rule.get("status", "ACCEPTED") == "EXPERIMENTAL":
            continue
        knowledge = rule["expects"]
        owners = knowledge_authorities.get(knowledge, set())
        if len(owners) != 1:
            raise ValueError(
                f"knowledge type {knowledge} must map to exactly one Authority; "
                f"got {sorted(owners)}"
            )
        [authority_id] = sorted(owners)
        broad = broad_by_knowledge.get(knowledge)
        if broad is None or broad not in production_by_capability:
            raise ValueError(
                f"cannot map completeness knowledge type {knowledge} to a broad production contract"
            )
        broad_requires = deepcopy(production_by_capability[broad]["requires"])

        source_key = rule["subjects_from"].split(".")[-1]
        for subject_name in journey.get(source_key, []) or []:
            subject = context_ids.get(subject_name)
            if not subject:
                raise ValueError(f"unknown strategic subject {subject_name!r}")
            scoped = _scoped_capability(subject, knowledge)
            if scoped in seen_scoped:
                continue
            seen_scoped.add(scoped)
            authority_by_id[authority_id]["produces"].append(
                {
                    "capability": scoped,
                    "requires": deepcopy(broad_requires),
                }
            )
            scoped_requirements.append(
                {
                    "capability": scoped,
                    "subject": subject,
                }
            )

    implementation_contract = contracts_by_consumer.get("IMPLEMENTATION")
    if implementation_contract is None:
        raise ValueError("NAPMS IMPLEMENTATION consumer contract is required")
    implementation_requires = [
        _normalized_requirement(item)
        for item in implementation_contract.get("requires", []) or []
    ]
    implementation_requires.extend(scoped_requirements)

    consumers = [
        {
            "id": "IMPLEMENTATION",
            "purpose": "Implement the accepted first-MVP NAPMS design without inventing engineering decisions.",
            "requires": implementation_requires,
        }
    ]

    graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "NAPMS-FIRST-MVP-ENGINEERING",
        "default_subject": "NAPMS-FIRST-MVP",
        "authorities": authorities,
        "consumers": consumers,
    }
    return graph, core_model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harness-root", type=Path, required=True)
    parser.add_argument("--graph-output", type=Path, required=True)
    parser.add_argument("--model-output", type=Path, required=True)
    args = parser.parse_args()

    graph, model = derive(harness_root=args.harness_root)
    args.graph_output.write_text(
        yaml.safe_dump(graph, sort_keys=False),
        encoding="utf-8",
    )
    args.model_output.write_text(
        yaml.safe_dump(model, sort_keys=False),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
