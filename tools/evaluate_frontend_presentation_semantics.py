#!/usr/bin/env python3
"""Deterministic semantic acceptance for NAPMS frontend presentation knowledge.

This validator proves design-knowledge sufficiency, not implementation conformance.
It emits Harness semantic evaluations consumed by Engineering Coverage. Product and
domain semantics remain owned by their canonical artifacts.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PRESENTATION = ROOT / "docs/contracts/ui/mvp-presentation-system.yaml"
SCREENS = ROOT / "docs/contracts/ui/mvp-screen-view-design.yaml"
VERIFICATION = ROOT / "docs/plans/mvp-frontend-verification.yaml"
TOKENS = ROOT / "docs/contracts/ui/mvp-design-tokens.json"
OPENAPI = ROOT / "docs/contracts/http/napms.openapi.yaml"

_harness_candidates = []
if os.environ.get("HARNESS_ROOT"):
    _harness_candidates.append(Path(os.environ["HARNESS_ROOT"]))
_harness_candidates.extend([ROOT / ".harness-tool", ROOT / ".harness-coverage-tool"])
HARNESS_ROOT = next(
    (path for path in _harness_candidates if (path / "frontend_screen_contracts.py").exists()),
    None,
)
if HARNESS_ROOT is None:
    raise SystemExit("Pinned Harness checkout with frontend_screen_contracts.py is required")
sys.path.insert(0, str(HARNESS_ROOT))

from frontend_screen_contracts import evaluate_frontend_screen_contracts

TOKEN_REF = re.compile(r"^\{([^{}]+)\}$")


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected mapping")
    return value


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected object")
    return value


def finding(code: str, message: str, **details: Any) -> dict[str, Any]:
    result = {"code": code, "message": message}
    result.update(details)
    return result


def token_index(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    def walk(value: Any, path: list[str]) -> None:
        if not isinstance(value, dict):
            return
        if "$value" in value:
            result[".".join(path)] = value
            return
        for key, child in value.items():
            if key.startswith("$"):
                continue
            walk(child, [*path, key])

    walk(document, [])
    return result


def validate_tokens(document: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    tokens = token_index(document)
    findings: list[dict[str, Any]] = []
    required = {
        "semantic.color.navigation.background",
        "semantic.color.navigation.text",
        "semantic.color.surface.page",
        "semantic.color.surface.default",
        "semantic.color.text.primary",
        "semantic.color.border.default",
        "semantic.color.action.primary",
        "semantic.color.focus.ring",
        "semantic.spacing.page",
        "component.app-shell.sidebar-width",
        "component.app-shell.workspace-padding",
        "component.control.height",
        "component.table.header-height",
        "component.table.row-height",
        "component.table.selection-column-width",
        "component.table.cell-padding-x",
    }
    for name in sorted(required - set(tokens)):
        findings.append(finding("MISSING_TOKEN", f"required token {name} is absent", token=name))

    allowed_types = {
        "color", "dimension", "fontFamily", "fontWeight", "duration",
        "cubicBezier", "number", "strokeStyle", "border", "transition",
        "shadow", "gradient", "typography",
    }
    for name, token in tokens.items():
        token_type = token.get("$type")
        if token_type not in allowed_types:
            findings.append(finding("INVALID_TOKEN_TYPE", f"{name} has unsupported $type {token_type!r}", token=name))
        value = token.get("$value")
        if isinstance(value, str):
            match = TOKEN_REF.fullmatch(value)
            if match and match.group(1) not in tokens:
                findings.append(finding("DANGLING_TOKEN_ALIAS", f"{name} references missing token {match.group(1)}", token=name))

    return tokens, findings


def evaluate_presentation(
    presentation: dict[str, Any],
    tokens_document: dict[str, Any],
) -> list[dict[str, Any]]:
    tokens, findings = validate_tokens(tokens_document)

    refs = presentation.get("reference_model")
    if not isinstance(refs, dict) or not refs.get("semantic_guard"):
        findings.append(finding("MISSING_REFERENCE_GUARD", "Presentation System must define the semantic boundary of visual/executable references."))
    sources = refs.get("sources", []) if isinstance(refs, dict) else []
    source_ids = {item.get("id") for item in sources if isinstance(item, dict)}
    for required in {"RESOURCE-CATALOGUE-CONCEPT", "RESOURCE-DETAIL-CONCEPT", "MAIN-WEBUI-PRESENTATION"}:
        if required not in source_ids:
            findings.append(finding("MISSING_REFERENCE_SOURCE", f"missing presentation evidence source {required}"))

    design_tokens = presentation.get("design_tokens", {})
    if design_tokens.get("canonical_source") != "docs/contracts/ui/mvp-design-tokens.json":
        findings.append(finding("TOKEN_AUTHORITY", "Presentation System must point to the canonical DTCG token source."))
    if design_tokens.get("format") != "DTCG-2025.10":
        findings.append(finding("TOKEN_FORMAT", "Canonical token format must be DTCG-2025.10 for this pilot."))

    invariants = presentation.get("layout", {}).get("material_invariants", []) or []
    if not invariants:
        findings.append(finding("MISSING_MATERIAL_INVARIANTS", "Presentation System has no material geometry invariants."))
    for item in invariants:
        token = item.get("token") if isinstance(item, dict) else None
        if not token or token not in tokens:
            findings.append(finding("INVALID_INVARIANT_TOKEN", f"material invariant references unknown token {token!r}", token=token))

    patterns = presentation.get("patterns", {}) or {}
    for pattern_id in ("APP-SHELL", "CATALOGUE", "DETAIL", "DATA-TABLE"):
        pattern = patterns.get(pattern_id)
        if not isinstance(pattern, dict) or not pattern.get("anatomy"):
            findings.append(finding("INCOMPLETE_PATTERN_ANATOMY", f"{pattern_id} must define material anatomy.", pattern=pattern_id))

    return findings


def evaluate_screens(
    screens: dict[str, Any],
    presentation: dict[str, Any],
    openapi: dict[str, Any],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    rows = screens.get("screens", []) or []
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict) and row.get("id")}
    required = set(screens.get("coverage", {}).get("required_workspaces", []) or [])
    if set(by_id) != required:
        findings.append(finding("SCREEN_INVENTORY_MISMATCH", "required workspace inventory and screen contracts differ."))

    pattern_ids = set((presentation.get("patterns") or {}).keys())
    for screen_id, row in by_id.items():
        region_ids = [item.get("id") for item in row.get("regions", []) or [] if isinstance(item, dict)]
        composition = row.get("composition")
        ordered = composition.get("ordered_regions", []) if isinstance(composition, dict) else []
        if not ordered:
            findings.append(finding("MISSING_SCREEN_COMPOSITION", f"{screen_id} has no explicit ordered composition.", screen=screen_id))
        elif len(ordered) != len(set(ordered)) or set(ordered) != set(region_ids):
            findings.append(finding("COMPOSITION_REGION_MISMATCH", f"{screen_id} composition must contain every semantic region exactly once.", screen=screen_id))
        for pattern in row.get("patterns", []) or []:
            if pattern not in pattern_ids:
                findings.append(finding("UNKNOWN_PATTERN", f"{screen_id} references unknown pattern {pattern}.", screen=screen_id, pattern=pattern))

    catalogue = by_id.get("RESOURCE-CATALOGUE", {})
    catalogue_patterns = set(catalogue.get("patterns", []) or [])
    if "DATA-TABLE" not in catalogue_patterns:
        findings.append(finding("RESOURCE_CATALOGUE_REFERENCE_PATTERN", "Resource Catalogue reference slice must use the accepted DATA-TABLE visual pattern."))
    if "FILTER-BAR" not in catalogue_patterns:
        findings.append(
            finding(
                "RESOURCE_CATALOGUE_QUERY_PATTERN",
                "Resource Catalogue must expose the accepted FILTER-BAR query pattern.",
            )
        )

    semantic_contract = catalogue.get("semantic_contract", {}) or {}
    catalogue_read = next(
        (
            row
            for row in semantic_contract.get("reads", []) or []
            if isinstance(row, dict) and row.get("operation_id") == "listResources"
        ),
        {},
    )
    accepted_query = set((catalogue_read.get("query") or {}).keys())
    required_query = {
        "search",
        "authorityScopeRef",
        "siteRef",
        "sortBy",
        "sortDirection",
        "page",
        "pageSize",
    }
    if not required_query.issubset(accepted_query):
        findings.append(
            finding(
                "RESOURCE_CATALOGUE_QUERY_CONTRACT",
                "Resource Catalogue query semantics must be explicit in Screen/View design.",
                missing=sorted(required_query - accepted_query),
            )
        )

    resource_get = ((openapi.get("paths") or {}).get("/v1/resources") or {}).get("get", {})
    openapi_parameters = set()
    component_parameters = (openapi.get("components") or {}).get("parameters", {}) or {}
    for parameter in resource_get.get("parameters", []) or []:
        if not isinstance(parameter, dict):
            continue
        if "$ref" in parameter:
            ref_name = str(parameter["$ref"]).rsplit("/", 1)[-1]
            resolved = component_parameters.get(ref_name, {}) or {}
            if resolved.get("in") == "query" and resolved.get("name"):
                openapi_parameters.add(resolved["name"])
        elif parameter.get("in") == "query" and parameter.get("name"):
            openapi_parameters.add(parameter["name"])
    if not required_query.issubset(openapi_parameters):
        findings.append(
            finding(
                "RESOURCE_CATALOGUE_HTTP_QUERY_CONTRACT",
                "listResources must realize every accepted catalogue query parameter in OpenAPI.",
                missing=sorted(required_query - openapi_parameters),
            )
        )

    adaptation = catalogue.get("reference_adaptation", {})
    excluded = {
        item.get("reference_feature")
        for item in adaptation.get("not_adopted", []) or []
        if isinstance(item, dict)
    }
    if "Resource-type-filter" not in excluded:
        findings.append(
            finding(
                "REFERENCE_EXCLUSION_MISSING",
                "Resource Catalogue must explicitly reject the unsupported Resource-type filter.",
                feature="Resource-type-filter",
            )
        )

    detail = by_id.get("RESOURCE-DETAIL", {})
    if not detail.get("reference_adaptation"):
        findings.append(finding("RESOURCE_DETAIL_REFERENCE_ADAPTATION", "Resource Detail must state how historical visual evidence is adopted without importing legacy semantics."))

    pilot = set(screens.get("coverage", {}).get("semantic_contract_pilot", []) or [])
    if pilot:
        result = evaluate_frontend_screen_contracts(
            presentation,
            screens,
            openapi,
            screen_ids=pilot,
        )
        for item in result["findings"]:
            details = {key: value for key, value in item.items() if key not in {"code", "detail"}}
            findings.append(
                finding(
                    f"SCREEN_SEMANTIC_{item['code']}",
                    item["detail"],
                    **details,
                )
            )

    return findings


def evaluate_verification(verification: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    evidence = verification.get("presentation_evidence")
    if not isinstance(evidence, dict):
        return [finding("MISSING_PRESENTATION_EVIDENCE", "Verification Design has no rendered-presentation evidence contract.")]

    if not evidence.get("design_time"):
        findings.append(finding("MISSING_DESIGN_TIME_PRESENTATION_PROOF", "Verification Design must validate canonical presentation knowledge before implementation."))
    runtime = evidence.get("implementation_time")
    if not isinstance(runtime, dict):
        findings.append(finding("MISSING_IMPLEMENTATION_PRESENTATION_PROOF", "Verification Design must define implementation-time presentation evidence."))
        return findings
    for key in ("environment", "geometry", "visual_regression", "responsive_matrix", "interaction", "reference_conformance"):
        if key not in runtime:
            findings.append(finding("MISSING_PRESENTATION_PROOF_DIMENSION", f"implementation-time presentation evidence misses {key}.", dimension=key))

    viewport_ids = {
        item.get("id")
        for item in runtime.get("responsive_matrix", {}).get("viewports", []) or []
        if isinstance(item, dict)
    }
    for expected in {"desktop-reference", "desktop-compact", "narrow"}:
        if expected not in viewport_ids:
            findings.append(finding("MISSING_VIEWPORT", f"responsive evidence misses {expected}.", viewport=expected))

    baseline = runtime.get("visual_regression", {}).get("baseline_governance")
    if not baseline:
        findings.append(finding("MISSING_BASELINE_GOVERNANCE", "Visual regression baselines must not be self-authorizing."))

    return findings


def semantic_evaluation(
    *,
    artifact: str,
    capability: str,
    claim: str,
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    accepted = not findings
    return {
        "version": 1,
        "kind": "harness-artifact-semantic-evaluation",
        "artifact": artifact,
        "capability": capability,
        "status": "ACCEPTED" if accepted else "REJECTED",
        "findings": findings,
        "semantic_claims": {"accepted": [claim] if accepted else []},
    }


def evaluate() -> dict[str, Any]:
    presentation = load_yaml(PRESENTATION)
    screens = load_yaml(SCREENS)
    verification = load_yaml(VERIFICATION)
    tokens = load_json(TOKENS)
    openapi = load_yaml(OPENAPI)

    return {
        "version": 1,
        "kind": "harness-semantic-evaluation-set",
        "semantic_evaluations": [
            semantic_evaluation(
                artifact="FRONTEND-PRESENTATION-SYSTEM",
                capability="engineering.frontend.presentation-system",
                claim="engineering.interface.human.presentation-system",
                findings=evaluate_presentation(presentation, tokens),
            ),
            semantic_evaluation(
                artifact="FRONTEND-SCREEN-VIEW-DESIGN",
                capability="engineering.frontend.screen-view-design",
                claim="engineering.interface.human.screen-composition",
                findings=evaluate_screens(screens, presentation, openapi),
            ),
            semantic_evaluation(
                artifact="FRONTEND-VERIFICATION",
                capability="engineering.frontend.presentation-verification",
                claim="engineering.verification.interface.presentation",
                findings=evaluate_verification(verification),
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--require-accepted", action="store_true")
    args = parser.parse_args()

    result = evaluate()
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)

    rejected = [
        item for item in result["semantic_evaluations"]
        if item["status"] != "ACCEPTED"
    ]
    if args.require_accepted and rejected:
        for item in rejected:
            print(
                f"{item['artifact']}: semantic acceptance REJECTED",
                *[f"  - {x['code']}: {x['message']}" for x in item["findings"]],
                sep="\n",
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
