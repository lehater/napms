#!/usr/bin/env python3
"""NAPMS project assertions over the pinned canonical Harness runtime."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = Path(os.environ.get("HARNESS_ROOT", ROOT / ".harness-tool"))
if not (HARNESS_ROOT / "engineering_graph.py").exists():
    raise SystemExit(
        "Pinned Harness runtime not found. Set HARNESS_ROOT or checkout the pinned "
        "lehater/harness commit into .harness-tool."
    )

sys.path.insert(0, str(HARNESS_ROOT))
from engineering_graph import evaluate_engineering_target  # noqa: E402
from integration_alignment import validate_project_alignment  # noqa: E402


def load(path: str):
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path} must be a mapping")
    return value


def main() -> int:
    source = load("docs/canonical-graph.yaml")
    projection = load("docs/harness-projection.yaml")
    graph = load("docs/harness-engineering-graph.yaml")

    aligned = validate_project_alignment(
        source,
        projection,
        graph,
        target_consumer="BACKEND-IMPLEMENTATION",
    )
    model = aligned["model"]

    backend = evaluate_engineering_target(
        graph, "BACKEND-IMPLEMENTATION", model
    )
    if backend["status"] != "COMPLETE":
        raise SystemExit(
            f"BACKEND-IMPLEMENTATION must remain COMPLETE, got {backend['status']}"
        )

    frontend = evaluate_engineering_target(
        graph, "FRONTEND-IMPLEMENTATION", model
    )
    actual_frontier = {item["capability"] for item in frontend["create"]}
    if frontend["status"] != "COMPLETE" or actual_frontier:
        raise SystemExit(
            "FRONTEND-IMPLEMENTATION target mismatch: "
            f"status={frontend['status']} create={sorted(actual_frontier)}"
        )

    print("NAPMS pinned Harness integration PASS")
    print("BACKEND-IMPLEMENTATION: COMPLETE")
    print("FRONTEND-IMPLEMENTATION: COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
