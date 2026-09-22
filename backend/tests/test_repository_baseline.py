from importlib import import_module


def test_canonical_backend_roots_are_importable() -> None:
    assert import_module("napms.contexts") is not None
    assert import_module("napms.platform") is not None
