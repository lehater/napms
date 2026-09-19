#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "docs/engineering-knowledge-completeness.yaml"

def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def coverage_for_node(node):
    path = node["path"]
    if not path.endswith((".yaml", ".yml")):
        return None
    data = load(ROOT / path)
    coverage = data.get("knowledge_coverage")
    if not isinstance(coverage, dict):
        return None
    subject = coverage.get("subject")
    knowledge = coverage.get("knowledge")
    if not subject or not knowledge:
        return None
    return subject, knowledge

def main():
    cfg = load(MODEL)
    journey = load(ROOT / cfg["sources"]["journey"])
    graph = load(ROOT / cfg["sources"]["canonical_graph"])
    nodes = graph["nodes"]
    coverage_index = {}
    for node in nodes:
        coverage = coverage_for_node(node)
        if coverage:
            coverage_index.setdefault(coverage, []).append(node)

    errors = []
    incomplete = []
    print("Engineering knowledge completeness (derived)")
    for rule in cfg["rules"]:
        subjects = list(journey.get(rule["subjects_from"].split(".")[-1], []))
        supporting = []
        if rule.get("supporting_subjects_from"):
            supporting = list(journey.get(rule["supporting_subjects_from"].split(".")[-1], []))
        rows = []
        for subject in subjects:
            strategic = load(ROOT / cfg["sources"]["strategic_contexts"])
            context_id = next((x["context_id"] for x in strategic["contexts"] if x["name"] == subject), None)
            knowledge = "tactical-domain-model" if rule["coverage_kind"] == "tactical-domain-model" else "domain-use-case"
            matches = coverage_index.get((context_id, knowledge), [])
            status = "PRESENT" if matches else "MISSING"
            rows.append((subject, status, [n["id"] for n in matches]))
        for subject in supporting:
            strategic = load(ROOT / cfg["sources"]["strategic_contexts"])
            context_id = next((x["context_id"] for x in strategic["contexts"] if x["name"] == subject), None)
            matches = coverage_index.get((context_id, "tactical-domain-model"), [])
            status = "PRESENT" if matches else "MISSING"
            rows.append((subject, status, [n["id"] for n in matches]))
        present = sum(1 for _,s,_ in rows if s == "PRESENT")
        missing = sum(1 for _,s,_ in rows if s == "MISSING")
        print(f"- {rule['id']}: PRESENT={present} MISSING={missing}")
        for subject, status, artifacts in rows:
            evidence = ",".join(artifacts) if artifacts else "-"
            print(f"  {status:7} {subject} [{evidence}]")
            if status != "PRESENT":
                incomplete.append((rule["id"], subject))
    if errors:
        for e in errors: print("ERROR", e)
        return 2
    print("\nCompleteness result:", "INCOMPLETE" if incomplete else "COMPLETE")
    if incomplete:
        print("Missing derived knowledge:")
        for rule, subject in incomplete:
            print(f"  {rule} :: {subject}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
