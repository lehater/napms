import ast
from pathlib import Path


ROOT = Path(__file__).parents[2]
APR = (
    ROOT
    / "src"
    / "napms"
    / "access_policy_realization"
)
TAE = (
    ROOT
    / "src"
    / "napms"
    / "contexts"
    / "technical_access_evidence"
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
                for alias in node.names
            )
        elif (
            isinstance(
                node,
                ast.ImportFrom,
            )
            and node.module
        ):
            yield node.module


def test_apr_adapters_do_not_bypass_peer_persistence():
    violations = []
    for path in (
        APR / "adapters"
    ).rglob("*.py"):
        for module in imported_modules(
            path
        ):
            if (
                module == "psycopg"
                or ".adapters.postgres"
                in module
            ):
                violations.append(
                    (path, module)
                )
    assert violations == []


def test_tae_does_not_depend_on_apr():
    violations = []
    for path in TAE.rglob("*.py"):
        for module in imported_modules(
            path
        ):
            if module.startswith(
                "napms.access_policy_realization"
            ):
                violations.append(
                    (path, module)
                )
    assert violations == []
