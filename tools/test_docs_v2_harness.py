import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("docs_v2_harness.py")
SPEC = importlib.util.spec_from_file_location("docs_v2_harness", MODULE_PATH)
h = importlib.util.module_from_spec(SPEC)
sys.modules["docs_v2_harness"] = h
SPEC.loader.exec_module(h)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def anchor(anchor_id: str, refs: str = "[]", status: str = "ACCEPTED", stage: str = "S1") -> str:
    return f"anchor_id: {anchor_id}\ntype_id: functional-requirement\nowner_stage: {stage}\nstatus: {status}\ncanonical_payload: {{value: x}}\nsemantic_refs: {refs}\n"


class HarnessTests(unittest.TestCase):
    def test_resume_from_repository_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / "docs-v2/meta/workstream-state.yaml", "roadmap: docs-v2/meta/roadmap.yaml\ncurrent_work: {phase: H14}\nblockers: []\n")
            write(root / "docs-v2/meta/roadmap.yaml", "id: roadmap\n")
            self.assertEqual(h.load_resume_context(root)["workstream"]["current_work"]["phase"], "H14")

    def test_dangling_reference_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / "docs-v2/a.yaml", anchor("A", "[{relation: DERIVES_FROM, target: {kind: anchor-current, anchor_id: MISSING}}]"))
            self.assertTrue(any("dangling" in error for error in h.validate_references(h.discover_anchors(root))))

    def test_affected_set_is_transitive_and_excludes_unrelated(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / "docs-v2/a.yaml", anchor("A"))
            write(root / "docs-v2/b.yaml", anchor("B", "[{relation: DERIVES_FROM, target: {kind: anchor-current, anchor_id: A}}]", stage="S2"))
            write(root / "docs-v2/c.yaml", anchor("C", "[{relation: REFINES, target: {kind: anchor-current, anchor_id: B}}]", stage="S3"))
            write(root / "docs-v2/x.yaml", anchor("X"))
            self.assertEqual(set(h.affected_set(h.discover_anchors(root), ["A"])), {"A", "B", "C"})

    def test_readiness_without_separate_transaction(self):
        state = {"blockers": [], "stage_states": {"S2": "ACCEPTED_CURRENT"}, "gates": {"G2": "NOT_EVALUATED"}}
        self.assertEqual(h.readiness(state, "G2")["result"], "PASS")

    def test_missing_stage_routes_rework(self):
        self.assertEqual(h.readiness({"blockers": [], "stage_states": {}, "gates": {}}, "G3")["result"], "REWORK")

    def test_stale_head_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
            write(root / "a", "1")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "one"], cwd=root, check=True)
            old = h.git_head(root)
            write(root / "a", "2")
            subprocess.run(["git", "commit", "-qam", "two"], cwd=root, check=True)
            with self.assertRaises(h.ConflictError):
                h.assert_expected_head(root, old)

    def test_missing_human_truth_routes_need_more_data(self):
        self.assertEqual(h.human_truth(True, False)["result"], "NEED_MORE_DATA")

    def test_generated_index_is_rebuildable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / "docs-v2/a.yaml", anchor("A"))
            self.assertEqual(h.discover_anchors(root), h.discover_anchors(root))

    def test_persistence_is_idempotent_and_docs_v2_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
            write(root / "seed", "1")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
            head = h.git_head(root)
            first = h.persist_files(root, head, {"docs-v2/x.yaml": "id: x\n"}, "change")
            second = h.persist_files(root, head, {"docs-v2/x.yaml": "id: x\n"}, "change")
            self.assertEqual(first["effect"], "committed")
            self.assertEqual(second["effect"], "already-applied")
            self.assertEqual(first["head"], second["head"])
            with self.assertRaises(h.HarnessError):
                h.persist_files(root, second["head"], {"docs/x": "bad"}, "bad")

    def test_fingerprint_is_deterministic(self):
        a = {"anchor_id": "A", "type_id": "x", "owner_stage": "S1", "canonical_payload": {"b": 2, "a": 1}}
        b = {"canonical_payload": {"a": 1, "b": 2}, "owner_stage": "S1", "type_id": "x", "anchor_id": "A"}
        self.assertEqual(h.semantic_fingerprint(a), h.semantic_fingerprint(b))


if __name__ == "__main__":
    unittest.main()
