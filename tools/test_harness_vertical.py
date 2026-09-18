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
    expected_engineering_authorities = {
        "DISCOVERY",
        "PRODUCT-REQUIREMENTS",
        "STRATEGIC-DOMAIN-DESIGN",
        "DOMAIN-USE-CASE-DESIGN",
        "TACTICAL-DOMAIN-DESIGN",
        "APPLICATION-JOURNEY-DESIGN",
        "SYSTEM-ARCHITECTURE",
        "SECURITY-ARCHITECTURE-DESIGN",
        "INTERFACE-DESIGN",
        "DATA-DESIGN",
        "QUALITY-DESIGN",
        "SECURITY-ANALYSIS",
        "OPERABILITY-DESIGN",
        "IMPLEMENTATION-DESIGN",
        "VERIFICATION-DESIGN",
    }
    assert authority_ids == expected_engineering_authorities

    # Domain subjects/Bounded Contexts are content inside design artifacts, not Harness Authorities.
    for domain_subject in {
        "RESOURCE-CATALOGUE",
        "AUTHORITY-MANAGEMENT",
        "APPLICATION-COMMUNICATION-CATALOGUE",
        "APPLICATION-DEPLOYMENT",
        "BUSINESS-CONNECTIVITY",
        "ACCESS-POLICY",
    }:
        assert domain_subject not in authority_ids

    assert {item["id"] for item in projection["root_authorities"]} == {
        "DISCOVERY",
        "PRODUCT-REQUIREMENTS",
        "STRATEGIC-DOMAIN-DESIGN",
    }
    assert baseline["public_capabilities"]["terminal"] == []
    assert baseline["public_capabilities"]["consumed"]
    assert requirement(baseline, "IMPLEMENTATION-DESIGN-INPUT", "asynchronous-contract")["status"] == "NOT_APPLICABLE"

    bad_boundary = copy.deepcopy(projection)
    del bad_boundary["authorities"][0]["boundary"]["public_contract"]
    expect_error(lambda: evaluate(graph, bad_boundary), "boundary.public_contract")

    missing_binding = copy.deepcopy(projection)
    missing_binding["bindings"] = [item for item in missing_binding["bindings"] if item["artifact"] != "RC-DISCOVERY"]
    expect_error(lambda: evaluate(graph, missing_binding), "Canonical artifacts without Authority binding")

    missing_input_contract = copy.deepcopy(projection)
    missing_input_contract["contracts"] = [
        item for item in missing_input_contract["contracts"]
        if item["id"] != "TACTICAL-DOMAIN-DESIGN-INPUT"
    ]
    expect_error(lambda: evaluate(graph, missing_input_contract), "non-root Authorities without input contract")

    invalid_root = copy.deepcopy(projection)
    invalid_root["root_authorities"].append({
        "id": "DATA-DESIGN",
        "reason": "Invalid regression root.",
    })
    expect_error(lambda: evaluate(graph, invalid_root), "root authority DATA-DESIGN has external upstream Authorities")

    phantom_input = copy.deepcopy(projection)
    contract = next(item for item in phantom_input["contracts"] if item["id"] == "DOMAIN-USE-CASE-DESIGN-INPUT")
    contract["requires"].append({
        "id": "phantom-product-input",
        "capability": "engineering.requirements.product-intent",
        "authority": "PRODUCT-REQUIREMENTS",
    })
    expect_error(lambda: evaluate(graph, phantom_input), "input contract has non-graph upstream Authorities")

    dead_public_output = copy.deepcopy(projection)
    system_rules = next(item for item in dead_public_output["bindings"] if item["artifact"] == "SYSTEM-RULES")
    system_rules["provides"].append("engineering.architecture.unused-output")
    expect_error(lambda: evaluate(graph, dead_public_output), "Unconsumed public capabilities")

    explicit_terminal = copy.deepcopy(dead_public_output)
    explicit_terminal["terminal_capabilities"].append({
        "capability": "engineering.architecture.unused-output",
        "authority": "SYSTEM-ARCHITECTURE",
        "reason": "Regression fixture: explicit terminal result has no downstream consumer in this graph.",
    })
    terminal_result = evaluate(graph, explicit_terminal)
    assert terminal_result["satisfied"]
    assert terminal_result["public_capabilities"]["terminal"] == ["engineering.architecture.unused-output"]

    redundant_terminal = copy.deepcopy(projection)
    redundant_terminal["terminal_capabilities"].append({
        "capability": "engineering.interface.http-contract",
        "authority": "INTERFACE-DESIGN",
        "reason": "Invalid regression fixture because the capability is already consumed.",
    })
    expect_error(lambda: evaluate(graph, redundant_terminal), "terminal capabilities are already consumed downstream")

    missing_http = copy.deepcopy(projection)
    openapi = next(item for item in missing_http["bindings"] if item["artifact"] == "OPENAPI")
    openapi["provides"].remove("engineering.interface.http-contract")
    result = evaluate(graph, missing_http)
    gap = requirement(result, "IMPLEMENTATION-CONSUMER", "interface")
    assert gap["status"] == "DESIGN_GAP"
    assert gap["question"]["authority"] == "INTERFACE-DESIGN"

    missing_security = copy.deepcopy(projection)
    security = next(item for item in missing_security["bindings"] if item["artifact"] == "SECURITY-ARCHITECTURE")
    security["provides"].remove("engineering.architecture.security")
    result = evaluate(graph, missing_security)
    gap = requirement(result, "IMPLEMENTATION-CONSUMER", "security-architecture")
    assert gap["status"] == "DESIGN_GAP"
    assert gap["question"]["authority"] == "SECURITY-ARCHITECTURE-DESIGN"

    missing_na_evidence = copy.deepcopy(projection)
    system_rules = next(item for item in missing_na_evidence["bindings"] if item["artifact"] == "SYSTEM-RULES")
    system_rules["provides"].remove("engineering.architecture.async-messaging-not-applicable")
    result = evaluate(graph, missing_na_evidence)
    gap = requirement(result, "IMPLEMENTATION-DESIGN-INPUT", "asynchronous-contract")
    assert gap["status"] == "DESIGN_GAP"
    assert gap["question"]["authority"] == "SYSTEM-ARCHITECTURE"

    blocked_architecture = copy.deepcopy(projection)
    blocked_architecture["questions"].append({
        "id": "Q-SYSTEM-ARCHITECTURE",
        "authority": "SYSTEM-ARCHITECTURE",
        "text": "Resolve a system-architecture uncertainty.",
        "blocks": ["SYSTEM-RULES"],
    })
    result = evaluate(graph, blocked_architecture)
    assert requirement(result, "IMPLEMENTATION-CONSUMER", "architecture-rules")["status"] == "BLOCKED"
    assert requirement(result, "IMPLEMENTATION-CONSUMER", "interface")["status"] == "BLOCKED"
    assert requirement(result, "IMPLEMENTATION-CONSUMER", "persistence")["status"] == "BLOCKED"

    blocked_domain_use_case = copy.deepcopy(projection)
    blocked_domain_use_case["questions"].append({
        "id": "Q-DOMAIN-USE-CASE",
        "authority": "DOMAIN-USE-CASE-DESIGN",
        "text": "Resolve a domain use-case uncertainty.",
        "blocks": ["RC-CURATION"],
    })
    result = evaluate(graph, blocked_domain_use_case)
    tactical = requirement(result, "TACTICAL-DOMAIN-DESIGN-INPUT", "use-case-model")
    assert tactical["status"] == "BLOCKED"
    impl_tactical = requirement(result, "IMPLEMENTATION-CONSUMER", "tactical-domain")
    assert impl_tactical["status"] == "BLOCKED"
    assert impl_tactical["blocked_by"] == ["Q-DOMAIN-USE-CASE"]
    assert requirement(result, "IMPLEMENTATION-CONSUMER", "journey")["status"] == "BLOCKED"

    wrong_expected_owner = copy.deepcopy(projection)
    contract = next(item for item in wrong_expected_owner["contracts"] if item["id"] == "IMPLEMENTATION-CONSUMER")
    req = next(item for item in contract["requires"] if item["id"] == "interface")
    req["authority"] = "DATA-DESIGN"
    expect_error(lambda: evaluate(graph, wrong_expected_owner), "expected DATA-DESIGN")

    print("Harness engineering-knowledge vertical acceptance PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
