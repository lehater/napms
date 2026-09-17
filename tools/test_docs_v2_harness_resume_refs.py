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


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ResumeRefTests(unittest.TestCase):
    def test_resume_loads_current_work_references(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / "docs-v2/meta/workstream-state.yaml", "roadmap: docs-v2/meta/roadmap.yaml\ncurrent_work:\n  phase: H14\n  plan_ref: docs-v2/meta/plan.yaml\n  implementation_state_ref: docs-v2/meta/implementation.yaml\nblockers: []\n")
            write(root / "docs-v2/meta/roadmap.yaml", "id: roadmap\n")
            write(root / "docs-v2/meta/plan.yaml", "id: plan\n")
            write(root / "docs-v2/meta/implementation.yaml", "id: implementation\n")
            context = h.load_resume_context(root)
            self.assertEqual(context["current_refs"]["plan_ref"]["id"], "plan")
            self.assertEqual(context["current_refs"]["implementation_state_ref"]["id"], "implementation")

    def test_resume_rejects_current_work_ref_outside_docs_v2(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / "docs-v2/meta/workstream-state.yaml", "roadmap: docs-v2/meta/roadmap.yaml\ncurrent_work:\n  phase: H14\n  plan_ref: docs/legacy.yaml\nblockers: []\n")
            write(root / "docs-v2/meta/roadmap.yaml", "id: roadmap\n")
            write(root / "docs/legacy.yaml", "id: legacy\n")
            with self.assertRaises(h.HarnessError):
                h.load_resume_context(root)


if __name__ == "__main__":
    unittest.main()
