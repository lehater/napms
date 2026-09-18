# Context Mapper pilot result

Status: historical experiment result; not a canonical design source.

This note preserves the conclusion from the `architecture/model-layout-pilot` branch so the branch can be retired without losing the reasoning.

## What was tested

The Resource Catalogue slice was represented in Context Mapper Language (CML) and validated/generated with Context Mapper CLI 6.12.0.

The comparison covered:

- Bounded Contexts and Context Map relations;
- Aggregate / Entity / Value Object structure;
- commands, events and simple command-to-event flows;
- NAPMS-specific invariants, policies and non-peer compositions;
- practical CI/tooling behavior.

## Findings

CML was a strong fit for the standard DDD-shaped subset:

- Bounded Context identity;
- context purpose/responsibilities;
- explicit upstream/downstream and other named Context Mapping patterns when already accepted;
- Aggregate, Aggregate Root, Entity and Value Object;
- commands/events and supported flow structure.

It was not a lossless owner for important NAPMS semantics:

- temporal/business invariants such as zero-or-one effective AddressSpace;
- Event Storming-style policies;
- fail-closed admission semantics inside flows;
- non-peer compositions such as Required Policy Materialization;
- deliberately deferred decisions and NAPMS-specific semantic constraints.

The practical tool check also found:

- `Resource` is a CML keyword and requires escaped identifiers;
- CLI parser errors are not reliably represented only by process exit code, so CI needs diagnostic checking;
- Maven/EMF adds runtime/tooling weight and log noise compared with the repository-local generators.

## Decision

Context Mapper/CML is **not** a required NAPMS Harness dependency and is **not** a canonical semantic source.

The adopted approach is:

```text
canonical NAPMS semantic models
        ↓
small deterministic projections
        ↓
PlantUML / Structurizr review surface
```

Specialized standard notations remain canonical only where they naturally own the whole concern, for example Structurizr DSL for C4 structure and OpenAPI for HTTP contracts.

Context Mapper may still be used ad hoc for workshops or experiments where its DDD metamodel fits, but normal repository validation and projection generation do not depend on it.

## Historical reference

Pilot branch: `architecture/model-layout-pilot`

Last pilot commit used for the comparison: `13a39b7b80b7beaec65bef98ea415ae908fc3bcf`
