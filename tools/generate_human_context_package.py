#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "docs/harness-core.yaml"
GRAPH = ROOT / "docs/canonical-graph.yaml"
DEFAULT_OUT = ROOT / "docs-generated/implementation-package"
SECTIONS = {
    "discovery": "01-product", "product-requirements": "01-product",
    "strategic-model": "02-domain", "use-case": "02-domain", "domain-language": "02-domain",
    "domain-decisions": "02-domain", "domain-process": "02-domain", "tactical-domain-model": "02-domain",
    "cross-context-use-case": "03-application", "ui-navigation-model": "03-application", "ui-screen-contract": "03-application",
    "structural-architecture": "04-architecture", "application-architecture-rules": "04-architecture",
    "module-contract-design": "04-architecture", "security-architecture": "04-architecture",
    "shared-technical-conventions": "05-interfaces", "contract-requirements": "05-interfaces", "http-contract": "05-interfaces",
    "physical-persistence-model": "06-data", "quality-requirements": "07-quality", "threat-model": "07-quality",
    "observability-requirements": "07-quality", "implementation-plan": "08-implementation", "test-intent": "09-verification",
}

def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def resolve(consumer_id):
    harness, graph = load(HARNESS), load(GRAPH)
    providers = {}
    for item in harness.get("artifact_providers", []):
        for capability in item.get("provides", []):
            providers[capability] = item["artifact"]
    contracts = {item["id"]: item for item in harness.get("input_contracts", [])}
    if consumer_id not in contracts:
        raise SystemExit("Unknown consumer/input contract: " + consumer_id)
    node_by_id = {item["id"]: item for item in graph["nodes"]}
    roots, unresolved = [], []
    for requirement in contracts[consumer_id].get("requires", []):
        capability = requirement["capability"]
        artifact = providers.get(capability)
        if not artifact:
            unresolved.append(capability)
        elif artifact in node_by_id:
            roots.append(artifact)
    if unresolved:
        raise SystemExit("Unresolved capabilities: " + ", ".join(sorted(unresolved)))
    closure = set()
    def visit(node_id):
        if node_id in closure:
            return
        closure.add(node_id)
        for dep in node_by_id[node_id].get("depends_on", []):
            visit(dep)
    for root in roots:
        visit(root)
    return roots, [node for node in graph["nodes"] if node["id"] in closure]

def render_readme(consumer_id, roots, nodes):
    lines = [
        "# Implementation Documentation Package", "",
        "> Generated view. Do not edit. Canonical sources are listed below.", "",
        "Consumer: " + consumer_id, "",
        "This is the human-readable control view of the exact canonical knowledge resolved for implementation.", "",
        "## Direct consumer artifacts", ""
    ]
    lines += ["- " + item for item in roots]
    lines += ["", "## Resolved canonical knowledge", ""]
    lines += ["- **" + node["id"].replace("-", " ").title() + "** — " + node["path"] for node in nodes]
    lines += ["", "## Reading rule", "",
        "This package owns no engineering truth. Edit the canonical source and regenerate this projection. "
        "The sources directory is a snapshot of the resolved canonical artifacts; manifest.yaml records "
        "the exact dependency closure used to build this package.", ""]
    return "
".join(lines)

def materialize(consumer_id, out):
    roots, nodes = resolve(consumer_id)
    if out.exists():
        shutil.rmtree(out)
    sources = out / "sources"
    human = out / "human"
    sources.mkdir(parents=True)
    human.mkdir(parents=True)
    manifest = {
        "version": 1,
        "kind": "human-context-package-manifest",
        "consumer": consumer_id,
        "generated_from": ["docs/harness-core.yaml", "docs/canonical-graph.yaml"],
        "direct_artifacts": roots,
        "artifacts": [{"id": n["id"], "kind": n["kind"], "canonical_path": n["path"]} for n in nodes],
    }
    (out / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (out / "README.md").write_text(render_readme(consumer_id, roots, nodes), encoding="utf-8")
    for node in nodes:
        src = ROOT / node["path"]
        if not src.exists():
            raise SystemExit("Canonical artifact does not exist: " + node["path"])
        dst = sources / node["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        section = SECTIONS.get(node["kind"], "99-reference")
        human_dir = human / section
        human_dir.mkdir(parents=True, exist_ok=True)
        human_doc = human_dir / (node["id"].lower() + ".md")
        body = src.read_text(encoding="utf-8")
        human_doc.write_text(
            "# " + node["id"].replace("-", " ").title() + "\
\
"
            "> Generated view. Do not edit. Canonical source: `" + node["path"] + "`\
\
"
            "Artifact kind: `" + node["kind"] + "`\
\
"
            "## Canonical content\
\
```yaml\
" + body.rstrip() + "\
```\
",
            encoding="utf-8",
        )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--consumer", default="IMPLEMENTATION-CONSUMER")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    materialize(args.consumer, Path(args.out))

if __name__ == "__main__":
    main()
