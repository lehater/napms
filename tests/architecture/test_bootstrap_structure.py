import ast
from pathlib import Path


ROOT = Path(__file__).parents[2]
NAPMS = ROOT / "src" / "napms"
BOOTSTRAP = NAPMS / "bootstrap"
RUNTIME = NAPMS / "runtime"
PYPROJECT = ROOT / "pyproject.toml"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_executable_process_entrypoints_live_under_bootstrap():
    for name in ("main.py", "config.py", "composition.py", "migrations.py", "local_seed.py"):
        assert (BOOTSTRAP / name).is_file()

    pyproject = PYPROJECT.read_text(encoding="utf-8")
    assert 'napms-http = "napms.bootstrap.main:run"' in pyproject
    assert 'napms-migrate = "napms.bootstrap.migrations:run"' in pyproject
    assert 'napms-seed-local = "napms.bootstrap.local_seed:run"' in pyproject
    assert "napms.runtime.main:run" not in pyproject
    assert "napms.runtime.migrations:run" not in pyproject
    assert "napms.runtime.local_seed:run" not in pyproject


def test_runtime_bootstrap_names_are_compatibility_facades_only():
    for name in ("main.py", "config.py", "composition.py", "migrations.py", "local_seed.py"):
        path = RUNTIME / name
        source = path.read_text(encoding="utf-8")
        assert "Compatibility facade" in source
        imports = _imports(path)
        assert imports
        assert all(module.startswith("napms.bootstrap") for module in imports)


def test_bootstrap_main_targets_bootstrap_module():
    source = (BOOTSTRAP / "main.py").read_text(encoding="utf-8")
    assert '"napms.bootstrap.main:app"' in source
    assert "napms.runtime.main:app" not in source


def test_composition_support_remains_separate_from_executable_bootstrap():
    composition = NAPMS / "composition"
    assert (composition / "greenfield_postgres.py").is_file()
    assert (composition / "postgres_migrations.py").is_file()
    assert (BOOTSTRAP / "composition.py").is_file()
