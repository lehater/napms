import ast
from pathlib import Path


ROOT = Path(__file__).parents[2]
NEP = (
    ROOT
    / "src"
    / "napms"
    / "contexts"
    / "network_enforcement_placement"
)


def imported_modules(path):
    tree = ast.parse(
        path.read_text(
            encoding="utf-8"
        )
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (
                alias.name
                for alias
                in node.names
            )
        elif (
            isinstance(
                node,
                ast.ImportFrom,
            )
            and node.module
        ):
            yield node.module


def test_nep_core_does_not_import_peer_bounded_contexts():
    violations = []
    for layer_name in (
        "domain",
        "application",
    ):
        for path in (
            NEP / layer_name
        ).rglob("*.py"):
            for module in imported_modules(
                path
            ):
                if (
                    module.startswith(
                        "napms."
                    )
                    and not module.startswith(
                        "napms.contexts.network_enforcement_placement"
                    )
                ):
                    violations.append(
                        (path, module)
                    )
    assert violations == []


def test_nep_postgres_references_only_owned_schema():
    violations = []
    for path in list(
        (
            NEP
            / "infrastructure"
            / "persistence"
            / "postgres"
        ).rglob("*.py")
    ) + list(
        (
            NEP
            / "infrastructure"
            / "persistence"
            / "postgres"
        ).rglob("*.sql")
    ):
        text = path.read_text(
            encoding="utf-8"
        )
        for schema in (
            "napms_access_policy",
            "napms_authority",
            "napms_application_catalogue",
            "napms_resource_catalogue",
            "napms_connectivity_requirements",
            "napms_connectivity_decision",
            "napms_technical_access_evidence",
        ):
            if schema in text:
                violations.append(
                    (path, schema)
                )
    assert violations == []
