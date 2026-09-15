# First MVP vertical — DDD convergence

Status: `active S2 Domain Design`.

Date: 2026-09-15.

## Goal

Finish the DDD needed by the first MVP vertical before any further code work.

The earlier S3/S4 work remains design evidence, but implementation is frozen. The existing experimental target APR code is left in the branch unchanged and is not authoritative domain truth.

## Lifecycle correction

The first vertical was moved toward implementation too early. Strategic ownership is substantially converged, but at least two Tactical DDD gaps remain material to implementation:

1. Application Deployment has an accepted strategic boundary but no accepted MVP Tactical model.
2. Access Policy Realization has accepted comparison/additive semantics but its MVP Tactical identity/lifecycle/invariant classification is not yet closed.

Therefore:

- Lifecycle stage returns to `S2 Domain Design`;
- previous G4 implementation authorization is revoked;
- no production code, tests, migrations, adapters, bootstrap or UI changes are permitted while this plan is active;
- existing code changes are not reverted, but no further implementation work may build on them until a later explicit S3/S4/G4 cycle after DDD closure.

## Scope

Close only DDD required by the accepted first MVP happy path:

```text
ACC InteractionContractRevision
-> AD ApplicationDeployment / ComponentPlacement
-> RC Resource / AddressSpace
-> AG bilateral authorization
-> AP current Policy Rule
-> RPM derived TargetRequiredPolicy
-> APR realization assessment / additive VerifiedChangeIntent
-> NEO controlled mutation semantics
```

Do not design persistence, transport, workflow wiring, provider adapters, migration mechanics or package structure here.

## Already coherent for MVP

Treat these as accepted unless the convergence pass exposes a direct contradiction:

- ACC Tactical model;
- RC Tactical model;
- AG Tactical model;
- AP Tactical model;
- NEP target Tactical model;
- NEO Tactical model;
- Strategic context ownership and public semantic edges in `docs/domain/context-map.md` and `docs/domain/strategic-model.md`.

## Active Tactical work

### 1. Application Deployment

Resolve at MVP scope:

- ApplicationDeployment sameness/continuity;
- whether ComponentPlacement has independent identity or is a relation/value inside deployment state;
- placement multiplicity semantics without imposing exactly-one placement;
- invariants for ComponentRef/ApplicationRef/ResourceRef;
- current placement-set meaning and empty placement meaning;
- minimum domain operations needed for scaling/migration;
- explicit classification of lifecycle details that are not required by current accepted behavior.

### 2. Access Policy Realization

Resolve at MVP scope:

- semantic identity/value classification of ComparisonScope, assessment, delta and VerifiedChangeIntent;
- whether any APR aggregate/durable lifecycle is actually required;
- minimum permit-space value vocabulary for the HostAddress-based first path;
- exact invariants for Realized/Drift/Uncomparable and additive-only ENSURE-PERMIT;
- verification meaning when `excess` remains after missing access is ensured;
- provenance/explainability as semantic guarantee versus storage concern;
- classification of remaining APR-Pxx items as MVP-domain work, future product work or downstream architecture/implementation work.

## Convergence checks

After AD and APR Tactical closure:

- check their public contracts against AG/AP/RPM/NEP/NEO;
- remove stale `S1-open` / `Tactical-open` statements that are actually resolved;
- preserve explicit deferrals for generalized scopes, Prefix-aware NEP, managed-policy removal and richer provider semantics;
- do not reopen accepted Strategic boundaries unless a real ownership contradiction is found.

## Exit / G2 rule

G2 may pass for the first MVP vertical only when:

- every domain concept needed by the vertical has explicit owner, identity/sameness and invariant semantics;
- every context that needs a Tactical model has one sufficient for the MVP slice;
- derived/value concepts are distinguished from durable entities/aggregates;
- no implementation step would need to invent domain meaning;
- remaining unknowns are explicitly outside the MVP and have a revisit trigger.

Even after G2 PASS, stop at design. Do not resume S3/S4/implementation unless explicitly requested later.
