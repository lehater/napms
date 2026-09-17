#!/usr/bin/env python3
from __future__ import annotations

import re
import textwrap
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
STRATEGIC_DIR = ROOT / "docs" / "migration" / "revalidated" / "h16-strategic" / "s2" / "strategic"
CAPABILITY_MAP = STRATEGIC_DIR / "capability-map.yaml"
CONTEXT_RELATIONSHIPS = STRATEGIC_DIR / "context-relationships.yaml"
GENERATED_DIR = ROOT / "docs-generated" / "architecture"
CONTEXT_MAP_OUTPUT = GENERATED_DIR / "context-map.puml"
COLLABORATION_MAP_OUTPUT = GENERATED_DIR / "strategic-collaboration-map.puml"


def load_accepted_payload(path: Path, expected_type: str) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("status") != "ACCEPTED":
        raise ValueError(f"{path}: projection source must have status ACCEPTED")
    if data.get("type_id") != expected_type:
        raise ValueError(f"{path}: expected type_id {expected_type!r}, got {data.get('type_id')!r}")
    payload = data.get("canonical_payload")
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: canonical_payload must be a mapping")
    return payload


def plantuml_alias(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return f"node_{slug}"


def plantuml_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def wrapped_lines(value: str, width: int = 78) -> list[str]:
    return textwrap.wrap(
        value,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [""]


def load_strategic_model() -> tuple[list[str], list[str], list[dict[str, str]]]:
    capability_payload = load_accepted_payload(CAPABILITY_MAP, "capability-map")
    relationship_payload = load_accepted_payload(CONTEXT_RELATIONSHIPS, "context-relationship-map")

    capabilities = capability_payload.get("capabilities", [])
    peer_cluster = next(
        (
            cluster
            for cluster in capability_payload.get("clustering", [])
            if cluster.get("cluster_id") == "CLUSTER-PEER-BOUNDED-CONTEXTS"
        ),
        None,
    )
    if peer_cluster is None:
        raise ValueError(f"{CAPABILITY_MAP}: missing CLUSTER-PEER-BOUNDED-CONTEXTS")

    capability_by_id = {item["capability_id"]: item for item in capabilities}
    peer_names: list[str] = []
    for capability_id in peer_cluster.get("capability_ids", []):
        if capability_id not in capability_by_id:
            raise ValueError(f"{CAPABILITY_MAP}: cluster references unknown capability {capability_id}")
        peer_names.append(capability_by_id[capability_id]["name"])

    composition_names = [item["id"] for item in capability_payload.get("non_peer_compositions", [])]
    known_nodes = set(peer_names) | set(composition_names)
    relationships = relationship_payload.get("relationships", [])

    normalized_relationships: list[dict[str, str]] = []
    for relationship in relationships:
        source = relationship.get("from")
        target = relationship.get("to")
        semantics = relationship.get("semantics")
        if not isinstance(source, str) or not isinstance(target, str) or not isinstance(semantics, str):
            raise ValueError(f"{CONTEXT_RELATIONSHIPS}: every relationship requires string from/to/semantics")
        for endpoint_name, endpoint_value in (("from", source), ("to", target)):
            if endpoint_value not in known_nodes:
                raise ValueError(
                    f"{CONTEXT_RELATIONSHIPS}: relationship {endpoint_name} endpoint {endpoint_value!r} "
                    "is not declared by the accepted capability map"
                )
        normalized_relationships.append({"from": source, "to": target, "semantics": semantics})

    return peer_names, composition_names, normalized_relationships


def projection_header() -> list[str]:
    return [
        "' GENERATED FILE - DO NOT EDIT",
        "' Projection only; semantic authority remains in the accepted S2 anchors below.",
        f"' Source: {CAPABILITY_MAP.relative_to(ROOT).as_posix()}",
        f"' Source: {CONTEXT_RELATIONSHIPS.relative_to(ROOT).as_posix()}",
    ]


def diagram_prelude(title: str) -> list[str]:
    return [
        "@startuml",
        f"title {title}",
        "left to right direction",
        "skinparam shadowing false",
        "skinparam roundcorner 12",
        "skinparam ArrowColor #5b6573",
        "skinparam rectangle {",
        "  BorderColor #2f5597",
        "  FontColor #1f2937",
        "}",
        "",
    ]


def append_relationship_legend(
    lines: list[str],
    relationships: list[dict[str, str]],
    *,
    include_composition_notation: bool,
) -> None:
    lines.extend(["", "legend bottom", "  <b>Notation</b>", "  Blue = peer Bounded Context"])
    if include_composition_notation:
        lines.append("  Grey = non-peer composition")
    lines.extend(
        [
            "  Arrows show accepted collaboration direction; no DDD Context Mapping pattern is inferred.",
            "",
            "  <b>Relationships</b>",
        ]
    )
    for relationship in relationships:
        lines.append(f"  {relationship['from']} -> {relationship['to']}")
        for semantic_line in wrapped_lines(relationship["semantics"]):
            lines.append(f"    {semantic_line}")
    lines.append("endlegend")


def render_context_map(
    peer_names: list[str], relationships: list[dict[str, str]]
) -> str:
    peer_set = set(peer_names)
    peer_relationships = [
        relationship
        for relationship in relationships
        if relationship["from"] in peer_set and relationship["to"] in peer_set
    ]

    lines = projection_header() + diagram_prelude("NAPMS DDD Context Map")
    for name in peer_names:
        lines.append(f'rectangle "{plantuml_text(name)}" as {plantuml_alias(name)} #dbeafe')

    lines.append("")
    for relationship in peer_relationships:
        lines.append(
            f"{plantuml_alias(relationship['from'])} --> {plantuml_alias(relationship['to'])}"
        )

    append_relationship_legend(lines, peer_relationships, include_composition_notation=False)
    lines.extend(["", "@enduml", ""])
    return "\n".join(lines)


def render_collaboration_map(
    peer_names: list[str],
    composition_names: list[str],
    relationships: list[dict[str, str]],
) -> str:
    lines = projection_header() + diagram_prelude("NAPMS Strategic Collaboration Map")
    for name in peer_names:
        lines.append(f'rectangle "{plantuml_text(name)}" as {plantuml_alias(name)} #dbeafe')

    if composition_names:
        lines.append("")
        for name in composition_names:
            lines.append(f'rectangle "{plantuml_text(name)}" as {plantuml_alias(name)} #f3f4f6')

    lines.append("")
    for relationship in relationships:
        lines.append(
            f"{plantuml_alias(relationship['from'])} --> {plantuml_alias(relationship['to'])}"
        )

    append_relationship_legend(lines, relationships, include_composition_notation=True)
    lines.extend(["", "@enduml", ""])
    return "\n".join(lines)


def main() -> int:
    peer_names, composition_names, relationships = load_strategic_model()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    projections = {
        CONTEXT_MAP_OUTPUT: render_context_map(peer_names, relationships),
        COLLABORATION_MAP_OUTPUT: render_collaboration_map(
            peer_names, composition_names, relationships
        ),
    }
    for path, content in projections.items():
        path.write_text(content, encoding="utf-8")
        print(f"generated {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
