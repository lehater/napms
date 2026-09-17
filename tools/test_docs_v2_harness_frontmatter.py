import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("docs_v2_harness.py")
SPEC = importlib.util.spec_from_file_location("docs_v2_harness", MODULE_PATH)
h = importlib.util.module_from_spec(SPEC)
sys.modules["docs_v2_harness"] = h
SPEC.loader.exec_module(h)

class FrontMatterAnchorTests(unittest.TestCase):
    def test_markdown_front_matter_anchor_resolves_yaml_dependency(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            d = root / "docs-v2"
            d.mkdir()
            (d / "requirement.md").write_text("---\nanchor_id: REQ\ntype_id: functional-requirement\nowner_stage: S1\nstatus: ACCEPTED\nsemantic_refs: []\n---\n# Requirement\n", encoding="utf-8")
            (d / "model.yaml").write_text("anchor_id: MODEL\ntype_id: domain-model\nowner_stage: S2\nstatus: ACCEPTED\nsemantic_refs:\n  - relation: DERIVES_FROM\n    target: {kind: anchor-current, anchor_id: REQ}\n", encoding="utf-8")
            anchors = h.discover_anchors(root)
            self.assertEqual(set(anchors), {"REQ", "MODEL"})
            self.assertEqual(h.validate_references(anchors), [])

    def test_unterminated_front_matter_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            d = root / "docs-v2"
            d.mkdir()
            (d / "bad.md").write_text("---\nanchor_id: BAD\n", encoding="utf-8")
            with self.assertRaises(h.HarnessError):
                h.discover_anchors(root)

if __name__ == "__main__":
    unittest.main()
