# Active execution

Current: `domain-erd-revalidation.md`

Goal: converge revalidated capabilities into coherent Strategic/Tactical DDD before affected Architecture or implementation proceeds.

Current task: resume APR Tactical DDD after the completed global Strategic convergence pass, beginning with APR-P03 effective technical access-space semantics.

Lifecycle stage: `S2`

Stage state: `NOT_STARTED`

Lifecycle basis: ADR-019, ADR-020 and ADR-021 each have G2 PASS for their completed S2 slices; the 2026-09-14 global Strategic convergence pass has PASS for current target boundaries/relationships/contracts and is canonicalized in `docs/domain/context-map.md`; no global G2/G3/G4 or implementation authorization exists.

Implementation authorization: `none`

Authorized scope: `none`

Authorization basis: `none`

## Working set

Read first:
- `docs/domain/access-policy-realization/README.md`
- `docs/process/tactical-ddd-stage.md`

Expand when needed:
- `docs/domain/context-map.md` when an APR question touches ownership/cross-context contracts;
- `docs/engineering/context-problems/access-policy-realization.md` for the specific APR-P03/P04/P05/P06/P08/P09/P10 question under review;
- provider/TAE/NEO artifacts only when the active tactical question requires them.

## Completed S2 / Strategic checkpoints

- governance chain — `G2 PASS` (ADR-019);
- required-policy materialization — `G2 PASS` (ADR-020);
- provider configured-policy interpretation/rendering boundary — `G2 PASS` for strategic ownership/contracts (ADR-021);
- global Strategic DDD convergence/context map — `PASS` for current target boundaries, semantic ownership and material relationships; this is not a blanket G2 for context-local Tactical DDD.

## Global Strategic convergence result

Canonical Context Map: `docs/domain/context-map.md`.

Closed findings:

- Network Environment Operations is normalized as a target Bounded Context with independent operation identity/lifecycle;
- Resource Catalogue -> Access Governance is explicit for effective Resource Scope Affiliation facts; Access Governance owns obligation/scope-selection behavior and Authority Management owns actor/action admission;
- provider/network environment and optional enterprise identity/source seams are explicit;
- strategic relationship contracts, unknown/time/provenance obligations and default no-private-model/no-shared-kernel policy are canonicalized;
- stale legacy Requirement/Decision governance wording in the canonical Resource role summary is aligned to Business Connectivity / Access Governance / Access Policy.

Deferred without blocking Strategic convergence:

- responsibility-scope change consequences for existing authorization: reopen S1 when concrete warning/reapproval/withdrawal behavior is required;
- overlapping applicable responsibility-scope selection: Access Governance behavior/Tactical question, with S1 re-entry if product behavior is missing;
- exact external organizational provider/reference shape: optional source detail until a concrete integration is selected.

## Completed provider-policy boundary S2

```text
provider/device configuration
    -> Provider Policy Interpreter          [adapter/integration]
    -> ConfiguredEffectivePolicySnapshot    [source-neutral projection]

TargetRequiredPolicy
+ ConfiguredEffectivePolicySnapshot
    -> APR                                  [BC]
       assessment / common-missing-excess
       vendor-neutral change design
       semantic verification
    -> VerifiedChangeIntent
    -> Provider Policy Renderer             [adapter/integration]
    -> TargetPolicyArtifact
    -> NEO                                  [BC]
```

Ownership results:

- provider interpretation is not a new BC and is not TAE domain ownership;
- TAE remains immutable source-qualified evidence and does not decide APR currentness/completeness;
- APR core remains provider-neutral;
- provider rendering is not APR domain ownership;
- semantic equivalence of rendered output is mandatory, while proof mechanism belongs to Architecture;
- NEO is a target BC owning controlled execution lifecycle and does not reinterpret policy meaning or placement;
- unsupported/incomplete provider semantics fail closed.

APR-P02 and APR-P07 strategic ownership questions are resolved by ADR-021. Their architecture/implementation mechanics remain downstream.

## Remaining dirty areas

- APR Tactical DDD: effective technical-region vocabulary/edge cases, change-design vocabulary, proposed-change verification, computation model and final ERD;
- NEP internal S2 revalidation against accepted G1 requirements;
- responsibility-scope change/overlap behavior only when a concrete product use case promotes those deferred questions;
- migration of legacy Requirement/Decision/Proposal/UI/API/runtime artifacts;
- S3 architecture for provider interpreter/renderer, completeness contracts, semantic-equivalence proof and target-artifact handoff.

## Blockers

No repository blocker for starting APR-P03.

## Gate

Governance chain: `G2 PASS`.

Required Policy Materialization: `G2 PASS`.

Provider policy boundary: `G2 PASS` for S2 ownership/contracts.

Global Strategic DDD/context map: `PASS` for current target scope.

Next selected slice: `APR-P03 S2 Tactical DDD NOT_STARTED`.

No implementation lease exists.

## Next

Resume **APR Tactical DDD** from provider-neutral contracts, beginning with APR-P03 effective technical access-space semantics and exact comparison/completeness behavior. This is the next dependency for change design/verification and later S3 data-local computation.

NEP internal S2 remains separately available and does not block APR's provider-neutral semantic model because APR consumes only the accepted public NEP target/locator contract.
