from pathlib import Path


ROOT = Path(__file__).parents[2]
NAPMS = ROOT / "src" / "napms"
BOOTSTRAP = NAPMS / "bootstrap"
RUNTIME = NAPMS / "runtime"
PYPROJECT = ROOT / "pyproject.toml"


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


def test_runtime_does_not_retain_bootstrap_compatibility_facades():
    for name in ("main.py", "config.py", "composition.py", "migrations.py", "local_seed.py"):
        assert not (RUNTIME / name).exists()


def test_bootstrap_main_targets_bootstrap_module():
    source = (BOOTSTRAP / "main.py").read_text(encoding="utf-8")
    assert '"napms.bootstrap.main:app"' in source
    assert "napms.runtime.main:app" not in source


def test_platform_support_is_separate_from_legacy_executable_bootstrap():
    platform = NAPMS / "platform"
    assert (platform / "bootstrap" / "greenfield.py").is_file()
    assert (platform / "database" / "migrations.py").is_file()
    assert not (NAPMS / "composition").exists()
    assert (BOOTSTRAP / "composition.py").is_file()
