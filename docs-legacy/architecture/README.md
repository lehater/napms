# Architecture map

This directory contains the architecture required to reconstruct and evolve NAPMS. Both **as-built** and **target** architecture are current project truth when the implemented system intentionally differs from the accepted target.

## Current as-built architecture

- `current-architecture.md` — integrated as-built application/runtime architecture and compatibility boundaries. Older semantic models in it remain reconstruction truth, not target-domain authority.
- `application-catalogue-target-boundary.md` — implemented Application Catalogue boundary and target-facing ownership constraints.
- `catalogue-curation-boundary.md` — implemented catalogue composition/authority/persistence boundary.
- `scoped-connectivity-inventory.md` — implemented owner-preserving connectivity read composition.
- `network-context-candidate-boundary.md` — implemented Checker/network-context composition boundary.
- `network-enforcement-placement-boundary.md` — implemented/compatibility NEP architecture.

## Current target / cross-cutting architecture

- `code-structure.md` — module/dependency taxonomy and structural guardrails.
- `first-mvp-policy-lifecycle-export.md` — current S3 candidate for target PolicyRule/RuleChange authoring, concrete ComponentDeployment ownership, complete vendor-neutral export, coherent snapshots and same-result JSON/CSV.
- `target-policy-authoring-boundary.md` — side-by-side target-vs-legacy authoring/persistence compatibility boundary.
- `technical-access-evidence-boundary.md` — current TAE structural boundary.
- `network-environment-operations-boundary.md` — current NEO structural boundary.
- `enterprise-identity-authoritative-sources-boundary.md` — authoritative-source extension seams.

Target semantic authority remains in current `docs/domain/` and `docs/requirements/`. As-built architecture must not silently redefine those target semantics.

## Selected first-MVP architecture status

G1/G2 now accept:

```text
BC Need
+ ACC exact revision
+ AD concrete source/destination ComponentDeployment
    -> AP PolicyRule / RuleChange
       Pending -> Accepted | Rejected
    -> current effective PolicyRule

current effective AP Rules
+ ACC + AD + RC
    -> Full Vendor-Neutral Policy Export
    -> short-lived immutable ExportResult
    -> JSON/table + CSV from the same result
```

The MVP does not embed customer-specific bilateral/quorum approval workflow. Authority Management may protect propose/decide/withdraw actions, but baseline AP decision semantics remain one formal Accepted/Rejected outcome. RC ResourceScopeAffiliation is not a mandatory AP decision dependency.

S3 is active and the architecture documents above are G3-review candidates, not implementation authorization. G4 is not yet granted.

Existing `/api/v1/normalized-policy`, legacy AccessRule and ACC compatibility deployment paths remain reconstructable as-built behavior until separately migrated.

Do not remove an as-built architecture contract merely because its capability has been implemented; remove it only when it no longer describes current as-built or current target design.
