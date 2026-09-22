#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAP = ROOT / ".github" / "ci-impact.json"


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _event_range(event_path: Path) -> tuple[str | None, str | None, bool]:
    payload = json.loads(event_path.read_text(encoding="utf-8"))
    action = payload.get("action")
    pull_request = payload.get("pull_request")

    if isinstance(pull_request, dict):
        head = str(pull_request["head"]["sha"])
        if action == "synchronize":
            before = payload.get("before")
            after = payload.get("after") or head
            if not before:
                raise RuntimeError(
                    "pull_request synchronize event is missing 'before'; "
                    "refusing to fall back to the cumulative PR diff"
                )
            return str(before), str(after), False
        return str(pull_request["base"]["sha"]), head, False

    before = payload.get("before")
    after = payload.get("after")
    if before and after:
        if str(before) == "0" * 40:
            return None, str(after), False
        return str(before), str(after), False

    # workflow_dispatch has no meaningful change range: explicit manual runs run the group.
    return None, None, True


def _changed_paths(base: str | None, head: str | None, run_all: bool) -> list[str]:
    if run_all:
        return []
    if head is None:
        raise RuntimeError("missing head revision")
    if base is None:
        output = _git("diff-tree", "--root", "--no-commit-id", "--name-only", "-r", head)
    else:
        output = _git("diff", "--name-only", "--diff-filter=ACMR", base, head)
    return [line.strip() for line in output.splitlines() if line.strip()]


def _matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Select CI groups from the incremental event change range."
    )
    parser.add_argument("--group", action="append", required=True)
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--event-path", type=Path, default=Path(os.environ["GITHUB_EVENT_PATH"]))
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()

    config = json.loads(args.map.read_text(encoding="utf-8"))
    groups = config["groups"]
    unknown = sorted(set(args.group) - set(groups))
    if unknown:
        raise SystemExit(f"unknown CI impact group(s): {', '.join(unknown)}")

    base, head, run_all = _event_range(args.event_path)
    changed = _changed_paths(base, head, run_all)

    outputs: dict[str, bool] = {}
    for group in args.group:
        outputs[group] = run_all or any(_matches(path, groups[group]) for path in changed)

    print(
        json.dumps(
            {
                "base": base,
                "head": head,
                "run_all": run_all,
                "changed_paths": changed,
                "groups": outputs,
            },
            indent=2,
            sort_keys=True,
        )
    )

    if args.github_output is not None:
        with args.github_output.open("a", encoding="utf-8") as target:
            for group, selected in outputs.items():
                target.write(f"{group}={'true' if selected else 'false'}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
