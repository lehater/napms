#!/usr/bin/env python3
from pathlib import Path
import argparse
import yaml

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "docs/canonical-graph.yaml"
HARNESS_PROJECTION = ROOT / "docs/harness-core.yaml"

def load():
    value = yaml.safe_load(GRAPH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit("canonical graph must be a mapping")
    return value

def validate_harness_projection(by_id):
    if not HARNESS_PROJECTION.exists():
        return 0

    value = yaml.safe_load(HARNESS_PROJECTION.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit("harness projection must be a mapping")
    if value.get("kind") != "harness-canonical-graph-projection":
        raise SystemExit("harness projection has unexpected kind")
    if value.get("source_graph") != "canonical-graph.yaml":
        raise SystemExit("harness projection must route through canonical-graph.yaml")

    authorities = value.get("authorities", [])
    authority_ids = [item.get("id") for item in authorities if isinstance(item, dict)]
    if (
        len(authority_ids) != len(authorities)
        or any(not item for item in authority_ids)
        or len(authority_ids) != len(set(authority_ids))
    ):
        raise SystemExit("harness projection authority IDs must be present and unique")
    authority_ids = set(authority_ids)

    bindings = value.get("bindings", [])
    if not isinstance(bindings, list) or not bindings:
        raise SystemExit("harness projection requires at least one binding")

    bound = {}
    capability_owner = {}
    for binding in bindings:
        if not isinstance(binding, dict):
            raise SystemExit("harness projection binding must be a mapping")
        if "path" in binding or "depends_on" in binding:
            raise SystemExit("harness projection must not copy path/depends_on routing metadata")
        artifact = binding.get("artifact")
        if not artifact or artifact in bound:
            raise SystemExit("harness projection binding artifact IDs must be present and unique")
        if artifact not in by_id:
            raise SystemExit(f"harness projection references unknown canonical node {artifact}")
        authority = binding.get("authority")
        if authority not in authority_ids:
            raise SystemExit(f"harness projection {artifact}: unknown authority {authority}")
        provides = binding.get("provides", []) or []
        if not isinstance(provides, list) or any(
            not isinstance(capability, str) or not capability for capability in provides
        ):
            raise SystemExit(f"harness projection {artifact}: invalid capability list")
        if len(provides) != len(set(provides)):
            raise SystemExit(f"harness projection {artifact}: duplicate capability")
        for capability in provides:
            previous = capability_owner.setdefault(capability, authority)
            if previous != authority:
                raise SystemExit(
                    f"harness projection capability {capability} spans authorities "
                    f"{previous} and {authority}"
                )
        bound[artifact] = authority

    questions = value.get("questions", []) or []
    if not isinstance(questions, list):
        raise SystemExit("harness projection questions must be a list")
    question_ids = set()
    for question in questions:
        if not isinstance(question, dict):
            raise SystemExit("harness projection question must be a mapping")
        question_id = question.get("id")
        if not question_id or question_id in question_ids:
            raise SystemExit("harness projection question IDs must be present and unique")
        question_ids.add(question_id)
        authority = question.get("authority")
        if authority not in authority_ids:
            raise SystemExit(f"harness projection question {question_id}: unknown authority {authority}")
        if not isinstance(question.get("text"), str) or not question.get("text"):
            raise SystemExit(f"harness projection question {question_id}: text is required")
        for artifact in question.get("blocks", []) or []:
            if artifact not in bound:
                raise SystemExit(
                    f"harness projection question {question_id}: unknown blocked artifact {artifact}"
                )
        resolution = question.get("resolution")
        if resolution is not None:
            if resolution not in bound:
                raise SystemExit(
                    f"harness projection question {question_id}: unknown resolution artifact {resolution}"
                )
            if bound[resolution] != authority:
                raise SystemExit(
                    f"harness projection question {question_id}: resolution authority mismatch"
                )

    return len(bindings)

def validate(graph):
    nodes = graph.get("nodes", [])
    ids = [node.get("id") for node in nodes]
    if None in ids or len(ids) != len(set(ids)):
        raise SystemExit("canonical graph node IDs must be present and unique")
    by_id = {node["id"]: node for node in nodes}
    paths = []
    for node in nodes:
        path = node.get("path")
        if not path or not (ROOT / path).exists():
            raise SystemExit(f"{node['id']}: missing path {path}")
        if path.startswith("docs/migration/revalidated/"):
            raise SystemExit(f"{node['id']}: current graph may not route through migration/revalidated")
        paths.append(path)
        for dep in node.get("depends_on", []):
            if dep not in by_id:
                raise SystemExit(f"{node['id']}: unknown dependency {dep}")
    if len(paths) != len(set(paths)):
        raise SystemExit("canonical graph paths must be unique owners")

    visiting, done = set(), set()
    def visit(node_id):
        if node_id in visiting:
            raise SystemExit(f"canonical graph cycle at {node_id}")
        if node_id in done:
            return
        visiting.add(node_id)
        for dep in by_id[node_id].get("depends_on", []):
            visit(dep)
        visiting.remove(node_id)
        done.add(node_id)
    for node_id in ids:
        visit(node_id)

    for projection in graph.get("projections", []):
        for source_id in projection.get("source_ids", []):
            if source_id not in by_id:
                raise SystemExit(f"projection {projection.get('id')}: unknown source {source_id}")
        for output in projection.get("outputs", []):
            if not output.startswith("docs-generated/"):
                raise SystemExit(f"projection {projection.get('id')}: output must be noncanonical docs-generated path")
    return by_id

def affected(by_id, start):
    if start not in by_id:
        raise SystemExit(f"unknown node {start}")
    reverse = {node_id: set() for node_id in by_id}
    for node_id, node in by_id.items():
        for dep in node.get("depends_on", []):
            reverse[dep].add(node_id)
    seen, queue = {start}, [start]
    while queue:
        current = queue.pop(0)
        for downstream in sorted(reverse[current]):
            if downstream not in seen:
                seen.add(downstream)
                queue.append(downstream)
    return [node_id for node_id in by_id if node_id in seen]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--affected")
    args = parser.parse_args()
    by_id = validate(load())
    binding_count = validate_harness_projection(by_id)
    print(f"canonical design graph PASS ({len(by_id)} nodes)")
    if binding_count:
        print(f"harness projection PASS ({binding_count} bindings)")
    if args.affected:
        print("affected:")
        for node_id in affected(by_id, args.affected):
            print(f"  - {node_id}: {by_id[node_id]['path']}")

if __name__ == "__main__":
    main()
