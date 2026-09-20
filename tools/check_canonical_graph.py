#!/usr/bin/env python3
from pathlib import Path
import argparse
import yaml

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "docs/canonical-graph.yaml"

def load():
    value = yaml.safe_load(GRAPH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit("canonical graph must be a mapping")
    return value

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
    print(f"canonical design graph PASS ({len(by_id)} nodes)")
    if args.affected:
        print("affected:")
        for node_id in affected(by_id, args.affected):
            print(f"  - {node_id}: {by_id[node_id]['path']}")

if __name__ == "__main__":
    main()
