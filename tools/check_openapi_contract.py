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

sec=api.get("components",{}).get("securitySchemes",{}).get("SessionCookie")
if not (isinstance(sec,dict) and sec.get("type")=="apiKey" and sec.get("in")=="cookie" and sec.get("name")=="napms_session"):
    fail("session cookie security differs")

schemas=api.get("components",{}).get("schemas",{})
def walk(value,path=""):
    if isinstance(value,dict):
        for key,item in value.items():
            if key.lower() in {"actor","actorid","actor_id"}:
                fail(f"trusted actor field appears at {path}/{key}")
            walk(item,f"{path}/{key}")
    elif isinstance(value,list):
        for index,item in enumerate(value):
            walk(item,f"{path}/{index}")
walk({k:v for k,v in schemas.items() if k.endswith("Request")})

refs=[item.get("$ref") for item in schemas.get("AddressSpace",{}).get("oneOf",[]) if isinstance(item,dict)]
if refs!=["#/components/schemas/HostAddress","#/components/schemas/Prefix"]:
    fail("AddressSpace XOR representation differs")

traffic=schemas.get("PublishRevisionRequest",{}).get("properties",{}).get("trafficAlternatives",{})
if traffic.get("minItems")!=1:
    fail("revision must require at least one traffic alternative")

if "rows" not in schemas.get("PolicyExportSuccess",{}).get("required",[]):
    fail("successful export must contain complete rows")
if "rows" in schemas.get("PolicyExportUnresolved",{}).get("properties",{}):
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
for forbidden in ("Kafka","RabbitMQ","provider-specific"):
    if forbidden in text:
        fail(f"unexpected out-of-scope contract term: {forbidden}")

print("OpenAPI contract PASS")
