#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "docs/engineering-knowledge-completeness.yaml"

def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def subject_for_node(node):
    path = node["path"]
    if not path.endswith((".yaml", ".yml")):
        return None
    data = load(ROOT / path)
    if node["kind"] == "use-case":
        owners = data.get("bounded_context") or data.get("owner") or data.get("context")
        if isinstance(owners, str):
            return owners
        # Current RC use-case is explicitly Resource Catalogue curation.
        if "resource-catalogue" in path:
            return "Resource Catalogue"
    if node["kind"] in {"tactical-domain-model", "domain-language"}:
        context = data.get("bounded_context") or data.get("context") or data.get("name")
        if isinstance(context, str):
            return context
        mapping = {
            "resource-catalogue": "Resource Catalogue",
            "authority-management": "Authority Management",
            "application-communication-catalogue": "Application Communication Catalogue",
            "application-deployment": "Application Deployment",
            "business-connectivity": "Business Connectivity",
            "access-policy": "Access Policy",
        }
        for token, subject in mapping.items():
            if token in path:
                return subject
    return None

def main():
    cfg = load(MODEL)
    journey = load(ROOT / cfg["sources"]["journey"])
    graph = load(ROOT / cfg["sources"]["canonical_graph"])
    nodes = graph["nodes"]
    by_kind = {}
    for node in nodes:
        by_kind.setdefault(node["kind"], []).append(node)

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
            matches = [n for n in by_kind.get(rule["coverage_kind"], []) if subject_for_node(n) == subject]
            status = "PRESENT" if matches else "MISSING"
            rows.append((subject, status, [n["id"] for n in matches]))
        for subject in supporting:
            kinds = rule.get("supporting_coverage_kinds", [rule["coverage_kind"]])
            matches = [n for kind in kinds for n in by_kind.get(kind, []) if subject_for_node(n) == subject]
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
