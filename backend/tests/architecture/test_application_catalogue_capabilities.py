import ast
from pathlib import Path


ROOT = Path(__file__).parents[2]
APPLICATION = (
    ROOT
    / "src"
    / "napms"
    / "contexts"
    / "application_catalogue"
    / "application"
)
CAPABILITIES = ("curation", "discovery", "target")
OLD_FLAT_MODULES = {
    "application_structure_curation.py",
    "binding_curation.py",
    "component_structure_curation.py",
    "curation.py",
    "curation_detail.py",
    "curation_mutation.py",
    "curation_read.py",
    "dcs_curation.py",
    "deployment_curation.py",
    "describe_interactions.py",
    "list_interactions.py",
    "participant_discovery.py",
    "resolve.py",
    "structure_curation.py",
    "target_binding_curation.py",
    "target_curation.py",
    "target_lifecycle.py",
    "target_metadata_curation.py",
    "target_ports.py",
    "target_read.py",
    "target_retirement.py",
    "target_selection_read.py",
    "target_structure_curation.py",
}


def _imported_modules(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


def test_application_root_contains_only_shared_ports_and_capabilities():
    assert {path.name for path in APPLICATION.iterdir() if path.name != "__pycache__"} == {
        "__init__.py",
        "ports.py",
        *CAPABILITIES,
    }
    assert all((APPLICATION / capability / "__init__.py").is_file() for capability in CAPABILITIES)


def test_old_flat_application_modules_are_absent():
    assert not OLD_FLAT_MODULES.intersection(path.name for path in APPLICATION.glob("*.py"))


def test_application_capabilities_do_not_depend_on_each_other_across_boundaries():
    forbidden = {
        "target": ("curation", "discovery"),
        "curation": ("target",),
        "discovery": ("target",),
    }
    violations = []
    prefix = "napms.contexts.application_catalogue.application."
    for capability, forbidden_capabilities in forbidden.items():
        for path in (APPLICATION / capability).rglob("*.py"):
            for module in _imported_modules(path):
                if module.startswith(tuple(prefix + value for value in forbidden_capabilities)):
                    violations.append((path, module))
    assert violations == []
