#!/usr/bin/env python3
from __future__ import annotations

import copy
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_harness_vertical import VerticalError  # noqa: E402
from prepare_authority_execution import (  # noqa: E402
    build_execution_context,
    find_undeclared_canonical_references,
    validate_write_set,
)


def load(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def main() -> int:
    graph = load("docs/canonical-graph.yaml")
    projection = load("docs/harness-core.yaml")

    architecture = build_execution_context("SYSTEM-ARCHITECTURE", graph, projection)
    assert architecture["status"] == "READY"
    assert find_undeclared_canonical_references(architecture, graph, ROOT) == []
    assert architecture["input_contracts"] == ["SYSTEM-ARCHITECTURE-INPUT"]
    assert {item["authority"] for item in architecture["input_artifacts"]} == {
        "APPLICATION-JOURNEY-DESIGN",
        "DOMAIN-USE-CASE-DESIGN",
        "PRODUCT-REQUIREMENTS",
        "STRATEGIC-DOMAIN-DESIGN",
        "TACTICAL-DOMAIN-DESIGN",
    }
    assert {item["id"] for item in architecture["owned_artifacts"]} == {
        "C4-STRUCTURE",
        "MODULE-CONTRACTS",
        "SYSTEM-RULES",
    }
    architecture_support = {item["id"] for item in architecture["supporting_input_artifacts"]}
    assert {"STRATEGIC-CAPABILITIES", "STRATEGIC-CONTEXTS"} <= architecture_support
    assert {"RC-LANGUAGE", "RC-DECISIONS", "RC-PROCESS"} <= architecture_support
    # Internal support may cross artifacts inside the provider Authority, but must not
    # bypass the consumer contract into another engineering Authority.
    assert "RC-CURATION" not in architecture_support
    assert set(architecture["access"]["write"]) == {
        "docs/architecture/mvp-module-contracts.yaml",
        "docs/architecture/mvp-system-rules.yaml",
        "docs/architecture/structurizr/workspace.dsl",
    }
    assert "engineering.architecture.c4-model" in architecture["public_outputs"]
    assert any(
        item["consumer"] == "INTERFACE-DESIGN"
        for item in architecture["downstream_consumers"]
    )

    assert validate_write_set(
        architecture,
        [
            "docs/architecture/mvp-system-rules.yaml",
            "docs/architecture/mvp-module-contracts.yaml",
        ],
    ) == [
        "docs/architecture/mvp-module-contracts.yaml",
        "docs/architecture/mvp-system-rules.yaml",
    ]
    try:
        validate_write_set(architecture, ["docs/contracts/http/napms.openapi.yaml"])
    except VerticalError as exc:
        assert "may not write outside owned artifacts" in str(exc)
    else:
        raise AssertionError("System Architecture must not be allowed to edit Interface Design artifacts")

    interface = build_execution_context("INTERFACE-DESIGN", graph, projection)
    assert interface["status"] == "READY"
    assert find_undeclared_canonical_references(interface, graph, ROOT) == []
    assert interface["input_contracts"] == ["INTERFACE-DESIGN-INPUT"]
    assert {item["id"] for item in interface["owned_artifacts"]} == {
        "HTTP-REQUIREMENTS",
        "MVP-UI-NAVIGATION",
        "OPENAPI",
        "RESOURCE-DETAIL-UI",
        "TECH-REPRESENTATION",
    }
    assert {item["authority"] for item in interface["input_artifacts"]} == {
        "APPLICATION-JOURNEY-DESIGN",
        "PRODUCT-REQUIREMENTS",
        "SECURITY-ARCHITECTURE-DESIGN",
        "SYSTEM-ARCHITECTURE",
        "TACTICAL-DOMAIN-DESIGN",
    }
    # Same generic builder, different Authority: no System-Architecture hardcoding.
    assert architecture["access"]["write"] != interface["access"]["write"]

    for authority in {item["id"] for item in projection["authorities"]}:
        context = build_execution_context(authority, graph, projection)
        assert find_undeclared_canonical_references(context, graph, ROOT) == [], authority

    root = build_execution_context("PRODUCT-REQUIREMENTS", graph, projection)
    assert root["status"] == "ROOT"
    assert root["input_contracts"] == []
    assert root["input_artifacts"] == []
    assert root["supporting_input_artifacts"] == []
    assert set(root["access"]["write"]) == {
        "docs/requirements/first-mvp-policy-export.yaml",
        "docs/requirements/first-mvp-quality-targets.yaml",
    }

    blocked_projection = copy.deepcopy(projection)
    blocked_projection["questions"].append(
        {
            "id": "Q-JOURNEY",
            "authority": "APPLICATION-JOURNEY-DESIGN",
            "text": "Resolve application-journey uncertainty before architecture.",
            "blocks": ["FIRST-MVP-JOURNEY"],
        }
    )
    blocked = build_execution_context("SYSTEM-ARCHITECTURE", graph, blocked_projection)
    assert blocked["status"] == "BLOCKED"
    journey = next(item for item in blocked["requirements"] if item["id"] == "application-journey")
    assert journey["status"] == "BLOCKED"
    assert journey["blocked_by"] == ["Q-JOURNEY"]
    assert blocked["blockers"][0]["owner"] == "APPLICATION-JOURNEY-DESIGN"
    try:
        validate_write_set(blocked, ["docs/architecture/mvp-system-rules.yaml"])
    except VerticalError as exc:
        assert "is BLOCKED; artifact production is not allowed" in str(exc)
    else:
        raise AssertionError("Blocked Authority must not produce artifacts")

    gap_projection = copy.deepcopy(projection)
    journey_binding = next(
        item for item in gap_projection["bindings"] if item["artifact"] == "FIRST-MVP-JOURNEY"
    )
    journey_binding["provides"].remove("engineering.application.journey")
    gap = build_execution_context("SYSTEM-ARCHITECTURE", graph, gap_projection)
    assert gap["status"] == "BLOCKED"
    journey_gap = next(item for item in gap["requirements"] if item["id"] == "application-journey")
    assert journey_gap["status"] == "DESIGN_GAP"
    assert journey_gap["question"]["authority"] == "APPLICATION-JOURNEY-DESIGN"

    print("Authority execution context acceptance PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
