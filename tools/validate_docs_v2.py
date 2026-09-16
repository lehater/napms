#!/usr/bin/env python3
"""Pilot-grade deterministic conformance checks for Documentation System v2."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "docs-v2" / "spec" / "artifacts.md"
EXECUTION = ROOT / "docs-v2" / "spec" / "agent-execution.md"

VALID_OWNERS = {"S0", "S1", "S2", "S3", "S4", "Implementation", "decision-owner"}
VALID_APPLICABILITY_PREFIXES = ("mandatory", "conditional", "optional")
MULTI_OWNER_RE = re.compile(r"(?:S[0-4]|Implementation|Validation)\s*/\s*(?:S[0-4]|Implementation|Validation)")
TABLE_ROW_RE = re.compile(r"^\| `([^`]+)` \| ([^|]+) \| ([^|]+) \|", re.MULTILINE)


def validate_artifact_catalog() -> list[str]:
    errors: list[str] = []
    if not ARTIFACTS.is_file():
        return ["missing docs-v2/spec/artifacts.md"]
    text = ARTIFACTS.read_text(encoding="utf-8-sig")
    rows = TABLE_ROW_RE.findall(text)
    if not rows:
        return ["artifact catalog contains no parseable artifact rows"]
    seen: set[str] = set()
    for artifact_id, owner, applicability in rows:
        owner = owner.strip()
        applicability = applicability.strip()
        if artifact_id in seen:
            errors.append(f"duplicate artifact type id: {artifact_id}")
        seen.add(artifact_id)
        if MULTI_OWNER_RE.search(owner):
            errors.append(f"artifact {artifact_id} has multiple semantic owners: {owner}")
        if owner not in VALID_OWNERS:
            errors.append(f"artifact {artifact_id} has unsupported owning stage: {owner}")
        if not applicability.startswith(VALID_APPLICABILITY_PREFIXES):
            errors.append(f"artifact {artifact_id} has invalid applicability: {applicability}")
    for required in {"functional-requirement", "domain-model", "http-contract", "implementation-plan", "automated-test"}:
        if required not in seen:
            errors.append(f"artifact catalog missing core type: {required}")
    if "requirements are organized by product/problem behavior, not by bounded context" not in text:
        errors.append("artifact catalog missing S1 requirement/bounded-context boundary invariant")
    if "Validation must reject multi-stage owner syntax" not in text:
        errors.append("artifact catalog does not declare deterministic single-owner validation")
    return errors


def validate_task_capsule_contract() -> list[str]:
    errors: list[str] = []
    if not EXECUTION.is_file():
        return ["missing docs-v2/spec/agent-execution.md"]
    text = EXECUTION.read_text(encoding="utf-8-sig")
    required_fields = ("scope:", "stage:", "state:", "task:", "primary_instruction:", "artifact_types:", "inputs:", "outputs:", "validation_profile:", "blockers:", "next:")
    for field in required_fields:
        if field not in text:
            errors.append(f"task capsule contract missing field: {field}")
    required_invariants = (
        "Every task has one primary instruction/skill",
        "G4 authorization",
        "one concrete task",
        "stop",
    )
    for marker in required_invariants:
        if marker not in text:
            errors.append(f"agent execution spec missing capsule invariant: {marker}")
    return errors


def main() -> int:
    errors = validate_artifact_catalog() + validate_task_capsule_contract()
    if errors:
        print("Documentation System v2 conformance failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("Documentation System v2 artifact/catalog capsule conformance OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
