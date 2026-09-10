# I29 — J02 Resource authoring journey

Status: `active`.

## Goal

Prove that the reusable user-journey-validation pattern from I28 works for Resource Catalogue authoring, then close only demonstrated P0/P1 gaps and retain deterministic regression evidence.

J02 goal: an admitted local user can create one access-relevant Resource, add/replace technical addresses, add/end Responsibility Scope affiliation and Resource Responsibility/contact, correct Resource identity state through accepted rename/retire semantics, then navigate away and reopen the durable result through normal UI discovery.

## Inputs

Canonical behavior:
- `docs/requirements/catalogue-curation.md`;
- `docs/requirements/web-ui-requirements.md`;
- `docs/decisions/ADR-007-i27-resource-lifecycle.md`;
- `docs/ui/screens.md`.

Execution surfaces:
- `web/src/features/catalogues/ResourcesPage.tsx`;
- `web/src/features/catalogues/ResourceDetailsPage.tsx`;
- Resource Catalogue HTTP/application adapters;
- full local compose stack and browser E2E.

Deterministic fixture:
- Resource `Orders Database`;
- initial address `10.20.30.40`, replacement `10.20.30.41`;
- Responsibility Scope `orders-prod`;
- Technical owner Team `Orders Platform`, external reference `team:orders-platform`, contact `orders@example.test`.

## WP-1 — Baseline

Execute J02 against current supported UI and accepted semantics. Record only reproducible P0-P3 findings. Static inspection may identify candidates but does not by itself close the journey gate.

Local exit:
- explicit baseline PASS/FAIL;
- every P0/P1 has blocked step, observed/expected result and owning implementation/semantic layer.

## WP-2 — Close P0/P1 gaps

Implement only accepted behavior required to remove demonstrated blockers. Preserve Resource identity and temporal history; do not introduce hard delete or ownership-implies-authority semantics.

Local exit:
- no J02 P0/P1 remains;
- normal correction/end/retire actions use accepted lifecycle/temporal semantics.

## WP-3 — Deterministic browser regression

Automate the stable J02 path through visible UI controls on the full local product stack. Verify durable reopen/search and the smallest high-value correction/history-ending confirmation paths.

Local exit:
- browser regression passes in applicable hosted CI;
- automation claims only deterministic behavior, not subjective usability quality.

## WP-4 — Reuse review

Compare J01 and J02 execution. Generalize shared test/workflow support only where two real journeys demonstrate reuse; keep product-specific truth out of the generic Skill/process layer.

Local exit:
- no unnecessary generic QA/orchestration layer;
- any shared browser harness extraction is justified by demonstrated duplication;
- accepted product/UI truth remains synchronized.

## Exit criteria

- J02 passes end-to-end through supported UI with no P0/P1 findings;
- Resource rename/retire and temporal relation behavior match accepted semantics;
- created Resource can be found and reopened after navigation away;
- current addresses, scope affiliation and responsibility/contact are understandable after reopen;
- deterministic J02 behavior has executable browser evidence;
- applicable core/Web/PostgreSQL/Harness/Knowledge/Docker/browser gates are green before integration.

## Blockers

None at plan start. Current chat cannot render the local Web UI directly, so hosted GitHub Actions is the executable browser surface when local browser execution is unavailable.

## Next

Run WP-1 baseline. Validate static candidate gaps against the supported HTTP/Web surface, then create the minimum executable browser baseline needed to prove actual journey blockers before implementing fixes.
