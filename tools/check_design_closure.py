#!/usr/bin/env python3
"""NAPMS aggregate implementation-design closure checks.

This is a derived CI assertion over existing canonical truth. It does not create
another readiness artifact or workflow state.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = Path(os.environ.get("HARNESS_ROOT", ROOT / ".harness-tool"))
if not (HARNESS_ROOT / "engineering_coverage.py").exists():
    raise SystemExit(
        "Pinned Harness runtime not found. Set HARNESS_ROOT or run make harness-bootstrap."
    )

sys.path.insert(0, str(HARNESS_ROOT))

from engineering_graph import evaluate_engineering_target  # noqa: E402
from engineering_coverage import evaluate_with_repository_policy, load_scope_source  # noqa: E402
from integration_alignment import validate_project_alignment  # noqa: E402

from evaluate_frontend_coverage_semantics import evaluate as evaluate_frontend_coverage_semantics


def load(relative: str):
    value = yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{relative} must contain a mapping")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def coverage_check(
    graph,
    source,
    projection,
    *,
    consumer: str,
    obligations_path: str,
    semantic_evaluations=None,
) -> None:
    aligned = validate_project_alignment(
        source,
        projection,
        graph,
        target_consumer=consumer,
    )
    target = evaluate_engineering_target(graph, consumer, aligned["model"])
    require(
        target["status"] == "COMPLETE",
        f"{consumer} structural target is {target['status']}, expected COMPLETE",
    )

    result = evaluate_with_repository_policy(
        graph=graph,
        realization=projection,
        consumer=consumer,
        scope="first-mvp",
        authority_aliases=load("docs/harness/coverage/authority-role-aliases-v1.yaml"),
        project_overlay=load("docs/harness/coverage/concern-activation-overlay-v1.yaml"),
        semantic_claim_bindings=load("docs/harness/coverage/semantic-claim-bindings-v1.yaml"),
        canonical_source=source,
        semantic_evaluations=semantic_evaluations,
        subject_obligations=load(obligations_path),
        scope_source=load_scope_source(ROOT / "docs/requirements/first-mvp-product-requirements.yaml"),
    )
    require(result["completion_ready"] is True, f"{consumer} Engineering Coverage is incomplete")
    require(result["remaining_work_count"] == 0, f"{consumer} has remaining Coverage work")
    require(result["work_items"] == [], f"{consumer} has actionable Coverage work items")
    require(result["question_frontier"] == [], f"{consumer} has blocking Coverage Questions")


def requirement_verification_check() -> None:
    requirements = load("docs/requirements/first-mvp-product-requirements.yaml")
    test_intent = load("docs/plans/first-mvp-test-intent.yaml")

    all_ids = {
        item["id"]
        for item in requirements["content"]["requirements"]
    }
    accepted = {
        item["id"]
        for item in requirements["content"]["requirements"]
        if item.get("status") == "ACCEPTED"
    }

    refs = set()
    for scenario in test_intent.get("required_scenarios", []) or []:
        scenario_refs = scenario.get("verifies", []) or []
        if not scenario_refs:
            raise SystemExit(f"verification scenario {scenario.get('id')} has no verifies refs")
        if not scenario.get("expect"):
            raise SystemExit(f"verification scenario {scenario.get('id')} has no observable expectation")
        refs.update(scenario_refs)

    unknown = sorted(refs - all_ids)
    missing = sorted(accepted - refs)
    require(not unknown, f"verification references unknown requirements: {unknown}")
    require(not missing, f"accepted requirements without verification disposition: {missing}")


def frontend_subject_test_check() -> None:
    obligations = load("docs/harness/coverage/frontend-subject-obligations-v1.yaml")
    test_design = load("docs/plans/mvp-frontend-test-design.yaml")

    required_subjects = {item["subject"] for item in obligations.get("subjects", []) or []}
    test_subjects = {
        item.get("subject")
        for item in test_design.get("tests", []) or []
        if item.get("subject") and item.get("subject") != "shared"
    }
    missing = sorted(required_subjects - test_subjects)
    require(not missing, f"frontend subjects without executable test contract: {missing}")


def main() -> int:
    graph = load("docs/harness-engineering-graph.yaml")
    source = load("docs/canonical-graph.yaml")
    projection = load("docs/harness-projection.yaml")

    coverage_check(
        graph,
        source,
        projection,
        consumer="BACKEND-IMPLEMENTATION",
        obligations_path="docs/harness/coverage/backend-subject-obligations-v1.yaml",
    )
    coverage_check(
        graph,
        source,
        projection,
        consumer="FRONTEND-IMPLEMENTATION",
        obligations_path="docs/harness/coverage/frontend-subject-obligations-v1.yaml",
        semantic_evaluations=evaluate_frontend_coverage_semantics(),
    )
    requirement_verification_check()
    frontend_subject_test_check()

    print("NAPMS implementation-design closure PASS")
    print("BACKEND-IMPLEMENTATION: structural + semantic coverage COMPLETE")
    print("FRONTEND-IMPLEMENTATION: structural + semantic coverage COMPLETE")
    print("Requirement verification traceability: COMPLETE")
    print("Frontend subject test coverage: COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
