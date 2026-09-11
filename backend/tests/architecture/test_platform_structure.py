import ast
from pathlib import Path


ROOT = Path(__file__).parents[2]
NAPMS = ROOT / "src" / "napms"
PLATFORM = NAPMS / "platform"
PYPROJECT = ROOT / "pyproject.toml"


def _imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


def test_production_package_has_final_top_level_taxonomy():
    entries = {path.name for path in NAPMS.iterdir() if path.name != "__pycache__"}
    assert entries == {"__init__.py", "contexts", "workflows", "platform"}
    for legacy in ("bootstrap", "runtime", "composition"):
        assert not (NAPMS / legacy).exists()


def test_console_entrypoints_use_platform_namespaces():
    pyproject = PYPROJECT.read_text(encoding="utf-8")
    assert 'napms-http = "napms.platform.bootstrap.main:run"' in pyproject
    assert 'napms-migrate = "napms.platform.database.cli:run"' in pyproject
    assert 'napms-seed-local = "napms.platform.bootstrap.local_seed:run"' in pyproject


def test_http_main_targets_platform_module():
    source = (PLATFORM / "bootstrap" / "main.py").read_text(encoding="utf-8")
    assert '"napms.platform.bootstrap.main:app"' in source


def test_platform_http_is_generic_and_feature_wiring_is_in_bootstrap():
    http_imports = {
        module
        for path in (PLATFORM / "http").rglob("*.py")
        for module in _imports(path)
    }
    assert not any(
        module.startswith(("napms.contexts", "napms.workflows"))
        for module in http_imports
    )
    assembly_imports = set(_imports(PLATFORM / "bootstrap" / "http_process.py"))
    assert any(module.startswith("napms.contexts") for module in assembly_imports)
    assert any(module.startswith("napms.workflows") for module in assembly_imports)


def test_core_does_not_import_platform():
    violations = []
    roots = tuple((NAPMS / "contexts").glob("*/domain"))
    roots += tuple((NAPMS / "contexts").glob("*/application"))
    roots += tuple((NAPMS / "workflows").glob("*/application"))
    for root in roots:
        for path in root.rglob("*.py"):
            for module in _imports(path):
                if module.startswith("napms.platform"):
                    violations.append((path, module))
    assert violations == []
