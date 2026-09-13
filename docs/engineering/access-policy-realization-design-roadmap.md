# Access Policy Realization Target Design Roadmap

Status: `active design roadmap; implementation gate closed`.

Date: 2026-09-13.

## Purpose

Carry the current Access Policy Realization problem statement through a complete target Tactical DDD and implementation-ready migration design without allowing the existing runtime model to redefine the target.

Canonical APR problem statement:

- `docs/domain/access-policy-realization/README.md`.

Parent domain-model review:

- `docs/plans/active/domain-erd-revalidation.md`.

The selected current execution stage is tracked separately under `docs/plans/active/`; this roadmap owns only the durable ordered sequence and stage gates.

## Fixed starting point

The following are accepted starting constraints for this roadmap:

- APR remains a separate bounded context;
- upstream target selection/relevance/path reasoning is outside APR;
- APR receives target-specific required policy input and comparable configured-policy input;
- the unit of comparison is effective access semantics, not raw firewall rule text or provider-native rule identity;
- exact semantic comparison is based on `common`, `missing` and `excess` access space;
- realization assessment, semantic delta and policy change design are distinct concepts;
- proposed changes require semantic pre-execution verification;
- rendering must preserve verified semantics;
- very large policy sets must not be required to cross the application boundary as complete in-memory object graphs;
- data-local computation may use PostgreSQL or another engine behind APR-owned semantics;
- physical database co-location does not permit APR to depend on peer-private persistence schemas;
- existing APR runtime types/code are migration evidence only until the target model is locked.

If any later finding conflicts with these constraints, use `docs/process/decision-protocol.md` and `docs/process/domain-change-protocol.md`; do not silently change a lower layer.

## Execution rule

For each stage:

```text
resolve semantic unknowns
    -> update highest canonical owner first
    -> propagate only required requirement/architecture/ADR deltas
    -> add executable/specification evidence where appropriate
    -> pass the stage exit gate
    -> select the next stage in docs/plans/active/
```

No runtime migration is authorized by stages D1-D7.

Implementation planning is opened only in D8 after the target model is accepted.

## Roadmap

| Stage | Objective | Primary durable outcome | Gate |
| --- | --- | --- | --- |
| D0 | reset APR framing | single current APR problem statement; obsolete APR model removed | complete |
| D1 | cross-context input/output contracts | exact target/required/configured contracts, ownership, time, completeness and provenance | open |
| D2 | effective-access semantics | exact technical access-space algebra, comparability and realization status semantics | blocked by D1 |
| D3 | semantic computation/data-local boundary | APR-owned computation contract and first storage/engine strategy | blocked by D2 |
| D4 | policy change design | vendor-neutral semantic-to-change model distinct from delta | blocked by D2/D3 |
| D5 | proposed-change verification | simulation/equivalence contract and failure/unknown semantics | blocked by D4 |
| D6 | rendering boundary | exact renderer input/output and APR-to-NEO handoff | blocked by D4/D5 |
| D7 | canonical Tactical DDD/ERD | target model, identities/lifecycles, derived/persisted decisions, invariants and ADRs | blocked by D1-D6 |
| D8 | implementation readiness and migration roadmap | target-vs-current gap report, ordered migration plan, validation/performance gates | blocked by accepted D7 |

## D0 — Problem framing reset — complete

Outcome already present on the design branch:

- old APR I18/I20/I21 target documentation was removed;
- strategic/ownership/architecture documentation was aligned with the new context boundary;
- `docs/domain/access-policy-realization/README.md` is the single current APR framing source;
- old runtime models are no longer canonical design input.

D0 is not a historical archive. Its only purpose here is to define the starting state for remaining work.

## D1 — Lock cross-context inputs and outputs

### Objective

Define exactly what APR receives and returns before choosing an internal object model or storage algorithm.

### Must resolve

1. **Policy target correlation**
   - opaque target reference consumed by APR;
   - policy/ACL/subpolicy locator where required;
   - whether one APR comparison unit is target, target+policy locator, or another explicit key;
   - guarantee that required and configured sides address the same comparison unit.

2. **Required effective-policy contract**
   - owning context/workflow for publishing target-specific required policy;
   - stable snapshot/reference identity;
   - exact effective-time semantics where required;
   - technical region payload or data-local projection contract;
   - provenance back to authoritative Access Policy / catalogue/resource inputs without copying their authority.

3. **Configured effective-policy contract**
   - owner of the configured technical evidence;
   - source/snapshot identity;
   - target/policy correlation;
   - explicit completeness meaning;
   - evidence/effective-time semantics;
   - provenance and failure/unknown behavior.

4. **Provider-specific normalization ownership**
   - who converts raw ordered ACL/provider semantics into comparable source-neutral effective access;
   - where permit/deny/default, objects/groups, ordering and any NAT-dependent semantics are resolved;
   - what APR may assume about published configured effective-policy input.

5. **Published integration boundary**
   - owner-published API/projection/view/event/table contract as appropriate;
   - no APR dependency on peer-private tables;
   - consistency/snapshot semantics when projections are physically co-located for data-local computation.

6. **Conceptual APR output contracts**
   - compact realization assessment reference/metadata;
   - semantic delta reference/access pattern;
   - provenance sufficient for downstream change design, verification and explanation.

### Durable artifacts

Update the highest applicable canonical owners, potentially including:

- APR domain framing/target model;
- upstream owner contract documentation where publication semantics change;
- APR requirements for observable contract behavior;
- architecture boundary for published/data-local integration;
- ADR only for consequential choices that need an explicit decision record.

### Exit gate

D1 is complete only when one comparison can be identified without ambiguity as:

```text
same APR comparison key
+ required effective-policy snapshot/reference
+ configured effective-policy snapshot/reference
+ explicit comparability/completeness/time contract
+ traceable provenance
```

and no APR contract needs NEP candidate/path/relevance semantics to interpret that input.

## D2 — Lock effective-access-space semantics and assessment rules

### Objective

Define the exact mathematical and business meaning of policy equality/difference independently from SQL, Python objects or a vendor rule model.

### Must resolve

- canonical dimensions of one technical region;
- IPv4/IPv6 representation and family rules;
- address ranges/CIDRs/ANY semantics;
- protocol semantics, including protocol ANY and non-port protocols;
- source/destination port semantics and NotApplicable/Any distinctions where needed;
- whether the core comparison is effective Permit space only or another explicit decision function;
- treatment boundary for ordered deny/default behavior before the APR comparison layer;
- NAT-dependent semantics and whether NAT is normalized upstream or included in APR comparison dimensions;
- canonical union/normalization rules;
- exact intersection/difference/equivalence semantics;
- comparison scope and configured completeness requirements;
- `Unknown` conditions and fail-closed behavior;
- final realization assessment vocabulary and derivation from semantic delta;
- delta explainability/provenance semantics.

### Required evidence

Specification-by-example must include at least:

- one `/24` versus two equivalent `/25` rules;
- partial coverage;
- over-permission only;
- simultaneous missing and excess access;
- empty but complete policy;
- empty but incomplete evidence;
- protocol/port edge cases;
- equivalent different rule/object decompositions;
- source/provider cases that cannot be normalized safely and therefore remain unknown/unsupported rather than widened.

### Exit gate

A storage-independent implementation can determine whether two complete comparable effective-policy sets are exact, under-realized, over-realized or divergent and can compute exact `common`, `missing`, `excess` without semantic widening/narrowing.

## D3 — Design the semantic computation and data-local boundary

### Objective

Make the domain semantics executable at large scale without forcing complete policy hydration into the application process.

### Must resolve

- APR-owned semantic engine/application port vocabulary;
- reference/snapshot-based operations rather than collection-shaped APIs for unbounded datasets;
- assessment/delta creation and paged/streamed delta retrieval;
- snapshot consistency and transaction/read-isolation requirements;
- derived workset/index/materialization lifecycle and rebuild semantics;
- concurrency/idempotency of recomputation where relevant;
- first PostgreSQL representation candidate for effective regions;
- range/multirange/index strategy only after D2 semantics are known;
- expected workload and benchmark dataset sufficient to reject obviously unsafe designs;
- explicit triggers for moving from relational/range computation to BDD/FDD/atomic-predicate or another symbolic representation.

### Design rule

`PolicySemanticEngine` is a semantic placeholder, not a required final type name. The contract must express APR language and remain independent of one persistence technology.

### Exit gate

The architecture can execute D2 semantics data-locally and return compact results without requiring complete required/configured policies in application memory. The selected first engine has a falsifiable performance/correctness validation plan.

## D4 — Design Policy Change

### Objective

Translate an exact semantic delta into a vendor-neutral change design without collapsing `missing/excess` into naive `Add/Remove/Replace` labels.

### Must resolve

- minimum MVP change-design vocabulary;
- base configured snapshot/revision correlation;
- relationship between semantic additions/removals and structural rule/object edits;
- whether MVP supports only semantic additions/removals or may safely reuse/modify existing rules/objects;
- deterministic strategy/selection rules where multiple valid designs exist;
- provenance from each change operation back to delta regions;
- unsupported/ambiguous design cases;
- explicit deferral boundary for policy optimization (redundancy/shadowing/unused/overly broad cleanup) unless required by change correctness.

### Exit gate

A change design is a distinct derived artifact that states how to transform the selected base policy toward the required semantics and retains enough information for verification and rendering.

## D5 — Design proposed-change semantic verification

### Objective

Define pre-execution proof that applying a proposed change to the selected base policy produces the required effective policy.

### Must resolve

- simulation/evaluation input contract;
- base snapshot revision protection;
- semantics of `effective(base + proposedChange)`;
- exact equality against required policy;
- remaining missing and introduced/remaining excess reporting;
- unsupported/unknown cases;
- whether verification materializes a proposed effective-policy workset or evaluates it symbolically/data-locally;
- provenance linking verification to exact base, desired input and change design.

### Exit gate

A proposed change cannot be called verified unless the engine proves semantic equality for complete comparable inputs. Operational apply/read-back remains outside APR.

## D6 — Lock rendering and APR-to-NEO handoff

### Objective

Define the representation boundary after semantic verification and before operational mutation.

### Must resolve

- whether rendering consumes a verified change design, a verified full target policy, or two explicit modes;
- provider/platform capability negotiation and unsupported behavior;
- renderer contract/version identity;
- deterministic output requirements;
- semantic equivalence obligation between verified intent and rendered representation;
- target/base revision information required by NEO;
- artifact provenance and integrity identity;
- clear separation between APR rendering verification and NEO apply/post-operation verification.

### Exit gate

One explicit APR output contract can be handed to NEO without NEO having to reinterpret desired-policy semantics or APR having to own connection/apply/rollback lifecycle.

## D7 — Lock canonical Tactical DDD, ERD and persistence decisions

### Objective

Consolidate D1-D6 into the final target model.

### Required deliverables

- one canonical APR Tactical DDD document;
- PlantUML ERD;
- entity/value-object/derived-projection table;
- identity and lifecycle decisions;
- aggregate-root decision, including an explicit decision that no aggregate is required where appropriate;
- persisted authoritative state versus derived computational state/worksets;
- cross-context contract table;
- full invariant list;
- use-case contracts;
- unresolved questions with explicit non-blocking deferrals/revisit triggers;
- consequential ADRs where required;
- requirements and architecture updated so no competing APR target model remains.

### Exit gate

The APR target model is internally consistent, mutually consistent with upstream owner contracts and sufficient to evaluate current code as migration evidence without inventing semantics.

## D8 — Implementation readiness and migration roadmap

### Objective

Plan implementation only after target semantics are locked.

### Must produce

1. **Target-vs-current gap report**
   - classify current APR domain/application/infrastructure/workflow/UI elements as retain, adapt, replace or remove;
   - rank semantic mismatches P0/P1/P2/P3;
   - identify old runtime concepts that must not survive by compatibility accident.

2. **Data/projection migration plan**
   - required upstream published projections/contracts;
   - schema/index/workset changes;
   - backfill/rebuild rules where needed;
   - compatibility period only where unavoidable and explicitly bounded.

3. **Ordered implementation increments**
   - Domain/Application/Ports first;
   - core/specification/architecture tests;
   - core/knowledge gates;
   - data-local infrastructure implementation;
   - integration adapters/projections;
   - rendering/NEO handoff;
   - operator/read/UI migration only after accepted backend semantics;
   - deletion of obsolete old APR paths rather than indefinite compatibility layers.

4. **Validation plan**
   - semantic acceptance corpus;
   - PostgreSQL/integration correctness tests;
   - workload/performance benchmark for the selected data-local engine;
   - architecture/knowledge/harness checks;
   - hosted PR gate when the later implementation PR is ready.

### Exit gate / implementation gate

Implementation may begin only when:

- D1-D7 are accepted;
- no blocking semantic unknown remains hidden in implementation choices;
- the target-vs-current gap report exists;
- the migration sequence and rollback/rebuild implications are understood;
- the first implementation work package has explicit executable acceptance criteria.

## Cross-stage guardrails

1. **No old-model resurrection.** Removed APR I18/I20/I21 documentation and current runtime types are not sources of target truth.
2. **No placement leakage.** APR does not reinterpret why a target was selected.
3. **No rule-text equality.** Provider configuration decomposition is not effective-policy equality.
4. **No implementation-first decisions.** SQL shape, Python type convenience or existing schema cannot settle unresolved semantics.
5. **No giant object-graph requirement.** Unbounded policy datasets remain behind references/data-local computation boundaries.
6. **No peer-private SQL coupling.** Published integration contracts remain explicit even when computation is physically co-located.
7. **No semantic widening for convenience.** Unsupported source semantics fail closed/unknown rather than broaden/narrow policy space.
8. **No execution ownership drift.** Connection/apply/retry/rollback/post-apply operation lifecycle remains NEO.
9. **No speculative optimization scope.** Policy cleanup/optimization enters only when required by accepted APR correctness/use cases.
10. **No premature durable lifecycle.** Derived assessments/deltas/change designs remain derived unless an accepted product workflow introduces independent identity/lifecycle.

## Roadmap completion

This roadmap is complete when D8 has produced an accepted implementation migration roadmap and the first implementation increment can be selected without reopening unresolved core APR semantics.

At completion, durable target truth must live in domain/requirements/architecture/decisions; active plan material is removed after its outcomes are absorbed, consistent with repository policy.
