import ast
from pathlib import Path


ROOT = Path(__file__).parents[2]
NAPMS = ROOT / "src" / "napms"
CONTEXTS = NAPMS / "contexts"

ACCESS_POLICY = NAPMS / "contexts" / "access_policy"
ACCESS_POLICY_REALIZATION = NAPMS / "contexts" / "access_policy_realization"
AUTHORITY_MANAGEMENT = NAPMS / "contexts" / "authority_management"
APPLICATION_CATALOGUE = NAPMS / "contexts" / "application_catalogue"
RESOURCE_CATALOGUE = NAPMS / "contexts" / "resource_catalogue"
CONNECTIVITY_REQUIREMENTS = NAPMS / "contexts" / "connectivity_requirements"
CONNECTIVITY_DECISION = NAPMS / "contexts" / "connectivity_decision"
TECHNICAL_ACCESS_EVIDENCE = NAPMS / "contexts" / "technical_access_evidence"
NETWORK_ENFORCEMENT_PLACEMENT = NAPMS / "contexts" / "network_enforcement_placement"
NETWORK_ENVIRONMENT_OPERATIONS = NAPMS / "contexts" / "network_environment_operations"
WORKFLOWS = NAPMS / "workflows"
REQUIREMENT_POLICY_ALIGNMENT = WORKFLOWS / "requirement_policy_alignment"
POLICY_EXPORT = WORKFLOWS / "policy_export"
SCOPED_CONNECTIVITY_INVENTORY = WORKFLOWS / "scoped_connectivity_inventory"
NETWORK_OPERATOR_VIEW = WORKFLOWS / "network_operator_view"
TRAFFIC_ANALYSIS = WORKFLOWS / "traffic_analysis"
ACC_TARGET_INTEGRATIONS = (
    APPLICATION_CATALOGUE / "infrastructure" / "integrations" / "target_dependencies.py"
)
ACC_TARGET_READ_MODEL = (
    APPLICATION_CATALOGUE
    / "infrastructure"
    / "read_models"
    / "postgres"
    / "target.py"
)
PLATFORM_HTTP = NAPMS / "platform" / "http"
APPLICATION_CATALOGUE_HTTP = APPLICATION_CATALOGUE / "presentation" / "http"
RESOURCE_CATALOGUE_HTTP = RESOURCE_CATALOGUE / "presentation" / "http"
APPLICATION_CATALOGUE_HTTP_SUPPORT = APPLICATION_CATALOGUE_HTTP / "support.py"
RESOURCE_CATALOGUE_HTTP_SUPPORT = RESOURCE_CATALOGUE_HTTP / "support.py"
CONNECTIVITY_REQUIREMENTS_HTTP = (
    CONNECTIVITY_REQUIREMENTS / "presentation" / "http" / "routes.py"
)
CONNECTIVITY_DECISION_HTTP = (
    CONNECTIVITY_DECISION / "presentation" / "http" / "routes.py"
)
ACCESS_POLICY_HTTP = ACCESS_POLICY / "presentation" / "http" / "routes.py"
REQUIREMENT_POLICY_ALIGNMENT_HTTP = (
    REQUIREMENT_POLICY_ALIGNMENT / "presentation" / "http" / "routes.py"
)
POLICY_EXPORT_HTTP = POLICY_EXPORT / "presentation" / "http" / "routes.py"
POLICY_EXPORT_HTTP_JSON = POLICY_EXPORT / "presentation" / "http" / "json.py"
SCOPED_CONNECTIVITY_HTTP = (
    SCOPED_CONNECTIVITY_INVENTORY / "presentation" / "http" / "routes.py"
)
NETWORK_OPERATOR_VIEW_HTTP = (
    NETWORK_OPERATOR_VIEW / "presentation" / "http" / "routes.py"
)
PROCESS_HTTP = PLATFORM_HTTP / "api.py"

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
    NETWORK_ENVIRONMENT_OPERATIONS / "domain",
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
    NETWORK_ENVIRONMENT_OPERATIONS / "application",
    REQUIREMENT_POLICY_ALIGNMENT / "application",
    POLICY_EXPORT / "application",
    SCOPED_CONNECTIVITY_INVENTORY / "application",
    NETWORK_OPERATOR_VIEW / "application",
    TRAFFIC_ANALYSIS / "application",
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

CONTEXT_ROOT_ENTRIES = {
    "__init__.py",
    "domain",
    "application",
    "infrastructure",
    "presentation",
}
WORKFLOW_ROOT_ENTRIES = {
    "__init__.py",
    "application",
    "infrastructure",
    "presentation",
}


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


def test_domain_layers_do_not_depend_on_application_or_outer_layers():
    violations = []
    for layer in DOMAIN_LAYERS:
        for path in layer.rglob("*.py"):
            for module in imported_modules(path):
                if (
                    ".application" in module
                    or ".infrastructure" in module
                    or ".presentation" in module
                ):
                    violations.append((path, module))
    assert violations == []


def test_context_core_has_no_outer_layer_dependencies():
    violations = []
    for context in CONTEXTS.iterdir():
        if not context.is_dir() or context.name == "__pycache__":
            continue
        for layer_name in ("domain", "application"):
            for path in (context / layer_name).rglob("*.py"):
                for module in imported_modules(path):
                    if ".infrastructure" in module or ".presentation" in module:
                        violations.append((path, module))
    assert violations == []


def test_context_roots_use_only_final_layers():
    violations = []
    for context in CONTEXTS.iterdir():
        if not context.is_dir() or context.name == "__pycache__":
            continue
        unexpected = {
            path.name
            for path in context.iterdir()
            if path.name != "__pycache__" and path.name not in CONTEXT_ROOT_ENTRIES
        }
        if unexpected:
            violations.append((context, unexpected))
    assert violations == []


def test_workflow_roots_use_only_final_layers():
    violations = []
    for workflow in WORKFLOWS.iterdir():
        if not workflow.is_dir() or workflow.name == "__pycache__":
            continue
        unexpected = {
            path.name
            for path in workflow.iterdir()
            if path.name != "__pycache__" and path.name not in WORKFLOW_ROOT_ENTRIES
        }
        if unexpected:
            violations.append((workflow, unexpected))
    assert violations == []


def test_forbidden_structural_buckets_are_absent_globally():
    violations = [
        path
        for path in NAPMS.rglob("*")
        if path.is_dir() and path.name in {"adapters", "composition"}
    ]
    assert violations == []


def test_application_catalogue_target_http_is_owner_local():
    assert (APPLICATION_CATALOGUE_HTTP / "target.py").is_file()
    assert (APPLICATION_CATALOGUE_HTTP / "target_retirement.py").is_file()
    assert not (PLATFORM_HTTP / "catalogue_target_http.py").exists()
    assert not (PLATFORM_HTTP / "catalogue_target_retirement_http.py").exists()


def test_catalogue_http_endpoints_are_not_implemented_in_runtime():
    assert list(PLATFORM_HTTP.glob("catalogue_*_http.py")) == []


def test_catalogue_owner_http_packages_exist():
    assert APPLICATION_CATALOGUE_HTTP.is_dir()
    assert RESOURCE_CATALOGUE_HTTP.is_dir()


def test_catalogue_http_support_is_owner_local():
    assert APPLICATION_CATALOGUE_HTTP_SUPPORT.is_file()
    assert RESOURCE_CATALOGUE_HTTP_SUPPORT.is_file()
    runtime_support = (PLATFORM_HTTP / "support.py").read_text(encoding="utf-8")
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
    assert not (PLATFORM_HTTP / "normalized_policy_json.py").exists()


def test_feature_http_is_owner_local():
    for path in (
        ACCESS_POLICY_HTTP,
        CONNECTIVITY_REQUIREMENTS_HTTP,
        CONNECTIVITY_DECISION_HTTP,
        REQUIREMENT_POLICY_ALIGNMENT_HTTP,
        POLICY_EXPORT_HTTP,
        SCOPED_CONNECTIVITY_HTTP,
        NETWORK_OPERATOR_VIEW_HTTP,
    ):
        assert path.is_file()
    assert not (PLATFORM_HTTP / "legacy_http_api.py").exists()


def test_process_http_has_no_feature_endpoint_implementation():
    forbidden_prefixes = (
        "napms.contexts.access_policy.application",
        "napms.contexts.access_policy.domain",
        "napms.contexts.connectivity_requirements.application",
        "napms.contexts.connectivity_requirements.domain",
        "napms.contexts.connectivity_decision.application",
        "napms.contexts.connectivity_decision.domain",
        "napms.workflows.requirement_policy_alignment.application",
        "napms.workflows.policy_export.application",
        "napms.workflows.scoped_connectivity_inventory.application",
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


POSTGRES_SCHEMA_OWNERS = (
    (
        ACCESS_POLICY / "infrastructure" / "persistence" / "postgres",
        "napms_access_policy",
    ),
    (
        AUTHORITY_MANAGEMENT / "infrastructure" / "persistence" / "postgres",
        "napms_authority",
    ),
    (
        APPLICATION_CATALOGUE / "infrastructure" / "persistence" / "postgres",
        "napms_application_catalogue",
    ),
    (
        RESOURCE_CATALOGUE / "infrastructure" / "persistence" / "postgres",
        "napms_resource_catalogue",
    ),
    (
        CONNECTIVITY_REQUIREMENTS / "infrastructure" / "persistence" / "postgres",
        "napms_connectivity_requirements",
    ),
    (
        CONNECTIVITY_DECISION / "infrastructure" / "persistence" / "postgres",
        "napms_connectivity_decision",
    ),
    (
        TECHNICAL_ACCESS_EVIDENCE / "infrastructure" / "persistence" / "postgres",
        "napms_technical_access_evidence",
    ),
    (
        NETWORK_ENFORCEMENT_PLACEMENT
        / "infrastructure"
        / "persistence"
        / "postgres",
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
        "napms.contexts.access_policy",
    ),
    (
        ACCESS_POLICY_REALIZATION,
        "napms.contexts.access_policy_realization",
    ),
    (
        AUTHORITY_MANAGEMENT,
        "napms.contexts.authority_management",
    ),
    (
        APPLICATION_CATALOGUE,
        "napms.contexts.application_catalogue",
    ),
    (
        RESOURCE_CATALOGUE,
        "napms.contexts.resource_catalogue",
    ),
    (
        CONNECTIVITY_REQUIREMENTS,
        "napms.contexts.connectivity_requirements",
    ),
    (
        CONNECTIVITY_DECISION,
        "napms.contexts.connectivity_decision",
    ),
    (
        TECHNICAL_ACCESS_EVIDENCE,
        "napms.contexts.technical_access_evidence",
    ),
    (
        NETWORK_ENFORCEMENT_PLACEMENT,
        "napms.contexts.network_enforcement_placement",
    ),
    (
        NETWORK_ENVIRONMENT_OPERATIONS,
        "napms.contexts.network_environment_operations",
    ),
)


def test_workflow_application_has_no_outer_layer_dependencies():
    violations = []
    for workflow in (
        REQUIREMENT_POLICY_ALIGNMENT,
        POLICY_EXPORT,
        SCOPED_CONNECTIVITY_INVENTORY,
        NETWORK_OPERATOR_VIEW,
        TRAFFIC_ANALYSIS,
    ):
        for path in (workflow / "application").rglob("*.py"):
            for module in imported_modules(path):
                if ".infrastructure" in module or ".presentation" in module:
                    violations.append((path, module))
    assert violations == []


def test_workflows_do_not_import_context_persistence_internals():
    violations = []
    for path in WORKFLOWS.rglob("*.py"):
        for module in imported_modules(path):
            if module.startswith("napms.contexts.") and ".infrastructure.persistence" in module:
                violations.append((path, module))
    assert violations == []


def test_acc_target_integrations_use_only_peer_application_contracts():
    violations = []
    for module in imported_modules(ACC_TARGET_INTEGRATIONS):
        if not module.startswith("napms.contexts."):
            continue
        if module.startswith("napms.contexts.application_catalogue."):
            continue
        if ".domain" in module or ".infrastructure" in module:
            violations.append(module)
    assert violations == []


def test_acc_target_read_model_has_no_resource_catalogue_sql():
    assert "napms_resource_catalogue" not in ACC_TARGET_READ_MODEL.read_text(
        encoding="utf-8"
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
                    "napms.contexts.connectivity_requirements",
                    "napms.contexts.access_policy",
                )
            ):
                violations.append((path, module))
    assert violations == []
