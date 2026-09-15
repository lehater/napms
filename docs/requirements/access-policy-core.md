# Access Policy product requirements

Status: `G1 revalidated for concrete Component deployments and revision-change semantics 2026-09-16`.

## Purpose

Access Policy exposes the current authoritative semantic network-access rule set. It does not decide approval authority or reinterpret evidence as authorization.

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
- a current Rule shall expose stable rule identity/provenance so downstream consumers can refer to the contributing Rule without using the peer-context endpoint pair as their external identifier;
- the exact revision reference is current Rule state, not by itself the identity of the concrete source/destination connection;
- changing traffic from one immutable revision to another for the same concrete endpoint pair shall be treated as a change to the current Rule semantics, not automatically as a different endpoint connection;
- while a revision change is pending governance, the previously authorized revision remains the effective Rule semantics;
- rejecting a proposed revision change leaves the effective Rule unchanged;
- only an accepted authorization change may advance the effective Rule to the approved revision;
- equivalent/retried/concurrent accepted outcomes shall not create duplicate current Rules for the same directed endpoint pair;
- rejected proposals/requests create no deny Rule;
- withdrawal makes the connection no longer effectively authorized without rewriting historical governance/provenance;
- a later accepted authorization may re-establish access for the same concrete endpoint pair while preserving historical decisions;
- a different Component Deployment on either side is a different concrete endpoint pair even when it represents the same Component definition;
- Resource address changes do not change Rule identity while the referenced Component Deployments remain the same;
- technical address/materialization failure does not silently erase semantic authorization truth;
- translation from Component Deployment to Resource/AddressSpace, configured-policy comparison, rendering and execution remains downstream of current semantic policy truth.

## Rule identity versus external reference

The product shall support a stable identity for a Policy Rule and allow downstream provenance to refer to that Rule through an opaque reference.

The exact internal identity type (`PolicyRuleId`) and external reference type (`PolicyRuleRef`) are Domain/Architecture decisions. The product requirement is only that a Rule remains stably referable across an approved traffic-revision change for the same concrete directed endpoint pair.

## Acceptance examples

1. Source deployment `CD-A1` to destination deployment `CD-B1` is authorized with revision `R1 = TCP/443` -> one effective Policy Rule contributes `R1` semantics.
2. Revision `R2 = TCP/8443` is proposed for the same `CD-A1 -> CD-B1` pair -> `R1` remains effective while the change is pending.
3. The R2 proposal is rejected -> the effective Policy Rule remains on R1.
4. The R2 proposal is approved -> the same concrete endpoint connection is now effective with R2 semantics and previous approval history remains explainable.
5. The same Component is separately deployed as `CD-A2` on another Resource -> `CD-A2 -> CD-B1` is a distinct concrete access relationship and is not authorized merely because `CD-A1 -> CD-B1` is authorized.
6. A Resource address changes for `CD-A1` -> the Rule remains the same semantic concrete connection; downstream export/materialization changes the address realization.
7. Missing Resource AddressSpace -> semantic Rule remains authoritative while technical materialization is unresolved.
8. A withdrawn connection contributes no current effective export row, but its historical decisions are not rewritten.

## Upstream boundary

The accepted product behavior requires governance to deliver explicit accepted/withdrawn current-policy outcomes. Whether governance history/change requests and Policy Rule current state remain separate Bounded Contexts or are one lifecycle owner is intentionally unresolved at G1 and must be decided in S2.
