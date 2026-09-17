---
anchor_id: NAPMS-S3-RC-ARCHITECTURE-BOUNDARY
type_id: architecture-decision
owner_stage: S3
scope:
  scope_id: H12-RC-CURATION-MVP
  product_area: Resource Catalogue curation
  lifecycle_boundary: S3 Software Architecture / Solution Design
status: ACCEPTED
canonical_payload: |-
  # Resource Catalogue curation architecture boundary

  ## Decision

  Realize Resource Catalogue curation as one application-owned consistency boundary around the accepted `Resource` aggregate. The application boundary orchestrates admission, domain mutation and persistence; the Resource Catalogue domain remains independent of transport, Authority Management implementation and persistence technology.

  ## Responsibilities

  The Resource Catalogue application boundary owns:

  - Resource curation use cases corresponding to the accepted S2 command semantics;
  - acquisition of authenticated Actor and server-owned effective action time from trusted runtime context;
  - selection of `CurateResourceCatalogue @ resource-catalogue` for every protected mutation;
  - synchronous Authority Management admission before invoking a protected domain mutation;
  - loading and saving one Resource aggregate through an application-owned persistence port;
  - one atomic persistence transaction for a Resource mutation, including end-and-successor creation for replacement operations;
  - safe duplicate-submission handling at the application boundary without weakening domain invariants;
  - explicit mapping of admission, validation, concurrency/idempotency and persistence outcomes to the outer delivery boundary.

  The Resource Catalogue domain boundary owns the accepted Resource aggregate, temporal fact semantics and invariants. It receives already-admitted mutation intent plus domain inputs and returns domain success/failure without depending on Authority Management, transport protocols or storage technology.

  Authority Management remains an external upstream dependency. Resource Catalogue consumes only an admission decision through an application-owned port; Authority assignments and effective-authority models do not enter the Resource aggregate.

  ## Mutation flow

  For every protected Resource mutation:

  1. the outer adapter invokes a Resource Catalogue application use case with untrusted request data plus trusted runtime identity/context;
  2. the application use case selects the fixed catalogue curation action/scope and asks the Authority Management port for admission at the effective action time;
  3. denial or unknown/ambiguous authority terminates the flow before domain mutation or persistence;
  4. the application loads the target Resource aggregate when required;
  5. the domain executes the accepted command semantics and invariants;
  6. the application persists the resulting aggregate/fact changes atomically for that Resource;
  7. the application returns an outcome suitable for an outer adapter to project without transferring semantic ownership to that adapter.

  Address-space replacement is one Resource mutation: ending the selected effective realization and establishing its successor commit atomically. A partial end-without-successor caused by infrastructure failure is not an accepted successful replacement outcome.

  ## Read flow

  Resource discovery/detail/workspace reads use a Resource Catalogue-owned read path that projects stable Resource identity and effective temporal facts for one logical `asOf`. Search, paging and scope-focused filtering are query concerns over RC-owned facts. Optional composition with externally owned display data may enrich presentation, but does not move Resource Catalogue semantic ownership to the composition layer.

  Missing current realization, scope affiliation or responsibility remains explicit in the projection as required by S1/S2.

  ## Concurrency and duplicate submission

  S1 requires stale/duplicate mutation to be handled safely but does not prescribe a protocol. S3 therefore requires an application-level mutation guard with these semantics:

  - a conflicting concurrent update must not silently overwrite a newer accepted Resource state;
  - an equivalent retry of a mutation that has a stable command identity may resolve to the already-known outcome;
  - incompatible reuse of the same command identity is an explicit conflict;
  - where no stable command identity is available, duplicate submission is rejected/prevented rather than applied twice.

  Exact token representation, transport headers and storage representation are S4/contract realization details unless a later S3 transport contract makes them externally observable.

  ## Dependency direction

  Outer delivery adapter -> Resource Catalogue application -> Resource Catalogue domain.

  Resource Catalogue application -> Authority admission port -> Authority Management adapter.

  Resource Catalogue application -> Resource persistence port -> persistence adapter.

  Dependencies point toward Resource Catalogue-owned application/domain abstractions. Runtime/deployment packaging may colocate adapters; colocation does not merge semantic ownership or Bounded Contexts.

  ## Deliberately unresolved until justified

  This decision does not select HTTP versus another delivery protocol, a database technology/schema, deployment topology, exact identifier encoding, exact concurrency token, or exact idempotency-key representation. Those choices require an applicable S3 contract/constraint or can remain S4 implementation design details.

  No asynchronous integration message is introduced by the accepted S0-S2 slice, so an event contract is not currently applicable.
semantic_refs:
- relation: DERIVES_FROM
  target: {kind: anchor-current, anchor_id: NAPMS-S2-RC-TACTICAL-MODEL}
  impact: semantic
  rationale_ref: provenance.derivation.rationale
- relation: CONSTRAINED_BY
  target: {kind: anchor-current, anchor_id: NAPMS-S1-RC-CURATION-AUTHORIZATION}
  impact: semantic
  rationale_ref: provenance.derivation.rationale
- relation: CONSTRAINED_BY
  target: {kind: anchor-current, anchor_id: NAPMS-S1-RC-CURATION-INTEGRITY}
  impact: semantic
  rationale_ref: provenance.derivation.rationale
- relation: DERIVES_FROM
  target: {kind: anchor-current, anchor_id: NAPMS-S2-RC-CONTEXT-RELATIONSHIPS}
  impact: semantic
  rationale_ref: provenance.derivation.rationale
provenance:
  origin_kind: derived
  source_refs: []
  authority_basis: accepted-docs-v2-upstream-design
  derivation:
    input_anchor_refs:
    - {anchor_id: NAPMS-S2-RC-TACTICAL-MODEL}
    - {anchor_id: NAPMS-S1-RC-CURATION-AUTHORIZATION}
    - {anchor_id: NAPMS-S1-RC-CURATION-INTEGRITY}
    - {anchor_id: NAPMS-S2-RC-CONTEXT-RELATIONSHIPS}
    derivation_rule_or_method: S3 architecture realization from accepted consistency, admission and integrity boundaries
    derivation_kind: architecture-realization
    rationale: >-
      The accepted Resource aggregate is the smallest atomic consistency boundary; S1 requires server-owned admission before mutation and safe mutation outcomes; S2 keeps Authority Management external. A Resource Catalogue application boundary with inward-pointing ports realizes those constraints without inventing transport, storage or deployment truth.
  recorded_at: '2026-09-17'
validation:
  freshness: STALE
  evidence_ref: null
  evidence_target: NAPMS-S3-RC-ARCHITECTURE-BOUNDARY
  profile: changed-and-affected-design
  profile_version: cp-v2
  enforcement_status: pending-runtime-validation
---
