#!/usr/bin/env python3
from pathlib import Path
import argparse
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_PATH = ROOT / "docs/model/contexts/resource-catalogue/domain-model.yaml"
PROCESS_PATH = ROOT / "docs/model/contexts/resource-catalogue/process-model.yaml"
DEFAULT_OUT = ROOT / "docs-generated/architecture"

def load(path):
    with path.open(encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected YAML mapping")
    return value

def alias(value):
    return "".join(ch if ch.isalnum() else "_" for ch in str(value))

def esc(value):
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

def header(title, source):
    return [
        "@startuml",
        "' GENERATED FILE - DO NOT EDIT",
        f"' Semantic authority: {source.relative_to(ROOT)}",
        f"title {title}",
        "skinparam shadowing false",
    ]

def render_domain(model):
    lines = header("Resource Catalogue Domain Model", DOMAIN_PATH)
    aggregate = model["aggregates"][0]
    root_id = aggregate["root_entity_ref"]
    lines.append(f'package "{esc(aggregate["name"])} aggregate" {{')
    for entity in model["entities"]:
        stereo = " <<Aggregate Root>>" if entity["entity_id"] == root_id else " <<Entity>>"
        lines.append(f'  class "{esc(entity["name"])}" as {alias(entity["entity_id"])}{stereo}')
    for vo in model["value_objects"]:
        lines.append(f'  class "{esc(vo["name"])}" as {alias(vo["value_object_id"])} <<Value Object>>')
    lines.append("}")
    lines.append("")
    for entity in model["entities"]:
        if entity.get("owner_aggregate_ref") == aggregate["aggregate_id"]:
            lines.append(f'{alias(root_id)} *-- {alias(entity["entity_id"])}')
        for attr in entity.get("attributes", []):
            match = next((vo for vo in model["value_objects"] if vo["name"] == attr), None)
            if match:
                lines.append(f'{alias(entity["entity_id"])} --> {alias(match["value_object_id"])} : {esc(attr)}')
    root = next(e for e in model["entities"] if e["entity_id"] == root_id)
    identity = root.get("identity")
    if identity:
        match = next((vo for vo in model["value_objects"] if vo["name"] == identity), None)
        if match:
            lines.append(f'{alias(root_id)} --> {alias(match["value_object_id"])} : identity')
    lines.extend(["", "legend left", "  |= Invariant |= Rule |"])
    for inv in model["invariants"]:
        lines.append(f'  | {esc(inv["invariant_id"])} | {esc(inv["rule"])} |')
    lines.extend([
        "  Diagram links only explicit aggregate ownership and exact value-object attribute/identity references.",
        "endlegend",
        "@enduml",
        "",
    ])
    return "\n".join(lines)

def kind_map(model):
    result = {}
    for p in model["policies"]:
        result[p["policy_id"]] = ("policy", p["name"])
    for c in model["commands"]:
        result[c["command_id"]] = ("command", c["name"])
    for e in model["domain_events"]:
        result[e["event_id"]] = ("event", e["name"])
    for raw in ("read-resource", "derive-current-projection", "expose-resource-ref"):
        result[raw] = ("action", raw)
    return result

def render_process(model):
    items = kind_map(model)
    lines = header("Resource Catalogue Curation Process", PROCESS_PATH)
    lines.append("start")
    flow_number = 0
    for flow in model["process_flows"]:
        flow_number += 1
        lines.append(f':FLOW {flow_number} — {esc(flow["name"])};')
        paths = [flow["sequence"]] if "sequence" in flow else flow.get("alternatives", [])
        for idx, path in enumerate(paths, start=1):
            if len(paths) > 1:
                lines.append(f':Alternative {idx};')
            for ref in path:
                kind, name = items.get(ref, ("action", ref))
                lines.append(f':[{kind}] {esc(name)};')
    lines.extend([
        "stop",
        "legend left",
        "  Rendering follows explicit process_flows only.",
        "  Policies remain visible and are not collapsed into command/event causality.",
        "endlegend",
        "@enduml",
        "",
    ])
    return "\n".join(lines)

def write_views(output):
    domain = load(DOMAIN_PATH)
    process = load(PROCESS_PATH)
    output.mkdir(parents=True, exist_ok=True)
    views = {
        "resource-catalogue-domain.puml": render_domain(domain),
        "resource-catalogue-process.puml": render_process(process),
    }
    for name, content in views.items():
        path = output / name
        path.write_text(content, encoding="utf-8")
        try:
            shown = path.relative_to(ROOT)
        except ValueError:
            shown = path
        print(f"generated {shown}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="napms-rc-views-") as tmp:
            write_views(Path(tmp))
    else:
        write_views(DEFAULT_OUT)

if __name__ == "__main__":
    main()
