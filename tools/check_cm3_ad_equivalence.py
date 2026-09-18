#!/usr/bin/env python3
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"docs/migration/revalidated/h17-mvp-journey/s2/tactical/mvp-journey-domain-model.yaml"
TARGET=ROOT/"docs/model/contexts/application-deployment/domain-model.yaml"
STRATEGIC=ROOT/"docs/model/strategic/bounded-contexts.yaml"
def load(p):
    with p.open(encoding="utf-8") as f: v=yaml.safe_load(f)
    if not isinstance(v,dict): raise SystemExit(f"{p}: expected mapping")
    return v
def fail(m): raise SystemExit(f"CM3 AD equivalence failed: {m}")
src=load(SOURCE); tgt=load(TARGET); strategic=load(STRATEGIC)
if src.get("status")!="ACCEPTED": fail("H17 source not ACCEPTED")
part=src["canonical_payload"]["participating_contexts"]["Application Deployment"]
for field in ("aggregate","invariants","public_semantics"):
    if tgt.get(field)!=part.get(field): fail(f"{field} differs")
if tgt.get("bounded_context_ref")!="BC-APPLICATION-DEPLOYMENT": fail("target BC ref differs")
if tgt["bounded_context_ref"] not in {x["context_id"] for x in strategic["contexts"]}: fail("strategic AD owner missing")
extra=set(tgt)-{"version","kind","id","bounded_context_ref","aggregate","invariants","public_semantics"}
if extra: fail(f"unexpected fields: {sorted(extra)}")
print("CM3 Application Deployment equivalence PASS")
