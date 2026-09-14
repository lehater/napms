# Active execution

Current: breadth-first capability revalidation before Strategic DDD recomposition.

Goal: establish one coherent accepted S1 product contract across business need, access governance, Access Policy and realization semantics before later domain boundaries are reused or redesigned.

Current task: consolidate the 2026-09-14 G1 passports with older accepted requirements that still encode superseded Connectivity Requirements / Connectivity Decision and Deployment↔Resource assumptions.

Lifecycle stage: `S1`

Stage state: `IN_PROGRESS`

Lifecycle basis: stakeholder-confirmed capability semantics are preserved in `docs/engineering/context-problems/capability-revalidation-checkpoint-2026-09-14.md`; `business-connectivity-g1.md`, `access-governance-g1.md` and `policy-realization-reconciliation-g1.md` are coherent, but `access-policy-core.md` and `application-catalogue-domain-target.md` still conflict with those accepted semantics. Existing Strategic DDD/capability ownership and APR rendering design are downstream `DIRTY` artifacts, not S1 truth.

Implementation authorization: `none`

Authorized scope: `none`

Authorization basis: `none`

## Working set

Read first:
- `docs/engineering/context-problems/capability-revalidation-checkpoint-2026-09-14.md`
- `docs/requirements/business-connectivity-g1.md`
- `docs/requirements/access-governance-g1.md`
- `docs/requirements/policy-realization-reconciliation-g1.md`
- `docs/requirements/access-policy-core.md`
- `docs/requirements/application-catalogue-domain-target.md`
- `docs/process/requirements-stage.md`

Load S2/domain artifacts only to identify downstream invalidation; do not use them to override accepted S1 behavior.

## Current G1 findings

### P1 — Access Policy requirement conflict

`docs/requirements/access-policy-core.md` still consumes one final `Connectivity Decision Allowed | NotAllowed` contract. The accepted access-governance semantics now require bilateral source/destination consent and explicit withdrawal semantics before current Policy Rule truth is derived.

Required action: revalidate Access Policy observable behavior against authorization grant/withdrawal semantics while preserving compatible Rule identity/deduplication guarantees.

### P1 — ComponentDeployment Resource-binding conflict

`docs/requirements/application-catalogue-domain-target.md` / ADR-015 currently allow zero or more Resource bindings per ComponentDeployment. The latest accepted MVP evidence requires each concrete ComponentDeployment to belong to exactly one Resource, with Resource association mandatory at creation and Resource movement not silently carrying authorization to a different concrete deployment.

Required action: revalidate the ACC target requirement before relying on ADR-015 as current S1 truth.

### Downstream DIRTY artifacts

The new S1 semantics invalidate assumptions in later-stage artifacts, including:
- `docs/domain/strategic-model.md` — old CR/CD BC exclusion and direct AM→Access Policy MVP authorization path;
- `docs/domain/capabilities.md` — old capability ownership/grouping around Connectivity Requirements/Decision;
- `docs/domain/access-policy-realization/README.md` — provider-specific rendering remains inside APR framing despite the newer normalized/provider-boundary direction.

Do not repair these S2/S3 artifacts until the current G1 requirement conflicts are consolidated and G1 is re-evaluated.

## NEP parked recovery state

NEP remains independently checkpointed after `G1 PASS`:
- `S0 Problem/Evidence` passed G0;
- `S1 Requirements` passed G1;
- accepted behavior is in `docs/requirements/network-enforcement-placement-core.md`;
- next NEP stage is S2 Domain Design revalidation;
- no runtime migration or implementation is authorized.

If NEP is resumed later, compare its existing target model/ADR against accepted S1 requirements rather than assuming the older S2 model remains valid unchanged.

## Other recovery facts

- Access Policy Realization implementation remains parked and unauthorized.
- APR unresolved future work remains at `docs/engineering/context-problems/access-policy-realization.md`.
- A completed gate for one slice does not authorize implementation or force other slices to the same lifecycle stage.
- Strategic DDD is intentionally deferred until the breadth-first G1 contract is coherent enough to support BC regrouping.

## Blockers

No external stakeholder decision is currently required for the two blocking S1 conflicts. Existing 2026-09-14 accepted evidence supplies the product semantics needed for requirements consolidation.

## Gate

Breadth-first capability G1: `REWORK`.

Blocking P1 findings:
1. Access Policy still depends on the superseded single Decision contract.
2. ACC ComponentDeployment Resource cardinality contradicts the latest accepted MVP behavior.

NEP remains separately at `G1 PASS` and is not reopened by this cross-capability review unless its own accepted requirements later change.

## Next

Rework the two conflicting S1 requirement owners, then run the G1 consistency gate again. If G1 passes, enter S2 Strategic DDD to regroup capabilities and rebuild the Context Map from the accepted passports; only then resume Tactical DDD for affected bounded contexts.
