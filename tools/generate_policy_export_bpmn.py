#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/model/processes/policy-export-process.yaml"
OUT = ROOT / "docs-generated/process/policy-export.bpmn"

BPMN = "http://www.omg.org/spec/BPMN/20100524/MODEL"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
ET.register_namespace("bpmn", BPMN)
ET.register_namespace("xsi", XSI)


def q(name: str) -> str:
    return f"{{{BPMN}}}{name}"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def load_process() -> dict:
    value = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "process source must be a mapping")
    require(value.get("kind") == "application-process", "unsupported process kind")
    require(value.get("status") == "CURRENT", "process source must be CURRENT")
    return value


def validate_source(model: dict) -> None:
    activities = model.get("activities") or []
    require(activities, "process must define activities")
    ids = [item.get("id") for item in activities]
    require(None not in ids and len(ids) == len(set(ids)), "activity ids must be present and unique")
    activity_ids = set(ids)

    boundary = model.get("instance_boundary") or {}
    for key in ("starts_with", "success_completion", "rejected_completion"):
        require(boundary.get(key) in activity_ids, f"{key} must reference an activity")

    relations = model.get("causal_relations") or []
    allowed = {"control-precedence", "guarded-alternative"}
    for relation in relations:
        require(relation.get("type") in allowed, f"unsupported causal relation: {relation.get('type')}")
        require(relation.get("from") in activity_ids, "relation source must be an activity")
        require(relation.get("to") in activity_ids, "relation target must be an activity")
        if relation["type"] == "guarded-alternative":
            require(bool(relation.get("guard")), "guarded alternative requires guard")

    applicability = model.get("applicability") or {}
    for key in ("waits", "timers", "parallel_branches", "convergence", "compensation"):
        require(
            applicability.get(key) == "NOT_APPLICABLE",
            f"BPMN v0 projection does not support applicable {key}; projection must fail closed",
        )
    require(
        (applicability.get("independent_process_state") or {}).get("status") == "NOT_APPLICABLE",
        "BPMN v0 projection does not support independent process state",
    )

    guarded = defaultdict(list)
    for relation in relations:
        if relation["type"] == "guarded-alternative":
            guarded[relation["from"]].append(relation)
    for source, branches in guarded.items():
        require(len(branches) >= 2, f"guarded source {source} requires at least two alternatives")


def render(model: dict) -> str:
    validate_source(model)

    definitions = ET.Element(
        q("definitions"),
        {
            "id": "Definitions_NAPMS_PolicyExport",
            "targetNamespace": "https://github.com/lehater/napms/process/policy-export",
        },
    )
    process = ET.SubElement(
        definitions,
        q("process"),
        {
            "id": model["id"].replace("-", "_"),
            "name": "Policy Export",
            "isExecutable": "false",
        },
    )
    ET.SubElement(
        process,
        q("documentation"),
    ).text = (
        "Generated projection from docs/model/processes/policy-export-process.yaml. "
        "This BPMN file contains no independent project truth."
    )

    activities = {item["id"]: item for item in model["activities"]}
    boundary = model["instance_boundary"]

    start = ET.SubElement(
        process,
        q("startEvent"),
        {"id": "START", "name": "Policy export invocation"},
    )

    for activity_id, activity in activities.items():
        tag = "userTask" if activity.get("participant") == "USER" else "task"
        node = ET.SubElement(
            process,
            q(tag),
            {"id": activity_id.replace("-", "_"), "name": activity_id},
        )
        ET.SubElement(node, q("documentation")).text = activity.get("responsibility", "")

    guarded = defaultdict(list)
    plain = []
    for relation in model["causal_relations"]:
        if relation["type"] == "guarded-alternative":
            guarded[relation["from"]].append(relation)
        else:
            plain.append(relation)

    gateways = {}
    for source in sorted(guarded):
        gateway_id = f"GW_{source.replace('-', '_')}"
        gateways[source] = gateway_id
        ET.SubElement(
            process,
            q("exclusiveGateway"),
            {"id": gateway_id, "name": f"{source} outcome"},
        )

    flows: list[tuple[str, str, str | None, str | None]] = []
    flows.append(("START", boundary["starts_with"].replace("-", "_"), None, None))

    for relation in plain:
        flows.append(
            (
                relation["from"].replace("-", "_"),
                relation["to"].replace("-", "_"),
                None,
                None,
            )
        )

    for source, branches in guarded.items():
        source_id = source.replace("-", "_")
        gateway_id = gateways[source]
        flows.append((source_id, gateway_id, None, None))
        for branch in branches:
            flows.append(
                (
                    gateway_id,
                    branch["to"].replace("-", "_"),
                    branch["guard"],
                    branch["guard"],
                )
            )

    success_id = boundary["success_completion"].replace("-", "_")
    rejected_id = boundary["rejected_completion"].replace("-", "_")
    ET.SubElement(process, q("endEvent"), {"id": "END_SUCCESS", "name": "Export exposed"})
    ET.SubElement(process, q("endEvent"), {"id": "END_REJECTED", "name": "Export rejected"})
    flows.append((success_id, "END_SUCCESS", None, None))
    flows.append((rejected_id, "END_REJECTED", None, None))

    for index, (source, target, name, expression) in enumerate(flows, start=1):
        attrs = {"id": f"FLOW_{index}", "sourceRef": source, "targetRef": target}
        if name:
            attrs["name"] = name
        flow = ET.SubElement(process, q("sequenceFlow"), attrs)
        if expression:
            condition = ET.SubElement(
                flow,
                q("conditionExpression"),
                {f"{{{XSI}}}type": "bpmn:tFormalExpression"},
            )
            condition.text = expression

    ET.indent(definitions, space="  ")
    return ET.tostring(definitions, encoding="unicode", xml_declaration=True) + "\n"


def validate_projection(text: str) -> None:
    root = ET.fromstring(text)
    process = root.find(q("process"))
    require(process is not None, "generated BPMN has no process")
    require(process.get("isExecutable") == "false", "generated BPMN must be non-executable")

    forbidden = ["serviceTask", "messageFlow", "parallelGateway", "intermediateCatchEvent", "boundaryEvent", "callActivity"]
    for tag in forbidden:
        require(not process.findall(q(tag)), f"projection invented unsupported BPMN {tag}")

    require(len(process.findall(q("startEvent"))) == 1, "projection must have one start event")
    require(len(process.findall(q("exclusiveGateway"))) == 1, "projection must have one explicit guarded decision")
    require(len(process.findall(q("endEvent"))) == 2, "projection must preserve success and rejected completion")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    model = load_process()
    text = render(model)
    validate_projection(text)

    if args.check:
        with tempfile.TemporaryDirectory(prefix="napms-policy-export-bpmn-") as tmp:
            path = Path(tmp) / OUT.name
            path.write_text(text, encoding="utf-8")
            ET.parse(path)
            print(f"generated and validated {path}")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(text, encoding="utf-8")
        print(f"generated {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
