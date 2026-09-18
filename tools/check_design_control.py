#!/usr/bin/env python3
from pathlib import Path
import re
import yaml

ROOT=Path(__file__).resolve().parents[1]

def load(path):
    value=yaml.safe_load((ROOT/path).read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise SystemExit(f"{path}: expected mapping")
    return value

def fail(message):
    raise SystemExit(f"Design control check failed: {message}")

graph=load("docs/canonical-graph.yaml")
control=load("docs/spec/harness-control-plane.yaml")
pointer=load("docs/meta/current-workstream.yaml")
agents=(ROOT/"AGENTS.md").read_text(encoding="utf-8")
readme=(ROOT/"docs/README.md").read_text(encoding="utf-8")
makefile=(ROOT/"Makefile").read_text(encoding="utf-8")
workflow=(ROOT/".github/workflows/design.yml").read_text(encoding="utf-8")

if control.get("authority",{}).get("routing_graph")!="docs/canonical-graph.yaml":
    fail("control plane does not route through canonical graph")

required_removed={"serialized task capsules","per-artifact fingerprints","H-phase creation","gate transaction artifacts"}
actual_removed=set(control.get("normal_work",{}).get("do_not_require",[]))
if not required_removed<=actual_removed:
    fail(f"control plane does not remove ordinary ceremony: {sorted(required_removed-actual_removed)}")

for node in graph.get("nodes",[]):
    path=node.get("path","")
    if path.startswith("docs/migration/revalidated/") or path.startswith("docs-legacy/"):
        fail(f"current graph routes through historical evidence: {path}")

status=pointer.get("status")
if status=="ACTIVE":
    state=pointer.get("state")
    if not state or not (ROOT/state).exists():
        fail("active workstream pointer has no valid state")
elif status=="NONE":
    if pointer.get("normal_start")!="docs/canonical-graph.yaml":
        fail("idle workstream pointer must route normal work to canonical graph")
else:
    fail(f"unsupported current-workstream status: {status}")

for text,name in ((agents,"AGENTS.md"),(readme,"docs/README.md")):
    if "canonical-graph.yaml" not in text:
        fail(f"{name} does not route to canonical graph")
    if "current-workstream.yaml" not in text:
        fail(f"{name} does not route to workstream pointer")

def target_body(target):
    marker=target+":"
    start=makefile.find(marker)
    if start<0:
        fail(f"missing Make target {target}")
    tail=makefile[start+len(marker):]
    match=re.search(r"\n[A-Za-z0-9_.-]+:",tail)
    return tail[:match.start()] if match else tail

check_body=target_body("design-check")
sync_body=target_body("design-sync")
for required in ("check_canonical_graph.py","check_openapi_contract.py","check_persistence_model.py","check_design_control.py"):
    if required not in check_body:
        fail(f"design-check missing {required}")
for legacy in ("canonical-model-check","harness-check","docs-v2-harness-check","knowledge-check","check_cm"):
    if legacy in makefile:
        fail(f"obsolete Make target/reference remains: {legacy}")
for generator in ("generate_strategic_views.py","generate_resource_catalogue_views.py","generate_acc_view.py","generate_ad_view.py","generate_bc_view.py","generate_ap_view.py","generate_mvp_journey_view.py","generate_persistence_erd.py"):
    if generator not in sync_body:
        fail(f"design-sync missing {generator}")

for retired in (".github/workflows/harness.yml",".github/workflows/docs-v2-harness.yml",".github/workflows/knowledge.yml",".github/workflows/canonical-model-migration.yml"):
    if (ROOT/retired).exists():
        fail(f"retired workflow still active: {retired}")

if "make design-check" not in workflow:
    fail("design workflow does not run make design-check")

for path in sorted((ROOT/".agents/skills").glob("*/SKILL.md")):
    text=path.read_text(encoding="utf-8")
    for forbidden in ("docs/process/","make harness-check","make knowledge-check","active capsule","Implementation authorization: G4 PASS","REOPEN(S"):
        if forbidden in text:
            fail(f"{path.relative_to(ROOT)} still contains retired Harness instruction: {forbidden}")

print("Design control PASS")
