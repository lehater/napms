from pathlib import Path
import re


ROOT = Path(__file__).parents[3]
WEB = ROOT / "web" / "src"
FEATURES = WEB / "features"


def _entries(path: Path) -> set[str]:
    return {entry.name for entry in path.iterdir()}


def _source_files(path: Path):
    yield from path.rglob("*.ts")
    yield from path.rglob("*.tsx")


def test_web_source_has_final_root_taxonomy():
    assert _entries(WEB) == {"app", "features", "components", "lib", "vite-env.d.ts"}
    assert _entries(WEB / "components") == {"ui"}


def test_legacy_root_and_shared_component_locations_are_absent():
    for legacy in ("api.ts", "App.tsx", "main.tsx", "index.css"):
        assert not (WEB / legacy).exists()
    assert not (WEB / "components" / "layout").exists()
    assert not (WEB / "components" / "catalogue").exists()


def test_feature_roots_only_contain_locality_directories():
    allowed = {"api", "model", "components", "pages"}
    for feature in FEATURES.iterdir():
        assert feature.is_dir()
        assert _entries(feature) <= allowed
        assert all(entry.is_dir() for entry in feature.iterdir())


def test_frontend_does_not_import_removed_root_api():
    violations = [
        path.relative_to(WEB)
        for path in _source_files(WEB)
        if re.search(r'from\s+["\']@/api["\']', path.read_text(encoding="utf-8"))
    ]
    assert violations == []


def test_lib_does_not_depend_on_app_or_features():
    violations = []
    for path in _source_files(WEB / "lib"):
        source = path.read_text(encoding="utf-8")
        if re.search(r'from\s+["\']@/(?:app|features)/', source):
            violations.append(path.relative_to(WEB))
    assert violations == []
