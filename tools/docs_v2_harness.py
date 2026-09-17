#!/usr/bin/env python3
"""Minimal repository-local runtime for Documentation System v2."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

SEMANTIC_RELATIONS = {"DERIVES_FROM", "CONSTRAINED_BY", "REALIZES", "REFINES", "DECIDED_BY"}
NON_SEMANTIC_RELATIONS = {"REFERENCES"}
EVIDENCE_RELATIONS = {"EVIDENCED_BY"}
VALID_RELATIONS = SEMANTIC_RELATIONS | NON_SEMANTIC_RELATIONS | EVIDENCE_RELATIONS


class HarnessError(RuntimeError):
    pass


class ConflictError(HarnessError):
    pass


@dataclass(frozen=True)
class Anchor:
    anchor_id: str
    type_id: str
    owner_stage: str
    status: str
    path: Path
    semantic_refs: tuple[dict[str, Any], ...]


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, yaml.YAMLError) as exc:
        raise HarnessError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise HarnessError(f"{path} must contain a mapping")
    return value


def semantic_fingerprint(document: dict[str, Any]) -> str:
    projection = {key: document.get(key) for key in ("anchor_id", "type_id", "owner_stage", "scope", "canonical_payload", "semantic_refs") if key in document}
    encoded = json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256-json-v1:" + hashlib.sha256(encoded).hexdigest()


def discover_anchors(root: Path) -> dict[str, Anchor]:
    anchors: dict[str, Anchor] = {}
    for path in sorted((root / "docs-v2").rglob("*.yaml")):
        document = load_yaml(path)
        anchor_id = document.get("anchor_id")
        if not anchor_id:
            continue
        missing = [key for key in ("type_id", "owner_stage", "status") if not document.get(key)]
        if missing:
            raise HarnessError(f"{path}: anchor {anchor_id} missing {missing}")
        if anchor_id in anchors:
            raise HarnessError(f"duplicate anchor_id {anchor_id}: {anchors[anchor_id].path} and {path}")
        refs = document.get("semantic_refs", [])
        if not isinstance(refs, list):
            raise HarnessError(f"{path}: semantic_refs must be a list")
        anchors[str(anchor_id)] = Anchor(str(anchor_id), str(document["type_id"]), str(document["owner_stage"]), str(document["status"]), path.relative_to(root), tuple(refs))
    return anchors


def validate_references(anchors: dict[str, Anchor]) -> list[str]:
    errors: list[str] = []
    for anchor in anchors.values():
        for ref in anchor.semantic_refs:
            if not isinstance(ref, dict):
                errors.append(f"{anchor.anchor_id}: semantic reference must be a mapping")
                continue
            relation = ref.get("relation")
            target = ref.get("target")
            if relation not in VALID_RELATIONS:
                errors.append(f"{anchor.anchor_id}: unknown relation {relation!r}")
                continue
            if not isinstance(target, dict):
                errors.append(f"{anchor.anchor_id}: relation {relation} has invalid target")
                continue
            if target.get("kind") == "anchor-current":
                target_id = target.get("anchor_id")
                if not target_id or target_id not in anchors:
                    errors.append(f"{anchor.anchor_id}: dangling current anchor reference {target_id!r}")
                elif anchors[target_id].status != "ACCEPTED":
                    errors.append(f"{anchor.anchor_id}: current dependency {target_id} is {anchors[target_id].status}, not ACCEPTED")
            elif target.get("kind") not in {"anchor-pinned", "evidence"}:
                errors.append(f"{anchor.anchor_id}: unsupported target kind {target.get('kind')!r}")
    return errors


def reverse_semantic_graph(anchors: dict[str, Anchor]) -> dict[str, set[str]]:
    graph = {anchor_id: set() for anchor_id in anchors}
    for dependent in anchors.values():
        for ref in dependent.semantic_refs:
            if not isinstance(ref, dict) or ref.get("relation") not in SEMANTIC_RELATIONS:
                continue
            target = ref.get("target") or {}
            if isinstance(target, dict) and target.get("kind") == "anchor-current" and target.get("anchor_id") in anchors:
                graph[target["anchor_id"]].add(dependent.anchor_id)
    return graph


def affected_set(anchors: dict[str, Anchor], changed: Iterable[str]) -> list[str]:
    graph = reverse_semantic_graph(anchors)
    queue = list(dict.fromkeys(changed))
    unknown = [item for item in queue if item not in anchors]
    if unknown:
        raise HarnessError(f"unknown changed anchor(s): {', '.join(unknown)}")
    seen = set(queue)
    while queue:
        current = queue.pop(0)
        for dependent in sorted(graph[current]):
            if dependent not in seen:
                seen.add(dependent); queue.append(dependent)
    return sorted(seen, key=lambda item: (anchors[item].owner_stage, item))


def _docs_v2_ref(root: Path, raw_ref: str, label: str) -> dict[str, Any]:
    rel = Path(raw_ref)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts or rel.parts[0] != "docs-v2":
        raise HarnessError(f"{label} must point inside docs-v2/**: {raw_ref}")
    return load_yaml(root / rel)


def load_resume_context(root: Path) -> dict[str, Any]:
    state = load_yaml(root / "docs-v2/meta/workstream-state.yaml")
    roadmap_ref = state.get("roadmap")
    if not isinstance(roadmap_ref, str) or not roadmap_ref:
        raise HarnessError("workstream state has no roadmap pointer")
    context: dict[str, Any] = {"workstream": state, "roadmap": _docs_v2_ref(root, roadmap_ref, "roadmap")}
    current = state.get("current_work") or {}
    if not isinstance(current, dict):
        raise HarnessError("workstream current_work must be a mapping")
    current_refs: dict[str, dict[str, Any]] = {}
    for key, value in current.items():
        if key.endswith("_ref") and value is not None:
            if not isinstance(value, str) or not value:
                raise HarnessError(f"current_work.{key} must be a non-empty repository path")
            current_refs[key] = _docs_v2_ref(root, value, f"current_work.{key}")
    context["current_refs"] = current_refs
    return context


def readiness(scope_state: dict[str, Any], gate: str) -> dict[str, str]:
    if scope_state.get("blockers"):
        return {"result": "BLOCKED", "reason": "scope has blockers"}
    gates = scope_state.get("gates") or {}
    if gates.get(gate) in {"PASS", "PASS_CURRENT"}:
        return {"result": "PASS", "reason": f"{gate} already current"}
    stage = {"G0": "S0", "G1": "S1", "G2": "S2", "G3": "S3", "G4": "S4"}.get(gate)
    if not stage:
        return {"result": "FAIL", "reason": f"unknown gate {gate}"}
    stage_state = (scope_state.get("stage_states") or {}).get(stage)
    if stage_state == "ACCEPTED_CURRENT":
        return {"result": "PASS", "reason": f"{stage} accepted/current and no blockers"}
    return {"result": "REWORK", "reason": f"{stage} is {stage_state or 'missing'}"}


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def assert_expected_head(root: Path, expected_head: str) -> None:
    current = git_head(root)
    if current != expected_head:
        raise ConflictError(f"stale repository basis: expected {expected_head}, current {current}")


def human_truth(required: bool, provided: bool) -> dict[str, str]:
    if required and not provided:
        return {"result": "NEED_MORE_DATA", "reason": "required human-owned truth is missing"}
    return {"result": "PASS", "reason": "no missing human-owned truth"}


def persist_files(root: Path, expected_head: str, files: dict[str, str], message: str) -> dict[str, str]:
    if not files:
        raise HarnessError("persistence change set is empty")
    normalized: dict[Path, str] = {}
    for raw_path, content in files.items():
        rel = Path(raw_path)
        if rel.is_absolute() or ".." in rel.parts or not rel.parts or rel.parts[0] != "docs-v2":
            raise HarnessError(f"runtime persistence is limited to docs-v2/**: {raw_path}")
        normalized[rel] = content
    already_applied = all((root / rel).is_file() and (root / rel).read_text(encoding="utf-8") == content for rel, content in normalized.items())
    if already_applied:
        return {"result": "PASS", "head": git_head(root), "effect": "already-applied"}
    assert_expected_head(root, expected_head)
    for rel, content in normalized.items():
        path = root / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "--", *[str(rel) for rel in normalized]], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return {"result": "PASS", "head": git_head(root), "effect": "committed"}


def validate_repo(root: Path) -> dict[str, Any]:
    context = load_resume_context(root)
    anchors = discover_anchors(root)
    errors = validate_references(anchors)
    return {"result": "PASS" if not errors else "FAIL", "anchors": len(anchors), "errors": errors, "current_work": context["workstream"].get("current_work")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True); sub.add_parser("resume"); sub.add_parser("validate")
    impact = sub.add_parser("impact"); impact.add_argument("anchor_ids", nargs="+")
    gate = sub.add_parser("readiness"); gate.add_argument("scope_state", type=Path); gate.add_argument("gate")
    cas = sub.add_parser("check-head"); cas.add_argument("expected_head")
    persist = sub.add_parser("persist"); persist.add_argument("expected_head"); persist.add_argument("manifest", type=Path); persist.add_argument("--message", default="docs-v2: persist Harness change set")
    args = parser.parse_args(); root = args.root.resolve()
    try:
        if args.command == "resume":
            context = load_resume_context(root); result = {"current_work": context["workstream"].get("current_work"), "loaded_current_refs": sorted(context["current_refs"]), "next_meaningful_work": context["workstream"].get("next_meaningful_work"), "blockers": context["workstream"].get("blockers", [])}
        elif args.command == "validate": result = validate_repo(root)
        elif args.command == "impact": result = {"affected": affected_set(discover_anchors(root), args.anchor_ids)}
        elif args.command == "readiness": result = readiness(load_yaml(root / args.scope_state), args.gate)
        elif args.command == "check-head": assert_expected_head(root, args.expected_head); result = {"result": "PASS", "head": args.expected_head}
        else:
            manifest = json.loads((root / args.manifest).read_text(encoding="utf-8")); result = persist_files(root, args.expected_head, manifest, args.message)
    except HarnessError as exc:
        print(json.dumps({"result": "FAIL", "error": str(exc)}, ensure_ascii=False)); return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str)); return 0 if result.get("result", "PASS") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
