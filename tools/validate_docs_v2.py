#!/usr/bin/env python3
"""Pilot-grade deterministic conformance checks for Documentation System v2."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "docs-v2" / "spec" / "artifacts.md"
EXECUTION = ROOT / "docs-v2" / "spec" / "agent-execution.md"
ROUTING_CASES = ROOT / "backend" / "tests" / "evals" / "docs-v2-routing-cases.json"
GATE_CASES = ROOT / "backend" / "tests" / "evals" / "docs-v2-gate-applicability-cases.json"

VALID_OWNERS = {"S0", "S1", "S2", "S3", "S4", "Implementation", "decision-owner"}
VALID_APPLICABILITY_PREFIXES = ("mandatory", "conditional", "optional")
VALID_STAGES = {"S0", "S1", "S2", "S3", "S4", "IMPLEMENTATION"}
VALID_PROFILES = {"artifact-edit", "gate-g0", "gate-g1", "gate-g2", "gate-g3", "gate-g4", "implementation-slice", "journey-validation", "repository-integration"}
MULTI_OWNER_RE = re.compile(r"(?:S[0-4]|Implementation|Validation)\s*/\s*(?:S[0-4]|Implementation|Validation)")
TABLE_ROW_RE = re.compile(r"^\| `([^`]+)` \| ([^|]+) \| ([^|]+) \|", re.MULTILINE)


def _catalog_rows() -> tuple[dict[str, tuple[str, str]], list[str]]:
    if not ARTIFACTS.is_file():
        return {}, ["missing docs-v2/spec/artifacts.md"]
    rows = TABLE_ROW_RE.findall(ARTIFACTS.read_text(encoding="utf-8-sig"))
    if not rows:
        return {}, ["artifact catalog contains no parseable artifact rows"]
    result: dict[str, tuple[str, str]] = {}
    errors: list[str] = []
    for artifact_id, owner, applicability in rows:
        if artifact_id in result:
            errors.append(f"duplicate artifact type id: {artifact_id}")
        result[artifact_id] = (owner.strip(), applicability.strip())
    return result, errors


def validate_artifact_catalog(catalog: dict[str, tuple[str, str]]) -> list[str]:
    errors: list[str] = []
    text = ARTIFACTS.read_text(encoding="utf-8-sig")
    for artifact_id, (owner, applicability) in catalog.items():
        if MULTI_OWNER_RE.search(owner): errors.append(f"artifact {artifact_id} has multiple semantic owners: {owner}")
        if owner not in VALID_OWNERS: errors.append(f"artifact {artifact_id} has unsupported owning stage: {owner}")
        if not applicability.startswith(VALID_APPLICABILITY_PREFIXES): errors.append(f"artifact {artifact_id} has invalid applicability: {applicability}")
    for required in {"functional-requirement", "domain-model", "http-contract", "implementation-plan", "automated-test"}:
        if required not in catalog: errors.append(f"artifact catalog missing core type: {required}")
    if "requirements are organized by product/problem behavior, not by bounded context" not in text: errors.append("artifact catalog missing S1 requirement/bounded-context boundary invariant")
    if "Validation must reject multi-stage owner syntax" not in text: errors.append("artifact catalog does not declare deterministic single-owner validation")
    return errors


def validate_task_capsule_contract() -> list[str]:
    if not EXECUTION.is_file(): return ["missing docs-v2/spec/agent-execution.md"]
    text = EXECUTION.read_text(encoding="utf-8-sig")
    errors: list[str] = []
    for field in ("scope:", "stage:", "state:", "task:", "primary_instruction:", "artifact_types:", "inputs:", "outputs:", "validation_profile:", "blockers:", "next:"):
        if field not in text: errors.append(f"task capsule contract missing field: {field}")
    for marker in ("Every task has one primary instruction/skill", "G4 authorization", "one concrete task", "stop"):
        if marker not in text: errors.append(f"agent execution spec missing capsule invariant: {marker}")
    return errors


def validate_routing_cases(catalog: dict[str, tuple[str, str]]) -> list[str]:
    errors: list[str] = []
    try:
        cases = json.loads(ROUTING_CASES.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read docs-v2 routing cases: {exc}"]
    ids: set[str] = set()
    required = {"id", "change", "stage", "primary_instruction", "artifact_types", "validation_profile"}
    for case in cases:
        missing = required - case.keys()
        if missing: errors.append(f"routing case missing fields {sorted(missing)}: {case.get('id', '<unknown>')}"); continue
        case_id = str(case["id"])
        if case_id in ids: errors.append(f"duplicate routing case id: {case_id}")
        ids.add(case_id)
        if case["stage"] not in VALID_STAGES: errors.append(f"routing case {case_id} has invalid stage: {case['stage']}")
        if not str(case["primary_instruction"]).strip(): errors.append(f"routing case {case_id} has empty primary instruction")
        artifacts = case["artifact_types"]
        if not isinstance(artifacts, list) or not artifacts: errors.append(f"routing case {case_id} must select artifact types"); continue
        unknown = sorted(set(artifacts) - catalog.keys())
        if unknown: errors.append(f"routing case {case_id} references unknown artifact types: {unknown}")
        if case["validation_profile"] not in VALID_PROFILES: errors.append(f"routing case {case_id} has unknown validation profile: {case['validation_profile']}")
    covered = {case.get("stage") for case in cases}
    for stage in {"S1", "S2", "S3", "S4", "IMPLEMENTATION"} - covered: errors.append(f"routing corpus missing representative stage: {stage}")
    return errors


def _gate_result(applicability: str, condition: bool, present: bool) -> str:
    if applicability == "mandatory": return "PASS" if present else "BLOCK"
    if applicability == "conditional": return "PASS" if (not condition or present) else "BLOCK"
    if applicability == "optional": return "PASS"
    raise ValueError(f"unsupported applicability class: {applicability}")


def validate_gate_cases() -> list[str]:
    errors: list[str] = []
    try:
        cases = json.loads(GATE_CASES.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read gate applicability cases: {exc}"]
    ids: set[str] = set()
    for case in cases:
        case_id = str(case.get("id", "<unknown>"))
        if case_id in ids: errors.append(f"duplicate gate case id: {case_id}")
        ids.add(case_id)
        try:
            actual = _gate_result(str(case["class"]), bool(case["condition"]), bool(case["present"]))
            expected = str(case["expected"])
        except (KeyError, ValueError) as exc:
            errors.append(f"invalid gate case {case_id}: {exc}"); continue
        if actual != expected: errors.append(f"gate case {case_id}: expected {expected}, got {actual}")
    required = {("mandatory", True, False, "BLOCK"), ("conditional", True, False, "BLOCK"), ("conditional", False, False, "PASS"), ("optional", False, False, "PASS")}
    observed = {(str(c.get("class")), bool(c.get("condition")), bool(c.get("present")), str(c.get("expected"))) for c in cases}
    if not required <= observed: errors.append("gate applicability corpus lacks mandatory/conditional/optional boundary coverage")
    return errors


def main() -> int:
    catalog, errors = _catalog_rows()
    errors += validate_artifact_catalog(catalog)
    errors += validate_task_capsule_contract()
    errors += validate_routing_cases(catalog)
    errors += validate_gate_cases()
    if errors:
        print("Documentation System v2 conformance failed:", file=sys.stderr)
        for error in errors: print(f"  - {error}", file=sys.stderr)
        return 1
    print("Documentation System v2 catalog, capsule, routing and gate applicability conformance OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
