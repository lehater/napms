#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
REQ=ROOT/"docs/contracts/http/napms-api-requirements.yaml"
API=ROOT/"docs/contracts/http/napms.openapi.yaml"

def load(path):
    value=yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise SystemExit(f"{path}: expected mapping")
    return value

def fail(message):
    raise SystemExit(f"OpenAPI contract check failed: {message}")

req=load(REQ)
api=load(API)
if api.get("openapi")!="3.1.0":
    fail("OpenAPI version must be 3.1.0")

actual=[]
for path,item in api.get("paths",{}).items():
    for method in ("get","post","put","patch","delete"):
        if method in item:
            actual.append(f"{method.upper()} {path}")
expected=req["operations"]
if len(actual)!=len(set(actual)):
    fail(f"OpenAPI contains duplicate operations: {actual}")
if len(expected)!=len(set(expected)):
    fail(f"requirements contain duplicate operations: {expected}")
if set(actual)!=set(expected):
    fail(
        "operation set differs: "
        f"missing={sorted(set(expected)-set(actual))}, "
        f"unexpected={sorted(set(actual)-set(expected))}"
    )

sec=api.get("components",{}).get("securitySchemes",{}).get("OIDCBearer")
if not (isinstance(sec,dict) and sec.get("type")=="http" and sec.get("scheme")=="bearer" and sec.get("bearerFormat")=="JWT"):
    fail("OIDC bearer security differs")

schemas=api.get("components",{}).get("schemas",{})
def walk(value,path=""):
    if isinstance(value,dict):
        for key,item in value.items():
            if key.lower() in {
                "actor","actorid","actor_id","permissions",
                "authoritygrants","authority_grants","roleassignments","role_assignments",
                "groupmembership","group_membership",
            }:
                fail(f"trusted security field appears in request schema at {path}/{key}")
            walk(item,f"{path}/{key}")
    elif isinstance(value,list):
        for index,item in enumerate(value):
            walk(item,f"{path}/{index}")
walk({k:v for k,v in schemas.items() if k.endswith("Request")})

refs=[item.get("$ref") for item in schemas.get("AddressRealization",{}).get("oneOf",[]) if isinstance(item,dict)]
if refs!=["#/components/schemas/HostAddress","#/components/schemas/Prefix"]:
    fail("AddressRealization XOR representation differs")

traffic=schemas.get("PublishRevisionRequest",{}).get("properties",{}).get("trafficClauses",{})
if traffic.get("minItems")!=1:
    fail("revision must require at least one traffic clause")

interaction=schemas.get("CreateInteractionRequest",{}).get("required",[])
if interaction!=["sourceComponentRef","destinationComponentRef"]:
    fail("Interaction contract must not require one owning Application")

approval=schemas.get("RecordApprovalDecisionRequest",{}).get("properties",{}).get("result",{})
if approval.get("enum")!=["APPROVED","DENIED"]:
    fail("approval decision enum differs")

request_status=schemas.get("AccessRequestView",{}).get("properties",{}).get("status",{})
if request_status.get("enum")!=["PENDING","ALLOWED","DENIED","CANCELLED","EXPIRED","INVALIDATED"]:
    fail("AccessRequest terminal lifecycle differs")

rule_state=schemas.get("PolicyRuleView",{}).get("properties",{}).get("revocationState",{})
if rule_state.get("enum")!=["CURRENT","REVOKED"]:
    fail("PolicyRule revocation lifecycle differs")

if "DecideAccessRequestRequest" in schemas:
    fail("stale direct final permission decision request remains")
if "SetPolicyRuleOperationalStateRequest" in schemas:
    fail("stale reversible PolicyRule operational-state request remains")

materialization=schemas.get("PolicyMaterializationResult",{})
required=set(materialization.get("required",[]))
for field in ("evaluationAt","exportAuthorityEvidence","ruleProvenance","rows","issues"):
    if field not in required:
        fail(f"materialization missing required {field}")

request=schemas.get("PolicyMaterializationRequest",{}).get("properties",{}).get("policyRuleRefs",{})
if request.get("minItems")!=1 or request.get("uniqueItems") is not True:
    fail("explicit Rule subset contract differs")

create_resource=schemas.get("CreateResourceRequest",{})
required_create=set(create_resource.get("required",[]))
if "organizationalUnitRef" not in required_create or "authorityScopeRef" in required_create:
    fail("Resource organizational-owner creation contract differs")

resource_view=schemas.get("ResourceView",{})
resource_required=set(resource_view.get("required",[]))
for field in ("resourceRef","organizationalUnitRef","version","current","history"):
    if field not in resource_required:
        fail(f"ResourceView missing required {field}")
if "authorityScopeRef" in str(resource_view):
    fail("stale Resource AuthorityScopeRef semantics remain")
history=schemas.get("ResourceHistory",{})
if "organizationalOwnership" not in set(history.get("required",[])):
    fail("Resource ownership history is not explicit")

org_unit=schemas.get("OrganizationalUnitView",{})
for field in ("organizationalUnitRef","organizationRef","lifecycleState","version"):
    if field not in set(org_unit.get("required",[])):
        fail(f"OrganizationalUnitView missing required {field}")

policy=schemas.get("ApprovalPolicyView",{})
if not {"policyRef","organizationRef","currentRevision"}.issubset(set(policy.get("required",[]))):
    fail("ApprovalPolicy current immutable revision contract differs")

required_new_ops={
    "GET /v1/organization",
    "POST /v1/organizational-units",
    "PUT /v1/resources/{resourceRef}/organizational-owner",
    "POST /v1/approval-policies/{organizationRef}/revisions",
    "POST /v1/access-requests/{requestRef}/approval-decisions",
    "POST /v1/access-requests/{requestRef}/cancellation",
    "POST /v1/policy-rules/{policyRuleRef}/revocation",
}
if not required_new_ops.issubset(set(actual)):
    fail(f"revalidated operations missing: {sorted(required_new_ops-set(actual))}")

for stale in (
    "POST /v1/access-requests/{requestRef}/decision",
    "PUT /v1/policy-rules/{policyRuleRef}/operational-state",
):
    if stale in actual:
        fail(f"stale operation remains: {stale}")

process=schemas.get("CreateProcessRequest",{}).get("properties",{})
if "criticalityLabel" not in process:
    fail("BusinessProcess criticalityLabel missing")

payload_response=api.get("components",{}).get("responses",{}).get("PayloadTooLarge")
if not isinstance(payload_response,dict):
    fail("413 PayloadTooLarge response is not materialized")
for path,item in api.get("paths",{}).items():
    for method in ("post","put","patch"):
        operation=item.get(method)
        if not isinstance(operation,dict) or "requestBody" not in operation:
            continue
        if "413" not in operation.get("responses",{}):
            fail(f"{method.upper()} {path} request body has no 413 response")

text=API.read_text(encoding="utf-8")
for forbidden in (
    "RuleChange","SessionCookie","napms_session","same Application",
    "authorityScopeRef","AuthorityGrant","effectState","operational-state",
    "DecideAccessRequestRequest","SetPolicyRuleOperationalStateRequest",
):
    if forbidden in text:
        fail(f"stale contract term remains: {forbidden}")

ui=(ROOT/"docs/contracts/ui/resource-detail.yaml").read_text(encoding="utf-8")
for forbidden in (
    "Responsibility Scope affiliations","scope affiliations",
    "immutable AuthorityScopeRef","authorityScopeRef",
    "GET /api/resources/{resourceId}",
):
    if forbidden in ui:
        fail(f"stale Resource UI semantic remains: {forbidden}")
for required in (
    "current OrganizationalUnit owner",
    "PUT /v1/resources/{resourceRef}/organizational-owner",
    "ownership history",
    "GET /v1/resources/{resourceRef}",
):
    if required not in ui:
        fail(f"Resource UI missing current semantic: {required}")

print("OpenAPI contract PASS")
