# Application Deployment stale-reference audit — 2026-09-15

Status: `completed for target/domain/process documentation; runtime/history references classified`.

Scope: stale semantics introduced by the accepted ACC/AD/RC split and simplified Resource-level `HostAddress | Prefix` realization.

## Audit rules

Current target truth must not claim any of the following:

- ACC owns `ComponentDeployment` or Component-to-Resource placement;
- `DirectedInteractionIdentity{sourceComponentDeploymentRef,destinationComponentDeploymentRef,...}` is current authorization identity;
- RC target requires `ResourceEndpoint`;
- RPM expands all ResourceEndpoints;
- Resource migration necessarily changes the logical ApplicationDeployment identity.

Legacy/runtime documentation may contain those terms only when clearly classified as current-state/history/migration evidence.

## Findings and disposition

### P1 — corrected

- `docs/domain/semantic-ownership.md` and `capabilities.md` still assigned deployment to ACC and endpoint realization to RC. Rewritten to ACC/AD/RC ownership.
- `docs/domain/ubiquitous-language.md` was dominated by superseded CR/CD, ComponentDeployment, DeploymentResourceBinding and ResourceEndpoint vocabulary. Replaced with compact current target language; legacy terms are explicitly history/runtime only.
- `docs/domain/resource-role-model.md` claimed ResourceEndpoint as current RC identity and ComponentDeployment subject. Rewritten to Resource-level AddressSpace and ApplicationDeployment subject.
- ADR-015 still claimed current ACC-owned ComponentDeployment/DirectedInteractionIdentity. Marked superseded and retained only for rationale/migration history.
- ADR-020 still materialized ACC ComponentDeployments through ResourceEndpoints. Amended to AP + ACC + AD + RC + NEP composition.
- Access Governance Tactical model still used ComponentDeployment subject. Marked DIRTY and aligned to current strategic subject; G2 is blocked by active S1 behavior questions.
- Access Policy Tactical model and requirements still used ComponentDeployment subject. Aligned to `GovernedInteractionSubject` and Resource-independent identity.
- Access Governance G1 passport aligned to ApplicationDeployment subject while explicitly reopening the three newly material behavior questions.
- `docs/plans/active/README.md` and `domain-erd-revalidation.md` incorrectly said APR-P03 was next and that old governance/materialization G2 remained current. Active README corrected; superseded active plan deleted because Git history is the archive.
- `tools/validate_domain_model.py` expected an obsolete machine-readable schema and would fail the current strategic model. Validator aligned to participant-id/relationship projection and current convergence status.

### P2 — intentionally retained current-state/history

- `docs/domain/application-communication-catalogue/tactical-model.md` describes implemented I31/current-state ACC structures including compatibility ComponentDeployment and DirectedInteractionIdentity. It remains runtime evidence, not target authority; ACC README now states this explicitly.
- `docs/domain/resource-catalogue/tactical-model.md` describes I27 endpoint-address persistence/curation. RC README and target realization model explicitly supersede its endpoint shape for target semantics; it remains migration/history evidence because provenance and existing identifiers matter.
- ADR-012/013 and older application-catalogue UI/architecture artifacts describe implemented I31 history. They remain useful only for migration/current-state explanation.
- stakeholder evidence registers may mention ResourceEndpoint/old deployment interpretations because they are non-authoritative evidence. They are not rewritten retroactively.
- legacy Connectivity Requirements / Connectivity Decision runtime artifacts remain current-state/migration evidence, not target BCs.

## Current target authority

Use in this order for target design:

1. `docs/domain/strategic-model.md` — responsibilities/boundaries;
2. `docs/domain/context-map.md` — relationships/contracts;
3. `docs/domain/strategic-model.json` — machine-readable projection;
4. `docs/domain/application-communication-catalogue/target-model.md`;
5. `docs/domain/application-deployment/boundary.md`;
6. `docs/domain/resource-catalogue/target-realization-model.md`;
7. affected AG/AP target documents, subject to their explicit S1/Tactical status.

## Remaining blockers

No P0 ownership contradiction was found in the canonical target after corrections.

P1 product blockers remain only in Access Governance behavior:

1. selectable source/destination ApplicationDeployment pair rules;
2. authorization consequence when placement/scope changes alter approval obligations;
3. approval obligations when multiple Responsibility Scopes apply to one side.

These are not documentation cleanup defects and must be answered at S1.

## Validation note

The repository `knowledge gate` workflow runs only on pushes to `main`; therefore this branch does not receive that GitHub Actions run automatically. The validator itself was audited and corrected so the next local/PR/main `make knowledge-check` can validate the new strategic projection. No claim of CI PASS is made by this audit.
