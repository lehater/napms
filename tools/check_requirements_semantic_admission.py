#!/usr/bin/env python3
"""Strict Harness semantic admission for the purified first-MVP upstream chain."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = Path(os.environ.get("HARNESS_ROOT", ROOT / ".harness-tool"))
if not (HARNESS_ROOT / "semantic_admission.py").exists():
    raise SystemExit(
        "Pinned Harness runtime with semantic_admission.py is required; "
        "run make harness-bootstrap."
    )
sys.path.insert(0, str(HARNESS_ROOT))

from integration_alignment import validate_project_alignment  # noqa: E402
from semantic_admission import admit_artifact  # noqa: E402

GRAPH = ROOT / "docs/harness-engineering-graph.yaml"
CANONICAL = ROOT / "docs/canonical-graph.yaml"
PROJECTION = ROOT / "docs/harness-projection.yaml"
PROBLEM = ROOT / "docs/discovery/first-mvp-hcd-problem-evidence.yaml"
NEEDS = ROOT / "docs/discovery/first-mvp-hcd-user-needs.yaml"
REQUIREMENTS = ROOT / "docs/requirements/first-mvp-product-requirements.yaml"
REVIEW = ROOT / "docs/review/first-mvp-requirements-purification.yaml"

PROBLEM_ARTIFACT = "FIRST-MVP-HCD-PROBLEM-EVIDENCE"
NEEDS_ARTIFACT = "FIRST-MVP-HCD-USER-NEEDS"
REQUIREMENTS_ARTIFACT = "FIRST-MVP-REQUIREMENTS"

PROBLEM_CAPABILITY = "engineering.hcd.first-mvp.problem-evidence"
NEED_CAPABILITIES = {
    "application-components": "engineering.hcd.application-components.user-needs",
    "access-request": "engineering.hcd.access-request.user-needs",
    "policy-export": "engineering.hcd.policy-export.user-needs",
}
REQUIREMENT_CAPABILITIES = {
    "engineering.requirements.product-intent": None,
    "engineering.requirements.acceptance": None,
    "engineering.hcd.application-components.requirements": "application-components",
    "engineering.hcd.access-request.requirements": "access-request",
    "engineering.hcd.policy-export.requirements": "policy-export",
}

REQUIREMENT_NEED_MAP = {
    "REQ-MVP-001": ["NEED-APP-01", "NEED-REQUEST-01", "NEED-EXPORT-02"],
    "REQ-AUTH-001": ["NEED-REQUEST-02"],
    "REQ-AUTH-002": ["NEED-EXPORT-01"],
    "REQ-APP-001": ["NEED-APP-01"],
    "REQ-APP-002": ["NEED-APP-01"],
    "REQ-INT-001": ["NEED-APP-01"],
    "REQ-INT-002": ["NEED-APP-01"],
    "REQ-INT-003": ["NEED-APP-01"],
    "REQ-DEP-001": ["NEED-APP-01"],
    "REQ-DEP-002": ["NEED-APP-01"],
    "REQ-BUS-001": ["NEED-REQUEST-01"],
    "REQ-BUS-002": ["NEED-REQUEST-01"],
    "REQ-BUS-003": ["NEED-REQUEST-01"],
    "REQ-BUS-004": ["NEED-REQUEST-01"],
    "REQ-BUS-005": ["NEED-REQUEST-01"],
    "REQ-BUS-006": ["NEED-REQUEST-02"],
    "REQ-BUS-007": ["NEED-REQUEST-02"],
    "REQ-PERM-001": ["NEED-REQUEST-02"],
    "REQ-PERM-002": ["NEED-REQUEST-02"],
    "REQ-PERM-003": ["NEED-REQUEST-02"],
    "REQ-PERM-004": ["NEED-REQUEST-02"],
    "REQ-PERM-005": ["NEED-REQUEST-02"],
    "REQ-PERM-006": ["NEED-REQUEST-02"],
    "REQ-PERM-007": ["NEED-REQUEST-02"],
    "REQ-PERM-008": ["NEED-REQUEST-02"],
    "REQ-PERM-009": ["NEED-REQUEST-02"],
    "REQ-PERM-010": ["NEED-REQUEST-02"],
    "REQ-RULE-002": ["NEED-REQUEST-02"],
    "REQ-RULE-004": ["NEED-REQUEST-02", "NEED-EXPORT-02"],
    "REQ-RULE-005": ["NEED-REQUEST-02", "NEED-EXPORT-02"],
    "REQ-RULE-006": ["NEED-REQUEST-02"],
    "REQ-RULE-007": ["NEED-REQUEST-02"],
    "REQ-RULE-008": ["NEED-REQUEST-02"],
    "REQ-EXP-001": ["NEED-EXPORT-01"],
    "REQ-EXP-002": ["NEED-EXPORT-02"],
    "REQ-EXP-003": ["NEED-EXPORT-02"],
    "REQ-EXP-004": ["NEED-EXPORT-02"],
    "REQ-EXP-005": ["NEED-EXPORT-02"],
    "REQ-EXP-006": ["NEED-EXPORT-02"],
    "REQ-EXP-007": ["NEED-EXPORT-02"],
    "REQ-PROV-001": ["NEED-EXPORT-02"],
}

SUBJECT_REQUIREMENTS = {
    "application-components": {
        "REQ-MVP-001", "REQ-APP-001", "REQ-APP-002",
        "REQ-INT-001", "REQ-INT-002", "REQ-INT-003",
        "REQ-DEP-001", "REQ-DEP-002",
    },
    "access-request": {
        "REQ-MVP-001", "REQ-AUTH-001",
        "REQ-BUS-001", "REQ-BUS-002", "REQ-BUS-003", "REQ-BUS-004",
        "REQ-BUS-005", "REQ-BUS-006", "REQ-BUS-007", "REQ-BUS-008",
        "REQ-BUS-009", "REQ-PERM-001", "REQ-PERM-002", "REQ-PERM-003",
        "REQ-PERM-004", "REQ-PERM-005", "REQ-PERM-006", "REQ-PERM-007",
        "REQ-PERM-008", "REQ-PERM-009", "REQ-PERM-010",
        "REQ-ORG-001", "REQ-ORG-002",
        "REQ-RULE-002", "REQ-RULE-004", "REQ-RULE-005",
        "REQ-RULE-006", "REQ-RULE-007", "REQ-RULE-008",
    },
    "policy-export": {
        "REQ-MVP-001", "REQ-AUTH-002",
        "REQ-RULE-002", "REQ-RULE-004", "REQ-RULE-005",
        "REQ-RULE-006", "REQ-RULE-007", "REQ-RULE-008",
        "REQ-EXP-001", "REQ-EXP-002", "REQ-EXP-003", "REQ-EXP-004",
        "REQ-EXP-005", "REQ-EXP-006", "REQ-EXP-007", "REQ-PROV-001",
    },
}


def load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path.relative_to(ROOT)} must contain a mapping")
    return value


def review_checks(kind: str) -> list[str]:
    common = ["source-discipline", "authority-boundary", "no-invention"]
    extra = {
        "problem-evidence": ["evidence-not-solution"],
        "user-needs": ["need-not-normative-solution"],
        "product-requirements": [
            "observable-product-level",
            "no-downstream-design-promotion",
        ],
    }[kind]
    return sorted(common + extra)


def acceptance_id(capability: str, assertions: list[dict[str, Any]], checks: list[str]) -> str:
    semantic = [
        {
            "id": item["id"],
            "kind": item["kind"],
            "subject": item.get("subject"),
            "semantic_value": item.get("semantic_value"),
            "derived_from": sorted(item.get("derived_from", []) or []),
            "decision_authority": item.get("decision_authority"),
        }
        for item in assertions
    ]
    payload = json.dumps(
        {"capability": capability, "assertions": semantic, "checks": checks},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sem-sha256:" + hashlib.sha256(payload).hexdigest()


def canonical_path_guard(problem: dict[str, Any], needs: dict[str, Any]) -> None:
    forbidden = (
        "docs/requirements/",
        "docs/model/",
        "docs/architecture/",
        "docs/contracts/",
        "docs/plans/",
    )
    for label, document in (("Problem Evidence", problem), ("User Needs", needs)):
        text = yaml.safe_dump(document, sort_keys=False)
        leaks = [prefix for prefix in forbidden if prefix in text]
        if leaks:
            raise SystemExit(
                f"{label} contains downstream canonical reference(s): {leaks}"
            )


def lifecycle_doc(assertions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "version": 1,
        "kind": "harness-capability-lifecycle",
        "providers": assertions,
    }


def admit(
    *,
    graph,
    model,
    registry,
    contracts,
    capability: str,
    artifact: str,
    path: str,
    assertions: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    authority_refs: list[dict[str, str]],
    lifecycle_rows: list[dict[str, Any]],
    kind: str,
) -> dict[str, Any]:
    checks = review_checks(kind)
    candidate = {
        "id": artifact,
        "capability": capability,
        "path": path,
        "changed_paths": [path],
        "canonical_references": authority_refs,
        "semantic_assertions": assertions,
        "semantic_review": {"status": "ACCEPTED", "checks": checks},
    }
    result = admit_artifact(
        graph=graph,
        model=model,
        skill_registry=registry,
        knowledge_contracts=contracts,
        capability=capability,
        sources={"semantic_assertions": sources},
        candidate=candidate,
        acceptance_id=acceptance_id(capability, assertions, checks),
        lifecycle=lifecycle_doc(lifecycle_rows) if lifecycle_rows else None,
    )
    if result["status"] != "ACCEPTED":
        raise SystemExit(
            f"{capability} semantic admission REJECTED: "
            + json.dumps(result["findings"], sort_keys=True)
        )
    lifecycle_rows.append(result["lifecycle_assertion"])
    return result


def validate_purification_review(
    requirements: dict[str, Any],
    review: dict[str, Any],
) -> None:
    rows = requirements["content"]["requirements"]
    by_id = {item["id"]: item for item in rows}
    disposition = {
        item["id"]: item["disposition"]
        for item in review.get("existing_requirement_dispositions", []) or []
    }
    if len(disposition) != len(review.get("existing_requirement_dispositions", []) or []):
        raise SystemExit("purification review contains duplicate requirement disposition")
    expected_existing = set(disposition)
    current_or_retired = set(by_id) - set(review.get("added_requirements", []) or [])
    if expected_existing != current_or_retired:
        raise SystemExit(
            "purification disposition coverage mismatch: "
            f"missing={sorted(current_or_retired - expected_existing)} "
            f"extra={sorted(expected_existing - current_or_retired)}"
        )
    for req_id, kind in disposition.items():
        status = by_id[req_id].get("status")
        if kind == "RETIRE" and status != "RETIRED":
            raise SystemExit(f"{req_id} must be RETIRED")
        if kind != "RETIRE" and status != "ACCEPTED":
            raise SystemExit(f"{req_id} must remain ACCEPTED after {kind}")
    for req_id in review.get("added_requirements", []) or []:
        if by_id.get(req_id, {}).get("status") != "ACCEPTED":
            raise SystemExit(f"added requirement {req_id} is not ACCEPTED")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    graph = load(GRAPH)
    canonical = load(CANONICAL)
    projection = load(PROJECTION)
    problem = load(PROBLEM)
    needs = load(NEEDS)
    requirements = load(REQUIREMENTS)
    review = load(REVIEW)
    registry = load(HARNESS_ROOT / "skills/artifact-skill-registry-v0.yaml")
    contracts = load(
        HARNESS_ROOT / "spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml"
    )

    canonical_path_guard(problem, needs)
    validate_purification_review(requirements, review)

    aligned = validate_project_alignment(canonical, projection, graph)
    model = aligned["model"]
    lifecycle_rows: list[dict[str, Any]] = []
    evaluations: list[dict[str, Any]] = []

    problem_assertions = [
        {
            "id": item["id"],
            "kind": "problem-evidence",
            "subject": item["id"],
            "semantic_value": item["statement"],
            "decision_authority": "DISCOVERY",
        }
        for item in problem.get("observations", []) or []
    ]
    evaluations.append(
        admit(
            graph=graph,
            model=model,
            registry=registry,
            contracts=contracts,
            capability=PROBLEM_CAPABILITY,
            artifact=PROBLEM_ARTIFACT,
            path="docs/discovery/first-mvp-hcd-problem-evidence.yaml",
            assertions=problem_assertions,
            sources=[],
            authority_refs=[],
            lifecycle_rows=lifecycle_rows,
            kind="problem-evidence",
        )
    )

    source_problem = [
        {**item, "source_artifact": PROBLEM_ARTIFACT}
        for item in problem_assertions
    ]
    needs_by_subject: dict[str, list[dict[str, Any]]] = {}
    evidence_by_subject = {
        "application-components": ["OBS-APP-01"],
        "access-request": ["OBS-REQUEST-01"],
        "policy-export": ["OBS-EXPORT-01"],
    }
    for item in needs.get("user_needs", []) or []:
        subject = item["subject"]
        needs_by_subject.setdefault(subject, []).append(
            {
                "id": item["id"],
                "kind": "user-need",
                "subject": item["id"],
                "semantic_value": item["statement"],
                "derived_from": evidence_by_subject[subject],
                "decision_authority": "DISCOVERY",
            }
        )

    accepted_need_sources: list[dict[str, Any]] = []
    for subject, capability in NEED_CAPABILITIES.items():
        assertions = needs_by_subject[subject]
        result = admit(
            graph=graph,
            model=model,
            registry=registry,
            contracts=contracts,
            capability=capability,
            artifact=NEEDS_ARTIFACT,
            path="docs/discovery/first-mvp-hcd-user-needs.yaml",
            assertions=assertions,
            sources=source_problem,
            authority_refs=[
                {
                    "artifact": NEEDS_ARTIFACT,
                    "referenced_path": "docs/discovery/first-mvp-hcd-problem-evidence.yaml",
                }
            ],
            lifecycle_rows=lifecycle_rows,
            kind="user-needs",
        )
        evaluations.append(result)
        accepted_need_sources.extend(
            {**item, "source_artifact": NEEDS_ARTIFACT}
            for item in assertions
        )

    requirement_rows = requirements["content"]["requirements"]
    accepted_rows = [
        item for item in requirement_rows if item.get("status") == "ACCEPTED"
    ]
    accepted_ids = {item["id"] for item in accepted_rows}
    unknown_mapped = set(REQUIREMENT_NEED_MAP) - accepted_ids
    if unknown_mapped:
        raise SystemExit(f"need mapping references non-accepted requirements: {sorted(unknown_mapped)}")

    def requirement_assertion(item: dict[str, Any]) -> dict[str, Any]:
        result = {
            "id": item["id"],
            "kind": "product-requirement",
            "subject": item["id"],
            "semantic_value": item["statement"],
            "decision_authority": "PRODUCT-REQUIREMENTS",
        }
        derived = REQUIREMENT_NEED_MAP.get(item["id"], [])
        if derived:
            result["derived_from"] = derived
        return result

    all_requirement_assertions = [
        requirement_assertion(item) for item in accepted_rows
    ]
    req_refs = [
        {
            "artifact": REQUIREMENTS_ARTIFACT,
            "referenced_path": "docs/discovery/first-mvp-hcd-user-needs.yaml",
        },
        {
            "artifact": REQUIREMENTS_ARTIFACT,
            "referenced_path": "docs/requirements/first-mvp-quality-targets.yaml",
        },
    ]

    for capability, subject in REQUIREMENT_CAPABILITIES.items():
        if subject is None:
            assertions = all_requirement_assertions
        else:
            ids = SUBJECT_REQUIREMENTS[subject]
            missing = ids - accepted_ids
            if missing:
                raise SystemExit(
                    f"{subject} requirement capability references missing ids: {sorted(missing)}"
                )
            assertions = [
                item for item in all_requirement_assertions
                if item["id"] in ids
            ]
        evaluations.append(
            admit(
                graph=graph,
                model=model,
                registry=registry,
                contracts=contracts,
                capability=capability,
                artifact=REQUIREMENTS_ARTIFACT,
                path="docs/requirements/first-mvp-product-requirements.yaml",
                assertions=assertions,
                sources=accepted_need_sources,
                authority_refs=req_refs,
                lifecycle_rows=lifecycle_rows,
                kind="product-requirements",
            )
        )

    output = {
        "status": "ACCEPTED",
        "semantic_evaluations": evaluations,
        "lifecycle": lifecycle_doc(lifecycle_rows),
        "downstream_currentness": "UNKNOWN_UNTIL_OWNER_REVALIDATION",
    }
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(
            "NAPMS requirements semantic admission PASS "
            f"({len(evaluations)} capability evaluations)"
        )
        print(
            "Downstream semantic currentness: UNKNOWN until each owning Authority "
            "revalidates against the purified requirements baseline."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
