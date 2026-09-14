# Access Policy Realization — Context Problem Register

Bounded context: `Access Policy Realization`.

Status: `open problem register`.

Date: 2026-09-14.

Implementation gate: **closed while blocking target-design problems remain unresolved**.

## Purpose

Preserve unresolved APR design/migration problems across workstream switches without pretending that discovery order is an execution roadmap.

Canonical semantic framing:

- `docs/domain/access-policy-realization/README.md`.

Lifecycle/rules:

- `docs/process/plan-lifecycle.md`;
- `docs/engineering/context-problems/README.md`.

Current execution state is owned only by `docs/plans/active/README.md`; this register must not become a second current-work pointer.

Current runtime code and removed APR I18/I20/I21 documentation are migration evidence only, not target truth.

## Accepted starting constraints

- APR is a separate bounded context.
- Target selection/relevance/path reasoning is upstream.
- APR compares target-specific required effective policy with comparable configured effective policy.
- Equality is effective-access equality, not raw rule/configuration equality.
- Exact semantic difference is expressed through `common`, `missing`, `excess`.
- Realization assessment, Semantic Delta and Policy Change Design are distinct.
- Proposed changes require semantic pre-execution verification.
- Rendering must preserve verified semantics; operational mutation remains NEO.
- Very large policy sets must not require mandatory full in-memory hydration.
- Data-local computation may use PostgreSQL or another engine behind APR semantics.
- Peer-private persistence is not a cross-context integration contract.
- Materialized worksets/indexes remain derived unless a future accepted lifecycle says otherwise.

## Stakeholder evidence

The following observations were harvested from stakeholder discussion on 2026-09-13 and 2026-09-14. They are **non-authoritative source evidence**: useful input for APR-P01/P03/P05/P07/P11 and later Requirements/Domain work, but not accepted requirements or domain truth by themselves.

Observed / normalized evidence:

- A natural user-facing comparison result is scoped to a concrete firewall and a concrete access list, and explains what access is missing and what access is excess.
- Users may ask for several materially different outcomes around the same realization data, including:
  - the semantic difference for a specific firewall/access list;
  - a correction for a specific firewall/access list;
  - a check or correction for a specific source-destination pair, optionally constrained by service, on a specific firewall;
  - an audit of a firewall/access list.
- The semantic difference may be consumed without applying a change: for pair-access verification, audit/reporting, or preparation of recommended changes for another person.
- A comparison result may be used as input to produce configuration that brings the access list into the required state.
- "Implemented correctly" primarily means semantic correctness of effective behavior: everything that must be allowed is allowed, everything that must be denied is denied, and there is neither unintended access nor unintended blocking.
- Semantic correctness and configuration optimality are distinct. A configuration may be semantically correct while still being structurally or operationally suboptimal.
- Raw or structural rule comparison is insufficient where deny rules, ordering, nested groups/objects, default action, or similar constructs affect effective behavior; comparison must reason over normalized effective access semantics.
- For a concrete firewall/device, an operator may want to select a provider-supported representation strategy that keeps the same effective access semantics while reducing configuration size, for example a future `permit + deny` form instead of permit-only decomposition.
- A device-specific representation choice affects both write and read sides: if the system can render a provider construct, the provider interpreter must be able to read that construct back and recover the same effective access semantics for later APR comparison.
- Corporate address allocation may carry site/organizational meaning known to operators. On a particular firewall, an operator may know that many exact source/destination relations can intentionally be represented at broader site-prefix granularity to reduce ACL size.
- Such coarse aggregation is materially different from representation optimization because it may intentionally widen effective access on that target. The stakeholder preference is to consider an explicit/manual per-device directive rather than requiring the system to infer transit/edge roles or automatically decide where widening is safe.

Candidate interpretations to revisit only in their owning lifecycle stage:

- possible use-case candidates: access-list realization audit, pair accessibility check, and preparation of remediation recommendations;
- a possible multi-actor journey exists where one user obtains the difference and prepares recommended changes for another person; any review/approval step remains a hypothesis until supported by further evidence;
- firewall + access-list scope is strong evidence for a user-facing result boundary, but does **not** by itself establish APR aggregate identity, persistence partitioning, or internal computational unit;
- candidate future use case — **device-specific semantically equivalent representation optimization**: an operator selects or inherits a per-device rendering preference; a provider renderer may choose permit-only, future permit+deny, or another semantically equivalent representation only when the effective access space is preserved and the corresponding interpreter can recover it correctly;
- candidate future use case — **explicit target-specific coarse aggregation**: an operator explicitly identifies a concrete firewall and source/destination prefix envelopes for which exact technical requirements may be represented by a broader target-level permit, based on corporate addressing/site structure; this is a deliberate target-level relaxation, not a renderer-only optimization;
- candidate future journey for coarse aggregation: select firewall -> define source/destination aggregation envelopes and optional traffic scope -> inspect the expected widening and rule-count reduction -> explicitly accept the directive -> materialize target-specific required policy -> compare actual realization against that target-specific policy;
- current/default behavior remains conceptually exact realization unless a future owning stage explicitly accepts another target-specific realization policy; the candidate journey must not be read as an accepted relaxation rule.

Relevant open problems:

- APR-P01: evidence favors firewall + access-list as a natural user result/correlation scope, while the canonical comparison key remains unresolved until S1/S2 acceptance.
- APR-P03: evidence strongly supports effective semantic allow/deny equivalence rather than raw rule equality; exact technical-region semantics remain unresolved.
- APR-P05: semantic delta has independent user value beyond remediation, and remediation/config generation is a separate downstream outcome; the concrete change-design vocabulary remains unresolved.
- APR-P07: future device-specific rendering strategies require an explicit provider/device capability/preference contract and symmetric interpreter support; exact representation selection remains downstream design.
- APR-P11: explicit target-specific coarse aggregation may require a separate target-realization policy layer because it can intentionally widen target effective access and therefore cannot be treated as semantically equivalent rendering.

## Open problems

Problem IDs are stable references only. They do not encode priority or sequence.

### APR-P01 — Comparison key and required-policy publication

Need to determine:
- the minimum opaque target/policy correlation used for one APR comparison;
- whether the unit is target, target + ACL/policy locator, or another explicit partition;
- how required/configured sides prove they address the same unit;
- who publishes target-specific required effective policy;
- required snapshot/reference/time/provenance semantics;
- whether the required side is transferred or referenced through a data-local projection.

Known dependency: must remain consistent with configured-policy scope in APR-P02 and comparability semantics in APR-P03.

### APR-P02 — Configured effective-policy publication and normalization ownership

Need to determine:
- which owner publishes comparable configured effective policy;
- relationship to TAE source/scope/capture/snapshot;
- explicit completeness semantics;
- target/policy correlation;
- who resolves ordered ACL behavior, Permit/Block/default behavior, nested objects/groups, protocol/service aliases and attachment/subpolicy semantics;
- treatment of NAT-dependent semantics;
- fail-closed behavior for unsupported source constructs.

Blocking concern: raw provider rows cannot be treated as trustworthy effective policy.

### APR-P03 — Effective technical access-space semantics

Need to lock:
- canonical technical-region dimensions;
- IPv4/IPv6 rules;
- Any/range/CIDR semantics;
- protocol and source/destination-port semantics;
- whether comparison is effective Permit space only or another explicit decision function;
- canonical union/intersection/difference/equivalence;
- comparison-scope and completeness rules;
- Unknown/unsupported semantics;
- final realization-assessment derivation from semantic delta;
- delta provenance/explainability.

Required evidence should include equivalent different decompositions (`/24` vs two `/25`), partial coverage, over-permission, simultaneous missing/excess, empty-complete vs empty-incomplete evidence, protocol/port edge cases and unrepresentable provider semantics.

Known dependency: APR-P01/P02 must expose enough scope/normalization information; implementation technology must not define this model.

### APR-P04 — Data-local semantic computation

Need to determine:
- APR semantic-engine/application contract;
- reference/snapshot-based operations for unbounded datasets;
- compact assessment/delta references and paged/streamed access;
- consistency/isolation requirements;
- derived workset/index/materialization lifecycle;
- first PostgreSQL representation/index candidate;
- workload/benchmark evidence;
- objective triggers for BDD/FDD/atomic-predicate or another symbolic engine.

Known dependency: materially depends on APR-P03 and on the publication boundaries from APR-P01/P02.

### APR-P05 — Semantic Delta versus Policy Change Design

Need to determine:
- minimum vendor-neutral change-design vocabulary;
- base configured snapshot/revision correlation;
- relationship between semantic additions/removals and structural rule/object edits;
- whether MVP may reuse/modify existing rules/objects;
- deterministic behavior where multiple valid designs exist;
- provenance from changes back to delta regions;
- unsupported/ambiguous cases;
- boundary between correctness and later optimization/cleanup.

Known dependency: requires APR-P03 semantics; engine technology from APR-P04 may support it but must not define the concept.

### APR-P06 — Proposed-change semantic verification

Need to determine:
- simulation/evaluation contract;
- base revision protection;
- semantics of `effective(base + proposedChange)`;
- exact equality against required policy;
- remaining missing and introduced/remaining excess reporting;
- Unknown/unsupported behavior;
- workset versus symbolic/data-local evaluation;
- provenance linking required input, configured base and change design.

Known dependency: APR-P03 + APR-P05; likely implemented through APR-P04 capability.

### APR-P07 — Rendering boundary and APR-to-NEO handoff

Need to determine:
- whether rendering consumes verified change design, verified full target policy, or explicit modes;
- provider/platform capability negotiation and unsupported behavior;
- target/device-specific rendering preferences and how they are configured without becoming APR domain semantics;
- whether semantically equivalent strategies such as permit-only versus future permit+deny are selectable, automatic, or both;
- the invariant that a renderer may emit only constructs the provider interpreter can subsequently interpret back into trustworthy effective semantics for the supported comparison scope;
- renderer identity/version and deterministic-output requirements;
- semantic-equivalence obligation for rendered artifacts;
- target/base revision and integrity/provenance metadata needed by NEO;
- exact division between APR semantic/render verification and NEO operational verification.

Known dependency: APR-P05/P06. ADR-021 already fixes provider interpretation/rendering as integration/adapter responsibilities and requires semantic preservation/fail-closed behavior; this problem now concerns the remaining tactical/architectural contract details, not ownership.

### APR-P08 — Technical-to-domain attribution/explanation

Need to determine:
- which user/operator explanations require business/domain attribution;
- which owner data provides attribution;
- trace granularity;
- ambiguity/Unknown behavior;
- whether technical realization remains conclusive when technical equality is provable but attribution is incomplete.

Known dependency: uses APR-P03 region semantics and provenance from APR-P01/P02, but should not become a prerequisite for pure technical equality without a concrete invariant.

### APR-P09 — Canonical Tactical DDD / ERD / persistence decisions

Need to consolidate accepted decisions into:
- entities/value objects/domain services/derived projections;
- identity/lifecycle choices;
- aggregate-root decision, including explicit `none` if appropriate;
- authoritative persisted state versus derived computational state;
- cross-context contracts;
- invariants/use-case contracts;
- PlantUML ERD;
- required ADRs;
- explicit deferrals/revisit triggers.

Blocking concern: implementation migration should not establish the target model by accident.

Known dependency: final model must be consistent with accepted resolutions of the other APR problems that affect it; this does not require solving them in numerical order.

### APR-P10 — Target-versus-current gap and migration

Known gap directions already visible:
- current runtime still owns placement-related outcomes that belong upstream;
- old technical-to-domain resolution is entangled with reconciliation;
- application reconciliation materializes policy object graphs;
- old `DesiredEnforcementPolicy` / `ManagedReconciliationScope` concepts do not match the new boundary;
- old `Add | Remove | Replace | No-op` summary is insufficient as concrete change design;
- current renderer consumes the old desired-policy representation;
- Network Operator Realization workflow/UI still consumes old APR runtime concepts.

After target semantics are sufficiently locked, produce:
- retain/adapt/replace/remove classification;
- P0/P1/P2/P3 semantic gap report;
- required projection/schema/index/workset changes;
- rebuild/backfill rules;
- bounded compatibility needs if unavoidable;
- ordered migration increments only where actual dependencies require order;
- semantic/integration/scale validation plan.

Known dependency: depends on the accepted target model, not on current code structure.

### APR-P11 — Explicit target-specific coarse aggregation

Potential future capability only; **not an accepted requirement or domain rule**.

Need to determine, only if this candidate is later promoted by its owning lifecycle stage:
- whether there is a legitimate product need to intentionally widen effective access on a selected target in exchange for materially smaller/simpler ACLs;
- the owner of a target-specific aggregation/realization directive;
- actor authority required to create, change, disable or approve such a directive;
- how a directive identifies the concrete firewall/target and source/destination aggregation envelopes;
- whether protocol/service constraints are part of the directive;
- whether one exact required relation is enough to activate a whole envelope or whether another activation rule is required;
- how expected widening is calculated and shown before acceptance;
- provenance/audit requirements: who authorized the relaxation, when, for which target/envelopes, and why;
- lifecycle when corporate addressing, site ownership, target topology or target relevance changes;
- how `TargetRequiredPolicy` is derived from exact authorization plus explicit target-level realization policy;
- how APR distinguishes accepted target-level widening from unintended `excess`;
- whether coarse aggregation creates dependencies on other enforcement points and, if so, how those dependencies are represented or explicitly avoided;
- fail-closed behavior where the directive is stale, ambiguous, outside its scope or cannot be proven applicable.

Current constraint for design work outside this candidate: do not require automatic edge/transit classification, path proof, or coarse aggregation semantics. Preserve exact realization as the working/default model until an owning-stage decision explicitly changes it.

Revisit trigger: measured ACL/configuration pressure or an explicit operator workflow demonstrates that semantic-preserving compression is insufficient and that coarse target-level aggregation provides material operational value.

## Known cross-context dependencies

- NEP target/locator publication constrains APR-P01.
- TAE/provider evidence semantics constrain APR-P02.
- Access Policy/ACC/RC technical intent and provenance constrain APR-P01/P08.
- Provider/device capability and profile semantics constrain APR-P07 and any future APR-P11 realization directive, but must not silently redefine authorization semantics.
- NEO output requirements constrain APR-P07 but do not own APR semantics.
- Measured workload/scale evidence constrains APR-P04 implementation choice and is also required before APR-P11 can be justified as more than a speculative optimization.

These are dependency facts, not project priority.

## Implementation blockers

Implementation that commits to the new APR target remains blocked until the intended slice has, at minimum:
- a trustworthy comparison unit and required/configured input contract;
- exact effective-access semantics for that slice;
- fail-closed completeness/unsupported behavior;
- no resurrection of NEP placement semantics or raw-rule equality inside APR;
- enough accepted Tactical DDD to evaluate current code as migration evidence rather than target truth.

A future active plan may select a smaller safe slice, but it must state which open problems it depends on and which are explicitly deferred.

## Evidence still needed

Likely evidence gaps include:
- representative provider policy semantics;
- realistic policy-size/workload distributions;
- concrete NAT/ordered deny/default cases;
- operator explainability examples;
- renderer/NEO capability constraints affecting change design;
- representative devices where semantically equivalent permit/deny compression materially reduces configuration size;
- representative devices/policies where exact compression remains insufficient and explicit coarse aggregation would provide enough operational benefit to justify intentional target-level widening.

Do not invent these to close a design question.

## Revisit triggers

Revisit affected problems when:
- NEP target/locator publication changes;
- TAE gains source completeness/coverage semantics;
- a provider exposes semantics not representable by the current model;
- measured scale invalidates the selected representation;
- provider/device profiles gain target-specific rendering preferences or capability negotiation;
- measured configuration pressure creates a concrete need to evaluate explicit target-specific coarse aggregation;
- product requirements introduce durable editable/approvable change plans;
- NEO requires additional verified artifact metadata;
- new user workflows require stronger attribution/explanation.

## Relationship to planning

This register intentionally contains no total `P01 -> P02 -> ...` execution sequence.

When APR work is selected:
1. revalidate canonical APR truth and affected dependencies;
2. choose the concrete problem or causally connected subset;
3. create/update an active `PLAN-*.md` for that execution;
4. create a separate roadmap only if the selected work reveals a durable ordered migration/delivery sequence whose order is itself worth preserving.
