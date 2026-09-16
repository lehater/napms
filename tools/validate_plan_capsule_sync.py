#!/usr/bin/env python3
"""Detect obvious durable active-plan/resume-capsule drift without semantic prose comparison."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = ROOT / "docs" / "plans" / "active"
INDEX = ACTIVE / "README.md"
CURRENT_RE = re.compile(r"^Current:\s+`([^`]+)`", re.MULTILINE)
CURRENT_TASK_RE = re.compile(r"^Current task:\s+(.+)$", re.MULTILINE)
MILESTONE_RE = re.compile(r"\bM(\d+)\b", re.IGNORECASE)


def section(text: str, heading: str) -> str:
    lines = text.splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return ""
    result: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        result.append(line)
    return "\n".join(result)


def main() -> int:
    capsule = INDEX.read_text(encoding="utf-8-sig")
    current = CURRENT_RE.search(capsule)
    task = CURRENT_TASK_RE.search(capsule)
    if not current or not task:
        print("Plan/capsule sync check skipped: base plan validator owns malformed capsule detection")
        return 0
    plan_path = ACTIVE / current.group(1)
    if not plan_path.is_file():
        print("Plan/capsule sync check skipped: base plan validator owns missing-plan detection")
        return 0
    next_text = section(plan_path.read_text(encoding="utf-8-sig"), "## Next")
    task_ms = [int(value) for value in MILESTONE_RE.findall(task.group(1))]
    next_ms = [int(value) for value in MILESTONE_RE.findall(next_text)]
    errors: list[str] = []
    if task_ms and next_ms and max(task_ms) < min(next_ms):
        errors.append(f"active capsule references M{max(task_ms)} while plan Next references M{min(next_ms)}")
    if "paused" in next_text.lower() and "pause" not in task.group(1).lower() and "review" not in task.group(1).lower():
        errors.append("active capsule does not reflect plan pause/review state")
    if errors:
        print("Plan/capsule sync failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("Plan/capsule drift check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
