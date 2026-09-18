#!/usr/bin/env python3
from pathlib import Path
import argparse
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
CAP_PATH = ROOT / "docs/model/strategic/capabilities.yaml"
BC_PATH = ROOT / "docs/model/strategic/bounded-contexts.yaml"
REL_PATH = ROOT / "docs/model/strategic/context-relationships.yaml"
DEFAULT_OUT = ROOT / "docs-generated/architecture"

def load(path):
    with path.open(encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected YAML mapping")
    return value

def alias(name):
    return "".join(ch if ch.isalnum() else "_" for ch in name)

def q(value):
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

def header(title):
    return [
        "@startuml",
        "' GENERATED FILE - DO NOT EDIT",
        "' Semantic authority:",
        f"'   {CAP_PATH.relative_to(ROOT)}",
        f"'   {BC_PATH.relative_to(ROOT)}",
        f"'   {REL_PATH.relative_to(ROOT)}",
        f"title {title}",
        "skinparam shadowing false",
        "skinparam componentStyle rectangle",
    ]

def context_map(caps, bcs, rels):
    peer = {c["name"] for c in bcs["contexts"]}
    lines = header("NAPMS Domain Context Map")
    for ctx in bcs["contexts"]:
        lines.append(f'rectangle "{q(ctx["name"])}" as {alias(ctx["name"])} <<Bounded Context>>')
    lines.append("")
    index = 1
    legend = []
    for rel in rels["whole_domain_relationships"]:
        if rel["from"] in peer and rel["to"] in peer:
            lines.append(f'{alias(rel["from"])} --> {alias(rel["to"])} : [{index}]')
            legend.append((index, rel["semantics"]))
            index += 1
    for rel in rels["context_mapping_relationships"]:
        label = "U → D"
        if rel.get("patterns"):
            label += " / " + ", ".join(rel["patterns"])
        lines.append(f'{alias(rel["from"])} --> {alias(rel["to"])} : [{index}] {q(label)}')
        legend.append((index, rel["semantics"]))
        index += 1
    lines.extend(["", "legend left", "  |= # |= Semantics |"])
    for number, semantics in legend:
        lines.append(f"  | {number} | {q(semantics)} |")
    lines.extend([
        "  Peer BC relationships only. Non-peer compositions are intentionally excluded.",
        "  Generic whole-domain arrows are not promoted to named DDD patterns.",
        "endlegend",
        "@enduml",
        "",
    ])
    return "\n".join(lines)

def collaboration_map(caps, bcs, rels):
    peer = {c["name"] for c in bcs["contexts"]}
    compositions = {x["id"] for x in caps["non_peer_compositions"]}
    lines = header("NAPMS Strategic Collaboration Map")
    for ctx in bcs["contexts"]:
        lines.append(f'rectangle "{q(ctx["name"])}" as {alias(ctx["name"])} <<Bounded Context>>')
    for item in caps["non_peer_compositions"]:
        lines.append(f'rectangle "{q(item["id"])}" as {alias(item["id"])} <<Non-peer composition>>')
    lines.append("")
    index = 1
    legend = []
    for rel in rels["whole_domain_relationships"]:
        if rel["from"] not in peer | compositions or rel["to"] not in peer | compositions:
            raise SystemExit(f"unknown relationship endpoint: {rel}")
        lines.append(f'{alias(rel["from"])} --> {alias(rel["to"])} : [{index}]')
        legend.append((index, rel["semantics"]))
        index += 1
    for rel in rels["context_mapping_relationships"]:
        lines.append(f'{alias(rel["from"])} --> {alias(rel["to"])} : [{index}] U → D')
        legend.append((index, rel["semantics"]))
        index += 1
    lines.extend(["", "legend left", "  |= # |= Semantics |"])
    for number, semantics in legend:
        lines.append(f"  | {number} | {q(semantics)} |")
    lines.extend([
        "  Non-peer compositions are review nodes, not Bounded Contexts.",
        "endlegend",
        "@enduml",
        "",
    ])
    return "\n".join(lines)

def write_views(output):
    caps = load(CAP_PATH)
    bcs = load(BC_PATH)
    rels = load(REL_PATH)
    output.mkdir(parents=True, exist_ok=True)
    views = {
        "context-map.puml": context_map(caps, bcs, rels),
        "strategic-collaboration-map.puml": collaboration_map(caps, bcs, rels),
    }
    for name, content in views.items():
        path = output / name
        path.write_text(content, encoding="utf-8")
        print(f"generated {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="napms-strategic-views-") as tmp:
            write_views(Path(tmp))
    else:
        write_views(DEFAULT_OUT)

if __name__ == "__main__":
    main()
