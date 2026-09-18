#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]

def load(path):
    value=yaml.safe_load((ROOT/path).read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise SystemExit(f"{path}: expected mapping")
    return value

def fail(message):
    raise SystemExit(f"CM6 Harness simplification failed: {message}")

graph=load("docs/canonical-graph.yaml")
control=load("docs/spec/harness-control-plane.yaml")
pointer=load("docs/meta/current-workstream.yaml")
agents=(ROOT/"AGENTS.md").read_text(encoding="utf-8")
readme=(ROOT/"docs/README.md").read_text(encoding="utf-8")
makefile=(ROOT/"Makefile").read_text(encoding="utf-8")
workflow=(ROOT/".github/workflows/design.yml").read_text(encoding="utf-8")

if control.get("authority",{}).get("routing_graph")!="docs/canonical-graph.yaml":
    fail("control plane does not route through canonical graph")
if control.get("normal_work",{}).get("do_not_require") is None:
    fail("control plane does not explicitly remove ordinary ceremony")
for forbidden in ("serialized task capsules","per-artifact fingerprints","H-phase creation","gate transaction artifacts"):
    if forbidden not in control["normal_work"]["do_not_require"]:
        fail(f"missing do-not-require rule: {forbidden}")

for node in graph.get("nodes",[]):
    path=node.get("path","")
    if path.startswith("docs/migration/revalidated/") or path.startswith("docs-legacy/"):
        fail(f"current graph routes through historical evidence: {path}")

if pointer.get("state")!="docs/meta/canonical-model-migration/workstream-state.yaml":
    fail("active migration pointer differs")
for text,name in ((agents,"AGENTS.md"),(readme,"docs/README.md")):
    if "docs/canonical-graph.yaml" not in text and "canonical-graph.yaml" not in text:
        fail(f"{name} does not route to canonical graph")
    if "docs/meta/current-workstream.yaml" not in text and "meta/current-workstream.yaml" not in text:
        fail(f"{name} does not route to workstream pointer")

def target_body(target):
    marker=target+":"
    start=makefile.find(marker)
    if start<0: fail(f"missing Make target {target}")
    tail=makefile[start+len(marker):]
    next_target=len(tail)
    import re
    m=re.search(r"\n[A-Za-z0-9_.-]+:",tail)
    if m: next_target=m.start()
    return tail[:next_target]

check_body=target_body("design-check")
sync_body=target_body("design-sync")
if "check_canonical_graph.py" not in check_body:
    fail("design-check does not validate canonical graph")
if "check_cm" in check_body or "migration/revalidated" in check_body:
    fail("design-check still depends on migration equivalence")
for generator in ("generate_strategic_views.py","generate_resource_catalogue_views.py","generate_acc_view.py","generate_ad_view.py","generate_bc_view.py","generate_ap_view.py","generate_mvp_journey_view.py","generate_persistence_erd.py"):
    if generator not in sync_body:
        fail(f"design-sync missing {generator}")

if "make design-check" not in workflow:
    fail("design workflow does not use normal design-check")

print("CM6 Harness simplification PASS")
