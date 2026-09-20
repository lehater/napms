#!/usr/bin/env python3
from __future__ import annotations
import os, sys
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
HARNESS=Path(os.environ.get("HUMAN_PROJECTION_HARNESS", ROOT/".human-projection-harness"))
sys.path.insert(0,str(HARNESS))
from engineering_graph import evaluate_engineering_target
from human_projection import compile_manifest, validate_recipe
from integration_alignment import validate_project_alignment

def load(path):
    return yaml.safe_load((ROOT/path).read_text(encoding="utf-8"))

def main():
    source=load("docs/canonical-graph.yaml")
    projection=load("docs/harness-projection.yaml")
    graph=load("docs/harness-engineering-graph.yaml")

    aligned=validate_project_alignment(source,projection,graph,target_consumer="BACKEND-IMPLEMENTATION")
    model=aligned["model"]

    backend=compile_manifest(graph,model,"BACKEND-IMPLEMENTATION",harness_version="research-prototype",project_revision="napms-research",recipe_id="napms-backend-human-docs")
    assert backend["target"]["status"]=="COMPLETE", backend["target"]
    plan=validate_recipe(load("docs/research/human-projection/backend.yaml"),backend)
    assert [d["id"] for d in plan["documents"]]==[
        "overview","domain","architecture-and-interfaces","quality-and-operations","implementation-and-verification"
    ]
    assert len(backend["sources"])>10
    assert not backend["unresolved"]

    frontend=compile_manifest(graph,model,"FRONTEND-IMPLEMENTATION",harness_version="research-prototype",project_revision="napms-research")
    assert frontend["target"]["status"]=="READY", frontend["target"]
    unresolved={item["capability"] for item in frontend["unresolved"]}
    assert "engineering.frontend.human-interface" in unresolved, unresolved
    assert "engineering.frontend.human-interface" in frontend["target"]["create"], frontend["target"]

    # Existing project-local package generator remains benchmark/evidence during research.
    assert (ROOT/"tools/generate_human_context_package.py").is_file()

    print("NAPMS human projection research PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
