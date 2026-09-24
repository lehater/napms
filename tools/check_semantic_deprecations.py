#!/usr/bin/env python3
"""Fail when superseded semantic models leak back into current canonical design.

This is intentionally narrower than a generic vocabulary linter: every token below
names a concrete decision that was retired during first-MVP requirement purification
and downstream revalidation.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CANONICAL_CURRENT = [
    "docs/model/strategic/capabilities.yaml",
    "docs/model/strategic/bounded-contexts.yaml",
    "docs/model/strategic/context-relationships.yaml",
    "docs/model/use-cases/organization-structure-administration.yaml",
    "docs/model/use-cases/resource-catalogue-curation.yaml",
    "docs/model/use-cases/authority-management.yaml",
    "docs/model/use-cases/access-policy.yaml",
    "docs/model/use-cases/first-mvp-policy-export.yaml",
    "docs/model/tasks/access-request-task-model.yaml",
    "docs/model/use-cases/access-request-human-journey.yaml",
    "docs/model/tasks/policy-export-task-model.yaml",
    "docs/model/use-cases/policy-export-human-journey.yaml",
    "docs/model/contexts/organization-structure/domain-model.yaml",
    "docs/model/contexts/resource-catalogue/language.yaml",
    "docs/model/contexts/resource-catalogue/decisions.yaml",
    "docs/model/contexts/resource-catalogue/process-model.yaml",
    "docs/model/contexts/resource-catalogue/domain-model.yaml",
    "docs/model/contexts/authority-management/language.yaml",
    "docs/model/contexts/authority-management/domain-model.yaml",
    "docs/model/contexts/access-policy/domain-model.yaml",
    "docs/architecture/structurizr/workspace.dsl",
    "docs/architecture/mvp-system-rules.yaml",
    "docs/architecture/mvp-module-contracts.yaml",
    "docs/architecture/mvp-security-architecture.yaml",
    "docs/architecture/mvp-threat-model.yaml",
    "docs/architecture/persistence/mvp-persistence.yaml",
    "docs/architecture/mvp-backend-component-design.yaml",
    "docs/contracts/http/napms-api-requirements.yaml",
    "docs/contracts/http/napms.openapi.yaml",
    "docs/contracts/ui/resource-detail.yaml",
    "docs/contracts/ui/mvp-human-interface.yaml",
    "docs/contracts/ui/mvp-navigation.yaml",
    "docs/contracts/ui/mvp-screen-view-design.yaml",
    "docs/architecture/mvp-frontend-component-design.yaml",
    "docs/plans/first-mvp-implementation-readiness.yaml",
    "docs/plans/first-mvp-test-intent.yaml",
    "docs/plans/mvp-frontend-verification.yaml",
    "docs/plans/mvp-frontend-test-design.yaml",
    "docs/plans/mvp-frontend-implementation-design.yaml",
]

RETIRED = {
    "AuthorityScopeRef": "Resource-scoped immutable authority affiliation was replaced by Organization/OrganizationalUnit semantic scope.",
    "AuthorityGrant": "Bearer-token authority grants were replaced by persisted Role/RoleAssignment evaluation.",
    "RequireScopedAuthority": "Authority port was replaced by RequireEffectiveAuthority.",
    "ResolveAuthorityScope": "Resource no longer owns a standalone authority-scope identity.",
    "RecordPermissionDecision": "Direct final permission decision was replaced by side approval decisions plus system finalization.",
    "SetPolicyRuleOperationalState": "Reversible Rule operational state was replaced by terminal revocation.",
    "setPolicyRuleOperationalState": "Reversible Rule operational-state HTTP operation was retired.",
    "decideAccessRequest": "Direct final AccessRequest decision HTTP operation was retired.",
    "DecideAccessRequestRequest": "Direct final AccessRequest decision request shape was retired.",
    "effectState": "PolicyRule ACTIVE/INACTIVE effect state was replaced by authorization episodes and revocation.",
    "/operational-state": "Reversible PolicyRule operational-state endpoint was retired.",
    "Active/Inactive": "Reversible PolicyRule Active/Inactive semantics were retired.",
    "ACTIVE/INACTIVE": "Reversible PolicyRule ACTIVE/INACTIVE semantics were retired.",
    "decisionResult": "AccessRequest catalogue/result semantics now use full terminal status and approval history.",
}

violations = []
for relative in CANONICAL_CURRENT:
    path = ROOT / relative
    if not path.is_file():
        violations.append((relative, "<missing>", "canonical current artifact is missing"))
        continue
    text = path.read_text(encoding="utf-8")
    for token, rationale in RETIRED.items():
        if token in text:
            line = text[: text.index(token)].count("\n") + 1
            violations.append((relative, token, f"line {line}: {rationale}"))

if violations:
    print("Semantic deprecation invariant FAILED")
    for path, token, detail in violations:
        print(f"- {path}: {token}: {detail}")
    raise SystemExit(2)

print(f"Semantic deprecation invariant PASS ({len(CANONICAL_CURRENT)} canonical artifacts)")
