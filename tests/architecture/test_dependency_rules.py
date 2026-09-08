import ast
from pathlib import Path


ROOT = Path(__file__).parents[2]
NAPMS = ROOT / "src" / "napms"

ACCESS_POLICY = NAPMS / "access_policy"
AUTHORITY_MANAGEMENT = NAPMS / "authority_management"
APPLICATION_CATALOGUE = NAPMS / "application_catalogue"
RESOURCE_CATALOGUE = NAPMS / "resource_catalogue"
CONNECTIVITY_REQUIREMENTS = NAPMS / "connectivity_requirements"

DOMAIN_LAYERS = (
    ACCESS_POLICY / "domain",
    AUTHORITY_MANAGEMENT / "domain",
    APPLICATION_CATALOGUE / "domain",
    RESOURCE_CATALOGUE / "domain",
    CONNECTIVITY_REQUIREMENTS / "domain",
)
APPLICATION_LAYERS = (
    ACCESS_POLICY / "application",
    AUTHORITY_MANAGEMENT / "application",
    APPLICATION_CATALOGUE / "application",
    RESOURCE_CATALOGUE / "application",
    CONNECTIVITY_REQUIREMENTS / "application",
    NAPMS / "policy_export" / "application",
)
CORE_LAYERS = DOMAIN_LAYERS + APPLICATION_LAYERS

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


def test_core_has_no_infrastructure_framework_imports():
    violations = []
    for layer in CORE_LAYERS:
        for path in layer.rglob("*.py"):
            for module in imported_modules(path):
                if module.split(".")[0].lower() in FORBIDDEN_INFRASTRUCTURE_ROOTS:
                    violations.append((path, module))
    assert violations == []


def test_domain_layers_do_not_depend_on_application_or_adapters():
    violations = []
    for layer in DOMAIN_LAYERS:
        for path in layer.rglob("*.py"):
            for module in imported_modules(path):
                if ".application" in module or ".adapters" in module:
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


POSTGRES_SCHEMA_OWNERS = (
    (
        NAPMS / "access_policy" / "adapters" / "postgres",
        "napms_access_policy",
    ),
    (
        NAPMS / "authority_management" / "adapters" / "postgres",
        "napms_authority",
    ),
    (
        NAPMS / "application_catalogue" / "adapters" / "postgres",
        "napms_application_catalogue",
    ),
    (
        NAPMS / "resource_catalogue" / "adapters" / "postgres",
        "napms_resource_catalogue",
    ),
    (
        NAPMS / "connectivity_requirements" / "adapters" / "postgres",
        "napms_connectivity_requirements",
    ),
)


def test_postgres_modules_do_not_read_or_reference_other_module_schemas():
    all_schemas = {schema for _, schema in POSTGRES_SCHEMA_OWNERS}
    violations = []
    for module_path, owned_schema in POSTGRES_SCHEMA_OWNERS:
        for path in list(module_path.rglob("*.py")) + list(module_path.rglob("*.sql")):
            text = path.read_text(encoding="utf-8")
            for schema in all_schemas - {owned_schema}:
                if schema in text:
                    violations.append((path, owned_schema, schema))
    assert violations == []


BOUNDED_CONTEXT_CORES = (
    (
        ACCESS_POLICY,
        "napms.access_policy",
    ),
    (
        AUTHORITY_MANAGEMENT,
        "napms.authority_management",
    ),
    (
        APPLICATION_CATALOGUE,
        "napms.application_catalogue",
    ),
    (
        RESOURCE_CATALOGUE,
        "napms.resource_catalogue",
    ),
    (
        CONNECTIVITY_REQUIREMENTS,
        "napms.connectivity_requirements",
    ),
)


def test_bounded_context_core_does_not_import_another_bounded_context():
    violations = []
    for context_path, owned_prefix in BOUNDED_CONTEXT_CORES:
        for layer_name in ("domain", "application"):
            layer = context_path / layer_name
            for path in layer.rglob("*.py"):
                for module in imported_modules(path):
                    if (
                        module.startswith("napms.")
                        and not module.startswith(owned_prefix)
                    ):
                        violations.append((path, owned_prefix, module))
    assert violations == []
