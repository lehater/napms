import ast
from pathlib import Path


ROOT = Path(__file__).parents[2]
CORE = ROOT / "src" / "napms" / "access_policy"
DOMAIN = CORE / "domain"
FORBIDDEN_FRAMEWORKS = ("fastapi", "pyodbc", "sqlalchemy", "pydantic", "uvicorn")


def imported_modules(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


def test_access_policy_core_has_no_infrastructure_framework_imports():
    violations = []
    for path in CORE.rglob("*.py"):
        for module in imported_modules(path):
            if module.split(".")[0].lower() in FORBIDDEN_FRAMEWORKS:
                violations.append((path, module))
    assert violations == []


def test_domain_does_not_depend_on_application_layer():
    violations = []
    for path in DOMAIN.rglob("*.py"):
        for module in imported_modules(path):
            if module.startswith("napms.access_policy.application"):
                violations.append((path, module))
    assert violations == []
