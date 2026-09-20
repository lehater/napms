#!/usr/bin/env python3
from pathlib import Path
import argparse,tempfile,yaml

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"docs/model/contexts/access-policy/domain-model.yaml"
OUT=ROOT/"docs-generated/architecture"

def esc(v):
    return str(v).replace("\\","\\\\").replace('"','\\\"').replace("\n","\\n")

def render(m):
    lines=[
        "@startuml",
        "' GENERATED FILE - DO NOT EDIT",
        f"' Semantic authority: {SOURCE.relative_to(ROOT)}",
        "title Access Policy Domain Model",
        "skinparam shadowing false",
    ]
    for i,name in enumerate(m.get("aggregates",[]),1):
        lines.append(f'rectangle "{esc(name)}" as A{i} <<Aggregate>>')
    for i,name in enumerate(m.get("entities",[]),1):
        lines.append(f'rectangle "{esc(name)}" as E{i} <<Entity/History>>')
    lines += ["","legend left","  |= Invariant |"]
    lines += [f"  | {esc(x)} |" for x in m["invariants"]]
    lines += ["  |= Public semantics |"]
    lines += [f"  | {esc(x)} |" for x in m["public_semantics"]]
    lines += ["endlegend","@enduml",""]
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
    m=yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    if a.check:
        with tempfile.TemporaryDirectory(prefix="napms-ap-view-") as tmp:
            path=Path(tmp)/"access-policy-domain.puml";path.write_text(render(m),encoding="utf-8");print(f"generated {path}")
    else:
        OUT.mkdir(parents=True,exist_ok=True);path=OUT/"access-policy-domain.puml";path.write_text(render(m),encoding="utf-8");print(f"generated {path.relative_to(ROOT)}")
if __name__=="__main__": main()
