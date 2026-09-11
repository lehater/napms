import ast
from pathlib import Path


ROOT = Path(__file__).parents[2]
NAPMS = ROOT / "src" / "napms"

ACCESS_POLICY = NAPMS / "access_policy"
ACCESS_POLICY_REALIZATION = NAPMS / "access_policy_realization"
AUTHORITY_MANAGEMENT = NAPMS / "authority_management"
APPLICATION_CATALOGUE = NAPMS / "application_catalogue"
RESOURCE_CATALOGUE = NAPMS / "resource_catalogue"
CONNECTIVITY_REQUIREMENTS = NAPMS / "connectivity_requirements"
CONNECTIVITY_DECISION = NAPMS / "connectivity_decision"
TECHNICAL_ACCESS_EVIDENCE = NAPMS / "technical_access_evidence"
NETWORK_ENFORCEMENT_PLACEMENT = NAPMS / "network_enforcement_placement"
REQUIREMENT_POLICY_ALIGNMENT = NAPMS / "requirement_policy_alignment"
POLICY_EXPORT = NAPMS / "policy_export"
SCOPED_CONNECTIVITY_INVENTORY = NAPMS / "scoped_connectivity_inventory"
RUNTIME = NAPMS / "runtime"
APPLICATION_CATALOGUE_HTTP = APPLICATION_CATALOGUE / "adapters" / "http"
RESOURCE_CATALOGUE_HTTP = RESOURCE_CATALOGUE / "adapters" / "http"
APPLICATION_CATALOGUE_HTTP_SUPPORT = APPLICATION_CATALOGUE_HTTP / "support.py"
RESOURCE_CATALOGUE_HTTP_SUPPORT = RESOURCE_CATALOGUE_HTTP / "support.py"
CONNECTIVITY_REQUIREMENTS_HTTP = CONNECTIVITY_REQUIREMENTS / "adapters" / "http.py"
CONNECTIVITY_DECISION_HTTP = CONNECTIVITY_DECISION / "adapters" / "http.py"
ACCESS_POLICY_HTTP = ACCESS_POLICY / "adapters" / "http.py"
REQUIREMENT_POLICY_ALIGNMENT_HTTP = REQUIREMENT_POLICY_ALIGNMENT / "adapters" / "http.py"
POLICY_EXPORT_HTTP = POLICY_EXPORT / "adapters" / "http.py"
POLICY_EXPORT_HTTP_JSON = POLICY_EXPORT / "adapters" / "http_json.py"
SCOPED_CONNECTIVITY_HTTP = SCOPED_CONNECTIVITY_INVENTORY / "adapters" / "http.py"
PROCESS_HTTP = RUNTIME / "http_api.py"

DOMAIN_LAYERS = (
    ACCESS_POLICY / "domain",
    ACCESS_POLICY_REALIZATION / "domain",
    AUTHORITY_MANAGEMENT / "domain",
    APPLICATION_CATALOGUE / "domain",
    RESOURCE_CATALOGUE / "domain",
    CONNECTIVITY_REQUIREMENTS / "domain",
    CONNECTIVITY_DECISION / "domain",
    TECHNICAL_ACCESS_EVIDENCE / "domain",
    NETWORK_ENFORCEMENT_PLACEMENT / "domain",
)
APPLICATION_LAYERS = (
    ACCESS_POLICY / "application",
    ACCESS_POLICY_REALIZATION / "application",
    AUTHORITY_MANAGEMENT / "application",
    APPLICATION_CATALOGUE / "application",
    RESOURCE_CATALOGUE / "application",
    CONNECTIVITY_REQUIREMENTS / "application",
    CONNECTIVITY_DECISION / "application",
    TECHNICAL_ACCESS_EVIDENCE / "application",
    NETWORK_ENFORCEMENT_PLACEMENT / "application",
    REQUIREMENT_POLICY_ALIGNMENT / "application",
    POLICY_EXPORT / "application",
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


def _route_names(path: Path, receiver: str) -> set[str]:
    names = set()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        for decorator in getattr(node, "decorator_list", ()):
            if not (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and isinstance(decorator.func.value, ast.Name)
                and decorator.func.value.id == receiver
            ):
                continue
            for keyword in decorator.keywords:
                if (
                    keyword.arg == "name"
                    and isinstance(keyword.value, ast.Constant)
                    and isinstance(keyword.value.value, str)
                ):
                    names.add(keyword.value.value)
    return names


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


def test_semantic_owner_adapters_do_not_depend_on_process_http_assembly():
    violations = []
    adapter_roots = sorted(
        path / "adapters"
        for path in NAPMS.iterdir()
        if path.is_dir() and (path / "adapters").is_dir()
    )
    for adapter_root in adapter_roots:
        for path in adapter_root.rglob("*.py"):
            for module in imported_modules(path):
                if module == "napms.runtime.http_api":
                    violations.append((path, module))
    assert violations == []


def test_application_catalogue_target_http_is_owner_local():
    assert (APPLICATION_CATALOGUE_HTTP / "target.py").is_file()
    assert (APPLICATION_CATALOGUE_HTTP / "target_retirement.py").is_file()
    assert not (RUNTIME / "catalogue_target_http.py").exists()
    assert not (RUNTIME / "catalogue_target_retirement_http.py").exists()


def test_catalogue_http_endpoints_are_not_implemented_in_runtime():
    assert list(RUNTIME.glob("catalogue_*_http.py")) == []


def test_catalogue_owner_http_packages_exist():
    assert APPLICATION_CATALOGUE_HTTP.is_dir()
    assert RESOURCE_CATALOGUE_HTTP.is_dir()


def test_catalogue_http_support_is_owner_local():
    assert APPLICATION_CATALOGUE_HTTP_SUPPORT.is_file()
    assert RESOURCE_CATALOGUE_HTTP_SUPPORT.is_file()
    runtime_support = (RUNTIME / "http_support.py").read_text(encoding="utf-8")
    forbidden_vocabulary = (
        "InvalidCatalogueTime",
        "InvalidCatalogueInterval",
        "CatalogueAuthorityDenied",
        "CatalogueMutationFailed",
        "CataloguePersistenceOutcomeUnknown",
    )
    assert all(value not in runtime_support for value in forbidden_vocabulary)


def test_policy_export_json_serialization_is_owner_local():
    assert POLICY_EXPORT_HTTP_JSON.is_file()
    assert not (RUNTIME / "normalized_policy_json.py").exists()


def test_feature_http_is_owner_local():
    for path in (
        ACCESS_POLICY_HTTP,
        CONNECTIVITY_REQUIREMENTS_HTTP,
        CONNECTIVITY_DECISION_HTTP,
        REQUIREMENT_POLICY_ALIGNMENT_HTTP,
        POLICY_EXPORT_HTTP,
        SCOPED_CONNECTIVITY_HTTP,
    ):
        assert path.is_file()
    assert not (RUNTIME / "legacy_http_api.py").exists()


def test_process_http_has_no_feature_endpoint_implementation():
    forbidden_prefixes = (
        "napms.access_policy.application",
        "napms.access_policy.domain",
        "napms.connectivity_requirements.application",
        "napms.connectivity_requirements.domain",
        "napms.connectivity_decision.application",
        "napms.connectivity_decision.domain",
        "napms.requirement_policy_alignment.application",
        "napms.policy_export.application",
        "napms.scoped_connectivity_inventory.application",
    )
    assert all(
        not module.startswith(forbidden_prefixes)
        for module in imported_modules(PROCESS_HTTP)
    )


def test_process_http_has_only_direct_process_routes():
    assert _route_names(PROCESS_HTTP, "app") == {
        "CreateSession",
        "GetSession",
        "DeleteSession",
        "Liveness",
        "Readiness",
    }


def test_semantic_adapters_do_not_import_process_http_api():
    violations = []
    for path in NAPMS.glob("*/adapters/**/*.py"):
        for module in imported_modules(path):
            if module == "napms.runtime.http_api":
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
    (
        NAPMS / "connectivity_decision" / "adapters" / "postgres",
        "napms_connectivity_decision",
    ),
    (
        NAPMS / "technical_access_evidence" / "adapters" / "postgres",
        "napms_technical_access_evidence",
    ),
    (
        NAPMS / "network_enforcement_placement" / "adapters" / "postgres",
        "napms_network_enforcement_placement",
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
        ACCESS_POLICY_REALIZATION,
        "napms.access_policy_realization",
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
    (
        CONNECTIVITY_DECISION,
        "napms.connectivity_decision",
    ),
    (
        TECHNICAL_ACCESS_EVIDENCE,
        "napms.technical_access_evidence",
    ),
    (
        NETWORK_ENFORCEMENT_PLACEMENT,
        "napms.network_enforcement_placement",
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


def test_alignment_application_does_not_import_source_bounded_contexts():
    violations = []
    layer = REQUIREMENT_POLICY_ALIGNMENT / "application"
    for path in layer.rglob("*.py"):
        for module in imported_modules(path):
            if module.startswith(
                (
                    "napms.connectivity_requirements",
                    "napms.access_policy",
                )
            ):
                violations.append((path, module))
    assert violations == []
