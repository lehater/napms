# Active execution

Current: `domain-erd-revalidation.md`

Goal: converge revalidated capabilities into coherent Strategic/Tactical DDD before affected Architecture or implementation proceeds.

Current task: select the next S2 slice after completing provider-policy interpretation/rendering ownership.

Lifecycle stage: `S2`

Stage state: `NOT_STARTED`

Implementation authorization: `none`

Authorized scope: `none`

Authorization basis: `none`

## Lifecycle basis

Completed S2 slices:

- governance chain — `G2 PASS` (ADR-019);
- required-policy materialization — `G2 PASS` (ADR-020);
- provider configured-policy interpretation/rendering boundary — `G2 PASS` for strategic ownership/contracts (ADR-021).

No G3/G4 or implementation authorization exists.

## Completed provider-policy boundary S2

ADR-021 resolves the previously dirty boundary:

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
- semantic equivalence of rendered output is mandatory, while the proof mechanism belongs to Architecture;
- NEO executes a supplied target artifact and does not reinterpret policy meaning;
- unsupported/incomplete provider semantics fail closed.

APR-P02 and APR-P07 strategic ownership questions are resolved by ADR-021. Their architecture/implementation mechanics remain downstream.

## Remaining dirty areas

- APR Tactical DDD: effective technical-region vocabulary/edge cases, change-design vocabulary, proposed-change verification, computation model and final ERD;
- NEP internal S2 revalidation against accepted G1 requirements;
- responsibility-scope change consequences for existing authorization;
- Process organizational-responsibility integration semantics;
- migration of legacy Requirement/Decision/Proposal/UI/API/runtime artifacts;
- S3 architecture for provider interpreter/renderer, completeness contracts, semantic-equivalence proof and target-artifact handoff.

## Blockers

No repository blocker for selecting the next S2 slice.

## Gate

Governance chain: `G2 PASS`.

Required Policy Materialization: `G2 PASS`.

Provider policy boundary: `G2 PASS` for S2 ownership/contracts.

Next selected slice: `S2 NOT_STARTED`.

No implementation lease exists.

## Next

The end-to-end ownership chain is now stable enough that further S2 work can proceed independently by context.

Preferred next slice: resume **APR Tactical DDD** from provider-neutral contracts, beginning with APR-P03 effective technical access-space semantics and the exact comparison/completeness model. This is the next dependency for change design/verification and later S3 data-local computation.

NEP internal S2 remains separately available and does not block APR's provider-neutral semantic model because APR consumes only the accepted public NEP target/locator contract.
