#!/usr/bin/env python3
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("docs_v2_harness", HERE / "docs_v2_harness.py")
h = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = h
SPEC.loader.exec_module(h)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def anchor(aid: str, refs: str = "[]", status: str = "ACCEPTED", stage: str = "S1") -> str:
    return f"anchor_id: {aid}\ntype_id: test\nowner_stage: {stage}\nstatus: {status}\nsemantic_refs: {refs}\n"


class HarnessTests(unittest.TestCase):
    def test_resume_loads_state_roadmap_and_current_refs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / "docs/meta/workstream-state.yaml", "roadmap: docs/meta/roadmap.yaml\ncurrent_work:\n  predecessor_ref: docs/evidence.yaml\n")
            write(root / "docs/meta/roadmap.yaml", "id: roadmap\n")
            write(root / "docs/evidence.yaml", "id: evidence\n")
            context = h.load_resume_context(root)
            self.assertEqual(context["roadmap"]["id"], "roadmap")
            self.assertEqual(context["current_refs"]["predecessor_ref"]["id"], "evidence")

    def test_resume_supports_legacy_fixture_namespace(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / "docs-v2/meta/workstream-state.yaml", "roadmap: docs-v2/meta/roadmap.yaml\ncurrent_work: {}\n")
            write(root / "docs-v2/meta/roadmap.yaml", "id: roadmap\n")
            self.assertEqual(h.load_resume_context(root)["roadmap"]["id"], "roadmap")

    def test_reference_validation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / "docs/a.yaml", anchor("A"))
            refs = '[{relation: DERIVES_FROM, target: {kind: anchor-current, anchor_id: A}}]'
            write(root / "docs/b.yaml", anchor("B", refs=refs, stage="S2"))
            anchors = h.discover_anchors(root)
            self.assertEqual(h.validate_references(anchors), [])

    def test_reference_validation_rejects_nonaccepted_current_dependency(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / "docs/a.yaml", anchor("A", status="CANDIDATE"))
            refs = '[{relation: DERIVES_FROM, target: {kind: anchor-current, anchor_id: A}}]'
            write(root / "docs/b.yaml", anchor("B", refs=refs, stage="S2"))
            self.assertTrue(h.validate_references(h.discover_anchors(root)))

    def test_affected_set_is_transitive(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / "docs/a.yaml", anchor("A"))
            write(root / "docs/b.yaml", anchor("B", '[{relation: DERIVES_FROM, target: {kind: anchor-current, anchor_id: A}}]', stage="S2"))
            write(root / "docs/c.yaml", anchor("C", '[{relation: REALIZES, target: {kind: anchor-current, anchor_id: B}}]', stage="S3"))
            self.assertEqual(h.affected_set(h.discover_anchors(root), ["A"]), ["A", "B", "C"])

    def test_readiness(self):
        state = {"blockers": [], "gates": {}, "stage_states": {"S3": "ACCEPTED_CURRENT"}}
        self.assertEqual(h.readiness(state, "G3")["result"], "PASS")
        state["blockers"] = ["x"]
        self.assertEqual(h.readiness(state, "G3")["result"], "BLOCKED")

    def test_human_truth(self):
        self.assertEqual(h.human_truth(True, False)["result"], "NEED_MORE_DATA")
        self.assertEqual(h.human_truth(True, True)["result"], "PASS")

    def test_discovery_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / "docs/a.yaml", anchor("A"))
            self.assertEqual(h.discover_anchors(root), h.discover_anchors(root))

    def test_persistence_is_idempotent_and_docs_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
            write(root / "seed", "1")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
            head = h.git_head(root)
            first = h.persist_files(root, head, {"docs/x.yaml": "id: x\n"}, "change")
            second = h.persist_files(root, head, {"docs/x.yaml": "id: x\n"}, "change")
            self.assertEqual(first["effect"], "committed")
            self.assertEqual(second["effect"], "already-applied")
            self.assertEqual(first["head"], second["head"])
            with self.assertRaises(h.HarnessError):
                h.persist_files(root, second["head"], {"docs-legacy/x": "bad"}, "bad")

    def test_fingerprint_is_deterministic(self):
        a = {"anchor_id": "A", "type_id": "x", "owner_stage": "S1", "canonical_payload": {"b": 2, "a": 1}}
        b = {"canonical_payload": {"a": 1, "b": 2}, "owner_stage": "S1", "type_id": "x", "anchor_id": "A"}
        self.assertEqual(h.semantic_fingerprint(a), h.semantic_fingerprint(b))


if __name__ == "__main__":
    unittest.main()
