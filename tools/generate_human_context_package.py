#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = Path(os.environ.get("HARNESS_ROOT", ROOT / ".harness-tool"))
if not (HARNESS_ROOT / "engineering_graph.py").exists():
    raise SystemExit(
        "Pinned Harness runtime not found. Set HARNESS_ROOT or checkout the pinned "
        "lehater/harness commit into .harness-tool."
    )

sys.path.insert(0, str(HARNESS_ROOT))
from human_projection import compile_manifest, realize_projection_model  # noqa: E402

GRAPH = ROOT / "docs/canonical-graph.yaml"
PROJECTION = ROOT / "docs/harness-projection.yaml"
ENGINEERING = ROOT / "docs/harness-engineering-graph.yaml"
DEFAULT_OUT = ROOT / "docs-generated/implementation-package"

SECTIONS = {
    "discovery": "01-product",
    "product-requirements": "01-product",
    "strategic-model": "02-domain",
    "use-case": "02-domain",
    "domain-language": "02-domain",
    "domain-decisions": "02-domain",
    "domain-process": "02-domain",
    "tactical-domain-model": "02-domain",
    "cross-context-use-case": "03-application",
    "ui-navigation-model": "03-application",
    "ui-screen-contract": "03-application",
    "structural-architecture": "04-architecture",
    "application-architecture-rules": "04-architecture",
    "module-contract-design": "04-architecture",
    "security-architecture": "04-architecture",
    "shared-technical-conventions": "05-interfaces",
    "contract-requirements": "05-interfaces",
    "http-contract": "05-interfaces",
    "physical-persistence-model": "06-data",
    "quality-requirements": "07-quality",
    "threat-model": "07-quality",
    "observability-requirements": "07-quality",
    "component-design": "08-implementation",
    "implementation-plan": "08-implementation",
    "test-intent": "09-verification",
}


def load(path: Path):
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path.relative_to(ROOT)} must be a mapping")
    return value


def resolve(consumer_id: str):
    source = load(GRAPH)
    projection = load(PROJECTION)
    engineering = load(ENGINEERING)
    model = realize_projection_model(
        engineering,
        consumer_id=consumer_id,
        source_graph=source,
        projection=projection,
    )
    manifest = compile_manifest(
        engineering,
        model,
        consumer_id,
        harness_version=(ROOT / ".harness-version").read_text(encoding="utf-8").strip(),
        source_root=ROOT,
    )

    node_by_id = {item["id"]: item for item in source["nodes"]}
    nodes = [
        node_by_id[item["artifact"]]
        for item in manifest["sources"]
        if item["artifact"] in node_by_id
    ]
    return manifest, manifest["direct_provider_artifacts"], nodes

def render_readme(consumer_id, roots, nodes):
    lines = [
        "# Implementation Documentation Package",
        "",
        "> Generated view. Do not edit. Canonical sources are listed below.",
        "",
        "Consumer: " + consumer_id,
        "",
        "Scope: selected Consumer capability closure",
        "",
        "This is the human-readable control view of the exact canonical knowledge resolved for implementation.",
        "",
        "## Direct resolved provider artifacts",
        "",
    ]
    lines += ["- " + item for item in roots]
    lines += ["", "## Resolved canonical knowledge", ""]
    lines += [
        "- **" + node["id"].replace("-", " ").title() + "** — " + node["path"]
        for node in nodes
    ]
    lines += [
        "",
        "## Reading rule",
        "",
        "This package owns no engineering truth. Edit the canonical source and regenerate this projection. "
        "The sources directory is a snapshot of the resolved canonical artifacts; manifest.yaml records "
        "the exact dependency closure used to build this package.",
        "",
    ]
    return "\n".join(lines)


def materialize(consumer_id, out):
    manifest, roots, nodes = resolve(consumer_id)
    if out.exists():
        shutil.rmtree(out)
    sources = out / "sources"
    human = out / "human"
    sources.mkdir(parents=True)
    human.mkdir(parents=True)
    (out / "manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )
    (out / "README.md").write_text(
        render_readme(consumer_id, roots, nodes), encoding="utf-8"
    )
    nl = "\n"
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
        body = src.read_text(encoding="utf-8").rstrip()
        rendered = (
            "# " + node["id"].replace("-", " ").title() + nl + nl
            + "> Generated view. Do not edit. Canonical source: " + node["path"] + nl + nl
            + "Artifact kind: " + node["kind"] + nl + nl
            + "## Canonical content" + nl + nl + "~~~yaml" + nl
            + body + nl + "~~~" + nl
        )
        human_doc.write_text(rendered, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--consumer", default="BACKEND-IMPLEMENTATION")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    materialize(args.consumer, Path(args.out))


if __name__ == "__main__":
    main()
