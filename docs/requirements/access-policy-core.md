# Access Policy product requirements

Status: `G1 revalidated for concrete Component deployments and formal RuleChange decisions 2026-09-16`.

## Purpose

The product exposes one current authoritative semantic network-access rule set. The MVP records a formal decision on each proposed change without embedding customer-specific approval workflow. Technical evidence is never reinterpreted as authorization merely because it was observed.

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
- each proposed Rule change shall have one formal state: `Pending`, `Accepted` or `Rejected`;
- while a revision change is `Pending`, the previously authorized revision remains the effective Rule semantics;
- a `Rejected` change leaves the effective Rule unchanged and creates no deny Rule;
- only an `Accepted` applicable change may advance the effective Rule to the proposed revision;
- the MVP shall not require built-in bilateral source/destination approvals, quorum, approval ordering or Responsibility Scope resolution in order to accept/reject a RuleChange;
- organization-specific approval procedures may occur outside NAPMS and provide the formal decision outcome through an authorized integration/action;
- actor authority may protect propose/decide/withdraw operations but is not itself the approval workflow model;
- equivalent/retried/concurrent processing shall not create duplicate current Rules for the same directed endpoint pair or duplicate semantic decision attempts;
- withdrawal makes the connection no longer effectively authorized without rewriting historical change/decision provenance;
- a later accepted change may re-establish access for the same concrete endpoint pair while preserving historical decisions;
- a different Component Deployment on either side is a different concrete endpoint pair even when it represents the same Component definition;
- Resource address changes do not change Rule identity while the referenced Component Deployments remain the same;
- technical address/materialization failure does not silently erase semantic authorization truth;
- translation from Component Deployment to Resource/AddressSpace, configured-policy comparison, rendering and execution remains downstream of current semantic policy truth.

## Stable rule reference

The product shall support a stable identity for a Policy Rule and allow downstream provenance to refer to that Rule through an opaque reference.

The product requirement is that a Rule remains stably referable across an accepted traffic-revision change for the same concrete directed endpoint pair. S2 defines the domain names `PolicyRuleId` internally and `PolicyRuleRef` externally; exact runtime representation belongs downstream.

## Formal decision outcome

The minimum MVP lifecycle for one change is:

```text
Pending -> Accepted
Pending -> Rejected
```

The product records who/what submitted the change, who/what made the formal decision when applicable, timestamps and provenance references sufficient for audit/explanation.

NAPMS does not require knowledge of whether that decision was produced by a manager, CAB, ticketing workflow, two-party approval, automated policy, external governance system or another customer procedure.

## Acceptance examples

1. `CD-A1 -> CD-B1` is effective with `R1 = TCP/443` -> one effective Policy Rule contributes R1 semantics.
2. `R2 = TCP/8443` is proposed for the same pair -> R1 remains effective while the change is Pending.
3. R2 is Rejected -> the effective Rule remains on R1.
4. R2 is Accepted -> the same concrete Rule is now effective with R2 semantics and previous decision history remains explainable.
5. An external approval system reaches an approval outcome and an authorized integration records `Accepted` -> AP applies the same RuleChange transition; AP does not reproduce the external workflow internally.
6. The same Component is separately deployed as `CD-A2` on another Resource -> `CD-A2 -> CD-B1` is a distinct concrete access relationship and is not authorized merely because `CD-A1 -> CD-B1` is authorized.
7. A Resource address changes for `CD-A1` -> the Rule remains the same semantic connection; downstream export/materialization changes the address realization.
8. Missing Resource AddressSpace -> semantic Rule remains authoritative while technical materialization is unresolved.
9. A withdrawn connection contributes no current effective export row, but its historical decisions are not rewritten.

## Domain alignment

The Rule lifecycle remains one Access Policy ownership boundary: `PolicyRule` is the Aggregate Root and distinct formal change attempts are `RuleChange` children. The dependent S2 model must not reintroduce customer-specific approval entities or bilateral scope-resolution semantics unless a later accepted requirement reopens them.

No implementation authorization is implied.
