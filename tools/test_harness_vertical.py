#!/usr/bin/env python3
from __future__ import annotations

import copy
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_harness_vertical import VerticalError, evaluate  # noqa: E402


def load(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def requirement(result, contract_id, requirement_id):
    contract = next(item for item in result["contracts"] if item["id"] == contract_id)
    return next(item for item in contract["requirements"] if item["id"] == requirement_id)


def expect_error(fn, contains: str):
    try:
        fn()
    except VerticalError as exc:
        assert contains in str(exc), (contains, str(exc))
    else:
        raise AssertionError(f"expected VerticalError containing {contains!r}")


def main() -> int:
    graph = load("docs/canonical-graph.yaml")
    projection = load("docs/harness-core.yaml")

    baseline = evaluate(graph, projection)
    assert baseline["satisfied"]
    assert {item["id"] for item in graph["nodes"]} == {item["artifact"] for item in projection["bindings"]}
    authority_ids = {item["id"] for item in projection["authorities"]}
    assert "DOMAIN-DESIGN" not in authority_ids
    assert "SYSTEM-ARCHITECTURE" not in authority_ids
    assert "TECHNICAL-REPRESENTATION" not in authority_ids
    assert requirement(baseline, "IMPLEMENTATION-PLAN-INPUT", "asynchronous-contract")["status"] == "NOT_APPLICABLE"

    bad_boundary = copy.deepcopy(projection)
    del bad_boundary["authorities"][0]["boundary"]["public_contract"]
    expect_error(lambda: evaluate(graph, bad_boundary), "boundary.public_contract")

    missing_binding = copy.deepcopy(projection)
    missing_binding["bindings"] = [item for item in missing_binding["bindings"] if item["artifact"] != "RC-DISCOVERY"]
    expect_error(lambda: evaluate(graph, missing_binding), "Canonical artifacts without Authority binding")

    missing_http = copy.deepcopy(projection)
    openapi = next(item for item in missing_http["bindings"] if item["artifact"] == "OPENAPI")
    openapi["provides"].remove("architecture.http-contract")
    result = evaluate(graph, missing_http)
    gap = requirement(result, "IMPLEMENTATION-CONSUMER", "http-contract")
    assert gap["status"] == "DESIGN_GAP"
    assert gap["question"]["authority"] == "HTTP-CONTRACT"

    missing_security = copy.deepcopy(projection)
    security = next(item for item in missing_security["bindings"] if item["artifact"] == "SECURITY-ARCHITECTURE")
    security["provides"].remove("architecture.security-boundary")
    result = evaluate(graph, missing_security)
    gap = requirement(result, "IMPLEMENTATION-CONSUMER", "security-boundary")
    assert gap["status"] == "DESIGN_GAP"
    assert gap["question"]["authority"] == "SECURITY-ARCHITECTURE"

    missing_na_evidence = copy.deepcopy(projection)
    system_rules = next(item for item in missing_na_evidence["bindings"] if item["artifact"] == "SYSTEM-RULES")
    system_rules["provides"].remove("architecture.async-messaging-not-applicable")
    result = evaluate(graph, missing_na_evidence)
    gap = requirement(result, "IMPLEMENTATION-PLAN-INPUT", "asynchronous-contract")
    assert gap["status"] == "DESIGN_GAP"
    assert gap["question"]["authority"] == "APPLICATION-ARCHITECTURE"

    blocked_upstream = copy.deepcopy(projection)
    blocked_upstream["questions"].append({
        "id": "Q-APPLICATION-ARCH",
        "authority": "APPLICATION-ARCHITECTURE",
        "text": "Resolve an application-architecture uncertainty.",
        "blocks": ["SYSTEM-RULES"],
    })
    result = evaluate(graph, blocked_upstream)
    assert requirement(result, "IMPLEMENTATION-CONSUMER", "module-contracts")["status"] == "BLOCKED"
    assert requirement(result, "IMPLEMENTATION-CONSUMER", "http-contract")["status"] == "BLOCKED"
    assert requirement(result, "IMPLEMENTATION-CONSUMER", "persistence")["status"] == "BLOCKED"

    wrong_expected_owner = copy.deepcopy(projection)
    contract = next(item for item in wrong_expected_owner["contracts"] if item["id"] == "IMPLEMENTATION-CONSUMER")
    req = next(item for item in contract["requires"] if item["id"] == "resource")
    req["authority"] = "ACCESS-POLICY"
    expect_error(lambda: evaluate(graph, wrong_expected_owner), "expected ACCESS-POLICY")

    print("Harness documentation vertical acceptance PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
