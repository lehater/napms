#!/usr/bin/env python3
"""Validate active-plan continuity and lifecycle."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = ROOT / "docs" / "plans" / "active"
INDEX = ACTIVE / "README.md"
CURRENT_RE = re.compile(r"^Current:\s+(?:`([^`]+)`|(none)\.?)\s*$", re.MULTILINE | re.IGNORECASE)
STATUS_RE = re.compile(r"^Status:\s+`([^`]+)`\s*$", re.MULTILINE)
REQUIRED_HEADINGS = [
    "## Goal",
    "## Current stage",
    "## Inputs",
    "## Exit criteria",
    "## Blockers",
    "## Next",
]


def main() -> int:
    errors: list[str] = []
    if not INDEX.is_file():
        errors.append("missing docs/plans/active/README.md")
    else:
        text = INDEX.read_text(encoding="utf-8-sig")
        match = CURRENT_RE.search(text)
        if not match:
            errors.append("active plan index must contain Current: `<plan-file>`")
        elif match.group(2):
            if any(ACTIVE.glob("PLAN-*.md")):
                errors.append("Current: none requires no PLAN-*.md files under active/")
        else:
            current = ACTIVE / match.group(1)
            if not current.is_file():
                errors.append(f"current plan does not exist: {current.relative_to(ROOT)}")
            else:
                plan = current.read_text(encoding="utf-8-sig")
                status_match = STATUS_RE.search(plan)
                if not status_match:
                    errors.append(f"{current.relative_to(ROOT)}: missing Status")
                else:
                    status = status_match.group(1).strip().lower()
                    if status.startswith(("complete", "completed", "superseded")):
                        errors.append(f"{current.relative_to(ROOT)}: completed/superseded plan must not remain active")
                for heading in REQUIRED_HEADINGS:
                    if heading not in plan:
                        errors.append(f"{current.relative_to(ROOT)}: missing {heading}")

    for path in ACTIVE.glob("PLAN-*.md"):
        text = path.read_text(encoding="utf-8-sig")
        match = STATUS_RE.search(text)
        if match and match.group(1).strip().lower().startswith(("complete", "completed", "superseded")):
            errors.append(f"{path.relative_to(ROOT)}: inactive history must be removed from active/")

    if errors:
        print("Plan validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("Active plan continuity OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
