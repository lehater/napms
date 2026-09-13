#!/usr/bin/env python3
"""Validate executable regression cases for the conceptual change lifecycle."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "backend" / "tests" / "evals" / "lifecycle-transition-cases.json"

SEMANTIC_STAGES = ("S0", "S1", "S2", "S3", "S4")
STAGE_INDEX = {stage: index for index, stage in enumerate(SEMANTIC_STAGES)}
NEXT_STAGE = {
    "S0": "S1",
    "S1": "S2",
    "S2": "S3",
    "S3": "S4",
    "S4": "IMPLEMENTATION",
}
VALID_OUTCOMES = {"PASS", "REWORK", "BLOCKED", "REOPEN", "ENTRY", "INTERNAL_REROUTE"}


def transition(
    *,
    current_stage: str | None,
    outcome: str,
    target_stage: str | None,
    dependent_stages: list[str] | None = None,
) -> tuple[str, list[str], str]:
    if outcome not in VALID_OUTCOMES:
        raise ValueError(f"unsupported lifecycle outcome: {outcome}")

    if outcome == "ENTRY":
        if current_stage is not None:
            raise ValueError("ENTRY requires no current stage")
        if target_stage not in SEMANTIC_STAGES:
            raise ValueError("direct entry may target only S0-S4; IMPLEMENTATION requires G4")
        if dependent_stages:
            raise ValueError("ENTRY must not declare dependent dirty stages")
        return target_stage, [], "none"

    if current_stage not in {*SEMANTIC_STAGES, "IMPLEMENTATION"}:
        raise ValueError(f"invalid current lifecycle stage: {current_stage}")

    if outcome == "PASS":
        if current_stage == "IMPLEMENTATION":
            raise ValueError("IMPLEMENTATION is execution mode, not a semantic gate stage")
        if dependent_stages:
            raise ValueError("PASS must not declare dependent dirty stages")
        next_stage = NEXT_STAGE[current_stage]
        authorization = "G4 PASS" if current_stage == "S4" else "none"
        return next_stage, [], authorization

    if outcome in {"REWORK", "BLOCKED"}:
        if dependent_stages:
            raise ValueError(f"{outcome} must not declare dependent dirty stages")
        return current_stage, [], "none"

    if outcome == "INTERNAL_REROUTE":
        if current_stage != "S2" or target_stage != "S2":
            raise ValueError("internal Strategic/Tactical reroute is valid only inside S2")
        if dependent_stages:
            raise ValueError("internal S2 reroute must not declare top-level dirty stages")
        return "S2", [], "none"

    if target_stage not in SEMANTIC_STAGES:
        raise ValueError("REOPEN target must be one top-level semantic stage S0-S4")

    current_index = (
        len(SEMANTIC_STAGES)
        if current_stage == "IMPLEMENTATION"
        else STAGE_INDEX[current_stage]
    )
    target_index = STAGE_INDEX[target_stage]
    if target_index >= current_index:
        raise ValueError("REOPEN must target an earlier semantic stage")

    if dependent_stages is None:
        raise ValueError(
            "REOPEN cases must declare dependent_stages; dirty propagation is dependency-based, not sequence-based"
        )
    if len(dependent_stages) != len(set(dependent_stages)):
        raise ValueError("dependent_stages must not contain duplicates")

    dirty: list[str] = []
    for stage in dependent_stages:
        if stage not in SEMANTIC_STAGES:
            raise ValueError(f"invalid dependent semantic stage: {stage}")
        stage_index = STAGE_INDEX[stage]
        if stage_index <= target_index or stage_index > min(current_index, len(SEMANTIC_STAGES) - 1):
            raise ValueError(
                f"dependent stage {stage} must be downstream of {target_stage} and not later than the detecting stage"
            )
        dirty.append(stage)

    dirty.sort(key=STAGE_INDEX.__getitem__)
    return target_stage, dirty, "none"


def main() -> int:
    try:
        cases = json.loads(CASES.read_text(encoding="utf-8"))
        if not isinstance(cases, list) or not cases:
            raise ValueError("lifecycle transition corpus must be a non-empty JSON array")

        ids: set[str] = set()
        covered_outcomes: set[str] = set()
        for case in cases:
            if not isinstance(case, dict):
                raise ValueError("every lifecycle case must be an object")
            missing = {"id", "current_stage", "outcome"} - case.keys()
            if missing:
                raise ValueError(f"lifecycle case missing fields: {sorted(missing)}")

            case_id = str(case["id"])
            if case_id in ids:
                raise ValueError(f"duplicate lifecycle case id: {case_id}")
            ids.add(case_id)

            outcome = str(case["outcome"])
            covered_outcomes.add(outcome)
            expected_error = bool(case.get("expected_error", False))

            dependent_stages = case.get("dependent_stages")
            if dependent_stages is not None and not isinstance(dependent_stages, list):
                raise ValueError(f"{case_id}: dependent_stages must be an array")

            try:
                stage, dirty, authorization = transition(
                    current_stage=case.get("current_stage"),
                    outcome=outcome,
                    target_stage=case.get("target_stage"),
                    dependent_stages=dependent_stages,
                )
            except ValueError:
                if expected_error:
                    continue
                raise

            if expected_error:
                raise ValueError(f"{case_id}: expected transition rejection but transition succeeded")

            expected_stage = case.get("expected_stage")
            expected_dirty = case.get("expected_dirty")
            expected_authorization = case.get("expected_authorization")
            if stage != expected_stage:
                raise ValueError(f"{case_id}: expected stage {expected_stage!r}, got {stage!r}")
            if dirty != expected_dirty:
                raise ValueError(f"{case_id}: expected dirty {expected_dirty!r}, got {dirty!r}")
            if authorization != expected_authorization:
                raise ValueError(
                    f"{case_id}: expected authorization {expected_authorization!r}, got {authorization!r}"
                )

        missing_outcomes = VALID_OUTCOMES - covered_outcomes
        if missing_outcomes:
            raise ValueError(
                "lifecycle transition corpus must cover every outcome: "
                + ", ".join(sorted(missing_outcomes))
            )

        if not any(case.get("expected_error") for case in cases):
            raise ValueError("lifecycle transition corpus must include invalid-transition cases")

        if not any(
            case.get("current_stage") == "IMPLEMENTATION"
            and case.get("outcome") == "REOPEN"
            for case in cases
        ):
            raise ValueError("lifecycle corpus must cover implementation reopen / G4 revocation")

        if not any(
            case.get("outcome") == "REOPEN"
            and case.get("dependent_stages")
            and len(case["dependent_stages"])
            < (
                len(SEMANTIC_STAGES)
                - STAGE_INDEX[str(case.get("target_stage"))]
                - 1
            )
            for case in cases
            if case.get("target_stage") in STAGE_INDEX
        ):
            raise ValueError(
                "lifecycle corpus must prove selective dependency-based invalidation"
            )

    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Lifecycle transition validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Lifecycle transition corpus OK: {len(cases)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
