#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


def _expectation_id(requirement_id: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", requirement_id.upper()).strip("-")


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _dependency_expectations(
    model: dict[str, Any],
    capability_to_expectation: dict[str, str],
) -> dict[str, list[str]]:
    artifacts = {item["id"]: item for item in model.get("artifacts", [])}
    providers: dict[str, list[str]] = {}
    for artifact in artifacts.values():
        for capability in artifact.get("provides", []) or []:
            providers.setdefault(capability, []).append(artifact["id"])

    cache: dict[str, set[str]] = {}

    def upstream(artifact_id: str) -> set[str]:
        if artifact_id in cache:
            return set(cache[artifact_id])
        result: set[str] = set()
        for dependency in artifacts[artifact_id].get("depends_on", []) or []:
            result.add(dependency)
            result.update(upstream(dependency))
        cache[artifact_id] = set(result)
        return result

    result: dict[str, list[str]] = {}
    for capability, expectation_id in capability_to_expectation.items():
        dependencies: set[str] = set()
        for provider in providers.get(capability, []):
            for upstream_id in upstream(provider):
                for upstream_capability in artifacts[upstream_id].get("provides", []) or []:
                    upstream_expectation = capability_to_expectation.get(upstream_capability)
                    if upstream_expectation and upstream_expectation != expectation_id:
                        dependencies.add(upstream_expectation)
        result[expectation_id] = sorted(dependencies)
    return result


def derive(
    projection_path: Path,
    consumer_id: str,
    harness_root: Path,
    *,
    drop_capability: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    sys.path.insert(0, str(harness_root))
    from adapters.canonical_graph import load_projection

    projection = _load_yaml(projection_path)
    contracts = [
        item
        for item in projection.get("contracts", []) or []
        if item.get("consumer") == consumer_id
    ]
    if len(contracts) != 1:
        raise ValueError(
            f"expected exactly one consumer contract for {consumer_id}, got {len(contracts)}"
        )
    contract = contracts[0]

    complete_model = load_projection(projection_path)

    requirements = contract.get("requires", []) or []
    capability_to_expectation: dict[str, str] = {}
    normalized: list[dict[str, str]] = []
    for requirement in requirements:
        requirement_id = requirement.get("id")
        capability = requirement.get("capability")
        authority = requirement.get("authority")
        not_applicable = requirement.get("not_applicable")
        if isinstance(not_applicable, dict):
            evidence_capability = not_applicable.get("evidence_capability")
            if not isinstance(evidence_capability, str) or not evidence_capability:
                raise ValueError(
                    f"not_applicable requirement lacks evidence capability: {requirement!r}"
                )
            capability = evidence_capability
        if not all(isinstance(value, str) and value for value in (requirement_id, capability, authority)):
            raise ValueError(f"invalid consumer requirement: {requirement!r}")
        expectation_id = _expectation_id(requirement_id)
        if capability in capability_to_expectation:
            raise ValueError(f"duplicate consumer capability: {capability}")
        capability_to_expectation[capability] = expectation_id
        normalized.append(
            {
                "id": expectation_id,
                "capability": capability,
                "authority": authority,
            }
        )

    dependency_map = _dependency_expectations(
        complete_model,
        capability_to_expectation,
    )
    expectations: list[dict[str, Any]] = []
    for item in normalized:
        expectation = {
            "id": item["id"],
            "subject": consumer_id,
            "capability": item["capability"],
            "authority": item["authority"],
        }
        dependencies = dependency_map.get(item["id"], [])
        if dependencies:
            expectation["depends_on"] = dependencies
        expectations.append(expectation)

    model = complete_model
    if drop_capability:
        import copy
        model = copy.deepcopy(complete_model)
        for artifact in model.get("artifacts", []):
            artifact["provides"] = [
                value
                for value in artifact.get("provides", []) or []
                if value != drop_capability
            ]

    profile = {
        "version": 1,
        "kind": "harness-design-profile",
        "id": f"NAPMS-{consumer_id}-CURRENT-HARNESS-PILOT",
        "expectations": expectations,
    }
    return profile, model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("projection", type=Path)
    parser.add_argument("consumer")
    parser.add_argument("--harness-root", type=Path, required=True)
    parser.add_argument("--profile-output", type=Path, required=True)
    parser.add_argument("--model-output", type=Path, required=True)
    parser.add_argument("--drop-capability")
    args = parser.parse_args()

    profile, model = derive(
        args.projection,
        args.consumer,
        args.harness_root,
        drop_capability=args.drop_capability,
    )
    args.profile_output.write_text(
        yaml.safe_dump(profile, sort_keys=False),
        encoding="utf-8",
    )
    args.model_output.write_text(
        yaml.safe_dump(model, sort_keys=False),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
