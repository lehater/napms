#!/usr/bin/env python3
"""Validate active-plan continuity, resume locality and lifecycle."""

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
REQUIRED_CAPSULE_MARKERS = (
    "Current:",
    "Goal:",
    "Current task:",
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


def main() -> int:
    errors: list[str] = []
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
            if any(ACTIVE.glob("PLAN-*.md")):
                errors.append(
                    "Current: none requires no PLAN-*.md files under active/"
                )
        else:
            for marker in REQUIRED_CAPSULE_MARKERS:
                if marker not in capsule:
                    errors.append(
                        f"active resume capsule missing marker: {marker}"
                    )

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

    for path in ACTIVE.glob("PLAN-*.md"):
        text = path.read_text(encoding="utf-8-sig")
        match = STATUS_RE.search(text)
        if (
            match
            and match.group(1)
            .strip()
            .lower()
            .startswith(("complete", "completed", "superseded"))
        ):
            errors.append(
                f"{path.relative_to(ROOT)}: inactive history must be removed "
                "from active/"
            )

    if errors:
        print("Plan validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("Active plan continuity and context budget OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
