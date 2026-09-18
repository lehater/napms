#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/"docs/architecture/persistence/mvp-persistence.yaml"

EXPECTED={
 "resource_catalogue":{"resource","resource_address_space"},
 "application_communication_catalogue":{"application_definition","component","interaction","interaction_contract_revision"},
 "application_deployment":{"component_deployment"},
 "business_connectivity":{"business_process","connectivity_need"},
 "access_policy":{"policy_rule","rule_change"},
 "authority_management":{"actor","authority_assignment"},
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
        if len([c for c in columns if c.get("primary_key")])!=1:
            fail(f"{schema}.{table}: expected one primary key")
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

for key,index in {
 ("resource_catalogue","resource_address_space"):"uq_resource_address_space_current",
 ("application_communication_catalogue","interaction"):"uq_interaction_directed_pair",
 ("application_communication_catalogue","interaction_contract_revision"):"uq_interaction_current_revision",
 ("access_policy","policy_rule"):"uq_policy_rule_non_retired_pair",
 ("access_policy","rule_change"):"uq_rule_change_pending_per_rule",
}.items():
    if index not in index_names(*key):
        fail(f"required invariant index missing: {index}")

for key,names in {
 ("application_deployment","component_deployment"):{"component_ref","resource_ref"},
 ("business_connectivity","connectivity_need"):{"interaction_ref"},
 ("access_policy","policy_rule"):{"source_component_deployment_ref","destination_component_deployment_ref","effective_revision_ref"},
 ("access_policy","rule_change"):{"revision_ref","connectivity_need_ref"},
}.items():
    columns={c["name"]:c for c in table(*key)["columns"]}
    for name in names:
        if name not in columns or "external_owner" not in columns[name]:
            fail(f"external owner reference missing: {key}.{name}")

print("Persistence model PASS")
