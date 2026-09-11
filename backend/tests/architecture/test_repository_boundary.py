import ast
from pathlib import Path


BACKEND = Path(__file__).parents[2]
REPOSITORY = BACKEND.parent
SRC = BACKEND / "src"


def imported_modules(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


def test_legacy_repository_shapes_are_not_present():
    assert not (REPOSITORY / "apps").exists()
    assert not (REPOSITORY / "legacy").exists()
    assert not (REPOSITORY / "prototype").exists()


def test_backend_owns_python_package_and_tests():
    assert (BACKEND / "pyproject.toml").is_file()
    assert (BACKEND / "Dockerfile").is_file()
    assert SRC.is_dir()
    assert (BACKEND / "tests").is_dir()
    assert not (REPOSITORY / "pyproject.toml").exists()
    assert not (REPOSITORY / "Dockerfile").exists()
    assert not (REPOSITORY / "src").exists()
    assert not (REPOSITORY / "tests").exists()


def test_product_source_uses_napms_package_not_old_napm_package():
    violations = []
    for path in SRC.rglob("*.py"):
        for module in imported_modules(path):
            if module == "napm" or module.startswith("napm."):
                violations.append((path, module))
    assert violations == []
