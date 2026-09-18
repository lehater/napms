#!/usr/bin/env python3
from pathlib import Path
import argparse
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/model/contexts/application-communication-catalogue/domain-model.yaml"
DEFAULT_OUT = ROOT / "docs-generated/architecture"

def load(path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)

def esc(v):
    return str(v).replace("\\","\\\\").replace('"','\\"').replace("\n","\\n")

def render(model):
    lines = [
        "@startuml",
        "' GENERATED FILE - DO NOT EDIT",
        f"' Semantic authority: {SOURCE.relative_to(ROOT)}",
        "title Application Communication Catalogue Domain Model",
        "skinparam shadowing false",
        f'rectangle "{esc(model["aggregate"])}" as Aggregate <<Aggregate>>',
    ]
    for idx, entity in enumerate(model["entities"], start=1):
        lines.append(f'rectangle "{esc(entity)}" as E{idx} <<Entity>>')
    lines += ["", "legend left", "  No associations are inferred from the accepted source.", "  |= Invariant |"]
    for inv in model["invariants"]:
        lines.append(f"  | {esc(inv)} |")
    lines.append("  |= Public semantics |")
    for item in model["public_semantics"]:
        lines.append(f"  | {esc(item)} |")
    lines += ["endlegend","@enduml",""]
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); a=p.parse_args()
    model=load(SOURCE)
    if a.check:
        with tempfile.TemporaryDirectory(prefix="napms-acc-view-") as tmp:
            path=Path(tmp)/"application-communication-catalogue-domain.puml"
            path.write_text(render(model),encoding="utf-8")
            print(f"generated {path}")
    else:
        DEFAULT_OUT.mkdir(parents=True,exist_ok=True)
        path=DEFAULT_OUT/"application-communication-catalogue-domain.puml"
        path.write_text(render(model),encoding="utf-8")
        print(f"generated {path.relative_to(ROOT)}")

if __name__=="__main__":
    main()
