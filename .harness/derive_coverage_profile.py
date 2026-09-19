#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _scoped_capability(subject: str, knowledge: str) -> str:
    return f"napms.coverage.{knowledge}.{subject}"


def derive(
    *,
    harness_root: Path,
    completeness_path: Path,
    projection_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    sys.path.insert(0, str(ROOT / "tools"))
    sys.path.insert(0, str(harness_root))

    from adapters.canonical_graph import load_projection
    from check_knowledge_completeness import coverage_for_node

    completeness = _load(completeness_path)
    journey = _load(ROOT / completeness["sources"]["journey"])
    strategic = _load(ROOT / completeness["sources"]["strategic_contexts"])
    graph = _load(ROOT / completeness["sources"]["canonical_graph"])
    projection = _load(projection_path)

    model = load_projection(projection_path)
    model_artifacts = {item["id"]: item for item in model["artifacts"]}
    binding_authority = {
        item["artifact"]: item["authority"]
        for item in projection.get("bindings", [])
    }

    coverage_index: dict[tuple[str, str], list[str]] = {}
    knowledge_authorities: dict[str, set[str]] = {}
    for node in graph.get("nodes", []):
        for subject, knowledge in coverage_for_node(node):
            coverage_index.setdefault((subject, knowledge), []).append(node["id"])
            authority = binding_authority.get(node["id"])
            if authority:
                knowledge_authorities.setdefault(knowledge, set()).add(authority)
                artifact = model_artifacts[node["id"]]
                scoped = _scoped_capability(subject, knowledge)
                if scoped not in artifact["provides"]:
                    artifact["provides"].append(scoped)
                    artifact["provides"].sort()

    context_ids = {
        item["name"]: item["context_id"]
        for item in strategic.get("contexts", [])
    }

    expectations: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()
    for rule in completeness.get("expectation_rules", []):
        if rule.get("status", "ACCEPTED") == "EXPERIMENTAL":
            continue
        knowledge = rule["expects"]
        authorities = knowledge_authorities.get(knowledge, set())
        if len(authorities) != 1:
            raise ValueError(
                f"knowledge type {knowledge} must map to exactly one Authority; got {sorted(authorities)}"
            )
        [authority] = sorted(authorities)

        source_key = rule["subjects_from"].split(".")[-1]
        for subject_name in journey.get(source_key, []) or []:
            subject = context_ids.get(subject_name)
            if not subject:
                raise ValueError(
                    f"cannot resolve strategic context id for {subject_name!r}"
                )
            capability = _scoped_capability(subject, knowledge)
            pair = (subject, capability)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            expectations.append(
                {
                    "id": f"{rule['id']}--{subject}",
                    "subject": subject,
                    "capability": capability,
                    "authority": authority,
                }
            )

    profile = {
        "version": 1,
        "kind": "harness-design-profile",
        "id": "NAPMS-ENGINEERING-KNOWLEDGE-COVERAGE-PILOT",
        "expectations": expectations,
    }
    return profile, model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harness-root", type=Path, required=True)
    parser.add_argument(
        "--completeness",
        type=Path,
        default=Path("docs/engineering-knowledge-completeness.yaml"),
    )
    parser.add_argument(
        "--projection",
        type=Path,
        default=Path("docs/harness-core.yaml"),
    )
    parser.add_argument("--profile-output", type=Path, required=True)
    parser.add_argument("--model-output", type=Path, required=True)
    args = parser.parse_args()

    profile, model = derive(
        harness_root=args.harness_root,
        completeness_path=args.completeness,
        projection_path=args.projection,
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
