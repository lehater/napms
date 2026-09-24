#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/"docs/architecture/persistence/mvp-persistence.yaml"

EXPECTED={
 "organization_structure":{"organization","organizational_unit","organizational_unit_parent_history"},
 "resource_catalogue":{"resource","resource_ownership_history","site","responsibility_group","resource_site_history","resource_endpoint","resource_endpoint_address_history","resource_responsibility_history"},
 "application_communication_catalogue":{"application","component","interaction","interaction_revision","interaction_traffic_clause","interaction_port_range"},
 "application_deployment":{"component_deployment"},
 "business_connectivity":{"business_process","connectivity_need"},
 "authority_management":{"role","role_action","role_assignment"},
 "access_policy":{"approval_policy","approval_policy_revision","authority_evidence","access_request","access_request_approval_basis_side","access_request_approval_obligation","access_request_approval_decision","policy_rule","policy_rule_authorization_evidence","policy_rule_revocation","policy_rule_justification"},
 "application_edge":{"idempotency_record"},
}

def fail(message):
    raise SystemExit(f"Persistence model check failed: {message}")

model=yaml.safe_load(MODEL.read_text(encoding="utf-8"))
if not isinstance(model,dict):
    fail("expected mapping")
if model.get("physical_detail_status")!="COMPLETE_FOR_FIRST_MVP":
    fail("physical detail not complete")
if model.get("erd_status")!="GENERATED_FROM_THIS_MODEL":
    fail("ERD status differs")

schemas=model.get("schemas",{})
if set(schemas)!=set(EXPECTED):
    fail(f"schema set differs: {set(schemas)}")

for schema,names in EXPECTED.items():
    tables=schemas[schema].get("tables",{})
    if set(tables)!=names:
        fail(f"{schema} table set differs: {set(tables)}")
    for table,tdef in tables.items():
        columns=tdef.get("columns",[])
        if not columns:
            fail(f"{schema}.{table}: no columns")
        if not any(c.get("primary_key") for c in columns):
            fail(f"{schema}.{table}: missing primary key")
        col_names={c["name"] for c in columns}
        for fk in tdef.get("local_foreign_keys",[]):
            ref_schema,ref_table=fk["references"].split(".",1)
            if ref_schema!=schema:
                fail(f"{schema}.{table}: cross-schema database FK is forbidden")
            if not set(fk["columns"])<=col_names:
                fail(f"{schema}.{table}: FK source column missing")
            target_cols={c["name"] for c in schemas[ref_schema]["tables"][ref_table]["columns"]}
            if not set(fk["target_columns"])<=target_cols:
                fail(f"{schema}.{table}: FK target column missing")

def table(schema,name):
    return schemas[schema]["tables"][name]

def index_names(schema,name):
    return {item["name"] for item in table(schema,name).get("indexes",[])}

required_indexes={
 ("organization_structure","organizational_unit_parent_history"):"uq_unit_current_parent_fact",
 ("resource_catalogue","resource_ownership_history"):"uq_resource_current_owner_fact",
 ("resource_catalogue","resource_endpoint_address_history"):"uq_endpoint_current_address",
 ("resource_catalogue","resource_responsibility_history"):"uq_resource_current_responsibility",
 ("application_communication_catalogue","interaction_revision"):"uq_interaction_revision_no",
 ("authority_management","role_action"):"uq_role_action",
 ("access_policy","access_request"):"uq_pending_access_subject",
 ("access_policy","access_request_approval_decision"):"uq_approval_decision_obligation",
 ("access_policy","policy_rule"):"uq_current_policy_rule_access_subject",
 ("access_policy","policy_rule"):"uq_policy_rule_access_request",
 ("access_policy","policy_rule_authorization_evidence"):"uq_authorization_request",
 ("access_policy","policy_rule_revocation"):"uq_policy_rule_revocation",
 ("access_policy","policy_rule_justification"):"uq_rule_need_justification",
 ("application_edge","idempotency_record"):"uq_idempotency_scope",
}
# policy_rule has two required indexes; check separately because dict keys cannot repeat.
required_index_sets={
 ("access_policy","policy_rule"):{"uq_current_policy_rule_access_subject","uq_policy_rule_access_request"},
}
for key,index in required_indexes.items():
    if index not in index_names(*key):
        fail(f"required invariant index missing: {index}")
for key,indexes in required_index_sets.items():
    missing=indexes-index_names(*key)
    if missing:
        fail(f"required invariant indexes missing: {sorted(missing)}")

required_external={
 ("resource_catalogue","resource"):{"organizational_unit_ref"},
 ("resource_catalogue","resource_ownership_history"):{"organizational_unit_ref"},
 ("application_deployment","component_deployment"):{"component_ref","resource_ref"},
 ("business_connectivity","connectivity_need"):{"interaction_ref","participant_component_ref"},
 ("authority_management","role_assignment"):{"scope_ref"},
 ("access_policy","approval_policy"):{"organization_ref"},
 ("access_policy","authority_evidence"):{"scope_ref"},
 ("access_policy","access_request"):{"source_deployment_ref","destination_deployment_ref","interaction_revision_ref","initial_need_ref"},
 ("access_policy","access_request_approval_basis_side"):{"scope_ref"},
 ("access_policy","policy_rule"):{"source_deployment_ref","destination_deployment_ref","interaction_revision_ref"},
 ("access_policy","policy_rule_revocation"):{"scope_ref"},
 ("access_policy","policy_rule_justification"):{"need_ref"},
}
for key,names in required_external.items():
    columns={c["name"]:c for c in table(*key)["columns"]}
    for name in names:
        if name not in columns or "external_owner" not in columns[name]:
            fail(f"external owner reference missing: {key}.{name}")

resource_cols={c["name"] for c in table("resource_catalogue","resource")["columns"]}
if "organizational_unit_ref" not in resource_cols or "authority_scope_ref" in resource_cols:
    fail("Resource current organizational owner persistence differs")

rule_cols={c["name"] for c in table("access_policy","policy_rule")["columns"]}
if "effect_state" in rule_cols or "revoked_at" not in rule_cols:
    fail("PolicyRule authorization-episode lifecycle persistence differs")

request_cols={c["name"] for c in table("access_policy","access_request")["columns"]}
if "status" not in request_cols or "decision_result" in request_cols:
    fail("AccessRequest terminal lifecycle persistence differs")

process_cols={c["name"] for c in table("business_connectivity","business_process")["columns"]}
if "criticality_label" not in process_cols:
    fail("BusinessProcess criticality_label missing")

interaction_cols={c["name"] for c in table("application_communication_catalogue","interaction")["columns"]}
if "application_ref" in interaction_cols:
    fail("Interaction must not carry one owning application_ref")

print("Persistence model PASS")
