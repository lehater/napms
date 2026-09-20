#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/"docs/architecture/persistence/mvp-persistence.yaml"

EXPECTED={
 "resource_catalogue":{"resource","site","responsibility_group","resource_site_history","resource_endpoint","resource_endpoint_address_history","resource_responsibility_history"},
 "application_communication_catalogue":{"application","component","interaction","interaction_revision","interaction_traffic_clause","interaction_port_range"},
 "application_deployment":{"component_deployment"},
 "business_connectivity":{"business_process","connectivity_need"},
 "access_policy":{"access_request","access_request_authority_evidence","policy_rule","policy_rule_authorization_evidence","policy_rule_justification","policy_rule_operational_history"},
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
 ("resource_catalogue","resource_endpoint_address_history"):"uq_endpoint_current_address",
 ("resource_catalogue","resource_responsibility_history"):"uq_resource_current_responsibility",
 ("application_communication_catalogue","interaction_revision"):"uq_interaction_revision_no",
 ("access_policy","policy_rule"):"uq_policy_rule_access_subject",
 ("access_policy","policy_rule_authorization_evidence"):"uq_authorization_request",
 ("access_policy","policy_rule_justification"):"uq_rule_need_justification",
 ("application_edge","idempotency_record"):"uq_idempotency_scope",
}
for key,index in required_indexes.items():
    if index not in index_names(*key):
        fail(f"required invariant index missing: {index}")

required_external={
 ("application_deployment","component_deployment"):{"component_ref","resource_ref"},
 ("business_connectivity","connectivity_need"):{"interaction_ref","participant_component_ref"},
 ("access_policy","access_request"):{"source_deployment_ref","destination_deployment_ref","interaction_revision_ref","initial_need_ref"},
 ("access_policy","policy_rule"):{"source_deployment_ref","destination_deployment_ref","interaction_revision_ref"},
 ("access_policy","policy_rule_justification"):{"need_ref"},
}
for key,names in required_external.items():
    columns={c["name"]:c for c in table(*key)["columns"]}
    for name in names:
        if name not in columns or "external_owner" not in columns[name]:
            fail(f"external owner reference missing: {key}.{name}")

resource_cols={c["name"] for c in table("resource_catalogue","resource")["columns"]}
if "authority_scope_ref" not in resource_cols:
    fail("Resource authority_scope_ref missing")

process_cols={c["name"] for c in table("business_connectivity","business_process")["columns"]}
if "criticality_label" not in process_cols:
    fail("BusinessProcess criticality_label missing")

interaction_cols={c["name"] for c in table("application_communication_catalogue","interaction")["columns"]}
if "application_ref" in interaction_cols:
    fail("Interaction must not carry one owning application_ref")

print("Persistence model PASS")
