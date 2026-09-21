#!/usr/bin/env python3
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
NAVIGATION = ROOT / "docs/contracts/ui/mvp-navigation.yaml"
PRESENTATION = ROOT / "docs/contracts/ui/mvp-presentation-system.yaml"
SCREENS = ROOT / "docs/contracts/ui/mvp-screen-view-design.yaml"

def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def fail(errors, message):
    errors.append(message)

def main() -> int:
    errors = []
    navigation = load(NAVIGATION)
    presentation = load(PRESENTATION)
    screens = load(SCREENS)

    navigation_ids = [item["id"] for item in navigation.get("workspaces", [])]
    presentation_ids = list(presentation.get("scope", {}).get("surfaces", []))
    screen_rows = screens.get("screens", [])
    screen_ids = [item.get("id") for item in screen_rows]

    if len(screen_ids) != len(set(screen_ids)):
        fail(errors, "screen/view contract contains duplicate screen ids")

    if set(screen_ids) != set(navigation_ids):
        missing = sorted(set(navigation_ids) - set(screen_ids))
        extra = sorted(set(screen_ids) - set(navigation_ids))
        if missing:
            fail(errors, "screen/view contract missing navigation workspaces: " + ", ".join(missing))
        if extra:
            fail(errors, "screen/view contract contains non-canonical workspaces: " + ", ".join(extra))

    if set(presentation_ids) != set(navigation_ids):
        missing = sorted(set(navigation_ids) - set(presentation_ids))
        extra = sorted(set(presentation_ids) - set(navigation_ids))
        if missing:
            fail(errors, "Presentation System scope missing workspaces: " + ", ".join(missing))
        if extra:
            fail(errors, "Presentation System scope contains non-canonical workspaces: " + ", ".join(extra))

    inherited = screens.get("inherits")
    expected = presentation.get("id")
    if inherited != expected:
        fail(errors, f"screen/view design inherits {inherited!r}; expected {expected!r}")

    pattern_ids = set((presentation.get("patterns") or {}).keys())
    for row in screen_rows:
        screen_id = row.get("id", "<unknown>")
        if not row.get("purpose"):
            fail(errors, f"{screen_id}: purpose is required")
        if not row.get("regions"):
            fail(errors, f"{screen_id}: at least one region is required")
        if not row.get("states"):
            fail(errors, f"{screen_id}: state variants are required")
        if "overrides" not in row:
            fail(errors, f"{screen_id}: overrides must be explicit, even when empty")
        for pattern in row.get("patterns", []) or []:
            if pattern not in pattern_ids:
                fail(errors, f"{screen_id}: unknown Presentation System pattern {pattern}")
        for region in row.get("regions", []) or []:
            pattern = region.get("pattern")
            if pattern and pattern not in pattern_ids:
                fail(errors, f"{screen_id}: region {region.get('id')} references unknown pattern {pattern}")

    coverage = screens.get("coverage", {})
    coverage_ids = coverage.get("required_workspaces", []) or []
    if set(coverage_ids) != set(navigation_ids):
        fail(errors, "screen/view coverage.required_workspaces must equal canonical navigation workspace inventory")

    if errors:
        print("Frontend design closure validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Frontend design closure PASS: {len(screen_ids)} workspaces inherit {expected}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
