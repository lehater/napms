#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import textwrap
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
STRATEGIC_DIR = ROOT / "docs" / "migration" / "revalidated" / "h16-strategic" / "s2" / "strategic"
CAPABILITY_MAP = STRATEGIC_DIR / "capability-map.yaml"
CONTEXT_RELATIONSHIPS = STRATEGIC_DIR / "context-relationships.yaml"
CONTEXT_MAP_OUTPUT = ROOT / "docs-generated" / "architecture" / "context-map.puml"


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


def wrap_label(value: str, width: int = 44) -> str:
    return "\\n".join(
        textwrap.wrap(
            value,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def render_context_map() -> str:
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

    for relationship in relationships:
        for endpoint in ("from", "to"):
            name = relationship.get(endpoint)
            if name not in known_nodes:
                raise ValueError(
                    f"{CONTEXT_RELATIONSHIPS}: relationship {endpoint} endpoint {name!r} "
                    "is not declared by the accepted capability map"
                )

    lines = [
        "' GENERATED FILE - DO NOT EDIT",
        "' Projection only; semantic authority remains in the accepted S2 anchors below.",
        f"' Source: {CAPABILITY_MAP.relative_to(ROOT).as_posix()}",
        f"' Source: {CONTEXT_RELATIONSHIPS.relative_to(ROOT).as_posix()}",
        "@startuml",
        "title NAPMS DDD Context Map",
        "left to right direction",
        "skinparam shadowing false",
        "skinparam roundcorner 12",
        "skinparam ArrowColor #5b6573",
        "skinparam ArrowFontColor #3f4752",
        "skinparam ArrowFontSize 10",
        "skinparam rectangle {",
        "  BorderColor #2f5597",
        "  FontColor #1f2937",
        "}",
        "",
        "legend top left",
        "  |= Color |= Meaning |",
        "  |<#dbeafe> | Peer Bounded Context |",
        "  |<#f3f4f6> | Non-peer composition |",
        "endlegend",
        "",
    ]

    for name in peer_names:
        lines.append(
            f'rectangle "{plantuml_text(name)}" as {plantuml_alias(name)} #dbeafe'
        )

    if composition_names:
        lines.append("")
        for name in composition_names:
            lines.append(
                f'rectangle "{plantuml_text(name)}" as {plantuml_alias(name)} #f3f4f6'
            )

    lines.append("")
    for relationship in relationships:
        source = plantuml_alias(relationship["from"])
        target = plantuml_alias(relationship["to"])
        semantics = plantuml_text(wrap_label(relationship["semantics"]))
        lines.append(f'{source} --> {target} : {semantics}')

    lines.extend(["", "@enduml", ""])
    return "\n".join(lines)


def check_output(path: Path, expected: str) -> bool:
    if not path.exists():
        print(f"stale projection: {path.relative_to(ROOT)} does not exist", file=sys.stderr)
        return False
    actual = path.read_text(encoding="utf-8")
    if actual != expected:
        print(
            f"stale projection: {path.relative_to(ROOT)} does not match its canonical sources; "
            "run `make architecture-sync`",
            file=sys.stderr,
        )
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate non-canonical architecture views from accepted machine-readable design artifacts."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when committed generated views differ from canonical sources",
    )
    args = parser.parse_args()

    try:
        context_map = render_context_map()
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        print(f"architecture projection error: {exc}", file=sys.stderr)
        return 1

    if args.check:
        return 0 if check_output(CONTEXT_MAP_OUTPUT, context_map) else 1

    CONTEXT_MAP_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    CONTEXT_MAP_OUTPUT.write_text(context_map, encoding="utf-8")
    print(f"generated {CONTEXT_MAP_OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
