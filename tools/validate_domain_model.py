#!/usr/bin/env python3
"""Validate the machine-readable living Strategic DDD projection."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "docs" / "domain" / "strategic-model.json"
DOMAIN = ROOT / "docs" / "domain"

def main() -> int:
    try:
        model = json.loads(MODEL.read_text(encoding="utf-8"))
        required = {"model_id", "status", "bounded_contexts", "participants", "relationships", "invariants"}
        missing = required - model.keys()
        if missing:
            raise ValueError(f"missing model fields: {sorted(missing)}")
        participant_ids = []
        for item in model["participants"]:
            if not isinstance(item, dict) or not item.get("id") or not item.get("kind") or not item.get("name"):
                raise ValueError("each participant requires id, kind and name")
            participant_ids.append(item["id"])
        if len(participant_ids) != len(set(participant_ids)):
            raise ValueError("participant ids must be unique")
        bounded_ids = set(model["bounded_contexts"])
        unknown_bcs = sorted(bounded_ids - set(participant_ids))
        if unknown_bcs:
            raise ValueError(f"bounded_contexts reference unknown participants: {unknown_bcs}")
        wrong_kind = sorted(item["id"] for item in model["participants"] if item["id"] in bounded_ids and item["kind"] != "bounded_context")
        if wrong_kind:
            raise ValueError(f"bounded context ids have wrong participant kind: {wrong_kind}")
        for edge in model["relationships"]:
            if not isinstance(edge, dict) or not edge.get("source") or not edge.get("target") or not edge.get("contract"):
                raise ValueError("each relationship requires source, target and contract")
            unknown = {edge["source"], edge["target"]} - set(participant_ids)
            if unknown:
                raise ValueError(f"relationship references unknown participants: {sorted(unknown)}")
        if model["status"] not in {"accepted", "affected-edge-converged-s1-open"}:
            raise ValueError(f"unsupported living Strategic DDD status: {model['status']}")
        stale = []
        for path in DOMAIN.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json"} and "DDD-BDM-009" in path.read_text(encoding="utf-8-sig"):
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            raise ValueError("current domain docs reference superseded DDD-BDM-009: " + ", ".join(stale))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("Domain model validation failed:", file=sys.stderr)
        print(f"  - {exc}", file=sys.stderr)
        return 1
    print(f"Domain model OK: {len(bounded_ids)} bounded contexts, {len(model['relationships'])} relationships")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
