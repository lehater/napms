#!/usr/bin/env python3
"""Research regression for HCD User Needs -> Task Model closure on real NAPMS downstream artifacts."""
from __future__ import annotations

import copy
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = Path(os.environ.get("HARNESS_ROOT", ROOT / ".harness-tool"))
if not (HARNESS_ROOT / "engineering_graph.py").exists():
    raise SystemExit(
        "Pinned Harness runtime not found. Set HARNESS_ROOT or run make harness-bootstrap."
    )

sys.path.insert(0, str(HARNESS_ROOT))
from agent_router import route_create_work  # noqa: E402
from engineering_graph import evaluate_engineering_target, validate_engineering_graph  # noqa: E402

PILOT = ROOT / "docs" / "research" / "hcd-requirements-task-closure-v1"


def load(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path} must contain a mapping")
    return value


GRAPH = load(PILOT / "engineering-graph.yaml")
CURRENT = load(PILOT / "core-state-current.yaml")
PROBLEM_ACCEPTED = load(PILOT / "accepted-problem-evidence.yaml")
USER_NEEDS_ACCEPTED = load(PILOT / "accepted-user-needs.yaml")
REGISTRY = load(HARNESS_ROOT / "skills" / "artifact-skill-registry-v0.yaml")


def with_artifact(model: dict, artifact: dict) -> dict:
    result = copy.deepcopy(model)
    result.setdefault("artifacts", []).append(artifact)
    return result


PROBLEM = {
    "id": "PILOT-PROBLEM-EVIDENCE",
    "path": "docs/research/hcd-requirements-task-closure-v1/accepted-problem-evidence.yaml",
    "authority": "DISCOVERY",
    "provides": ["pilot.first-mvp.problem-evidence"],
}

USER_NEEDS = {
    "id": "PILOT-USER-NEEDS",
    "path": "docs/research/hcd-requirements-task-closure-v1/accepted-user-needs.yaml",
    "authority": "DISCOVERY",
    "provides": [
        "pilot.application-components.user-needs",
        "pilot.access-request.user-needs",
        "pilot.policy-export.user-needs",
    ],
    "depends_on": ["PILOT-PROBLEM-EVIDENCE"],
}

TASK_MODEL = {
    "id": "PILOT-TASK-MODEL",
    "path": "docs/research/hcd-requirements-task-closure-v1/fixtures/task-model.yaml",
    "authority": "APPLICATION-JOURNEY-DESIGN",
    "provides": [
        "pilot.application-components.task-model",
        "pilot.access-request.task-model",
        "pilot.policy-export.task-model",
    ],
    "depends_on": ["PILOT-USER-NEEDS", "FIRST-MVP-REQUIREMENTS"],
}

HUMAN_JOURNEYS = {
    "id": "PILOT-HUMAN-JOURNEYS",
    "path": "docs/research/hcd-requirements-task-closure-v1/fixtures/human-journeys.yaml",
    "authority": "APPLICATION-JOURNEY-DESIGN",
    "provides": [
        "pilot.application-components.user-journey",
        "pilot.access-request.user-journey",
        "pilot.policy-export.user-journey",
    ],
    "depends_on": ["PILOT-TASK-MODEL", "FIRST-MVP-REQUIREMENTS"],
}


def source_refs(value):
    refs = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"evidence_refs", "source_refs", "refs"} and isinstance(item, list):
                refs.extend(str(ref) for ref in item)
            refs.extend(source_refs(item))
    elif isinstance(value, list):
        for item in value:
            refs.extend(source_refs(item))
    return refs


def validate_accepted_hcd() -> None:
    for artifact in (PROBLEM_ACCEPTED, USER_NEEDS_ACCEPTED):
        if artifact.get("status") != "ACCEPTED":
            raise AssertionError(artifact)
        if artifact.get("canonical") is not False:
            raise AssertionError(artifact)
        forbidden = ("docs/contracts/ui/", "web/", "backend/", "docs/architecture/")
        leaked = [ref for ref in source_refs(artifact) if ref.startswith(forbidden)]
        if leaked:
            raise AssertionError(("downstream source leak", leaked))

    needs = USER_NEEDS_ACCEPTED.get("user_needs", [])
    subjects = {item.get("subject") for item in needs}
    expected_subjects = {"application-components", "access-request", "policy-export"}
    if subjects != expected_subjects or len(needs) != 5:
        raise AssertionError(needs)

    for need in needs:
        refs = need.get("evidence_refs", [])
        if not refs:
            raise AssertionError(need)
        if not any(
            str(ref).startswith("docs/requirements/first-mvp-product-requirements.yaml#")
            for ref in refs
        ):
            raise AssertionError(("need lacks current canonical corroboration", need))

    task_questions = USER_NEEDS_ACCEPTED.get("task_model_questions", [])
    blocking_subjects = {
        item.get("subject")
        for item in task_questions
        if item.get("blocking_task_model") is True
    }
    if blocking_subjects != expected_subjects:
        raise AssertionError((blocking_subjects, task_questions))

    sufficiency = USER_NEEDS_ACCEPTED.get("sufficiency_review", {})
    if sufficiency.get("status") != "ACCEPTED":
        raise AssertionError(sufficiency)

    clarification = USER_NEEDS_ACCEPTED.get("semantic_clarification", {})
    if clarification.get("interaction_rule") != (
        "Interaction endpoints must belong to the same Application profile. "
        "Cross-Application Interaction is invalid."
    ):
        raise AssertionError(clarification)


def routed_kinds(model: dict) -> list[dict]:
    result = route_create_work(GRAPH, "HCD-PILOT", model, REGISTRY)
    if result["target_status"] != "READY":
        raise AssertionError(result)
    if result["unrouted"]:
        raise AssertionError(result)
    return result["routed"]


def assert_frontier(model: dict, kind: str, authority: str, expected_capabilities: set[str]) -> None:
    routed = routed_kinds(model)
    matching = [
        item for item in routed
        if item["knowledge_kind"] == kind and item["authority"] == authority
    ]
    if len(matching) != 1:
        raise AssertionError(routed)
    if set(matching[0]["capabilities"]) != expected_capabilities:
        raise AssertionError(matching[0])

    forbidden = {
        "human-interface-design",
        "screen-view-design",
    }
    if kind != "user-journey-design":
        forbidden.add("user-journey-design")
    if any(item["knowledge_kind"] in forbidden for item in routed):
        raise AssertionError(routed)


def main() -> int:
    validate_engineering_graph(GRAPH)
    validate_accepted_hcd()

    # Real downstream providers exist now, but the missing root causal knowledge
    # keeps every requirement/task/interface expectation downstream pending.
    current_eval = evaluate_engineering_target(GRAPH, "HCD-PILOT", CURRENT)
    if current_eval["status"] != "READY":
        raise AssertionError(current_eval)
    pending = {item["capability"] for item in current_eval["pending"]}
    for capability in (
        "pilot.application-components.requirements",
        "pilot.access-request.requirements",
        "pilot.policy-export.requirements",
        "pilot.application-components.human-interface",
        "pilot.access-request.human-interface",
        "pilot.policy-export.human-interface",
        "pilot.application-components.screen-view",
        "pilot.access-request.screen-view",
        "pilot.policy-export.screen-view",
    ):
        if capability not in pending:
            raise AssertionError((capability, current_eval))

    assert_frontier(
        CURRENT,
        "problem-evidence",
        "DISCOVERY",
        {"pilot.first-mvp.problem-evidence"},
    )

    with_problem = with_artifact(CURRENT, PROBLEM)
    assert_frontier(
        with_problem,
        "user-needs",
        "DISCOVERY",
        {
            "pilot.application-components.user-needs",
            "pilot.access-request.user-needs",
            "pilot.policy-export.user-needs",
        },
    )

    with_needs = with_artifact(with_problem, USER_NEEDS)
    assert_frontier(
        with_needs,
        "task-model",
        "APPLICATION-JOURNEY-DESIGN",
        {
            "pilot.application-components.task-model",
            "pilot.access-request.task-model",
            "pilot.policy-export.task-model",
        },
    )

    with_tasks = with_artifact(with_needs, TASK_MODEL)
    assert_frontier(
        with_tasks,
        "user-journey-design",
        "APPLICATION-JOURNEY-DESIGN",
        {
            "pilot.application-components.user-journey",
            "pilot.access-request.user-journey",
            "pilot.policy-export.user-journey",
        },
    )

    with_journeys = with_artifact(with_tasks, HUMAN_JOURNEYS)
    complete = evaluate_engineering_target(GRAPH, "HCD-PILOT", with_journeys)
    if complete["status"] != "COMPLETE":
        raise AssertionError(complete)
    if complete["create"] or complete["wait"] or complete["pending"]:
        raise AssertionError(complete)

    print("NAPMS HCD causal closure pilot: PASS")
    print(
        "accepted user-needs:",
        len(USER_NEEDS_ACCEPTED["user_needs"]),
        "task-model questions:",
        len(USER_NEEDS_ACCEPTED["task_model_questions"]),
        "status:",
        USER_NEEDS_ACCEPTED["sufficiency_review"]["status"],
    )
    print("current -> problem-evidence")
    print("problem-evidence -> user-needs[3]")
    print("user-needs -> task-model[3]")
    print("task-model -> human user-journey[3]")
    print("human user-journey -> existing human-interface/screen providers -> COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
