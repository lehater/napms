#!/usr/bin/env python3
"""Validate active-plan continuity, resume locality and lifecycle lease."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = ROOT / "docs" / "plans" / "active"
INDEX = ACTIVE / "README.md"

CAPSULE_MAX_BYTES = 6 * 1024
READ_FIRST_MAX_FILES = 5
READ_FIRST_MAX_BYTES = 24 * 1024

CURRENT_RE = re.compile(
    r"^Current:\s+(?:`([^`]+)`|(none)\.?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
CURRENT_TASK_RE = re.compile(r"^Current task:\s+(.+?)\s*$", re.MULTILINE)
WORK_PACKAGE_RE = re.compile(r"\b(WP-\d+)\b")
STATUS_RE = re.compile(r"^Status:\s+`([^`]+)`\s*$", re.MULTILINE)
LIFECYCLE_STAGE_RE = re.compile(
    r"^Lifecycle stage:\s+`(S0|S1|S2|S3|S4|IMPLEMENTATION|META)`\s*$",
    re.MULTILINE,
)
STAGE_STATE_RE = re.compile(
    r"^Stage state:\s+`(NOT_STARTED|IN_PROGRESS|BLOCKED|GATE_FAILED|ACCEPTED|DIRTY)`\s*$",
    re.MULTILINE,
)
LIFECYCLE_BASIS_RE = re.compile(r"^Lifecycle basis:\s+(.+?)\s*$", re.MULTILINE)
IMPLEMENTATION_AUTH_RE = re.compile(
    r"^Implementation authorization:\s+`(none|G4 PASS)`\s*$",
    re.MULTILINE,
)
AUTHORIZED_SCOPE_RE = re.compile(r"^Authorized scope:\s+`([^`]+)`\s*$", re.MULTILINE)
AUTHORIZATION_BASIS_RE = re.compile(r"^Authorization basis:\s+`([^`]+)`\s*$", re.MULTILINE)
REQUIRED_CAPSULE_MARKERS = (
    "Current:",
    "Goal:",
    "Current task:",
    "Lifecycle stage:",
    "Stage state:",
    "Lifecycle basis:",
    "Implementation authorization:",
    "Authorized scope:",
    "Authorization basis:",
    "## Working set",
    "Read first:",
    "## Blockers",
    "## Gate",
    "## Next",
)
REQUIRED_PLAN_HEADINGS = (
    "## Goal",
    "## Inputs",
    "## Exit criteria",
    "## Blockers",
    "## Next",
)
PATH_BULLET_RE = re.compile(r"^\s*-\s+`([^`]+)`(?:\s+.*)?$")


def _active_plan_paths() -> list[Path]:
    return sorted(path for path in ACTIVE.glob("*.md") if path != INDEX)


def _section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return None

    collected: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        collected.append(line)
    return "\n".join(collected)


def _read_first_paths(text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    working_set = _section(text, "## Working set")
    if working_set is None:
        return [], ["active resume capsule missing ## Working set"]

    lines = working_set.splitlines()
    try:
        start = next(
            index for index, line in enumerate(lines)
            if line.strip() == "Read first:"
        ) + 1
    except StopIteration:
        return [], ["active resume capsule missing Read first:"]

    paths: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("Expand "):
            break
        match = PATH_BULLET_RE.match(line)
        if not match:
            errors.append(
                "Read first entries must be backtick repository-file bullets: "
                + stripped
            )
            continue
        paths.append(match.group(1))

    if not paths:
        errors.append("Read first must contain at least one repository file")
    return paths, errors


def _validate_read_first(paths: list[str]) -> list[str]:
    errors: list[str] = []
    if len(paths) > READ_FIRST_MAX_FILES:
        errors.append(
            f"Read first has {len(paths)} files; maximum is {READ_FIRST_MAX_FILES}"
        )

    if len(paths) != len(set(paths)):
        errors.append("Read first contains duplicate file paths")

    root = ROOT.resolve()
    total_bytes = 0
    for value in paths:
        relative = Path(value)
        if relative.is_absolute():
            errors.append(f"Read first path must be repository-relative: {value}")
            continue

        if relative.name == "AGENTS.md" or (
            len(relative.parts) >= 3
            and relative.parts[0] == ".agents"
            and relative.parts[1] == "skills"
            and relative.name == "SKILL.md"
        ):
            errors.append(
                "Read first must not duplicate routed AGENTS/Skill content: "
                + value
            )

        candidate = (ROOT / relative).resolve()
        if candidate != root and root not in candidate.parents:
            errors.append(f"Read first path escapes repository root: {value}")
            continue
        if not candidate.is_file():
            errors.append(f"Read first path does not exist as a file: {value}")
            continue

        total_bytes += candidate.stat().st_size

    if total_bytes > READ_FIRST_MAX_BYTES:
        errors.append(
            "Read first total size "
            f"{total_bytes} bytes exceeds {READ_FIRST_MAX_BYTES} bytes"
        )
    return errors


def _validate_lifecycle_lease(capsule: str) -> list[str]:
    errors: list[str] = []

    stage_match = LIFECYCLE_STAGE_RE.search(capsule)
    state_match = STAGE_STATE_RE.search(capsule)
    lifecycle_basis_match = LIFECYCLE_BASIS_RE.search(capsule)
    auth_match = IMPLEMENTATION_AUTH_RE.search(capsule)
    scope_match = AUTHORIZED_SCOPE_RE.search(capsule)
    auth_basis_match = AUTHORIZATION_BASIS_RE.search(capsule)

    if not stage_match:
        errors.append("Lifecycle stage must be one of S0-S4, IMPLEMENTATION, META")
    if not state_match:
        errors.append("Stage state must use the lifecycle state enum")
    if not lifecycle_basis_match or not lifecycle_basis_match.group(1).strip():
        errors.append("Lifecycle basis must be a non-empty one-line durable reference/trigger")
    if not auth_match:
        errors.append("Implementation authorization must be `none` or `G4 PASS`")
    if not scope_match:
        errors.append("Authorized scope must be a backticked value")
    if not auth_basis_match:
        errors.append("Authorization basis must be a backticked value")

    if not all([stage_match, state_match, auth_match, scope_match, auth_basis_match]):
        return errors

    stage = stage_match.group(1)
    state = state_match.group(1)
    authorization = auth_match.group(1)
    scope = scope_match.group(1).strip()
    authorization_basis = auth_basis_match.group(1).strip()

    if stage == "IMPLEMENTATION":
        if authorization != "G4 PASS":
            errors.append("IMPLEMENTATION stage requires `Implementation authorization: G4 PASS`")
        if scope.lower() == "none" or not scope:
            errors.append("IMPLEMENTATION stage requires a non-none Authorized scope")
        if authorization_basis.lower() == "none" or not authorization_basis:
            errors.append("IMPLEMENTATION stage requires a non-none Authorization basis")
        if state in {"ACCEPTED", "DIRTY", "NOT_STARTED"}:
            errors.append(
                "IMPLEMENTATION stage state must represent active/suspended execution, not ACCEPTED/DIRTY/NOT_STARTED"
            )
    else:
        if authorization != "none":
            errors.append("G4 authorization is valid only in IMPLEMENTATION execution mode")
        if scope.lower() != "none":
            errors.append("Authorized scope must be `none` outside IMPLEMENTATION")
        if authorization_basis.lower() != "none":
            errors.append("Authorization basis must be `none` outside IMPLEMENTATION")

    return errors


def main() -> int:
    errors: list[str] = []
    active_plans = _active_plan_paths()

    if not INDEX.is_file():
        errors.append("missing docs/plans/active/README.md")
    else:
        capsule = INDEX.read_text(encoding="utf-8-sig")
        if len(capsule.encode("utf-8")) > CAPSULE_MAX_BYTES:
            errors.append(
                f"active resume capsule exceeds {CAPSULE_MAX_BYTES} bytes"
            )

        match = CURRENT_RE.search(capsule)
        if not match:
            errors.append(
                "active plan index must contain Current: `<plan-file>` or Current: none."
            )
        elif match.group(2):
            if active_plans:
                errors.append(
                    "Current: none requires no plan files under docs/plans/active/"
                )
        else:
            for marker in REQUIRED_CAPSULE_MARKERS:
                if marker not in capsule:
                    errors.append(
                        f"active resume capsule missing marker: {marker}"
                    )

            errors.extend(_validate_lifecycle_lease(capsule))

            read_first, read_first_errors = _read_first_paths(capsule)
            errors.extend(read_first_errors)
            errors.extend(_validate_read_first(read_first))

            current = ACTIVE / match.group(1)
            if not current.is_file():
                errors.append(
                    f"current plan does not exist: {current.relative_to(ROOT)}"
                )
            else:
                plan = current.read_text(encoding="utf-8-sig")
                status_match = STATUS_RE.search(plan)
                if not status_match:
                    errors.append(
                        f"{current.relative_to(ROOT)}: missing Status"
                    )
                else:
                    status = status_match.group(1).strip().lower()
                    if status.startswith(
                        ("complete", "completed", "superseded")
                    ):
                        errors.append(
                            f"{current.relative_to(ROOT)}: "
                            "completed/superseded plan must not remain active"
                        )

                for heading in REQUIRED_PLAN_HEADINGS:
                    if heading not in plan:
                        errors.append(
                            f"{current.relative_to(ROOT)}: missing {heading}"
                        )

                if "## Current stage" in plan or "## Current task" in plan:
                    errors.append(
                        f"{current.relative_to(ROOT)}: mutable current task/stage "
                        "belongs only in docs/plans/active/README.md"
                    )

                current_task = CURRENT_TASK_RE.search(capsule)
                if current_task:
                    work_package = WORK_PACKAGE_RE.search(
                        current_task.group(1)
                    )
                    if work_package:
                        heading = f"## {work_package.group(1)}"
                        if heading not in plan:
                            errors.append(
                                "resume capsule selects "
                                f"{work_package.group(1)} but current plan "
                                "does not define that work package"
                            )

    for path in active_plans:
        text = path.read_text(encoding="utf-8-sig")
        status_match = STATUS_RE.search(text)
        if not status_match:
            errors.append(
                f"{path.relative_to(ROOT)}: active plan artifact must declare Status"
            )
            continue
        status = status_match.group(1).strip().lower()
        if status.startswith(("complete", "completed", "superseded")):
            errors.append(
                f"{path.relative_to(ROOT)}: inactive history must be removed "
                "from active/"
            )

    if errors:
        print("Plan validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("Active plan continuity, lifecycle lease and context budget OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
