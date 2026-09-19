#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "docs/engineering-knowledge-completeness.yaml"
GRAPH = ROOT / "docs/canonical-graph.yaml"
VALID = {"PRESENT", "PARTIAL", "MISSING", "NOT_REQUIRED"}

def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def main():
    model, graph = load(MODEL), load(GRAPH)
    artifact_ids = {n["id"] for n in graph["nodes"]}
    errors, incomplete = [], []
    print("Engineering knowledge completeness")
    for expectation in model.get("expectations", []):
        eid = expectation["id"]
        required = expectation.get("required_subjects", [])
        coverage = expectation.get("coverage", {})
        if set(required) != set(coverage):
            errors.append(f"{eid}: required_subjects and coverage keys differ")
        present = partial = missing = 0
        for subject in required:
            item = coverage.get(subject, {})
            status = item.get("status")
            artifacts = item.get("artifacts", [])
            if status not in VALID:
                errors.append(f"{eid}/{subject}: invalid status {status!r}")
                continue
            unknown = [a for a in artifacts if a not in artifact_ids]
            if unknown:
                errors.append(f"{eid}/{subject}: unknown artifacts {unknown}")
            if status == "MISSING" and artifacts:
                errors.append(f"{eid}/{subject}: MISSING must not reference artifacts")
            if status in {"PRESENT", "PARTIAL"} and not artifacts:
                errors.append(f"{eid}/{subject}: {status} must reference evidence")
            if status == "PRESENT": present += 1
            elif status == "PARTIAL": partial += 1
            elif status == "MISSING": missing += 1
            if status != "PRESENT":
                incomplete.append((eid, subject, status))
        print(f"- {eid}: PRESENT={present} PARTIAL={partial} MISSING={missing}")
        for excluded in expectation.get("excluded_subjects", []):
            if not excluded.get("reason"):
                errors.append(f"{eid}/{excluded.get('subject')}: exclusion requires reason")
    if errors:
        print("\nStructural errors:")
        for error in errors: print("  ERROR", error)
        return 2
    if incomplete:
        print("\nIncomplete knowledge:")
        for eid, subject, status in incomplete:
            print(f"  {status:7} {eid} :: {subject}")
        print("\nCompleteness result: INCOMPLETE (diagnostic pilot; semantic review remains human)")
    else:
        print("\nCompleteness result: COMPLETE")
    return 0

if __name__ == "__main__":
    sys.exit(main())
