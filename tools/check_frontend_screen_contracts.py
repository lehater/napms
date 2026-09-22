#!/usr/bin/env python3
from pathlib import Path
import os
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = Path(os.environ.get("HARNESS_ROOT", ROOT / ".harness-tool")).resolve()
sys.path.insert(0, str(HARNESS_ROOT))

from frontend_screen_contracts import evaluate_frontend_screen_contracts  # noqa: E402

PRESENTATION = ROOT / "docs/contracts/ui/mvp-presentation-system.yaml"
SCREENS = ROOT / "docs/contracts/ui/mvp-screen-view-design.yaml"
OPENAPI = ROOT / "docs/contracts/http/napms.openapi.yaml"


def load(path: Path):
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected mapping")
    return value


def main() -> int:
    presentation = load(PRESENTATION)
    screens = load(SCREENS)
    openapi = load(OPENAPI)

    pilot = screens.get("coverage", {}).get("semantic_contract_pilot", {})
    proven = set(pilot.get("proven", []) or [])
    remaining = set(pilot.get("remaining", []) or [])
    inventory = {row.get("id") for row in screens.get("screens", []) or []}

    errors = []
    if not proven:
        errors.append("semantic_contract_pilot.proven must identify the evaluated screens")
    if proven & remaining:
        errors.append("semantic_contract_pilot proven/remaining sets overlap")
    if proven | remaining != inventory:
        errors.append("semantic_contract_pilot proven + remaining must equal the canonical screen inventory")

    result = evaluate_frontend_screen_contracts(
        presentation,
        screens,
        openapi,
        screen_ids=proven,
    )
    if result["status"] != "ACCEPTED":
        for finding in result["findings"]:
            errors.append(
                f"{finding.get('screen', '<presentation>')}: "
                f"{finding['code']}: {finding['detail']}"
            )

    if errors:
        print("Frontend screen semantic closure failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(
        "Frontend screen semantic closure PASS: "
        f"{len(proven)} proven pilot screens; {len(remaining)} explicitly remaining"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
