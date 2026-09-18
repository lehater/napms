#!/usr/bin/env python3
from __future__ import annotations

import copy
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_harness_vertical import evaluate  # noqa: E402


def load(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def requirement(result, contract_id, requirement_id):
    contract = next(item for item in result["contracts"] if item["id"] == contract_id)
    return next(item for item in contract["requirements"] if item["id"] == requirement_id)


def main() -> int:
    graph = load("docs/canonical-graph.yaml")
    projection = load("docs/harness-core.yaml")

    baseline = evaluate(graph, projection)
    assert baseline["satisfied"]
    assert requirement(baseline, "ARCHITECTURE-TO-IMPLEMENTATION-DESIGN", "asynchronous-contract")["status"] == "NOT_APPLICABLE"

    missing_http = copy.deepcopy(projection)
    openapi = next(item for item in missing_http["bindings"] if item["artifact"] == "OPENAPI")
    openapi["provides"].remove("architecture.http-contract")
    result = evaluate(graph, missing_http)
    gap = requirement(result, "IMPLEMENTATION-CONSUMER", "http-contract")
    assert gap["status"] == "DESIGN_GAP"
    assert gap["question"]["authority"] == "SYSTEM-ARCHITECTURE"

    missing_na_evidence = copy.deepcopy(projection)
    tech = next(item for item in missing_na_evidence["bindings"] if item["artifact"] == "TECH-REPRESENTATION")
    tech["provides"].remove("architecture.async-messaging-not-applicable")
    result = evaluate(graph, missing_na_evidence)
    assert requirement(result, "ARCHITECTURE-TO-IMPLEMENTATION-DESIGN", "asynchronous-contract")["status"] == "DESIGN_GAP"

    blocked_upstream = copy.deepcopy(projection)
    blocked_upstream["questions"].append({
        "id": "Q-SYSTEM-RULE",
        "authority": "SYSTEM-ARCHITECTURE",
        "text": "Resolve an architecture rule uncertainty.",
        "blocks": ["SYSTEM-RULES"],
    })
    result = evaluate(graph, blocked_upstream)
    blocked = requirement(result, "IMPLEMENTATION-CONSUMER", "http-contract")
    assert blocked["status"] == "BLOCKED"
    assert blocked["blocked_by"] == ["Q-SYSTEM-RULE"]

    print("Harness documentation vertical acceptance PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
