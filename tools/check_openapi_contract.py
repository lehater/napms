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
if actual!=req["operations"]:
    fail(f"operation set/order differs: {actual}")

sec=api.get("components",{}).get("securitySchemes",{}).get("OIDCBearer")
if not (isinstance(sec,dict) and sec.get("type")=="http" and sec.get("scheme")=="bearer" and sec.get("bearerFormat")=="JWT"):
    fail("OIDC bearer security differs")

schemas=api.get("components",{}).get("schemas",{})
def walk(value,path=""):
    if isinstance(value,dict):
        for key,item in value.items():
            if key.lower() in {"actor","actorid","actor_id","permissions","authoritygrants","authority_grants"}:
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

decision=schemas.get("DecideAccessRequestRequest",{}).get("properties",{}).get("result",{})
if decision.get("enum")!=["ALLOWED","DENIED"]:
    fail("permission decision enum differs")

operational=schemas.get("SetPolicyRuleOperationalStateRequest",{}).get("properties",{}).get("effectState",{})
if operational.get("enum")!=["ACTIVE","INACTIVE"]:
    fail("PolicyRule operational state differs")

materialization=schemas.get("PolicyMaterializationResult",{})
required=set(materialization.get("required",[]))
for field in ("evaluationAt","exportAuthorityEvidence","ruleProvenance","rows","issues"):
    if field not in required:
        fail(f"materialization missing required {field}")

request=schemas.get("PolicyMaterializationRequest",{}).get("properties",{}).get("policyRuleRefs",{})
if request.get("minItems")!=1 or request.get("uniqueItems") is not True:
    fail("explicit Rule subset contract differs")

create_resource=schemas.get("CreateResourceRequest",{})
if "authorityScopeRef" not in create_resource.get("required",[]):
    fail("Resource authorityScopeRef missing")

process=schemas.get("CreateProcessRequest",{}).get("properties",{})
if "criticalityLabel" not in process:
    fail("BusinessProcess criticalityLabel missing")

resource_view=schemas.get("ResourceView",{})
resource_required=set(resource_view.get("required",[]))
for field in ("resourceRef","authorityScopeRef","version","current","history"):
    if field not in resource_required:
        fail(f"ResourceView missing required {field}")
if "scopeAffiliations" in str(resource_view):
    fail("stale Resource scope-affiliation semantics remain")

required_resource_ops={
    "DELETE /v1/resources/{resourceRef}/endpoints/{endpointRef}/address",
    "PUT /v1/resources/{resourceRef}/site",
    "PUT /v1/resources/{resourceRef}/responsibilities/{role}",
}
if not required_resource_ops.issubset(set(actual)):
    fail(f"Resource curation operations missing: {sorted(required_resource_ops-set(actual))}")

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
for forbidden in ("RuleChange","SessionCookie","napms_session","same Application"):
    if forbidden in text:
        fail(f"stale contract term remains: {forbidden}")

print("OpenAPI contract PASS")
