#!/usr/bin/env python3
from pathlib import Path
import argparse,tempfile,yaml
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"docs/model/contexts/application-deployment/domain-model.yaml"
OUT=ROOT/"docs-generated/architecture"
def esc(v): return str(v).replace("\\","\\\\").replace('"','\\"').replace("\n","\\n")
def load(): return yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
def render(m):
    lines=["@startuml","' GENERATED FILE - DO NOT EDIT",f"' Semantic authority: {SOURCE.relative_to(ROOT)}","title Application Deployment Domain Model","skinparam shadowing false",f'rectangle "{esc(m["aggregate"])}" as Aggregate <<Aggregate>>',"","legend left","  |= Invariant |"]
    lines += [f"  | {esc(x)} |" for x in m["invariants"]]
    lines += ["  |= Public semantics |"]+[f"  | {esc(x)} |" for x in m["public_semantics"]]+["endlegend","@enduml",""]
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args();m=load()
    if a.check:
        path=OUT/"application-deployment-domain.puml";expected=render(m)
        if not path.is_file() or path.read_text(encoding="utf-8") != expected: raise SystemExit(f"generated projection is stale: {path.relative_to(ROOT)}; run make design-sync")
        print(f"checked {path.relative_to(ROOT)}")
    else:
        OUT.mkdir(parents=True,exist_ok=True);path=OUT/"application-deployment-domain.puml";path.write_text(render(m),encoding="utf-8");print(f"generated {path.relative_to(ROOT)}")
if __name__=="__main__": main()
