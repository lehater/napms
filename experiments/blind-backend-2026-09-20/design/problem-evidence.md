# Blind backend problem evidence

Status: ACCEPTED for experiment

## Problem

Network-access work is currently experienced at too low a technical abstraction when expressed directly as firewall/access-list syntax. Users need a semantic, explainable path from business/application intent to desired network access and ultimately to a complete technical policy representation, while preserving the ability to trace technical outcomes back to their business/application justification.

## Affected actors

- catalogue/application curators describing Resources, Applications, Components, Interactions and deployments;
- business/application stakeholders describing why connectivity is needed;
- actors requesting/deciding connectivity;
- consumers of generated policy who need a complete explainable vendor-neutral result.

## Desired current MVP outcome

For the selected backend MVP, a user can describe Resource/application communication truth, establish business-backed connectivity intent and access decisions, and obtain a complete explainable vendor-neutral normalized policy representation of current effective desired access.

## Evidence

- `source-evidence-network-intent.md`: stakeholder discovery/revalidation evidence, 2026-09-13/14.
- `source-product-wave1.md`: accepted initial product requirements copied into the 2026-09-08 greenfield baseline.
- `source-corpus.yaml#SRC-MVP-001`: explicit 2026-09-17 stakeholder confirmation of the narrow MVP.
- `source-corpus.yaml#SRC-BC-001..003`: stakeholder-revalidated business-connectivity observable behavior.
- `source-corpus.yaml#SRC-EXP-001`: current experiment statement that Resource/application/interaction description must lead to resulting access policy.

## Current scope boundary

Included:
- Resource description and network-address realization needed for access policy;
- reusable Application/Component/Interaction description;
- concrete Component deployment on Resource;
- business Process/Connectivity Need justification;
- deliberate connectivity request/permission outcome/current desired access;
- complete explainable vendor-neutral policy materialization/export.

Problem-space evidence about brownfield traffic analysis, configured-policy reconciliation, remediation, provider rendering, device mutation and business-driven cleanup is retained as future evidence but is outside the selected MVP unless separately promoted by Product Requirements.

Frontend/UI structure is outside this backend experiment.

## Unresolved downstream decisions

- exact domain ownership/aggregate structure;
- exact authorization/identity realization for protected actions;
- external API transport and representation;
- persistence technology/schema;
- runtime/deployment topology and numeric scale/SLA targets;
- detailed verification/test mechanics.
