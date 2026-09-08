import ast
from pathlib import Path


ROOT = Path(__file__).parents[2]
SRC = ROOT / "src"


def imported_modules(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


def test_legacy_repository_shapes_are_not_present():
    assert not (ROOT / "apps").exists()
    assert not (ROOT / "legacy").exists()
    assert not (ROOT / "prototype").exists()


def test_product_source_uses_napms_package_not_old_napm_package():
    violations = []
    for path in SRC.rglob("*.py"):
        for module in imported_modules(path):
            if module == "napm" or module.startswith("napm."):
                violations.append((path, module))
    assert violations == []
