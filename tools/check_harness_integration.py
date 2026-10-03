#!/usr/bin/env python3
"""NAPMS project assertions over the pinned canonical Harness runtime."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = Path(os.environ.get("HARNESS_ROOT", ROOT / ".harness-tool"))
if not (HARNESS_ROOT / "engineering_graph.py").exists():
    raise SystemExit(
        "Pinned Harness runtime not found. Set HARNESS_ROOT or checkout the pinned "
        "lehater/harness commit into .harness-tool."
    )

sys.path.insert(0, str(HARNESS_ROOT))
from engineering_graph import evaluate_engineering_target  # noqa: E402
from integration_alignment import validate_project_alignment  # noqa: E402


def load(path: str):
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path} must be a mapping")
    return value

def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def process_capability_check(graph, model) -> None:
    application = next(
        authority
        for authority in graph["authorities"]
        if authority["id"] == "APPLICATION-JOURNEY-DESIGN"
    )
    process = next(
        production
        for production in application["produces"]
        if production["capability"] == "engineering.application.process.policy-export"
    )
    require(
        process["knowledge_kind"] == "application-design",
        "policy-export process must reuse the application-design knowledge kind",
    )
    require(
        set(process["requires"])
        == {
            "engineering.requirements.product-intent",
            "engineering.application.journey",
            "engineering.application.materialization-semantics",
            "engineering.hcd.policy-export.task-model",
            "engineering.hcd.policy-export.user-journey",
        },
        "policy-export process capability prerequisite closure drifted",
    )

    system = next(
        authority
        for authority in graph["authorities"]
        if authority["id"] == "SYSTEM-ARCHITECTURE"
    )
    rules = next(
        production
        for production in system["produces"]
        if production["capability"] == "engineering.architecture.rules"
    )
    require(
        "engineering.application.process.policy-export" in rules["requires"],
        "system architecture rules must consume the process capability directly",
    )
    require(
        "engineering.application.journey" not in rules["requires"],
        "system architecture rules must not reconstruct process flow from the broad journey capability",
    )

    process_doc = load("docs/model/processes/policy-export-process.yaml")
    require(process_doc.get("kind") == "application-process", "invalid process artifact kind")
    require(process_doc.get("status") == "CURRENT", "policy-export process must be CURRENT")
    boundary = process_doc.get("instance_boundary", {})
    require(boundary.get("starts_with") == "SELECT-SCOPE", "process start boundary drifted")
    require(boundary.get("success_completion") == "EXPORT-EXPOSED", "process success boundary drifted")
    require(
        boundary.get("rejected_completion") == "EXPORT-AUTHORITY-DENIED",
        "process rejection boundary drifted",
    )

    activity_ids = {item["id"] for item in process_doc.get("activities", [])}
    required_activities = {
        "SELECT-SCOPE",
        "EXECUTE-EXPORT",
        "ESTABLISH-EVALUATION-CONTEXT",
        "CHECK-EXPORT-AUTHORITY",
        "EVALUATE-EFFECTIVE-POLICY",
        "MATERIALIZE-ENRICHED-ROWS",
        "EXPORT-EXPOSED",
        "EXPORT-AUTHORITY-DENIED",
    }
    require(
        activity_ids == required_activities,
        f"process activity contract drifted: {sorted(activity_ids)}",
    )

    relation_types = {
        item.get("type")
        for item in process_doc.get("causal_relations", [])
    }
    require(
        relation_types == {"control-precedence", "guarded-alternative"},
        f"process causal relation types drifted: {sorted(relation_types)}",
    )
    applicability = process_doc.get("applicability", {})
    for key in ("waits", "timers", "parallel_branches", "convergence", "compensation"):
        require(
            applicability.get(key) == "NOT_APPLICABLE",
            f"process {key} applicability must remain explicit",
        )
    require(
        applicability.get("independent_process_state", {}).get("status")
        == "NOT_APPLICABLE",
        "independent process state must remain explicitly NOT_APPLICABLE",
    )

    artifacts = {item["id"]: item for item in model.get("artifacts", [])}
    provider = artifacts.get("POLICY-EXPORT-PROCESS", {})
    require(
        "engineering.application.process.policy-export" in provider.get("provides", []),
        "aligned project model must expose POLICY-EXPORT-PROCESS as the process provider",
    )
    system_rules = artifacts.get("SYSTEM-RULES", {})
    require(
        "POLICY-EXPORT-PROCESS" in system_rules.get("depends_on", []),
        "SYSTEM-RULES must depend directly on POLICY-EXPORT-PROCESS",
    )
    require(
        "FIRST-MVP-JOURNEY" not in system_rules.get("depends_on", []),
        "SYSTEM-RULES must not retain a direct journey dependency for process reconstruction",
    )



def main() -> int:
    source = load("docs/canonical-graph.yaml")
    projection = load("docs/harness-projection.yaml")
    graph = load("docs/harness-engineering-graph.yaml")

    backend_alignment = validate_project_alignment(
        source,
        projection,
        graph,
        target_consumer="BACKEND-IMPLEMENTATION",
    )
    frontend_alignment = validate_project_alignment(
        source,
        projection,
        graph,
        target_consumer="FRONTEND-IMPLEMENTATION",
    )
    model = frontend_alignment["model"]
    process_capability_check(graph, model)

    backend = evaluate_engineering_target(
        graph, "BACKEND-IMPLEMENTATION", model
    )
    if backend["status"] != "COMPLETE":
        raise SystemExit(
            f"BACKEND-IMPLEMENTATION must remain COMPLETE, got {backend['status']}"
        )

    frontend = evaluate_engineering_target(
        graph, "FRONTEND-IMPLEMENTATION", model
    )
    actual_create = {item["capability"] for item in frontend["create"]}
    actual_wait = {item["capability"] for item in frontend["wait"]}
    actual_questions = {
        question
        for item in frontend["wait"]
        for question in item.get("questions", [])
    }
    expected_create = {
        "engineering.hcd.access-request.human-interface",
        "engineering.hcd.policy-export.human-interface",
    }
    if (
        frontend["status"] != "READY"
        or actual_create != expected_create
        or actual_wait
        or actual_questions
    ):
        raise SystemExit(
            "FRONTEND-IMPLEMENTATION causal frontier mismatch: "
            f"status={frontend['status']} create={sorted(actual_create)} "
            f"wait={sorted(actual_wait)} questions={sorted(actual_questions)}"
        )

    print("NAPMS pinned Harness integration PASS")
    print("POLICY-EXPORT process capability: direct SYSTEM-RULES dependency PASS")
    print("BACKEND-IMPLEMENTATION: COMPLETE")
    print("FRONTEND-IMPLEMENTATION: READY")
    print("HCD frontier: human-interface[access-request, policy-export]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
