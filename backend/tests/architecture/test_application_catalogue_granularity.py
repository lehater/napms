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
CURATION = APPLICATION / "curation"
STRUCTURE_EXPORTS = CURATION / "structure.py"
APPLICATION_MUTATIONS = CURATION / "application_structure.py"
COMPONENT_MUTATIONS = CURATION / "component_structure.py"
SHARED_MUTATION = CURATION / "mutation.py"


def test_structure_mutations_are_split_by_owner():
    assert APPLICATION_MUTATIONS.is_file()
    assert COMPONENT_MUTATIONS.is_file()
    assert SHARED_MUTATION.is_file()

    application_source = APPLICATION_MUTATIONS.read_text(encoding="utf-8")
    component_source = COMPONENT_MUTATIONS.read_text(encoding="utf-8")

    assert "class RenameApplication" in application_source
    assert "class RetireApplication" in application_source
    assert "class CreateComponent" not in application_source

    assert "class CreateComponent" in component_source
    assert "class RenameComponent" in component_source
    assert "class RetireComponent" in component_source
    assert "class RenameApplication" not in component_source


def test_structure_exports_contain_no_use_case_implementation():
    tree = ast.parse(STRUCTURE_EXPORTS.read_text(encoding="utf-8"))
    implementation_nodes = (
        ast.ClassDef,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
    )
    violations = [
        node.name
        for node in tree.body
        if isinstance(node, implementation_nodes)
    ]
    assert violations == []
