#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
S1=ROOT/"docs/migration/revalidated/h17-mvp-journey/s1/mvp-vendor-neutral-policy-export.yaml"
S2=ROOT/"docs/migration/revalidated/h17-mvp-journey/s2/tactical/mvp-journey-domain-model.yaml"
TARGET=ROOT/"docs/model/use-cases/first-mvp-policy-export.yaml"

def load(p):
    with p.open(encoding="utf-8") as f:
        v=yaml.safe_load(f)
    if not isinstance(v,dict):
        raise SystemExit(f"{p}: expected mapping")
    return v

def fail(m):
    raise SystemExit(f"CM4 MVP journey equivalence failed: {m}")

s1=load(S1)
s2=load(S2)
tgt=load(TARGET)
if s1.get("status")!="ACCEPTED" or s2.get("status")!="ACCEPTED":
    fail("H17 source not ACCEPTED")

p1=s1["canonical_payload"]
for field in (
    "goal","journey","participating_strategic_owners","supporting_owner",
    "workflow_composition","required_semantics","output_row_minimum",
    "non_goals","acceptance_examples"
):
    if tgt.get(field)!=p1.get(field):
        fail(f"S1 field {field} differs")

p2=s2["canonical_payload"]
for field in ("cross_context_flow","materialization_join","explicit_deferrals"):
    if tgt.get(field)!=p2.get(field):
        fail(f"S2 field {field} differs")

if tgt["workflow_composition"].get("peer_bounded_context") is not False:
    fail("workflow composition must remain non-peer")

expected_refs={
  "Resource Catalogue":"docs/model/contexts/resource-catalogue/domain-model.yaml",
  "Application Communication Catalogue":"docs/model/contexts/application-communication-catalogue/domain-model.yaml",
  "Application Deployment":"docs/model/contexts/application-deployment/domain-model.yaml",
  "Business Connectivity":"docs/model/contexts/business-connectivity/domain-model.yaml",
  "Access Policy":"docs/model/contexts/access-policy/domain-model.yaml",
  "Authority Management":"docs/model/contexts/authority-management/language.yaml",
}
if tgt.get("context_model_refs")!=expected_refs:
    fail("context model refs differ")
for rel in list(expected_refs.values())+list(tgt.get("strategic_refs",{}).values()):
    if not (ROOT/rel).exists():
        fail(f"missing target dependency {rel}")

allowed={
 "version","kind","id","goal","journey","participating_strategic_owners",
 "supporting_owner","workflow_composition","required_semantics","output_row_minimum",
 "non_goals","acceptance_examples","cross_context_flow","materialization_join",
 "explicit_deferrals","context_model_refs","strategic_refs"
}
extra=set(tgt)-allowed
if extra:
    fail(f"unexpected fields: {sorted(extra)}")
print("CM4 MVP journey equivalence PASS")
