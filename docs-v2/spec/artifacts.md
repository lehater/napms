# Artifact catalog specification

Status: SKELETON — M2 owns completion.

## Purpose

Define the finite catalog of canonical artifact types and the rules for when each artifact is required.

## Classification

Every artifact type will be classified as:

- `mandatory` — always required for the owning scope/stage;
- `conditional` — required only when an explicit applicability condition is true;
- `optional` — useful evidence but never required by default.

## Initial catalog to specify

| Area | Candidate canonical artifacts | Preferred source format |
|---|---|---|
| Problem | problem statement, evidence, journey | Markdown |
| Requirements | functional behavior, quality requirements, constraints, acceptance scenarios | Markdown / Gherkin |
| Domain | context map, domain model, state model, glossary, traceability | PlantUML + Markdown |
| Architecture | C4 views, significant flows, deployment, persistence model | PlantUML |
| Contracts | HTTP, event and schema contracts | OpenAPI / AsyncAPI / JSON Schema |
| Decisions | significant architectural/domain decisions | ADR Markdown |
| Readiness | implementation plan, migrations, test intent, work package | Markdown / native executable formats |
| Validation | automated tests and journey/E2E evidence | test source |

## Required specification per artifact type

M2 must define at least: stable artifact id/type, owning stage, applicability, canonical format, location rule reference, required inputs, gate relevance, validation rules, allowed generated projections and traceability semantics.

The catalog must not organize S1 requirements by bounded context. Bounded-context ownership is discovered in S2 and represented through traceability/projections.