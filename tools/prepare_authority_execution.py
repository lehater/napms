#!/usr/bin/env python3
"""NAPMS adapter for the pinned Harness Authority execution context."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = Path(os.environ.get("HARNESS_ROOT", ROOT / ".harness-tool"))
if not (HARNESS_ROOT / "authority_context.py").exists():
    raise SystemExit(
        "Pinned Harness runtime not found. Set HARNESS_ROOT or checkout the pinned "
        "lehater/harness commit into .harness-tool."
    )

sys.path.insert(0, str(HARNESS_ROOT))
from authority_context import (  # noqa: E402
    build_authority_context,
    validate_extracted_references,
    validate_write_set,
)
from integration_alignment import validate_project_alignment  # noqa: E402


def load(path: str):
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path} must be a mapping")
    return value


def extract_canonical_references(
    context: dict,
    source_graph: dict,
) -> list[dict[str, str]]:
    """NAPMS-specific text/path extractor; Harness owns boundary validation."""
    canonical_paths = sorted(
        node["path"]
        for node in source_graph.get("nodes", [])
        if isinstance(node, dict) and isinstance(node.get("path"), str)
    )
    references: list[dict[str, str]] = []
    for owned in context.get("owned_artifacts", []):
        path = owned.get("path")
        if not path:
            continue
        text = (ROOT / path).read_text(encoding="utf-8")
        for candidate in canonical_paths:
            if candidate != path and candidate in text:
                references.append(
                    {
                        "artifact": owned["id"],
                        "referenced_path": candidate,
                    }
                )
    return references


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("authority")
    parser.add_argument(
        "--capability",
        action="append",
        dest="capabilities",
        required=True,
        help="Produced capability whose bounded context is being prepared; repeatable.",
    )
    parser.add_argument("--check-write", nargs="*")
    args = parser.parse_args()

    source = load("docs/canonical-graph.yaml")
    projection = load("docs/harness-projection.yaml")
    graph = load("docs/harness-engineering-graph.yaml")
    model = validate_project_alignment(
        source,
        projection,
        graph,
        target_consumer="BACKEND-IMPLEMENTATION",
    )["model"]

    context = build_authority_context(
        graph,
        model,
        args.authority,
        args.capabilities,
    )

    references = extract_canonical_references(context, source)
    validate_extracted_references(context, references)
    context["canonical_references"] = references

    if args.check_write is not None:
        context["validated_write_set"] = validate_write_set(
            context, args.check_write
        )

    print(json.dumps(context, indent=2, sort_keys=False))
    return 2 if context["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
