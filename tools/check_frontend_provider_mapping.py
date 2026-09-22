#!/usr/bin/env python3
"""Validate NAPMS presentation-provider realization against canonical screen patterns."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = Path(os.environ.get("HARNESS_ROOT", ROOT / ".harness-tool"))
if not (HARNESS_ROOT / "frontend_screen_contracts.py").exists():
    raise SystemExit("Pinned Harness checkout with frontend_screen_contracts.py is required")
sys.path.insert(0, str(HARNESS_ROOT))

from frontend_screen_contracts import evaluate_presentation_provider_contract  # noqa: E402


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected mapping")
    return value


def main() -> int:
    presentation = load_yaml(ROOT / "docs/contracts/ui/mvp-presentation-system.yaml")
    screens = load_yaml(ROOT / "docs/contracts/ui/mvp-screen-view-design.yaml")
    components = load_yaml(ROOT / "docs/architecture/mvp-frontend-component-design.yaml")
    provider = components.get("presentation_provider")
    if not isinstance(provider, dict):
        print("frontend provider mapping: missing presentation_provider in Component Design")
        return 1

    coverage = {
        item
        for item in (provider.get("coverage_screens", []) or [])
        if isinstance(item, str) and item
    }
    if not coverage:
        print("frontend provider mapping: coverage_screens must name the migrated screen scope")
        return 1

    findings = evaluate_presentation_provider_contract(
        presentation,
        screens,
        provider,
        screen_ids=coverage,
    )
    if findings:
        print("frontend provider mapping: REJECTED")
        for item in findings:
            print(f"- {item['code']}: {item['detail']}")
        return 1

    print(
        "frontend provider mapping: PASS "
        f"(provider={provider.get('provider')} screens={','.join(sorted(coverage))})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
