#!/usr/bin/env python3
from pathlib import Path
import argparse,tempfile,yaml

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"docs/model/use-cases/first-mvp-policy-export.yaml"
OUT=ROOT/"docs-generated/architecture"

def esc(v):
    return str(v).replace("\\","\\\\").replace('"','\\"').replace("\n","\\n")

def render(m):
    lines=[
      "@startuml",
      "' GENERATED FILE - DO NOT EDIT",
      f"' Semantic authority: {SOURCE.relative_to(ROOT)}",
      "title First MVP Vendor-Neutral Policy Export",
      "skinparam shadowing false",
      "start",
    ]
    for step in m["cross_context_flow"]:
        lines.append(f':{esc(step["owner"])}\n{esc(step["result"])};')
    lines += [
      "stop",
      "",
      "legend left",
      f'  Goal: {esc(m["goal"])}',
      f'  Composition: {esc(m["workflow_composition"]["name"])} (non-peer)',
      "  Generated view contains no independent truth.",
      "endlegend",
      "@enduml",
      ""
    ]
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    m=yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    if a.check:
        with tempfile.TemporaryDirectory(prefix="napms-mvp-journey-") as tmp:
            path=Path(tmp)/"first-mvp-policy-export.puml"
            path.write_text(render(m),encoding="utf-8")
            print(f"generated {path}")
    else:
        OUT.mkdir(parents=True,exist_ok=True)
        path=OUT/"first-mvp-policy-export.puml"
        path.write_text(render(m),encoding="utf-8")
        print(f"generated {path.relative_to(ROOT)}")

if __name__=="__main__":
    main()
