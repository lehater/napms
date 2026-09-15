#!/usr/bin/env python3
"""Evaluate observed model Skill-routing results against the routing corpus."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "backend" / "tests" / "evals" / "skill-routing-cases.json"
NUMERIC_METRICS = (
    "files_read",
    "skills_loaded",
    "tool_calls_before_first_action",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_observations(path: Path) -> list[dict[str, Any]]:
    data = _load_json(path)
    if not isinstance(data, list) or not data:
        raise ValueError(f"{path}: observations must be a non-empty JSON array")
    rows: list[dict[str, Any]] = []
    ids: set[str] = set()
    for raw in data:
        if not isinstance(raw, dict):
            raise ValueError(f"{path}: every observation must be an object")
        case_id = str(raw.get("id", "")).strip()
        selected = str(raw.get("selected_skill", "")).strip()
        if not case_id or not selected:
            raise ValueError(f"{path}: every observation needs id and selected_skill")
        if case_id in ids:
            raise ValueError(f"{path}: duplicate observation id {case_id}")
        ids.add(case_id)
        for metric in NUMERIC_METRICS:
            if metric in raw:
                value = raw[metric]
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    raise ValueError(f"{path}: {case_id}.{metric} must be a non-negative integer")
        if "stopped_early" in raw and not isinstance(raw["stopped_early"], bool):
            raise ValueError(f"{path}: {case_id}.stopped_early must be boolean")
        rows.append(raw)
    return rows


def _metric_summary(rows: list[dict[str, Any]]) -> dict[str, float]:
    summary: dict[str, float] = {}
    for metric in NUMERIC_METRICS:
        values = [float(row[metric]) for row in rows if metric in row]
        if values:
            summary[f"{metric}.mean"] = statistics.fmean(values)
            summary[f"{metric}.median"] = statistics.median(values)
    early = [row["stopped_early"] for row in rows if "stopped_early" in row]
    if early:
        summary["stopped_early.rate"] = sum(bool(value) for value in early) / len(early)
    return summary


def _print_metrics(label: str, summary: dict[str, float]) -> None:
    if not summary:
        return
    print(f"{label} metrics:")
    for key in sorted(summary):
        print(f"  {key}: {summary[key]:.3f}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path, help="JSON observations from an actual model-routing run")
    parser.add_argument("--baseline", type=Path, help="optional prior observations for metric comparison")
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="allow evaluating only a subset of corpus case ids",
    )
    args = parser.parse_args()

    try:
        cases_raw = _load_json(CASES)
        if not isinstance(cases_raw, list) or not cases_raw:
            raise ValueError("routing corpus must be a non-empty JSON array")
        cases = {str(case["id"]): case for case in cases_raw}
        observations = _load_observations(args.results)
        observed = {str(row["id"]): row for row in observations}

        unknown = sorted(set(observed) - set(cases))
        if unknown:
            raise ValueError("unknown routing case ids: " + ", ".join(unknown))
        missing = sorted(set(cases) - set(observed))
        if missing and not args.allow_partial:
            raise ValueError("missing routing observations: " + ", ".join(missing))

        failures: list[str] = []
        for case_id, row in observed.items():
            case = cases[case_id]
            selected = str(row["selected_skill"])
            expected = str(case["expected_skill"])
            rejected = {str(value) for value in case.get("not_expected_skills", [])}
            if selected != expected:
                failures.append(
                    f"{case_id}: selected {selected!r}, expected {expected!r}"
                )
            if selected in rejected:
                failures.append(
                    f"{case_id}: selected explicitly rejected Skill {selected!r}"
                )

        total = len(observed)
        passed = total - len({failure.split(":", 1)[0] for failure in failures})
        print(f"Model routing observations: {passed}/{total} cases matched expected Skill")
        _print_metrics("current", _metric_summary(observations))

        if args.baseline:
            baseline = _load_observations(args.baseline)
            baseline_summary = _metric_summary(baseline)
            current_summary = _metric_summary(observations)
            _print_metrics("baseline", baseline_summary)
            shared = sorted(set(current_summary) & set(baseline_summary))
            if shared:
                print("metric delta (current - baseline; lower is better for these metrics):")
                for key in shared:
                    print(f"  {key}: {current_summary[key] - baseline_summary[key]:+.3f}")

        if failures:
            print("Routing evaluation failed:", file=sys.stderr)
            for failure in failures:
                print(f"  - {failure}", file=sys.stderr)
            return 1
        return 0

    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Skill routing result evaluation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
