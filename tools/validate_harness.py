#!/usr/bin/env python3
"""Validate the NAPMS repository-local agent harness."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---(?:\n|$)", re.DOTALL)
REQUIRED_SKILLS = {
    "execute-work-package",
    "implement-slice",
    "domain-model-change",
    "architecture-review",
    "resolve-decision",
    "agent-harness-design",
    "skill-design",
}


def parse_skill(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("missing YAML frontmatter")
    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, value = line.split(":", 1)
        if key in {"name", "description"}:
            value = value.strip()
            if value.startswith('"'):
                value = json.loads(value)
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            fields[key] = value
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not name or not description:
        raise ValueError("name and description are required")
    if not NAME_RE.fullmatch(name) or len(name) > 64:
        raise ValueError(f"invalid skill name {name!r}")
    if name != path.parent.name:
        raise ValueError("frontmatter name must match directory")
    if len(description) > 1024:
        raise ValueError("description exceeds 1024 characters")
    return name, description


def _ordered_markers(text: str, markers: list[str]) -> bool:
    position = -1
    for marker in markers:
        next_position = text.find(marker, position + 1)
        if next_position < 0:
            return False
        position = next_position
    return True


def main() -> int:
    errors: list[str] = []
    required = [
        ROOT / "AGENTS.md",
        ROOT / "src" / "AGENTS.md",
        ROOT / "web" / "AGENTS.md",
        ROOT / "docs" / "AGENTS.md",
        ROOT / ".agents" / "README.md",
        ROOT / ".agents" / "skills" / "AGENTS.md",
        ROOT / "docs" / "process" / "README.md",
        ROOT / "docs" / "process" / "plan-lifecycle.md",
        ROOT / "docs" / "process" / "working-loop.md",
        ROOT / "docs" / "plans" / "active" / "README.md",
        ROOT / "tests" / "evals" / "skill-routing-cases.json",
    ]
    for path in required:
        if not path.is_file():
            errors.append(
                f"missing required harness file: {path.relative_to(ROOT)}"
            )

    root_agents = ROOT / "AGENTS.md"
    if root_agents.is_file():
        text = root_agents.read_text(encoding="utf-8-sig")
        for marker in [
            ".agents/skills/",
            "docs/plans/active/README.md",
            "Read the full current",
            "PLAN-*.md",
            "non-authoritative recovery cache",
            "web/AGENTS.md",
            "squash merge",
            "must not commit directly to",
        ]:
            if marker not in text:
                errors.append(
                    f"AGENTS.md missing guardrail marker: {marker}"
                )

        startup_order = [
            "1. this file;",
            "2. `docs/plans/active/README.md`",
            "3. the nearest scoped `AGENTS.md`",
            "4. the smallest applicable Skill",
            "5. only the canonical artifacts and code",
        ]
        if not _ordered_markers(text, startup_order):
            errors.append(
                "AGENTS.md must preserve root -> capsule -> scoped AGENTS "
                "-> Skill -> working-set startup order"
            )

        if len(text.encode("utf-8")) > 12 * 1024:
            errors.append("AGENTS.md exceeds 12 KiB; keep it map-like")

    working_loop = ROOT / "docs" / "process" / "working-loop.md"
    if working_loop.is_file():
        text = working_loop.read_text(encoding="utf-8-sig")
        for marker in [
            "## Context rollover",
            "disposable execution context",
            "read-only by default",
        ]:
            if marker not in text:
                errors.append(
                    f"working-loop.md missing context-performance marker: "
                    f"{marker}"
                )

    execute_work_package = SKILLS / "execute-work-package" / "SKILL.md"
    if execute_work_package.is_file():
        text = execute_work_package.read_text(encoding="utf-8-sig")
        for marker in [
            "root `AGENTS.md` -> `docs/plans/active/README.md` "
            "-> nearest scoped `AGENTS.md`",
            "Read the full current plan only",
            "canonical truth and refresh the capsule",
            "context rollover",
        ]:
            if marker not in text:
                errors.append(
                    f"execute-work-package missing recovery marker: {marker}"
                )

    skill_paths = sorted(SKILLS.glob("*/SKILL.md")) if SKILLS.is_dir() else []
    names: set[str] = set()
    for path in skill_paths:
        try:
            name, _ = parse_skill(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        if name in names:
            errors.append(f"duplicate skill name: {name}")
        names.add(name)

    missing = sorted(REQUIRED_SKILLS - names)
    if missing:
        errors.append(
            "missing required core skills: " + ", ".join(missing)
        )

    if ROOT.joinpath("docs", "methodology").exists():
        errors.append(
            "legacy methodology tree must not be recreated; use docs/process"
        )
    if ROOT.joinpath("agent", "skills").exists():
        errors.append("deprecated agent/skills path exists")

    if errors:
        print("Harness validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Harness OK: {len(names)} skills validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
