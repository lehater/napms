#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/migration/revalidated/h17-mvp-journey/s2/tactical/mvp-journey-domain-model.yaml"
TARGET = ROOT / "docs/model/contexts/application-communication-catalogue/domain-model.yaml"
STRATEGIC = ROOT / "docs/model/strategic/bounded-contexts.yaml"

def load(path):
    with path.open(encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected YAML mapping")
    return value

def fail(msg):
    raise SystemExit(f"CM3 ACC equivalence failed: {msg}")

src = load(SOURCE)
tgt = load(TARGET)
strategic = load(STRATEGIC)
if src.get("status") != "ACCEPTED":
    fail("H17 tactical source is not ACCEPTED")
part = src["canonical_payload"]["participating_contexts"]["Application Communication Catalogue"]
expected = {k: v for k, v in part.items() if k != "strategic_anchor"}
for field in ("aggregate", "entities", "invariants", "public_semantics"):
    if tgt.get(field) != expected.get(field):
        fail(f"{field} differs from accepted H17 ACC payload")
if tgt.get("bounded_context_ref") != "BC-APPLICATION-COMMUNICATION-CATALOGUE":
    fail("target BC ref differs")
contexts = {x["context_id"]: x for x in strategic["contexts"]}
if tgt["bounded_context_ref"] not in contexts:
    fail("strategic ACC owner missing")
extra = set(tgt) - {"version","kind","id","bounded_context_ref","aggregate","entities","invariants","public_semantics"}
if extra:
    fail(f"unexpected fields may introduce non-source semantics: {sorted(extra)}")
print("CM3 Application Communication Catalogue equivalence PASS")
