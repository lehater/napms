#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

S0_PROBLEM = ROOT / "docs/migration/revalidated/h12-rc-curation/s0/problem-statement.md"
S0_JOURNEY = ROOT / "docs/migration/revalidated/h12-rc-curation/s0/user-journey.md"
S1_BEHAVIOR = ROOT / "docs/migration/revalidated/h12-rc-curation/s1/resource-curation-behavior.md"
S1_AUTH = ROOT / "docs/migration/revalidated/h12-rc-curation/s1/resource-curation-authorization.md"
S1_INTEGRITY = ROOT / "docs/migration/revalidated/h12-rc-curation/s1/resource-curation-integrity.md"
LOCAL_CAPS = ROOT / "docs/migration/revalidated/h12-rc-curation/s2/strategic/capability-map.yaml"
GLOSSARY = ROOT / "docs/migration/revalidated/h12-rc-curation/s2/strategic/domain-glossary.yaml"
DEC_AUTH = ROOT / "docs/migration/revalidated/h12-rc-curation/s2/process/mvp-authority-decision.yaml"
DEC_ROLES = ROOT / "docs/migration/revalidated/h12-rc-curation/s2/process/responsibility-role-decision.yaml"
PROCESS = ROOT / "docs/migration/revalidated/h12-rc-curation/s2/process/resource-curation-process.yaml"
DOMAIN = ROOT / "docs/migration/revalidated/h12-rc-curation/s2/tactical/resource-catalogue-domain-model.yaml"

DISCOVERY_T = ROOT / "docs/discovery/resource-catalogue.yaml"
USECASE_T = ROOT / "docs/model/use-cases/resource-catalogue-curation.yaml"
LANGUAGE_T = ROOT / "docs/model/contexts/resource-catalogue/language.yaml"
DECISIONS_T = ROOT / "docs/model/contexts/resource-catalogue/decisions.yaml"
PROCESS_T = ROOT / "docs/model/contexts/resource-catalogue/process-model.yaml"
DOMAIN_T = ROOT / "docs/model/contexts/resource-catalogue/domain-model.yaml"
STRATEGIC_BC_T = ROOT / "docs/model/strategic/bounded-contexts.yaml"

def load_yaml(path):
    with path.open(encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected YAML mapping")
    return value

def load_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"{path}: expected frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise SystemExit(f"{path}: malformed frontmatter")
    value = yaml.safe_load(parts[1])
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected frontmatter mapping")
    return value

def accepted(doc, path):
    if doc.get("status") != "ACCEPTED":
        raise SystemExit(f"{path}: source is not ACCEPTED")
    freshness = (doc.get("validation") or {}).get("freshness")
    if freshness is not None and freshness != "CURRENT":
        raise SystemExit(f"{path}: source freshness is {freshness!r}")

def fail(message):
    raise SystemExit(f"CM2 equivalence failed: {message}")

front_sources = {
    "problem": (S0_PROBLEM, load_frontmatter(S0_PROBLEM)),
    "journey": (S0_JOURNEY, load_frontmatter(S0_JOURNEY)),
    "behavior": (S1_BEHAVIOR, load_frontmatter(S1_BEHAVIOR)),
    "authorization": (S1_AUTH, load_frontmatter(S1_AUTH)),
    "integrity": (S1_INTEGRITY, load_frontmatter(S1_INTEGRITY)),
}
yaml_sources = {
    "local_caps": (LOCAL_CAPS, load_yaml(LOCAL_CAPS)),
    "glossary": (GLOSSARY, load_yaml(GLOSSARY)),
    "dec_auth": (DEC_AUTH, load_yaml(DEC_AUTH)),
    "dec_roles": (DEC_ROLES, load_yaml(DEC_ROLES)),
    "process": (PROCESS, load_yaml(PROCESS)),
    "domain": (DOMAIN, load_yaml(DOMAIN)),
}
for path, doc in list(front_sources.values()) + list(yaml_sources.values()):
    accepted(doc, path)

discovery = load_yaml(DISCOVERY_T)
usecase = load_yaml(USECASE_T)
language = load_yaml(LANGUAGE_T)
decisions = load_yaml(DECISIONS_T)
process = load_yaml(PROCESS_T)
domain = load_yaml(DOMAIN_T)
strategic_bcs = load_yaml(STRATEGIC_BC_T)

if discovery.get("problem") != front_sources["problem"][1]["canonical_payload"]:
    fail("discovery problem differs from accepted S0")
if discovery.get("journey") != front_sources["journey"][1]["canonical_payload"]:
    fail("discovery journey differs from accepted S0")
for key in ("behavior", "authorization", "integrity"):
    if usecase.get(key) != front_sources[key][1]["canonical_payload"]:
        fail(f"use-case {key} differs from accepted S1")

source_caps = yaml_sources["local_caps"][1]["canonical_payload"]
evidence = discovery.get("capability_discovery_evidence") or {}
source_cap_by_id = {x["capability_id"]: x for x in source_caps["capabilities"]}
target_cap_by_id = {x["capability_id"]: x for x in evidence.get("capabilities", [])}
if set(source_cap_by_id) != set(target_cap_by_id):
    fail("local capability evidence IDs differ")
for cap_id, src in source_cap_by_id.items():
    tgt = target_cap_by_id[cap_id]
    for field in ("capability_id", "name", "business_outcome", "responsibility", "language_terms"):
        if tgt.get(field) != src.get(field):
            fail(f"capability evidence {cap_id} field {field} differs")
expected_basis = {
    "CAP-RC-RESOURCE-CURATION": ["NAPMS-UC-RC-CURATION#behavior", "NAPMS-UC-RC-CURATION#integrity"],
    "CAP-AM-CURATION-ADMISSION": ["NAPMS-UC-RC-CURATION#authorization"],
}
for cap_id, refs in expected_basis.items():
    if target_cap_by_id[cap_id].get("basis_refs") != refs:
        fail(f"capability evidence {cap_id} target basis mapping differs")
if evidence.get("clustering") != source_caps.get("clustering"):
    fail("local capability clustering differs")

source_terms = yaml_sources["glossary"][1]["canonical_payload"]["terms"]
rc_terms = []
external_terms = []
for term in source_terms:
    anchor = term["context_ref"]["anchor_id"]
    stripped = {k: v for k, v in term.items() if k != "context_ref"}
    if anchor == "NAPMS-S2-BC-RESOURCE-CATALOGUE":
        rc_terms.append(stripped)
    else:
        external_terms.append((anchor, stripped))
if language.get("terms") != rc_terms:
    fail("Resource Catalogue language terms differ from accepted glossary")
if external_terms != [("NAPMS-S2-BC-AUTHORITY-MANAGEMENT", {
    "term_id": "TERM-EFFECTIVE-AUTHORITY",
    "term": "Effective Authority",
    "definition": "Authority Management determination of whether an Actor may perform an Action for the applicable scope and time.",
})]:
    fail("unexpected non-RC glossary ownership")
ext_refs = language.get("external_term_refs") or []
if not any(x.get("term") == "Effective Authority" and x.get("owner_context_ref") == "BC-AUTHORITY-MANAGEMENT" for x in ext_refs):
    fail("Resource Catalogue language does not preserve external ownership of Effective Authority")

decision_fields = (
    "decision", "decision_scope", "chosen_option_or_resolution", "rationale",
    "consequences", "rejected_options", "revisit_conditions",
)
src_decisions = {
    "DEC-RC-MVP-AUTHORITY": yaml_sources["dec_auth"][1]["canonical_payload"],
    "DEC-RC-RESPONSIBILITY-ROLES": yaml_sources["dec_roles"][1]["canonical_payload"],
}
target_decisions = {x["decision_id"]: x for x in decisions.get("decisions", [])}
if set(target_decisions) != set(src_decisions):
    fail("domain decision IDs differ")
for decision_id, src in src_decisions.items():
    tgt = target_decisions[decision_id]
    for field in decision_fields:
        if tgt.get(field) != src.get(field):
            fail(f"decision {decision_id} field {field} differs")

src_process = yaml_sources["process"][1]["canonical_payload"]
def strip_origin(items):
    return [{k: v for k, v in item.items() if k != "origin_class"} for item in items]

if process.get("name") != src_process.get("name"):
    fail("process name differs")
expected_contexts = ["BC-RESOURCE-CATALOGUE", "BC-AUTHORITY-MANAGEMENT"]
if process.get("bounded_context_refs") != expected_contexts:
    fail("process context refs do not point to target strategic owners")
for field in ("actors", "commands", "domain_events", "policies", "external_systems"):
    if process.get(field) != strip_origin(src_process.get(field, [])):
        fail(f"process field {field} differs after provenance-only normalization")
for field in ("process_flows", "timeline", "hotspots"):
    if process.get(field) != src_process.get(field):
        fail(f"process field {field} differs")

candidate = src_process["candidate_aggregates"][0]
if candidate["name"] != "Resource":
    fail("unexpected process candidate aggregate")
target_aggregate_names = {x["name"] for x in domain.get("aggregates", [])}
if candidate["name"] not in target_aggregate_names:
    fail("accepted process aggregate candidate is not realized by target domain model")
if set(candidate["command_refs"]) != {x["command_id"] for x in process["commands"]}:
    fail("process candidate aggregate command coverage was lost")

src_domain = yaml_sources["domain"][1]["canonical_payload"]
if domain.get("bounded_context_ref") != "BC-RESOURCE-CATALOGUE":
    fail("domain model does not reference target strategic BC")
for field in ("aggregates", "entities", "value_objects", "domain_services", "command_semantics", "deliberately_not_decided_here"):
    if domain.get(field) != src_domain.get(field):
        fail(f"domain field {field} differs")

src_inv = {x["invariant_id"]: x for x in src_domain["invariants"]}
tgt_inv = {x["invariant_id"]: x for x in domain["invariants"]}
if set(src_inv) != set(tgt_inv):
    fail("domain invariant IDs differ")
for invariant_id, src in src_inv.items():
    if tgt_inv[invariant_id].get("rule") != src.get("rule"):
        fail(f"invariant {invariant_id} rule differs")

expected_invariant_basis = {
    "INV-RC-STABLE-RESOURCE-IDENTITY": ["NAPMS-UC-RC-CURATION#behavior", "NAPMS-RC-CURATION-PROCESS"],
    "INV-RC-SINGLE-EFFECTIVE-ADDRESS-SPACE": ["NAPMS-UC-RC-CURATION#behavior", "NAPMS-RC-CURATION-PROCESS"],
    "INV-RC-HISTORY-PRESERVED": ["NAPMS-UC-RC-CURATION#integrity", "NAPMS-RC-CURATION-PROCESS"],
    "INV-RC-VALID-TEMPORAL-FACTS": ["NAPMS-UC-RC-CURATION#integrity"],
    "INV-RC-OPTIONAL-CURRENT-RELATIONS": ["NAPMS-UC-RC-CURATION#behavior", "NAPMS-RC-CURATION-PROCESS"],
    "INV-RC-RESPONSIBILITY-NOT-AUTHORITY": ["NAPMS-UC-RC-CURATION#authorization"],
    "INV-RC-RESPONSIBILITY-ROLE-EXTENSIBLE": ["NAPMS-RC-DOMAIN-DECISIONS#DEC-RC-RESPONSIBILITY-ROLES"],
}
for invariant_id, refs in expected_invariant_basis.items():
    if tgt_inv[invariant_id].get("basis_refs") != refs:
        fail(f"invariant {invariant_id} target basis mapping differs")

bc_by_id = {x["context_id"]: x for x in strategic_bcs.get("contexts", [])}
if "BC-RESOURCE-CATALOGUE" not in bc_by_id or "BC-AUTHORITY-MANAGEMENT" not in bc_by_id:
    fail("required strategic BC owners are missing")

required_dependencies = {
    DISCOVERY_T: [],
    USECASE_T: ["NAPMS-DISCOVERY-RC-CURATION"],
    LANGUAGE_T: ["NAPMS-UC-RC-CURATION"],
    DECISIONS_T: ["NAPMS-UC-RC-CURATION"],
    PROCESS_T: ["NAPMS-UC-RC-CURATION", "NAPMS-RC-DOMAIN-DECISIONS"],
    DOMAIN_T: ["NAPMS-UC-RC-CURATION", "NAPMS-RC-CURATION-PROCESS", "NAPMS-RC-DOMAIN-DECISIONS", "NAPMS-RC-LANGUAGE"],
}
target_docs = {
    DISCOVERY_T: discovery,
    USECASE_T: usecase,
    LANGUAGE_T: language,
    DECISIONS_T: decisions,
    PROCESS_T: process,
    DOMAIN_T: domain,
}
for path, refs in required_dependencies.items():
    if target_docs[path].get("depends_on", []) != refs:
        fail(f"{path.relative_to(ROOT)} dependency list differs")

print("CM2 Resource Catalogue equivalence PASS")
print("  S0 discovery: problem + journey")
print("  S1 use-case sections: behavior + authorization + integrity")
print(f"  RC language terms: {len(language['terms'])}")
print(f"  domain decisions: {len(decisions['decisions'])}")
print(f"  process commands/events/policies: {len(process['commands'])}/{len(process['domain_events'])}/{len(process['policies'])}")
print(f"  domain aggregates/entities/value objects/invariants: {len(domain['aggregates'])}/{len(domain['entities'])}/{len(domain['value_objects'])}/{len(domain['invariants'])}")
