import ast
from pathlib import Path


ROOT = Path(__file__).parents[2]
ACCESS_POLICY = ROOT / "src" / "napms" / "access_policy"
DOMAIN = ACCESS_POLICY / "domain"
APPLICATION = ACCESS_POLICY / "application"
POLICY_EXPORT_APPLICATION = ROOT / "src" / "napms" / "policy_export" / "application"
CORE_LAYERS = (DOMAIN, APPLICATION, POLICY_EXPORT_APPLICATION)
FORBIDDEN_INFRASTRUCTURE_ROOTS = (
    "fastapi",
    "psycopg",
    "pyodbc",
    "sqlalchemy",
    "pydantic",
    "uvicorn",
)


def imported_modules(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


def test_access_policy_core_has_no_infrastructure_framework_imports():
    violations = []
    for layer in CORE_LAYERS:
        for path in layer.rglob("*.py"):
            for module in imported_modules(path):
                if module.split(".")[0].lower() in FORBIDDEN_INFRASTRUCTURE_ROOTS:
                    violations.append((path, module))
    assert violations == []


def test_domain_does_not_depend_on_application_layer():
    violations = []
    for path in DOMAIN.rglob("*.py"):
        for module in imported_modules(path):
            if module.startswith("napms.access_policy.application"):
                violations.append((path, module))
    assert violations == []


def test_core_does_not_depend_on_adapter_layer():
    violations = []
    for layer in CORE_LAYERS:
        for path in layer.rglob("*.py"):
            for module in imported_modules(path):
                if ".adapters" in module:
                    violations.append((path, module))
    assert violations == []
