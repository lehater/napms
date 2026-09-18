#!/usr/bin/env python3
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

CAP_SOURCE = ROOT / "docs/migration/revalidated/h16-strategic/s2/strategic/capability-map.yaml"
REL_SOURCE = ROOT / "docs/migration/revalidated/h16-strategic/s2/strategic/context-relationships.yaml"
RC_REL_SOURCE = ROOT / "docs/migration/revalidated/h12-rc-curation/s2/strategic/context-relationships.yaml"

CAP_TARGET = ROOT / "docs/model/strategic/capabilities.yaml"
BC_TARGET = ROOT / "docs/model/strategic/bounded-contexts.yaml"
REL_TARGET = ROOT / "docs/model/strategic/context-relationships.yaml"

BC_SOURCES = [
    ROOT / "docs/migration/revalidated/h12-rc-curation/s2/strategic/bounded-context-resource-catalogue.yaml",
    ROOT / "docs/migration/revalidated/h12-rc-curation/s2/strategic/bounded-context-authority-management.yaml",
    ROOT / "docs/migration/revalidated/h16-strategic/s2/strategic/bounded-context-access-policy.yaml",
    ROOT / "docs/migration/revalidated/h16-strategic/s2/strategic/bounded-context-application-communication-catalogue.yaml",
    ROOT / "docs/migration/revalidated/h16-strategic/s2/strategic/bounded-context-application-deployment.yaml",
    ROOT / "docs/migration/revalidated/h16-strategic/s2/strategic/bounded-context-business-connectivity.yaml",
    ROOT / "docs/migration/revalidated/h16-strategic/s2/strategic/bounded-context-network-enforcement-placement.yaml",
    ROOT / "docs/migration/revalidated/h16-strategic/s2/strategic/bounded-context-technical-access-evidence.yaml",
    ROOT / "docs/migration/revalidated/h16-strategic/s2/strategic/bounded-context-access-policy-realization.yaml",
    ROOT / "docs/migration/revalidated/h16-strategic/s2/strategic/bounded-context-network-environment-operations.yaml",
]

SEMANTIC_BC_FIELDS = [
    "name",
    "purpose",
    "responsibility",
    "boundary_basis",
    "model_language_ownership",
]

def load(path):
    with path.open(encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected YAML mapping")
    return value

def require_accepted(doc, path):
    if doc.get("status") != "ACCEPTED":
        raise SystemExit(f"{path}: source is not ACCEPTED")
    freshness = (doc.get("validation") or {}).get("freshness")
    if freshness is not None and freshness != "CURRENT":
        raise SystemExit(f"{path}: source freshness is {freshness!r}, expected CURRENT")

def fail(message):
    raise SystemExit(message)

cap_source = load(CAP_SOURCE)
rel_source = load(REL_SOURCE)
rc_rel_source = load(RC_REL_SOURCE)
for path, doc in [(CAP_SOURCE, cap_source), (REL_SOURCE, rel_source), (RC_REL_SOURCE, rc_rel_source)]:
    require_accepted(doc, path)

bc_sources = {}
for path in BC_SOURCES:
    doc = load(path)
    require_accepted(doc, path)
    payload = doc["canonical_payload"]
    bc_sources[payload["name"]] = payload

cap_target = load(CAP_TARGET)
bc_target = load(BC_TARGET)
rel_target = load(REL_TARGET)

source_caps = cap_source["canonical_payload"]
if cap_target.get("capabilities") != source_caps.get("capabilities"):
    fail("CM1 equivalence failed: capabilities differ from accepted H16 payload")
cluster = source_caps["clustering"][0]["capability_ids"]
if cap_target.get("peer_bounded_context_capabilities") != cluster:
    fail("CM1 equivalence failed: peer BC capability cluster differs")
if cap_target.get("non_peer_compositions") != source_caps.get("non_peer_compositions"):
    fail("CM1 equivalence failed: non-peer compositions differ")
if cap_target.get("integration_capabilities") != source_caps.get("integration_capabilities"):
    fail("CM1 equivalence failed: integration capabilities differ")

target_caps_by_name = {c["name"]: c for c in cap_target["capabilities"]}
target_contexts = bc_target.get("contexts") or []
if len(target_contexts) != len(bc_sources):
    fail(f"CM1 equivalence failed: expected {len(bc_sources)} BCs, found {len(target_contexts)}")

seen_names = set()
seen_ids = set()
for target in target_contexts:
    name = target["name"]
    if name in seen_names:
        fail(f"duplicate target BC name: {name}")
    seen_names.add(name)
    if target["context_id"] in seen_ids:
        fail(f"duplicate target context_id: {target['context_id']}")
    seen_ids.add(target["context_id"])
    source = bc_sources.get(name)
    if source is None:
        fail(f"CM1 equivalence failed: target BC {name!r} has no accepted source")
    for field in SEMANTIC_BC_FIELDS:
        if target.get(field) != source.get(field):
            fail(f"CM1 equivalence failed: {name} field {field} differs")
    cap = target_caps_by_name.get(name)
    if cap is None or target.get("capability_ref") != cap.get("capability_id"):
        fail(f"CM1 equivalence failed: {name} capability_ref does not map to whole-domain capability")

if seen_names != set(bc_sources):
    fail("CM1 equivalence failed: target BC name set differs from accepted source set")

accepted_rel = rel_source["canonical_payload"]
if rel_target.get("whole_domain_relationships") != accepted_rel.get("relationships"):
    fail("CM1 equivalence failed: whole-domain relationships differ from accepted H16 payload")
if rel_target.get("strategic_invariants") != accepted_rel.get("strategic_invariants"):
    fail("CM1 equivalence failed: strategic invariants differ from accepted H16 payload")

rc_rel = rc_rel_source["canonical_payload"]["relationships"]
if len(rc_rel) != 1:
    fail("CM1 equivalence check expects exactly one accepted H12 RC/AM context relationship")
source_local = rc_rel[0]
target_local = rel_target.get("context_mapping_relationships") or []
if len(target_local) != 1:
    fail("CM1 equivalence failed: expected one target explicit Context Mapping relationship")
target_local = target_local[0]
anchor_to_name = {
    "NAPMS-S2-BC-AUTHORITY-MANAGEMENT": "Authority Management",
    "NAPMS-S2-BC-RESOURCE-CATALOGUE": "Resource Catalogue",
}
expected_local = {
    "relationship_id": source_local["relationship_id"],
    "from": anchor_to_name[source_local["context_a_ref"]["anchor_id"]],
    "to": anchor_to_name[source_local["context_b_ref"]["anchor_id"]],
    "direction": "upstream-downstream" if source_local["direction"] == "a-upstream-b" else source_local["direction"],
    "patterns": source_local["patterns"],
    "semantics": source_local["rationale"],
}
if target_local != expected_local:
    fail("CM1 equivalence failed: H12 Authority Management -> Resource Catalogue relationship differs")

peer_names = seen_names
composition_names = {x["id"] for x in cap_target["non_peer_compositions"]}
known_endpoints = peer_names | composition_names
for rel in rel_target["whole_domain_relationships"]:
    for endpoint in ("from", "to"):
        if rel[endpoint] not in known_endpoints:
            fail(f"unknown whole-domain relationship endpoint: {rel[endpoint]}")
for rel in rel_target["context_mapping_relationships"]:
    if rel["from"] not in peer_names or rel["to"] not in peer_names:
        fail("explicit Context Mapping relationship must connect peer Bounded Contexts")
    if rel.get("patterns") is None:
        fail("explicit Context Mapping relationship must preserve pattern certainty explicitly")

print("CM1 strategic equivalence PASS")
print(f"  capabilities: {len(cap_target['capabilities'])}")
print(f"  bounded contexts: {len(target_contexts)}")
print(f"  whole-domain relationships: {len(rel_target['whole_domain_relationships'])}")
print(f"  explicit context-mapping relationships: {len(rel_target['context_mapping_relationships'])}")
print(f"  non-peer compositions: {len(cap_target['non_peer_compositions'])}")
