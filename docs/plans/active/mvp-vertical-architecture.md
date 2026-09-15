# First MVP vertical — Architecture

Status: `completed — G3 PASS for first MVP vertical`.

Date: 2026-09-15.

## Goal

Define the smallest feasible target realization for the G2-accepted first MVP vertical without changing domain meaning or adding speculative infrastructure.

## Accepted semantic scope

```text
ACC InteractionContractRevision
-> AD ApplicationDeployment / ComponentPlacement
-> RC Resource / HostAddress realization
-> AG bilateral authorization
-> AP current Policy Rule
-> RPM TargetRequiredPolicy
-> PPI ConfiguredEffectivePolicySnapshot
-> APR exact comparison
-> VerifiedChangeIntent(ENSURE-PERMIT)
-> Provider Policy Renderer
-> TargetPolicyArtifact
-> NEO controlled mutation
```

## Architecture result

Canonical target architecture: `docs/architecture/first-mvp-vertical.md`.

G3 challenge/result: `docs/architecture/first-mvp-vertical-g3-review.md`.

Accepted architecture decisions for the first vertical:

- modular monolith, in-process application calls, existing PostgreSQL deployment;
- AG and AP retain separate semantic/persistence ownership;
- AG authorization transition -> AP current-rule handoff uses one focused local transaction/UoW in the modular monolith;
- technical realization is a separate cross-context `workflows/policy_realization` orchestration with no domain ownership;
- cross-context reads use explicit application contracts/consumer-owned ports, never peer SQL/domain imports;
- ACC/RC legacy runtime may be consumed only through bounded fail-closed workflow infrastructure adapters;
- NEP must implement the accepted target `AnalyzeTrafficPairs -> FirewallCandidate/accessListName` query; old path/attachment output is not adapted into target meaning;
- APR old managed-scope/placement orchestration is replaced for the target slice; reusable permit-space algebra may be retained;
- provider rendering is outside APR core behind a workflow/integration port;
- NEO current execution flow is retained/adapted around TargetPolicyArtifact;
- unresolved/incomplete/unknown/unsupported propagates fail-closed;
- no broker, durable workflow engine or distributed transaction is introduced.

## G3 result

`G3 PASS` for this exact first MVP vertical.

No unresolved P0/P1 architecture decision is delegated to implementation.

Implementation remains unauthorized until S4 Implementation Readiness evaluates concrete code/migration slices and G4 passes for a bounded scope.

## Next

Proceed to S4 Implementation Readiness for the first MVP vertical. Map exact modules/schema/tests, choose the smallest dependency-ordered slices and issue no implementation lease until G4 criteria are satisfied.
