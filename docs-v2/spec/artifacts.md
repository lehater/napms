# Artifact catalog specification

Status: M2 COMPLETE — artifact types and applicability contract defined; physical paths remain M3-owned.

## Purpose

Define the finite catalog of durable artifact types, when they are required, their canonical source representation and their lifecycle/gate role. Prefer a formal source artifact over prose that merely describes the same model.

## Applicability classes

Every artifact type is exactly one of:

- `mandatory` — required whenever its owning stage is entered for an affected scope;
- `conditional` — required only when its explicit applicability condition is true;
- `optional` — useful evidence or projection, never a default gate requirement.

A gate requires only applicable artifacts for the selected scope. Absence of a non-applicable conditional artifact is valid.

## Canonical-source rules

1. Store knowledge in Git as source, not as screenshots or manually exported renderings.
2. When a standard machine-readable notation adequately expresses the knowledge, that source is canonical.
3. Markdown remains canonical for knowledge that is primarily narrative: problem framing, requirements, rationale, decisions and plans.
4. Generated SVG/PNG/HTML/PDF views are projections unless an explicit consumer requires them as source; reproducible projections should normally not be committed.
5. Do not duplicate the same truth in multiple canonical artifacts. Cross-artifact views use references or generated projections.
6. Artifact identity follows the owned concept, not a gate name. Passing G1/G2/etc. changes lifecycle state; it does not rename the artifact.

## Catalog

| Type id | Stage | Applicability | Canonical source | Gate role |
|---|---|---|---|---|
| `problem-statement` | S0 | mandatory | Markdown | G0 |
| `evidence` | S0 | conditional: material claim requires durable evidence/reference | Markdown/reference/native evidence | G0 |
| `user-journey` | S0/S1 | conditional: behavior spans a meaningful actor journey | Markdown; executable scenario when useful | G0/G1 |
| `functional-requirement` | S1 | mandatory when observable behavior changes | Markdown | G1 |
| `quality-requirement` | S1 | conditional: quality attribute materially constrains scope | Markdown with measurable scenario | G1 and downstream constraints |
| `constraint` | S0/S1 | conditional: externally imposed or non-negotiable constraint exists | Markdown | earliest affected gate and downstream input |
| `acceptance-scenario` | S1 | conditional: requirement needs example-level executable/precise acceptance behavior | Gherkin `.feature` preferred when executable; otherwise Markdown | G1; later validation trace |
| `requirements-glossary` | S1 | conditional: terminology ambiguity is material before domain discovery | Markdown | G1 |
| `context-map` | S2 | conditional: more than one bounded context or boundary relation is relevant | PlantUML `.puml` | G2 |
| `domain-model` | S2 | mandatory for each affected bounded context whose semantics/model change | PlantUML `.puml` plus minimal explanatory Markdown only where notation is insufficient | G2 |
| `domain-glossary` | S2 | conditional: domain terms/invariants require durable definition | Markdown | G2 |
| `state-model` | S2 | conditional: entity/aggregate lifecycle has material states/transitions | PlantUML state diagram `.puml` | G2 |
| `requirement-domain-trace` | S2 | conditional: requirement is realized across discovered responsibilities/boundaries or ownership is not obvious | machine-readable mapping or generated index; schema finalized later | G2/downstream routing |
| `system-context` | S3 | conditional: external actors/systems or system boundary changes | C4/PlantUML `.puml` | G3 |
| `container-view` | S3 | conditional: runtime/deployable responsibility or container boundary changes | C4/PlantUML `.puml` | G3 |
| `interaction-flow` | S3 | conditional: non-trivial cross-boundary runtime interaction needs ordering/ownership clarity | PlantUML sequence `.puml` | G3 |
| `deployment-model` | S3 | conditional: deployment/topology/runtime placement materially affects scope | PlantUML `.puml` or infrastructure-native declarative source where it is the actual contract | G3 |
| `persistence-model` | S3/S4 | conditional: relational persistence/schema design materially changes | PlantUML ERD `.puml`; executable migration remains implementation/readiness evidence | G3/G4 as applicable |
| `http-contract` | S3 | conditional: HTTP boundary changes or is introduced | OpenAPI `.yaml` | G3 |
| `event-contract` | S3 | conditional: asynchronous event/message boundary changes or is introduced | AsyncAPI `.yaml` | G3 |
| `data-schema` | S3 | conditional: independently governed payload/schema contract is required | JSON Schema or contract-native schema | G3 |
| `decision-record` | owning decision stage | conditional: significant choice has alternatives/consequences worth preserving | ADR Markdown | relevant gate evidence |
| `implementation-plan` | S4 | mandatory for non-trivial implementation scope | Markdown | G4 |
| `migration` | S4/Implementation | conditional: persistent/external state requires transition | executable native format, e.g. SQL/migration source | G4 readiness + implementation |
| `test-intent` | S4 | mandatory for non-trivial implementation scope | Markdown references and/or test specification | G4 |
| `automated-test` | Implementation/Validation | conditional by implemented behavior/risk | test source code | validation evidence |
| `journey-e2e-test` | Implementation/Validation | conditional: accepted journey requires end-to-end proof | executable test source | validation evidence |

## Stage output profile

This is a routing profile, not a requirement to create every listed artifact.

| Stage | Expected durable output |
|---|---|
| S0 | problem/evidence and only necessary journeys/constraints |
| S1 | functional behavior plus applicable quality, constraint, acceptance and terminology artifacts |
| S2 | affected domain models plus applicable context/state/glossary/traceability artifacts |
| S3 | only architecture views/contracts/decisions needed by the affected boundaries |
| S4 | exact implementation plan, validation intent and applicable migration/readiness material |
| Implementation/Validation | source implementation and executable evidence; upstream artifacts updated only through normal reopen rules |

## Requirements boundary

S1 requirements are organized by product/problem behavior, not by bounded context. Bounded contexts are an S2 result. After S2, requirement-to-context ownership may be represented by `requirement-domain-trace` or generated context indexes without moving or duplicating the canonical requirement.

## Domain versus persistence

A domain model is not an ERD. `domain-model` expresses domain semantics and ownership at S2. `persistence-model` expresses relational realization only when persistence design is relevant, normally at S3/S4. Do not require an ERD merely because a domain model exists.

## Decision records

Do not create ADRs for routine choices already obvious from an owning artifact or convention. A `decision-record` is required only when preserving context, alternatives and consequences is materially useful for future work. The decision record references affected canonical artifacts; it does not replace them.

## Traceability

Traceability is sparse and semantic, not a full document matrix. Required links are only those needed to answer routing/validation questions such as:

- which accepted requirement drives this domain responsibility;
- which bounded context owns the behavior;
- which contract realizes a cross-boundary interaction;
- which acceptance/test evidence proves an accepted behavior.

Do not manually duplicate information solely to obtain traceability. Prefer stable identifiers and generated indexes where possible.

## Generated projections

Allowed projections include rendered diagrams, browsable API documentation, context-centric requirement indexes, traceability reports and documentation sites. A projection:

- identifies its canonical source(s);
- is reproducible when practical;
- never becomes an independent source of truth by being easier to read;
- does not need to be committed when CI/local tooling can regenerate it.

## Artifact specification contract

The future machine-readable catalog must expose, per artifact type:

```text
id
owning-stage
applicability-class
applicability-condition
canonical-format
location-rule
required-input-types
gate-relevance
validation-rule-ids
traceability-relations
allowed-projections
```

M2 defines the semantics of these fields. M3 defines physical `location-rule` values. M5 defines concrete `validation-rule-ids`. A later implementation iteration may encode this catalog in YAML/JSON; this Markdown remains the design specification until that representation is deliberately introduced and validated.

## M2 exit

M2 is complete when the finite initial catalog, applicability classes, canonical-source rules, lifecycle ownership, gate relevance, traceability principles and generated-projection rules are defined without creating product artifacts or fixing physical repository paths.
