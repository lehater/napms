#!/usr/bin/env python3
"""Validate structural coverage of NAPMS Skill routing examples."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
CASES = ROOT / "backend" / "tests" / "evals" / "skill-routing-cases.json"


def main() -> int:
    try:
        skills = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
        cases = json.loads(CASES.read_text(encoding="utf-8"))
        if not isinstance(cases, list) or not cases:
            raise ValueError("routing corpus must be a non-empty JSON array")

        ids: set[str] = set()
        coverage = Counter()
        for case in cases:
            missing = {"id", "prompt", "expected_skill"} - case.keys()
            if missing:
                raise ValueError(f"routing case missing fields: {sorted(missing)}")
            case_id = str(case["id"])
            if case_id in ids:
                raise ValueError(f"duplicate case id: {case_id}")
            ids.add(case_id)
            if not str(case["prompt"]).strip():
                raise ValueError(f"empty prompt: {case_id}")

            expected = str(case["expected_skill"])
            if expected not in skills:
                raise ValueError(f"unknown expected skill {expected!r} in {case_id}")
            coverage[expected] += 1

            rejected = case.get("not_expected_skills", [])
            if not isinstance(rejected, list) or any(not isinstance(x, str) for x in rejected):
                raise ValueError(f"not_expected_skills must be a string array in {case_id}")
            unknown = sorted(set(rejected) - skills)
            if unknown:
                raise ValueError(f"unknown rejected skills in {case_id}: {unknown}")
            if expected in rejected:
                raise ValueError(f"expected skill is also rejected in {case_id}")

        undercovered = sorted(skill for skill in skills if coverage[skill] < 2)
        if undercovered:
            raise ValueError("each Skill needs at least two routing cases: " + ", ".join(undercovered))

    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Skill routing validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Skill routing corpus OK: {len(cases)} cases for {len(skills)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
