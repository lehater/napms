#!/usr/bin/env python3
from __future__ import annotations
import copy, os, shutil, sys, tempfile
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
HARNESS=Path(os.environ.get("HUMAN_PROJECTION_HARNESS", ROOT/".human-projection-harness"))
sys.path.insert(0,str(HARNESS))
from engineering_graph import evaluate_engineering_target
from human_projection import compile_manifest, materialize_package, validate_projection_ir, validate_recipe
from integration_alignment import validate_project_alignment
from harness import CoreError

def load(path):
    return yaml.safe_load((ROOT/path).read_text(encoding="utf-8"))

def expect_error(fn, contains):
    try:
        fn()
    except CoreError as exc:
        assert contains in str(exc), (contains, str(exc))
    else:
        raise AssertionError(f"expected CoreError containing {contains!r}")


def synthetic_ir(plan):
    return {
        "version": 1,
        "kind": "harness-human-projection-ir",
        "manifest_digest": plan["manifest_digest"],
        "documents": [
            {
                "id": document["id"],
                "sections": [
                    {
                        "id": section["id"],
                        "claims": [
                            {
                                "text": f"Research projection for {section['title']}.",
                                "sources": [section["sources"][0]],
                            }
                        ],
                    }
                    for section in document["sections"]
                ],
            }
            for document in plan["documents"]
        ],
    }


def main():
    source=load("docs/canonical-graph.yaml")
    projection=load("docs/harness-projection.yaml")
    graph=load("docs/harness-engineering-graph.yaml")

    aligned=validate_project_alignment(source,projection,graph,target_consumer="BACKEND-IMPLEMENTATION")
    model=aligned["model"]

    backend=compile_manifest(graph,model,"BACKEND-IMPLEMENTATION",harness_version="research-prototype",project_revision="napms-research",recipe_id="napms-backend-human-docs",source_root=ROOT)
    assert backend["target"]["status"]=="COMPLETE", backend["target"]
    plan=validate_recipe(load("docs/research/human-projection/backend.yaml"),backend)
    assert [d["id"] for d in plan["documents"]]==[
        "overview","domain","architecture-and-interfaces","quality-and-operations","implementation-and-verification"
    ]
    assert len(backend["sources"])>10
    assert not backend["unresolved"]

    backend_ir=load("docs/research/human-projection/backend-narrative-ir.yaml")
    backend_ir["manifest_digest"]=plan["manifest_digest"]

    with tempfile.TemporaryDirectory() as temp_dir:
        review=Path(temp_dir)/"review"
        result=materialize_package(
            backend,
            plan,
            backend_ir,
            review,
            mode="REVIEW",
        )
        assert result["documents"]==[
            "architecture-and-interfaces.md",
            "domain.md",
            "implementation-and-verification.md",
            "overview.md",
            "quality-and-operations.md",
        ], result

        handoff=Path(temp_dir)/"handoff"
        handoff_result=materialize_package(
            backend,
            plan,
            backend_ir,
            handoff,
            mode="HANDOFF",
            source_root=ROOT,
        )
        assert len(handoff_result["sources"])==len(backend["sources"])
        assert (handoff/"manifest.yaml").is_file()
        assert (handoff/"sources/docs/canonical-graph.yaml").exists() is False

    evidence_plan=validate_recipe(
        load("docs/research/human-projection/evidence-sample.yaml"),
        backend,
    )
    evidence_ir=load("docs/research/human-projection/evidence-sample-ir.yaml")
    evidence_ir["manifest_digest"]=evidence_plan["manifest_digest"]
    validate_projection_ir(
        evidence_ir,
        evidence_plan,
        manifest=backend,
        source_root=ROOT,
        require_evidence=True,
    )

    # Controlled regeneration experiment: mutate one canonical quality fact in
    # an isolated source snapshot. Old IR must fail first on manifest digest,
    # and even a digest-only rebind must fail because the evidence excerpt is stale.
    with tempfile.TemporaryDirectory() as temp_dir:
        source_copy=Path(temp_dir)/"sources"
        for item in backend["sources"]:
            src=ROOT/item["path"]
            dst=source_copy/item["path"]
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(src,dst)

        quality=source_copy/"docs/architecture/mvp-quality-requirements.yaml"
        quality_text=quality.read_text(encoding="utf-8")
        old_excerpt="Numeric latency throughput availability and scale targets are explicitly NOT_REQUIRED, not unknown."
        new_excerpt="Numeric latency throughput availability and scale targets are explicitly REQUIRED for this controlled research mutation."
        assert old_excerpt in quality_text
        quality.write_text(quality_text.replace(old_excerpt,new_excerpt),encoding="utf-8")

        mutated_manifest=compile_manifest(
            graph,
            model,
            "BACKEND-IMPLEMENTATION",
            harness_version="research-prototype",
            project_revision="napms-controlled-mutation",
            source_root=source_copy,
        )
        mutated_plan=validate_recipe(
            load("docs/research/human-projection/evidence-sample.yaml"),
            mutated_manifest,
        )

        stale_ir=copy.deepcopy(evidence_ir)
        expect_error(
            lambda: validate_projection_ir(
                stale_ir,
                mutated_plan,
                manifest=mutated_manifest,
                source_root=source_copy,
                require_evidence=True,
            ),
            "manifest digest does not match",
        )

        digest_only=copy.deepcopy(evidence_ir)
        digest_only["manifest_digest"]=mutated_plan["manifest_digest"]
        expect_error(
            lambda: validate_projection_ir(
                digest_only,
                mutated_plan,
                manifest=mutated_manifest,
                source_root=source_copy,
                require_evidence=True,
            ),
            "excerpt not found",
        )

        regenerated=copy.deepcopy(digest_only)
        quality_claim=regenerated["documents"][0]["sections"][2]["claims"][0]
        quality_claim["text"]="Numeric latency, throughput, availability and scale targets are required in this controlled research mutation."
        quality_claim["evidence"][0]["excerpt"]=new_excerpt
        validate_projection_ir(
            regenerated,
            mutated_plan,
            manifest=mutated_manifest,
            source_root=source_copy,
            require_evidence=True,
        )

    frontend=compile_manifest(graph,model,"FRONTEND-IMPLEMENTATION",harness_version="research-prototype",project_revision="napms-research",source_root=ROOT)
    assert frontend["target"]["status"]=="READY", frontend["target"]
    unresolved={item["capability"] for item in frontend["unresolved"]}
    assert "engineering.frontend.human-interface" in unresolved, unresolved
    assert "engineering.frontend.human-interface" in frontend["target"]["create"], frontend["target"]

    # Existing project-local package generator remains benchmark/evidence during research.
    assert (ROOT/"tools/generate_human_context_package.py").is_file()

    print("NAPMS human projection research PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
