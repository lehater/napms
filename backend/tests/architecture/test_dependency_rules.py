from __future__ import annotations

import ast
from pathlib import Path


CONTEXT_ROOT = Path(__file__).parents[2] / "src" / "napms" / "contexts"
FORBIDDEN_TECHNICAL_IMPORTS = (
    "fastapi",
    "starlette",
    "psycopg",
    "pydantic",
)


def _imports(path: Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            found.append(node.module)
    return tuple(found)


def test_contexts_do_not_import_platform() -> None:
    violations: list[str] = []
    for path in CONTEXT_ROOT.rglob("*.py"):
        for imported in _imports(path):
            if imported == "napms.platform" or imported.startswith("napms.platform."):
                violations.append(f"{path.relative_to(CONTEXT_ROOT)} -> {imported}")
    assert not violations, "\n".join(violations)


def test_domain_and_application_are_technical_framework_free() -> None:
    violations: list[str] = []
    for path in CONTEXT_ROOT.rglob("*.py"):
        if not {"domain", "application"}.intersection(path.parts):
            continue
        for imported in _imports(path):
            if imported.startswith(FORBIDDEN_TECHNICAL_IMPORTS):
                violations.append(f"{path.relative_to(CONTEXT_ROOT)} -> {imported}")
    assert not violations, "\n".join(violations)
