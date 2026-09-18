#!/usr/bin/env python3
from pathlib import Path
import argparse,tempfile,yaml

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"docs/architecture/persistence/mvp-persistence.yaml"
OUT=ROOT/"docs-generated/architecture"

def esc(v):
    return str(v).replace("\\","\\\\").replace('"','\\"').replace("\n","\\n")

def alias(schema,table):
    return (schema+"__"+table).replace("-","_")

def render(m):
    lines=[
      "@startuml",
      "' GENERATED FILE - DO NOT EDIT",
      f"' Semantic authority: {SOURCE.relative_to(ROOT)}",
      "title NAPMS MVP Physical Persistence ERD",
      "hide circle",
      "skinparam shadowing false",
    ]
    fks=[]
    for schema,sdef in m["schemas"].items():
        lines.append(f'package "{esc(schema)}" {{')
        for table,tdef in sdef["tables"].items():
            a=alias(schema,table)
            lines.append(f'  entity "{esc(table)}" as {a} {{')
            for c in tdef["columns"]:
                marker="*" if c.get("primary_key") else ("+" if not c.get("nullable",True) else "")
                ext=f" <<owner-ref:{c['external_owner']}>>" if c.get("external_owner") else ""
                lines.append(f'    {marker} {esc(c["name"])} : {esc(c["type"])}{ext}')
            lines.append("  }")
            for fk in tdef.get("local_foreign_keys",[]):
                rs,rt=fk["references"].split(".",1)
                label=",".join(fk["columns"])
                fks.append((a,alias(rs,rt),label))
        lines.append("}")
    lines.append("")
    for src,dst,label in fks:
        lines.append(f'{src} }}o--|| {dst} : "{esc(label)}"')
    lines += [
      "",
      "legend left",
      "  Only same-module database foreign keys are drawn.",
      "  <<owner-ref:...>> columns are cross-module UUID references resolved through owner contracts, not database FKs.",
      "  This ERD is generated from the canonical physical persistence model.",
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
        path=OUT/"mvp-persistence-erd.puml"
        expected=render(m)
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"generated projection is stale: {path.relative_to(ROOT)}; run make design-sync")
        print(f"checked {path.relative_to(ROOT)}")
    else:
        OUT.mkdir(parents=True,exist_ok=True)
        path=OUT/"mvp-persistence-erd.puml"
        path.write_text(render(m),encoding="utf-8")
        print(f"generated {path.relative_to(ROOT)}")

if __name__=="__main__":
    main()
