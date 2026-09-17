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
CAPSULE_CASES = ROOT / "backend" / "tests" / "evals" / "docs-v2-task-capsule-cases.json"

VALID_OWNERS = {"S0", "S1", "S2", "S3", "S4", "Implementation", "decision-owner"}
VALID_APPLICABILITY_PREFIXES = ("mandatory", "conditional", "optional")
VALID_STAGES = {"S0", "S1", "S2", "S3", "S4", "IMPLEMENTATION"}
VALID_PROFILES = {"artifact-edit", "gate-g0", "gate-g1", "gate-g2", "gate-g3", "gate-g4", "implementation-slice", "journey-validation", "repository-integration"}
MULTI_OWNER_RE = re.compile(r"(?:S[0-4]|Implementation|Validation)\s*/\s*(?:S[0-4]|Implementation|Validation)")
TABLE_ROW_RE = re.compile(r"^\| `([^`]+)` \| ([^|]+) \| ([^|]+) \|", re.MULTILINE)
CAPSULE_FIELDS = {"scope", "stage", "state", "task", "primary_instruction", "artifact_types", "inputs", "outputs", "validation_profile", "implementation_authorization", "authorized_scope", "authorization_basis", "context_refs", "context_expansions", "blockers", "next"}


def _catalog_rows() -> tuple[dict[str, tuple[str, str]], list[str]]:
    if not ARTIFACTS.is_file(): return {}, ["missing docs-v2/spec/artifacts.md"]
    rows = TABLE_ROW_RE.findall(ARTIFACTS.read_text(encoding="utf-8-sig"))
    if not rows: return {}, ["artifact catalog contains no parseable artifact rows"]
    result: dict[str, tuple[str, str]] = {}; errors: list[str] = []
    for artifact_id, owner, applicability in rows:
        if artifact_id in result: errors.append(f"duplicate artifact type id: {artifact_id}")
        result[artifact_id] = (owner.strip(), applicability.strip())
    return result, errors


def validate_artifact_catalog(catalog: dict[str, tuple[str, str]]) -> list[str]:
    errors: list[str] = []; text = ARTIFACTS.read_text(encoding="utf-8-sig")
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
    text = EXECUTION.read_text(encoding="utf-8-sig"); errors: list[str] = []
    for field in CAPSULE_FIELDS:
        if f"{field}:" not in text: errors.append(f"task capsule contract missing field: {field}:")
    markers = ("exactly one `primary_instruction`", "For `IMPLEMENTATION` all three fields are mandatory", "stage: IMPLEMENTATION", "implementation_authorization: G4 PASS", "The capsule cannot create or broaden the lease", "every expansion has a recorded reason", "forbidden refs")
    for marker in markers:
        if marker not in text: errors.append(f"agent execution spec missing capsule invariant: {marker}")
    return errors


def _capsule_errors(capsule: object, catalog: dict[str, tuple[str, str]]) -> list[str]:
    if not isinstance(capsule, dict): return ["capsule must be an object"]
    errors: list[str] = []
    missing = CAPSULE_FIELDS - capsule.keys()
    if missing: errors.append(f"missing fields: {sorted(missing)}"); return errors
    stage = capsule["stage"]
    if stage not in VALID_STAGES: errors.append(f"invalid stage: {stage}")
    for field in ("scope", "task", "primary_instruction"):
        value = capsule[field]
        if not isinstance(value, str) or not value.strip(): errors.append(f"{field} must be one non-empty string")
    artifacts = capsule["artifact_types"]
    if not isinstance(artifacts, list) or not artifacts: errors.append("artifact_types must be a non-empty list")
    elif any(not isinstance(item, str) or item not in catalog for item in artifacts): errors.append("artifact_types contains unknown/non-string type")
    profiles = capsule["validation_profile"]
    if not isinstance(profiles, list) or not profiles or any(item not in VALID_PROFILES for item in profiles): errors.append("validation_profile contains no valid profile")
    for field in ("inputs", "outputs", "context_refs", "context_expansions", "blockers"):
        if not isinstance(capsule[field], list): errors.append(f"{field} must be a list")
    if stage == "IMPLEMENTATION":
        if capsule["implementation_authorization"] != "G4 PASS": errors.append("IMPLEMENTATION requires G4 PASS")
        if not isinstance(capsule["authorized_scope"], str) or not capsule["authorized_scope"].strip(): errors.append("IMPLEMENTATION requires authorized_scope")
        elif capsule["authorized_scope"] != capsule["scope"]: errors.append("implementation scope must equal authorized_scope")
        if not isinstance(capsule["authorization_basis"], str) or not capsule["authorization_basis"].strip(): errors.append("IMPLEMENTATION requires authorization_basis")
    elif any(capsule[field] is not None for field in ("implementation_authorization", "authorized_scope", "authorization_basis")):
        errors.append("non-implementation capsule must not carry implementation authorization")
    if isinstance(capsule["context_expansions"], list):
        for expansion in capsule["context_expansions"]:
            if not isinstance(expansion, dict) or not isinstance(expansion.get("ref"), str) or not expansion.get("ref", "").strip() or not isinstance(expansion.get("reason"), str) or not expansion.get("reason", "").strip():
                errors.append("every context expansion requires non-empty ref and reason")
    return errors


def validate_capsule_cases(catalog: dict[str, tuple[str, str]]) -> list[str]:
    try: cases = json.loads(CAPSULE_CASES.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: return [f"cannot read task capsule cases: {exc}"]
    errors: list[str] = []; ids: set[str] = set(); observed_expected: set[str] = set()
    for case in cases:
        case_id = str(case.get("id", "<unknown>")); expected = str(case.get("expected", ""))
        if case_id in ids: errors.append(f"duplicate task capsule case id: {case_id}")
        ids.add(case_id); observed_expected.add(expected)
        actual = "BLOCK" if _capsule_errors(case.get("capsule"), catalog) else "PASS"
        if expected not in {"PASS", "BLOCK"}: errors.append(f"task capsule case {case_id} has invalid expected result: {expected}")
        elif actual != expected: errors.append(f"task capsule case {case_id}: expected {expected}, got {actual}")
    if observed_expected != {"PASS", "BLOCK"}: errors.append("task capsule corpus must contain PASS and BLOCK cases")
    required_ids = {"valid-authorized-implementation", "implementation-missing-g4", "implementation-scope-mismatch", "nonimplementation-carries-lease", "multiple-primary-instructions", "unreasoned-context-expansion"}
    missing_ids = required_ids - ids
    if missing_ids: errors.append(f"task capsule corpus missing authorization/context boundaries: {sorted(missing_ids)}")
    return errors


def validate_routing_cases(catalog: dict[str, tuple[str, str]]) -> list[str]:
    errors: list[str] = []
    try: cases = json.loads(ROUTING_CASES.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: return [f"cannot read docs-v2 routing cases: {exc}"]
    ids: set[str] = set(); required = {"id", "change", "stage", "primary_instruction", "artifact_types", "validation_profile"}
    for case in cases:
        missing = required - case.keys()
        if missing: errors.append(f"routing case missing fields {sorted(missing)}: {case.get('id', '<unknown>')}"); continue
        case_id = str(case["id"])
        if case_id in ids: errors.append(f"duplicate routing case id: {case_id}")
        ids.add(case_id)
        if case["stage"] not in VALID_STAGES: errors.append(f"routing case {case_id} has invalid stage: {case['stage']}")
        if not isinstance(case["primary_instruction"], str) or not case["primary_instruction"].strip(): errors.append(f"routing case {case_id} has invalid primary instruction")
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
    try: cases = json.loads(GATE_CASES.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: return [f"cannot read gate applicability cases: {exc}"]
    ids: set[str] = set()
    for case in cases:
        case_id = str(case.get("id", "<unknown>"))
        if case_id in ids: errors.append(f"duplicate gate case id: {case_id}")
        ids.add(case_id)
        try: actual = _gate_result(str(case["class"]), bool(case["condition"]), bool(case["present"])); expected = str(case["expected"])
        except (KeyError, ValueError) as exc: errors.append(f"invalid gate case {case_id}: {exc}"); continue
        if actual != expected: errors.append(f"gate case {case_id}: expected {expected}, got {actual}")
    required = {("mandatory", True, False, "BLOCK"), ("conditional", True, False, "BLOCK"), ("conditional", False, False, "PASS"), ("optional", False, False, "PASS")}
    observed = {(str(c.get("class")), bool(c.get("condition")), bool(c.get("present")), str(c.get("expected"))) for c in cases}
    if not required <= observed: errors.append("gate applicability corpus lacks mandatory/conditional/optional boundary coverage")
    return errors


def main() -> int:
    catalog, errors = _catalog_rows()
    errors += validate_artifact_catalog(catalog)
    errors += validate_task_capsule_contract()
    errors += validate_capsule_cases(catalog)
    errors += validate_routing_cases(catalog)
    errors += validate_gate_cases()
    if errors:
        print("Documentation System v2 conformance failed:", file=sys.stderr)
        for error in errors: print(f"  - {error}", file=sys.stderr)
        return 1
    print("Documentation System v2 catalog, serialized capsule, routing and gate applicability conformance OK")
    return 0


if __name__ == "__main__": raise SystemExit(main())
