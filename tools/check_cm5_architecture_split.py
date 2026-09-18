#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
H18=ROOT/"docs/migration/revalidated/h18-mvp-architecture/s3/mvp-system-architecture.yaml"
H19=ROOT/"docs/migration/revalidated/h19-mvp-implementation-readiness/s4/mvp-implementation-readiness.yaml"
RULES=ROOT/"docs/architecture/mvp-system-rules.yaml"
PERSIST=ROOT/"docs/architecture/persistence/mvp-persistence.yaml"
API=ROOT/"docs/contracts/http/napms-api-requirements.yaml"
DSL=ROOT/"docs/architecture/structurizr/workspace.dsl"

def load(p):
    with p.open(encoding="utf-8") as f:
        v=yaml.safe_load(f)
    if not isinstance(v,dict):
        raise SystemExit(f"{p}: expected mapping")
    return v

def fail(m):
    raise SystemExit(f"CM5 architecture split failed: {m}")

h18=load(H18)
h19=load(H19)
rules=load(RULES)
persist=load(PERSIST)
api=load(API)
dsl=DSL.read_text(encoding="utf-8")

if h18.get("status")!="ACCEPTED" or h19.get("status")!="ACCEPTED":
    fail("source anchor not ACCEPTED")
a=h18["canonical_payload"]
i=h19["canonical_payload"]

if rules.get("architecture_goal")!=a["architecture_goal"]:
    fail("architecture_goal differs")
expected_boundary={k:a["frontend_backend_boundary"][k] for k in ("design_rule","required_capabilities","error_rule")}
if rules.get("application_boundary_rules")!=expected_boundary:
    fail("application boundary rules differ")
for field in ("interaction_rules","authorization","consistency","excluded_from_mvp_runtime","architecture_questions_remaining"):
    if rules.get(field)!=a.get(field):
        fail(f"architecture-rules field {field} differs")
expected_deployment={k:a["deployment"][k] for k in ("external_dependencies","evolution_rule")}
if rules.get("deployment_policy")!=expected_deployment:
    fail("deployment policy differs")

for field in ("topology","ownership","mutation_rule","read_rule","migration_rule","transaction_rule"):
    if persist.get(field)!=a["persistence"].get(field):
        fail(f"persistence H18 field {field} differs")
if persist.get("database")!=i["persistence"]["database"]:
    fail("persistence database differs")
detail_schemas=persist.get("schemas",{})
detail_table_set={schema:list(sdef.get("tables",{}).keys()) for schema,sdef in detail_schemas.items()}
if detail_table_set!=i["persistence"]["schemas"]:
    fail(f"persistence schema/table ownership differs: {detail_table_set}")
if persist.get("rules")!=i["persistence"]["rules"]:
    fail("persistence rules differ")

b=a["frontend_backend_boundary"]
if api.get("target_contract_format")!="OpenAPI":
    fail("API target format differs")
if api.get("delivery_protocol")!=b["protocol"]:
    fail("API protocol differs")
if api.get("payload_style")!=b["payload_style"]:
    fail("API payload style differs")
if api.get("design_rule")!=b["design_rule"] or api.get("required_capabilities")!=b["required_capabilities"] or api.get("error_rule")!=b["error_rule"]:
    fail("H18 API boundary semantics differ")
if api.get("contract_rule")!=i["application_api"]["contract"]:
    fail("H19 API contract rule differs")
if api.get("operations")!=i["application_api"]["operations"]:
    fail("H19 API operations differ")
if api.get("rules")!=i["application_api"]["rules"]:
    fail("H19 API rules differ")

required_tokens=[
    'container "Web Application"',
    'container "Backend"',
    'container "PostgreSQL"',
    'component "Resource Catalogue"',
    'component "Application Communication Catalogue"',
    'component "Application Deployment"',
    'component "Business Connectivity"',
    'component "Access Policy"',
    'component "Authority Management"',
    'component "Policy Export Composition"',
    'HTTP/JSON; CSV export',
    'deploymentEnvironment "MVP Baseline"',
]
for token in required_tokens:
    if token not in dsl:
        fail(f"Structurizr missing structural token: {token}")

for forbidden in ("Kafka","RabbitMQ","AsyncAPI"):
    if forbidden in dsl:
        fail(f"unexpected async runtime assertion in Structurizr: {forbidden}")

print("CM5 architecture split equivalence PASS")
