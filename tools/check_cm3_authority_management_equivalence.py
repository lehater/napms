#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = ROOT / "docs/migration/revalidated/h12-rc-curation/s2/strategic/domain-glossary.yaml"
H17 = ROOT / "docs/migration/revalidated/h17-mvp-journey/s2/tactical/mvp-journey-domain-model.yaml"
TARGET = ROOT / "docs/model/contexts/authority-management/language.yaml"
STRATEGIC = ROOT / "docs/model/strategic/bounded-contexts.yaml"
TACTICAL_TARGET = ROOT / "docs/model/contexts/authority-management/domain-model.yaml"

def load(path):
    with path.open(encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected YAML mapping")
    return value

def fail(message):
    raise SystemExit(f"CM3 Authority Management equivalence failed: {message}")

glossary = load(GLOSSARY)
h17 = load(H17)
target = load(TARGET)
strategic = load(STRATEGIC)

if glossary.get("status") != "ACCEPTED":
    fail("shared H12 glossary is not ACCEPTED")
if (glossary.get("validation") or {}).get("freshness") != "CURRENT":
    fail("shared H12 glossary is not CURRENT")
if h17.get("status") != "ACCEPTED":
    fail("H17 tactical source is not ACCEPTED")

am_terms = []
for term in glossary["canonical_payload"]["terms"]:
    if term["context_ref"]["anchor_id"] == "NAPMS-S2-BC-AUTHORITY-MANAGEMENT":
        am_terms.append({k: v for k, v in term.items() if k != "context_ref"})
if target.get("terms") != am_terms:
    fail("Authority Management language differs from accepted AM-owned glossary terms")

contexts = {x["context_id"]: x for x in strategic.get("contexts", [])}
if target.get("bounded_context_ref") != "BC-AUTHORITY-MANAGEMENT":
    fail("target language does not reference strategic Authority Management owner")
if "BC-AUTHORITY-MANAGEMENT" not in contexts:
    fail("strategic Authority Management owner is missing")

participating = h17["canonical_payload"].get("participating_contexts", {})
if "Authority Management" in participating:
    fail("H17 unexpectedly contains AM tactical payload; migration scope must be revisited")
if TACTICAL_TARGET.exists():
    fail("Authority Management tactical domain model exists without an accepted tactical source")

print("CM3 Authority Management equivalence PASS")
print(f"  language terms migrated: {len(am_terms)}")
print("  tactical model: intentionally absent (no accepted H17 AM tactical payload)")
