# Access Policy product requirements

Status: `G1 revalidated for concrete Component deployments and revision-change semantics 2026-09-16`.

## Purpose

The product exposes one current authoritative semantic network-access rule set. Approval authority remains external to rule semantics, and technical evidence is never reinterpreted as authorization merely because it was observed.

## Current rule meaning

One current Policy Rule represents one directed concrete connection between:

```text
source Component Deployment
    -> destination Component Deployment
```

and carries the exact immutable Interaction Contract Revision whose traffic semantics are currently effective for that connection.

The source and destination Component Deployments must realize the source and destination Components of the revision's owning Interaction.

A Policy Rule shall not require a duplicate `InteractionRef` merely to recover meaning already identified by the exact revision reference.

## Requirements

- at most one current authoritative Policy Rule meaning shall exist for one directed source/destination Component Deployment pair;
- a Rule shall expose stable identity/provenance so downstream consumers can refer to it without using the endpoint pair as their external identifier;
- the exact revision reference is current Rule state, not by itself the identity of the concrete source/destination connection;
- changing traffic from one immutable revision to another for the same concrete endpoint pair shall be treated as a change to the current Rule semantics, not automatically as a different endpoint connection;
- while a revision change is pending governance, the previously authorized revision remains the effective Rule semantics;
- rejecting a proposed revision change leaves the effective Rule unchanged;
- only an accepted applicable authorization change may advance the effective Rule to the approved revision;
- equivalent/retried/concurrent processing shall not create duplicate current Rules for the same directed endpoint pair;
- rejected proposals/change attempts create no deny Rule;
- withdrawal makes the connection no longer effectively authorized without rewriting historical governance/provenance;
- a later accepted authorization may re-establish access for the same concrete endpoint pair while preserving historical decisions;
- a different Component Deployment on either side is a different concrete endpoint pair even when it represents the same Component definition;
- Resource address changes do not change Rule identity while the referenced Component Deployments remain the same;
- technical address/materialization failure does not silently erase semantic authorization truth;
- translation from Component Deployment to Resource/AddressSpace, configured-policy comparison, rendering and execution remains downstream of current semantic policy truth.

## Stable rule reference

The product shall support a stable identity for a Policy Rule and allow downstream provenance to refer to that Rule through an opaque reference.

The product requirement is that a Rule remains stably referable across an approved traffic-revision change for the same concrete directed endpoint pair. S2 defines the domain names `PolicyRuleId` internally and `PolicyRuleRef` externally; exact runtime representation belongs downstream.

## Acceptance examples

1. `CD-A1 -> CD-B1` is authorized with `R1 = TCP/443` -> one effective Policy Rule contributes R1 semantics.
2. `R2 = TCP/8443` is proposed for the same pair -> R1 remains effective while the change is pending.
3. R2 is rejected -> the effective Rule remains on R1.
4. R2 is approved -> the same concrete Rule is now effective with R2 semantics and previous decision history remains explainable.
5. The same Component is separately deployed as `CD-A2` on another Resource -> `CD-A2 -> CD-B1` is a distinct concrete access relationship and is not authorized merely because `CD-A1 -> CD-B1` is authorized.
6. A Resource address changes for `CD-A1` -> the Rule remains the same semantic connection; downstream export/materialization changes the address realization.
7. Missing Resource AddressSpace -> semantic Rule remains authoritative while technical materialization is unresolved.
8. A withdrawn connection contributes no current effective export row, but its historical decisions are not rewritten.

## Domain alignment

S2 subsequently converged governance history and current Policy Rule state into one Access Policy lifecycle: `PolicyRule` is the Aggregate Root and distinct formal change attempts are `RuleChange` children. This resolves ownership without changing the G1 behavior above. See `docs/domain/access-policy/tactical-model.md` and ADR-019.

No implementation authorization is implied.
