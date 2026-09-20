#!/usr/bin/env python3
"""Differential proof for migration from NAPMS-local Harness to unified Harness."""
from __future__ import annotations

import copy
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = Path(os.environ.get("HARNESS_ROOT", ROOT / ".harness-tool"))

sys.path.insert(0, str(ROOT / "tools"))
from check_harness_vertical import VerticalError, evaluate as legacy_evaluate  # noqa: E402
from prepare_authority_execution import build_execution_context as legacy_context  # noqa: E402

sys.path.insert(0, str(HARNESS_ROOT))
from authority_context import build_authority_context as unified_context  # noqa: E402
from engineering_graph import evaluate_engineering_target  # noqa: E402
from harness import CoreError  # noqa: E402
from integration_alignment import validate_project_alignment  # noqa: E402


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def legacy_requirement(result, contract_id, requirement_id):
    contract = next(item for item in result["contracts"] if item["id"] == contract_id)
    return next(item for item in contract["requirements"] if item["id"] == requirement_id)


def expect_error(fn, exc_type, contains):
    try:
        fn()
    except exc_type as exc:
        assert contains in str(exc), (contains, str(exc))
    else:
        raise AssertionError(f"expected {exc_type.__name__}: {contains}")


def new_model(source, projection, graph):
    return validate_project_alignment(
        source,
        projection,
        graph,
        target_consumer="BACKEND-IMPLEMENTATION",
    )["model"]


def main() -> int:
    source = load(ROOT / "docs/canonical-graph.yaml")
    projection = load(ROOT / "docs/harness-core.yaml")
    graph = load(ROOT / "docs/harness-engineering-graph.yaml")

    # Baseline parity: old implementation says satisfied; new backend target says COMPLETE.
    legacy = legacy_evaluate(source, projection)
    assert legacy["satisfied"]
    model = new_model(source, projection, graph)
    backend = evaluate_engineering_target(graph, "BACKEND-IMPLEMENTATION", model)
    assert backend["status"] == "COMPLETE", backend

    # Missing HTTP contract: both route the gap to Interface Design.
    missing_http = copy.deepcopy(projection)
    openapi = next(item for item in missing_http["bindings"] if item["artifact"] == "OPENAPI")
    openapi["provides"].remove("engineering.interface.http-contract")
    legacy_http = legacy_evaluate(source, missing_http)
    old_gap = legacy_requirement(legacy_http, "IMPLEMENTATION-CONSUMER", "interface")
    assert old_gap["status"] == "DESIGN_GAP"
    assert old_gap["question"]["authority"] == "INTERFACE-DESIGN"
    http_model = new_model(source, missing_http, graph)
    new_http = evaluate_engineering_target(graph, "BACKEND-IMPLEMENTATION", http_model)
    assert new_http["status"] == "READY", new_http
    create = {item["capability"]: item["authority"] for item in new_http["create"]}
    assert create["engineering.interface.http-contract"] == "INTERFACE-DESIGN"

    # Missing security contract: same owner and actionable gap.
    missing_security = copy.deepcopy(projection)
    security = next(
        item for item in missing_security["bindings"]
        if item["artifact"] == "SECURITY-ARCHITECTURE"
    )
    security["provides"].remove("engineering.architecture.security")
    legacy_security = legacy_evaluate(source, missing_security)
    old_gap = legacy_requirement(
        legacy_security, "IMPLEMENTATION-CONSUMER", "security-architecture"
    )
    assert old_gap["status"] == "DESIGN_GAP"
    assert old_gap["question"]["authority"] == "SECURITY-ARCHITECTURE-DESIGN"
    security_model = new_model(source, missing_security, graph)
    new_security = evaluate_engineering_target(
        graph, "BACKEND-IMPLEMENTATION", security_model
    )
    create = {item["capability"]: item["authority"] for item in new_security["create"]}
    assert create["engineering.architecture.security"] == "SECURITY-ARCHITECTURE-DESIGN"

    # Artifact blocker propagates in both models.
    blocked_arch = copy.deepcopy(projection)
    blocked_arch["questions"].append(
        {
            "id": "Q-SYSTEM",
            "authority": "SYSTEM-ARCHITECTURE",
            "text": "Resolve architecture uncertainty.",
            "blocks": ["SYSTEM-RULES"],
        }
    )
    old_blocked = legacy_evaluate(source, blocked_arch)
    assert legacy_requirement(
        old_blocked, "IMPLEMENTATION-CONSUMER", "architecture-rules"
    )["status"] == "BLOCKED"
    blocked_model = new_model(source, blocked_arch, graph)
    new_blocked = evaluate_engineering_target(
        graph, "BACKEND-IMPLEMENTATION", blocked_model
    )
    assert "engineering.architecture.rules" in {
        item["capability"] for item in new_blocked["wait"]
    }

    # Hidden project dependency rejected by both.
    hidden_source = copy.deepcopy(source)
    interface_node = next(item for item in hidden_source["nodes"] if item["id"] == "OPENAPI")
    interface_node["depends_on"].append("RC-CURATION")
    expect_error(
        lambda: legacy_evaluate(hidden_source, projection),
        VerticalError,
        "input contract misses upstream Authorities",
    )
    expect_error(
        lambda: validate_project_alignment(
            hidden_source,
            projection,
            graph,
            target_consumer="BACKEND-IMPLEMENTATION",
        ),
        CoreError,
        "hidden project-graph upstream Authorities",
    )

    # Phantom capability dependency rejected by both.
    phantom_projection = copy.deepcopy(projection)
    contract = next(
        item for item in phantom_projection["contracts"]
        if item["id"] == "INTERFACE-DESIGN-INPUT"
    )
    contract["requires"].append(
        {
            "id": "phantom-data",
            "capability": "engineering.data.persistence-model",
            "authority": "DATA-DESIGN",
        }
    )
    expect_error(
        lambda: legacy_evaluate(source, phantom_projection),
        VerticalError,
        "non-graph upstream Authorities",
    )

    # New model owns topology in Engineering Graph: mutate it instead of a second contract list.
    phantom_graph = copy.deepcopy(graph)
    interface = next(
        item for item in phantom_graph["authorities"] if item["id"] == "INTERFACE-DESIGN"
    )
    http = next(
        item for item in interface["produces"]
        if item["capability"] == "engineering.interface.http-contract"
    )
    http["requires"].append("engineering.data.persistence-model")
    expect_error(
        lambda: validate_project_alignment(
            source,
            projection,
            phantom_graph,
            target_consumer="BACKEND-IMPLEMENTATION",
        ),
        CoreError,
        "phantom capability prerequisites",
    )

    # Authority write boundary remains equivalent for the existing system-rules slice.
    old_ctx = legacy_context("SYSTEM-ARCHITECTURE", source, projection)
    new_ctx = unified_context(
        graph,
        model,
        "SYSTEM-ARCHITECTURE",
        ["engineering.architecture.rules"],
    )
    assert old_ctx["status"] == "READY"
    assert new_ctx["status"] == "READY"
    assert set(old_ctx["access"]["write"]) == set(new_ctx["access"]["write"])

    # Intentional improvement: pre-provider Question is WAIT, not DESIGN_GAP.
    preprovider = copy.deepcopy(projection)
    openapi = next(item for item in preprovider["bindings"] if item["artifact"] == "OPENAPI")
    openapi["provides"].remove("engineering.interface.http-contract")
    preprovider["questions"].append(
        {
            "id": "Q-HTTP-PREPROVIDER",
            "authority": "INTERFACE-DESIGN",
            "text": "Resolve HTTP semantics before a provider can exist.",
            "blocks_capabilities": ["engineering.interface.http-contract"],
        }
    )
    old_preprovider = legacy_evaluate(source, preprovider)
    assert legacy_requirement(
        old_preprovider, "IMPLEMENTATION-CONSUMER", "interface"
    )["status"] == "DESIGN_GAP"
    pre_model = new_model(source, preprovider, graph)
    new_preprovider = evaluate_engineering_target(
        graph, "BACKEND-IMPLEMENTATION", pre_model
    )
    waiting = {item["capability"] for item in new_preprovider["wait"]}
    assert "engineering.interface.http-contract" in waiting

    # Frontend is no longer falsely covered by the backend consumer.
    frontend = evaluate_engineering_target(graph, "FRONTEND-IMPLEMENTATION", model)
    assert frontend["status"] == "READY", frontend
    assert {item["capability"] for item in frontend["create"]} == {
        "engineering.frontend.human-interface"
    }

    print("Unified Harness migration differential PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
