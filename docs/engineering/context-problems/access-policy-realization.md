# Access Policy Realization — Context Problem Register

Bounded context: `Access Policy Realization`.

Status: `open problem register; context not currently active`.

Date: 2026-09-13.

Implementation gate: **closed while blocking target-design problems remain unresolved**.

## Purpose

Preserve the unresolved APR design/migration problem space across workstream switches without pretending that all future work already has a reliable execution order.

Canonical APR semantic framing:

- `docs/domain/access-policy-realization/README.md`.

Planning lifecycle:

- `docs/process/plan-lifecycle.md`;
- `docs/engineering/context-problems/README.md`.

Current runtime code and removed APR I18/I20/I21 documentation are not target truth. Runtime code is migration evidence only after target semantics are established.

## Accepted starting constraints

The following are currently fixed by canonical APR framing and surrounding architecture:

- APR remains a separate bounded context;
- target selection/relevance/path reasoning is upstream of APR;
- APR compares target-specific required effective policy with comparable configured effective policy;
- policy equality is equality of effective access semantics, not raw firewall rule text, rule identity, object decomposition or rule count;
- semantic comparison requires exact `common`, `missing` and `excess` access space;
- realization assessment, semantic delta and policy change design are distinct concepts;
- proposed changes require semantic pre-execution verification;
- rendering must preserve verified semantics;
- operational connection/apply/retry/rollback/post-apply lifecycle belongs to NEO;
- very large policy sets must not require mandatory full in-memory hydration in the application process;
- data-local computation may use PostgreSQL or another implementation behind APR-owned semantics;
- physical database co-location does not authorize direct dependency on peer-private persistence schemas;
- derived computation/worksets do not become authoritative upstream truth merely because they are materialized.

If later evidence conflicts with these constraints, use the decision/domain-change protocols and update the highest canonical owner first.

## Open problem register

Problem IDs are stable references only. They do **not** express priority or execution order.

### APR-P01 — Comparison key and cross-context input contract

**Problem**

APR needs an exact definition of one comparable policy unit without importing NEP placement semantics.

Open questions:
- what opaque target reference APR receives;
- whether comparison identity is `target`, `target + policy/ACL locator`, or another explicit partition key;
- how required and configured sides prove they address the same unit;
- which owner/application composition publishes target-specific required effective policy;
- snapshot/reference identity and logical/effective time semantics;
- provenance required to trace the required side back to authoritative Access Policy/catalogue/resource facts without copying their authority;
- whether payload is transferred as rows or referenced through a data-local published projection.

**Blocks**

A confident reconciliation contract cannot exist until the two sides can be proven comparable.

**Dependencies**

No total-order dependency is asserted. This problem must be considered together with APR-P02 and APR-P03 because normalization/scope semantics constrain the comparison key.

### APR-P02 — Configured effective-policy publication and normalization ownership

**Problem**

Configured evidence currently originates from provider/source material, but APR must compare effective policy semantics rather than raw ACL rows.

Open questions:
- which owner publishes the configured effective-policy view consumed by APR;
- exact relationship to TAE Evidence Set/source scope/capture;
- configured snapshot/reference identity;
- evidence/effective-time semantics;
- explicit completeness meaning;
- how target/policy locator correlation is established;
- who resolves ordered ACL behavior, Permit/Block/default behavior, nested objects/groups, protocol/service aliases and attachment/subpolicy semantics;
- whether NAT-dependent semantics must be normalized upstream or represented in the effective comparison model;
- how unsupported source semantics fail closed instead of being widened/narrowed.

**Blocks**

Raw provider rows cannot be treated as a trustworthy configured policy side.

**Dependencies**

Closely coupled to APR-P01 and APR-P03. Choice of effective-access semantics may constrain what normalization must publish.

### APR-P03 — Effective technical access-space semantics and comparability

**Problem**

The mathematical/domain meaning of effective policy equality and difference is not yet fully locked.

Open questions:
- canonical dimensions of one technical region;
- IPv4/IPv6 family rules;
- Any/range/CIDR semantics;
- protocol semantics including protocol Any and non-port protocols;
- source/destination port Any/NotApplicable/range semantics;
- whether the core comparison is effective Permit space only or another explicit decision function;
- exact union/canonicalization/intersection/difference/equivalence rules;
- comparison-scope rules;
- completeness conditions required for a conclusive result;
- `Unknown`/unsupported/fail-closed semantics;
- final realization-assessment vocabulary and how it derives from `missing`/`excess`;
- exact provenance/explainability semantics for delta regions.

Required specification evidence should eventually cover:
- one `/24` versus two equivalent `/25` decompositions;
- partial coverage;
- over-permission only;
- simultaneous missing and excess;
- empty complete policy versus empty incomplete evidence;
- protocol/port edge cases;
- equivalent policies with different rule/object decomposition;
- source constructs that cannot be normalized safely.

**Blocks**

APR cannot choose a computation/storage strategy or prove policy equivalence without this semantic contract.

**Dependencies**

APR-P01/P02 must expose enough scope/normalization information for this model to be meaningful. The semantic model should not be chosen to fit an implementation technology.

### APR-P04 — Data-local semantic computation boundary

**Problem**

APR must execute exact set comparison for potentially very large policies without loading complete sets as application object graphs.

Open questions:
- application/semantic-engine contract vocabulary;
- reference/snapshot-based operations;
- compact assessment/delta result shape;
- paged/streamed delta retrieval;
- snapshot consistency and transaction/isolation requirements;
- derived workset/index/materialization lifecycle;
- rebuild/idempotency/concurrency semantics where needed;
- first PostgreSQL representation/index candidate;
- workload assumptions and benchmark corpus;
- falsifiable triggers for introducing BDD/FDD/atomic predicates or another symbolic engine.

**Blocks**

Large-volume implementation is unsafe until semantics are stable enough to test candidate engines.

**Dependencies**

Depends materially on APR-P03. APR-P01/P02 determine how data-local published projections can be referenced without peer-private schema coupling.

### APR-P05 — Semantic Delta versus Policy Change Design

**Problem**

`missing` and `excess` explain semantic difference but do not uniquely define how an existing policy should be edited.

Open questions:
- minimum vendor-neutral change-design vocabulary;
- base configured snapshot/revision correlation;
- relationship between semantic additions/removals and structural rule/object operations;
- whether MVP change design may reuse/modify existing rules/objects or starts with a more conservative semantic representation;
- deterministic strategy when multiple valid edit designs exist;
- provenance from change operations back to delta regions;
- unsupported/ambiguous design cases;
- boundary between correctness-driven change design and later optimization/cleanup (redundancy, shadowing, unused rules, broad rules).

**Blocks**

Rendering and semantic proposed-change verification need a well-defined change representation.

**Dependencies**

Requires the effective semantics of APR-P03. A concrete engine from APR-P04 may enable efficient design, but engine technology must not define the domain concept.

### APR-P06 — Proposed-change semantic verification

**Problem**

APR needs a proof that a proposed change applied to the selected base policy yields the required effective semantics before execution.

Open questions:
- simulation/evaluation input contract;
- base snapshot/revision protection;
- exact meaning of `effective(base + proposedChange)`;
- equality criterion against required policy;
- reporting of remaining missing and introduced/remaining excess;
- unsupported/unknown cases;
- whether verification materializes a proposed effective-policy workset or evaluates symbolically/data-locally;
- provenance linking required policy, base configured snapshot and change design.

**Blocks**

A change cannot be called verified, nor safely handed to rendering/execution, without this contract.

**Dependencies**

Depends on APR-P03 and APR-P05; likely implemented through the computation capability addressed by APR-P04.

### APR-P07 — Rendering boundary and APR-to-NEO handoff

**Problem**

The final representation boundary after semantic verification and before operational mutation is not yet locked.

Open questions:
- whether rendering consumes verified change design, verified full target policy, or two explicit modes;
- provider/platform capability negotiation;
- unsupported behavior;
- renderer contract/version identity;
- deterministic output requirements;
- semantic-equivalence obligation between verified intent and rendered artifact;
- target/base revision information required downstream;
- artifact provenance/integrity identity;
- exact division between APR semantic/render verification and NEO apply/post-operation verification.

**Blocks**

APR cannot define a stable downstream execution handoff until the verified semantic input and renderer contract are clear.

**Dependencies**

Depends on APR-P05/P06. Provider limitations may feed evidence back into the permitted change-design/render contract without redefining required policy semantics.

### APR-P08 — Technical-to-domain attribution/explanation role

**Problem**

APR needs explainability linking technical access regions to domain/business meaning, but technical equality should not become dependent on successful attribution unless a concrete invariant requires it.

Open questions:
- what attribution capability is required by users/operators;
- which upstream owner data it consumes;
- whether attribution is per delta region, input region, or another trace unit;
- how ambiguity/unknown attribution is represented;
- what reconciliation outcomes remain valid when technical equivalence is provable but business attribution is incomplete.

**Blocks**

Does not necessarily block pure technical equivalence, but may block explainability/product acceptance if left undefined.

**Dependencies**

Uses APR-P03 region semantics and cross-context provenance from APR-P01/P02.

### APR-P09 — Canonical Tactical DDD / ERD / persistence decisions

**Problem**

The final APR tactical model has not been consolidated after the old I18/I20/I21 model was removed.

Must eventually resolve:
- entities/value objects/domain services/derived projections;
- identity and lifecycle decisions;
- whether any aggregate root exists at all for the current computational model;
- authoritative persisted state versus derived worksets/cache/indexes;
- cross-context contract table;
- invariants;
- use-case contracts;
- final PlantUML ERD;
- required ADRs for consequential decisions;
- explicit non-blocking deferrals/revisit triggers.

**Blocks**

Implementation migration should not start from an unaccepted target model.

**Dependencies**

This model can evolve while other problems are resolved, but final lock must be consistent with all accepted decisions affecting APR-P01 through APR-P08.

### APR-P10 — Target-versus-current implementation gap and migration

**Problem**

Current APR runtime still embodies obsolete semantics and must be assessed only after target semantics are locked.

Known gap directions already visible:
- old runtime derives/owns placement-related outcomes that belong upstream;
- old `DomainAccessResolution`/technical-to-domain slice is entangled with reconciliation;
- application reconciliation materializes policy object graphs rather than using an explicit large-set semantic engine;
- old `DesiredEnforcementPolicy`/`ManagedReconciliationScope` concepts do not match the new target boundary;
- old `Add | Remove | Replace | No-op` change summary is insufficient as concrete change design;
- current rendering is coupled to the old desired-policy representation;
- Network Operator Realization workflow/UI still consumes old runtime concepts.

When target semantics are ready, produce:
- retain/adapt/replace/remove classification;
- P0/P1/P2/P3 semantic gap report;
- projection/schema/index/workset migration needs;
- data rebuild/backfill policy;
- bounded compatibility needs if any;
- ordered implementation increments only where implementation dependencies actually require them;
- semantic, integration and scale validation plan.

**Blocks**

Implementation migration remains closed until APR-P09 is sufficiently locked for the intended first increment.

**Dependencies**

Depends on accepted target semantics rather than on the current code structure.

## Known cross-context dependencies

The register currently knows about these relationships without assigning project priority:

- upstream target assignment/locator semantics constrain APR-P01;
- TAE/provider evidence semantics constrain APR-P02;
- Access Policy/ACC/RC published technical intent and provenance constrain APR-P01/P08;
- NEO execution contract constrains the output side of APR-P07 but does not own APR semantics;
- workload/scale evidence constrains APR-P04 implementation choice.

If any of these upstream contracts change while APR is parked, revalidate the affected problem before treating prior assumptions as current.

## Implementation blockers

APR implementation work that would commit to the new target model is blocked until, at minimum:

- one comparison unit and both required/configured input contracts are trustworthy enough for the intended slice;
- effective access-space semantics required by that slice are exact and testable;
- configured completeness/unsupported semantics fail closed;
- the chosen implementation slice does not resurrect NEP placement semantics or raw-rule equality inside APR;
- target Tactical DDD is sufficiently locked to classify current code as migration evidence rather than target truth.

A future active plan may deliberately select a smaller non-blocked design/implementation slice, but it must state which open problems it depends on and which remain safely deferred.

## Evidence still needed

Likely evidence gaps include:
- representative configured-policy source semantics across target platforms;
- realistic policy-size/workload distributions for computation design;
- concrete examples requiring NAT-aware or ordered deny/default normalization;
- product/operator examples for technical-to-domain explanation;
- target renderer/NEO capability constraints that affect the change-design contract.

Do not invent these merely to close a design question.

## Revisit triggers

Revisit affected problems when any of the following occurs:
- upstream NEP target/locator publication contract changes;
- TAE adds source completeness/coverage semantics;
- a concrete provider adapter exposes semantics not representable by the current effective-policy model;
- measured scale invalidates the selected data-local representation;
- product requirements introduce editable/approvable durable change-plan lifecycle;
- NEO handoff requirements require additional verified artifact metadata;
- a new explainability/user workflow requires stronger business attribution.

## Relationship to roadmaps and active plans

This register intentionally contains no total `P01 -> P02 -> ...` execution sequence.

When project-wide prioritization chooses APR work:
1. revalidate the canonical APR framing and affected dependencies;
2. choose the concrete problem or causally connected subset to address;
3. create/update an active `PLAN-*.md` for that execution;
4. create a separate APR roadmap only if the selected work exposes a durable ordered migration/delivery sequence worth preserving.

Until then APR remains non-active, with its unresolved problem space preserved here.
