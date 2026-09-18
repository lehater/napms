#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
OLD_IMPL=ROOT/"docs/migration/revalidated/h19-mvp-implementation-readiness/s4/mvp-implementation-readiness.yaml"
OLD_TEST=ROOT/"docs/migration/revalidated/h19-mvp-implementation-readiness/s4/mvp-test-intent.yaml"
NEW_IMPL=ROOT/"docs/plans/first-mvp-implementation-readiness.yaml"
NEW_TEST=ROOT/"docs/plans/first-mvp-test-intent.yaml"

def load(p):
    with p.open(encoding="utf-8") as f:
        v=yaml.safe_load(f)
    if not isinstance(v,dict): raise SystemExit(f"{p}: expected mapping")
    return v

def fail(m): raise SystemExit(f"CM6 S4 migration failed: {m}")

oi=load(OLD_IMPL)
ot=load(OLD_TEST)
ni=load(NEW_IMPL)
nt=load(NEW_TEST)
if oi.get("status")!="ACCEPTED" or ot.get("status")!="ACCEPTED":
    fail("H19 source not ACCEPTED")
pi=oi["canonical_payload"]
for field in ("goal","implementation_boundary","module_contracts","vertical_sequence","frontend","implementation_slices","completion_definition","open_questions"):
    if ni.get(field)!=pi.get(field):
        fail(f"implementation field {field} differs")
if ni.get("implementation_authorization")!="NOT_GRANTED_BY_THIS_ARTIFACT":
    fail("readiness must not authorize implementation")
for p in ni.get("design_refs",{}).values():
    if not (ROOT/p).exists():
        fail(f"missing design ref {p}")

pt=ot["canonical_payload"]
for field in ("purpose","levels","required_scenarios"):
    if nt.get(field)!=pt.get(field):
        fail(f"test-intent field {field} differs")
if "canonical design graph" not in nt.get("trace_rule",""):
    fail("target trace rule must point to canonical design graph")
for p in nt.get("design_refs",{}).values():
    if not (ROOT/p).exists():
        fail(f"missing test design ref {p}")

print("CM6 stable S4 owner equivalence PASS")
