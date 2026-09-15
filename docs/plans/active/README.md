# Active execution

Current: `MVP foundational domain convergence`.

Lifecycle stage: `S2 Tactical DDD — minimal happy-path convergence`.

Implementation authorization: `none`.

## MVP execution rule

The current objective is the smallest working end-to-end happy path, not feature-complete domain modelling.

For each affected Bounded Context:

- define only semantics required by the first end-to-end scenario;
- preserve stable context boundaries, identities and public contracts so later extension remains possible;
- defer revisions, richer lifecycle/state machines, migration machinery, optimization and edge-case semantics until a concrete requirement or implementation finding needs them;
- do not add extension mechanisms merely because they may be useful later;
- prefer a thin vertical path across contexts over completing every context in depth before integration.

The target progression is therefore minimal `ACC + RC -> AD`, then the smallest downstream governance/network/policy path needed to produce a working rule, with deeper modelling added only under demonstrated pressure.

## Current baseline

```text
ACC Application / Component / Interaction
        |
        v
AD ApplicationDeployment / ComponentPlacement -> ResourceRef
        |
        v
RC Resource -> effective AddressSpace [0..1] = HostAddress | Prefix
```

Canonical target authority:

- `docs/domain/strategic-model.md` — responsibilities/boundaries;
- `docs/domain/context-map.md` — relationships/contracts;
- `docs/domain/strategic-model.json` — machine-readable projection;
- `docs/domain/application-communication-catalogue/target-model.md` — current minimal ACC target;
- `docs/plans/active/application-deployment-boundary.md` — prior AD boundary convergence/audit record.

## ACC checkpoint

For the MVP, ACC owns an `ApplicationDefinition`, its `Component` identities and directed `Interaction` definitions.

Accepted current semantics:

- an Interaction describes possible communication between two Components of one Application Definition, not a deployment or network endpoint;
- self-interaction is allowed;
- one directed Component pair has at most one Interaction; reverse direction is distinct;
- Interaction endpoints are immutable; changing either endpoint creates another Interaction;
- Interaction has a stable identity and current traffic contract;
- dedicated `InteractionContractRevision` workflow is deferred beyond MVP;
- retirement means removal from active use, not physical deletion; active dependencies block retirement;
- richer restoration/history semantics are deferred unless the happy path needs them.

AD may use ACC Component/Interaction meaning plus Component placements to derive concrete technically possible interactions. ACC itself owns neither placements nor Resources nor concrete deployment pairs.

## Known downstream blockers

Access Governance still has S1 behavior questions around selectable ApplicationDeployment pairs, authorization behavior when placement/scope changes alter approval obligations, and obligations under overlapping Responsibility Scopes. Do not solve those questions speculatively while building the foundational happy path; reopen/resolve them when the minimal vertical slice reaches the affected governance behavior.

## Next

Start a fresh session from this capsule. Continue with the **minimal Resource Catalogue Tactical model**, then immediately revalidate the minimal Application Deployment model against ACC + RC. Avoid deeper ACC refinement unless the end-to-end slice exposes a blocking semantic gap.
