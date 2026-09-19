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
        return []
    data = load(ROOT / path)

    coverage = data.get("knowledge_coverage")
    if coverage is None:
        return []
    if not isinstance(coverage, dict):
        raise ValueError(f"{path}: knowledge_coverage must be a mapping")

    subject = coverage.get("subject")
    knowledge = coverage.get("knowledge")
    if not isinstance(subject, str) or not subject:
        raise ValueError(f"{path}: knowledge_coverage.subject is required")
    if not isinstance(knowledge, str) or not knowledge:
        raise ValueError(f"{path}: knowledge_coverage.knowledge is required")
    return [(subject, knowledge)]

def main():
    profile = load(MODEL)
    journey = load(ROOT / profile["sources"]["journey"])
    strategic = load(ROOT / profile["sources"]["strategic_contexts"])
    graph = load(ROOT / profile["sources"]["canonical_graph"])

    context_ids = {x["name"]: x["context_id"] for x in strategic["contexts"]}
    coverage_index = {}
    for node in graph["nodes"]:
        for coverage in coverage_for_node(node):
            coverage_index.setdefault(coverage, []).append(node)

    incomplete = []
    accepted_incomplete = []
    print("Engineering knowledge completeness")
    print("Profile:", profile["id"])
    for rule in profile["expectation_rules"]:
        source_key = rule["subjects_from"].split(".")[-1]
        subjects = list(journey.get(source_key, []))
        rows = []
        for subject in subjects:
            context_id = context_ids.get(subject)
            matches = coverage_index.get((context_id, rule["expects"]), [])
            status = "PRESENT" if matches else "MISSING"
            rows.append((subject, status, [n["id"] for n in matches]))
        present = sum(1 for _, s, _ in rows if s == "PRESENT")
        missing = sum(1 for _, s, _ in rows if s == "MISSING")
        policy = rule.get("status", "ACCEPTED")
        print(f"- {rule['id']} [{policy}]: PRESENT={present} MISSING={missing}")
        for subject, status, artifacts in rows:
            evidence = ",".join(artifacts) if artifacts else "-"
            print(f"  {status:7} {subject} [{evidence}]")
            if status == "MISSING":
                incomplete.append((rule["id"], policy, subject))
                if policy != "EXPERIMENTAL":
                    accepted_incomplete.append((rule["id"], subject))

    print("\nCompleteness result:", "INCOMPLETE" if accepted_incomplete else "COMPLETE")
    if incomplete:
        print("Missing derived knowledge:")
        for rule, policy, subject in incomplete:
            print(f"  {policy:12} {rule} :: {subject}")
    return 1 if accepted_incomplete else 0

if __name__ == "__main__":
    sys.exit(main())
