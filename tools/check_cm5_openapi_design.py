#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
REQ=ROOT/"docs/contracts/http/napms-api-requirements.yaml"
API=ROOT/"docs/contracts/http/napms.openapi.yaml"

def load(p):
    with p.open(encoding="utf-8") as f:
        v=yaml.safe_load(f)
    if not isinstance(v,dict):
        raise SystemExit(f"{p}: expected mapping")
    return v

def fail(m):
    raise SystemExit(f"CM5 OpenAPI design failed: {m}")

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

sec=api.get("components",{}).get("securitySchemes",{}).get("SessionCookie")
if sec!={"type":"apiKey","in":"cookie","name":"napms_session","description":sec.get("description")}:
    if not (isinstance(sec,dict) and sec.get("type")=="apiKey" and sec.get("in")=="cookie" and sec.get("name")=="napms_session"):
        fail("session cookie security differs")

schemas=api.get("components",{}).get("schemas",{})
def walk(v,path=""):
    if isinstance(v,dict):
        for k,x in v.items():
            lk=k.lower()
            if lk in {"actor","actorid","actor_id"}:
                fail(f"trusted actor field appears at {path}/{k}")
            walk(x,f"{path}/{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): walk(x,f"{path}/{i}")
walk({k:v for k,v in schemas.items() if k.endswith("Request")})

addr=schemas.get("AddressSpace",{})
refs=[x.get("$ref") for x in addr.get("oneOf",[]) if isinstance(x,dict)]
if refs!=["#/components/schemas/HostAddress","#/components/schemas/Prefix"]:
    fail("AddressSpace XOR representation differs")

traffic=schemas.get("PublishRevisionRequest",{}).get("properties",{}).get("trafficAlternatives",{})
if traffic.get("minItems")!=1:
    fail("revision must require at least one traffic alternative")

success=schemas.get("PolicyExportSuccess",{})
if "rows" not in success.get("required",[]):
    fail("successful export must own complete rows")
unresolved=schemas.get("PolicyExportUnresolved",{})
if "rows" in unresolved.get("properties",{}):
    fail("Unresolved export must not contain partial rows")

csv=api["paths"]["/api/policy-export.csv"]["get"]["responses"]
if "text/csv" not in csv["200"].get("content",{}):
    fail("CSV success media type missing")
if "text/csv" in csv["422"].get("content",{}):
    fail("Unresolved CSV response must not return CSV")

decision=schemas.get("DecideRuleChangeRequest",{}).get("properties",{}).get("decision",{})
if decision.get("enum")!=["Accepted","Rejected"]:
    fail("decision enum differs")

text=API.read_text(encoding="utf-8")
for forbidden in ("Kafka","RabbitMQ","firewall","provider-specific"):
    if forbidden in text:
        fail(f"unexpected out-of-scope contract term: {forbidden}")

print("CM5 OpenAPI design PASS")
