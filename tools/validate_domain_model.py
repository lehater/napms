#!/usr/bin/env python3
"""Validate machine-readable living Strategic DDD invariants."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "docs" / "domain" / "strategic-model.json"
DOMAIN = ROOT / "docs" / "domain"


def main() -> int:
    errors: list[str] = []
    try:
        model = json.loads(MODEL.read_text(encoding="utf-8"))
        required = {"model_id", "status", "bounded_contexts", "wave1_direct_participants", "external_seams", "invariants"}
        missing = required - model.keys()
        if missing:
            raise ValueError(f"missing model fields: {sorted(missing)}")

        contexts = model["bounded_contexts"]
        if not isinstance(contexts, list) or not contexts:
            raise ValueError("bounded_contexts must be a non-empty array")
        names = []
        for item in contexts:
            if not isinstance(item, dict) or not item.get("name") or not item.get("responsibility"):
                raise ValueError("each bounded context requires name and responsibility")
            names.append(item["name"])
        if len(names) != len(set(names)):
            raise ValueError("bounded context names must be unique")

        participants = model["wave1_direct_participants"]
        unknown = sorted(set(participants) - set(names))
        if unknown:
            raise ValueError(f"Wave-1 participants are not bounded contexts: {unknown}")

        seams = model["external_seams"]
        overlap = sorted(set(seams) & set(names))
        if overlap:
            raise ValueError(f"external seams must not also be bounded contexts: {overlap}")

        if model["status"] != "accepted":
            raise ValueError("living Strategic DDD model must have accepted status")

        stale = []
        for path in DOMAIN.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".json"}:
                continue
            text = path.read_text(encoding="utf-8-sig")
            if "DDD-BDM-009" in text:
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            raise ValueError("current domain docs reference superseded DDD-BDM-009: " + ", ".join(stale))

    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))

    if errors:
        print("Domain model validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Domain model OK: {len(names)} bounded contexts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
