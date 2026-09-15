# Business Connectivity — Tactical DDD model

Status: `current target`.

## Purpose

Own why application connectivity is needed, independently from approval, authorization, deployment and technical realization.

## Aggregate — BusinessProcess

```text
BusinessProcess {
    businessProcessRef
    name
    description?
    lifecycle: Active | Retired
    connectivityNeeds: Set<ConnectivityNeed>
}
```

`BusinessProcess` is the consistency owner for its Connectivity Needs.

## ConnectivityNeed

```text
ConnectivityNeed {
    connectivityNeedRef
    businessProcessRef
    interactionRef
    businessJustification
    state: Required | NoLongerRequired
    provenanceRef
}
```

Invariants:

- a Need references a stable ACC `InteractionRef`, not a deployment, Resource, address or access rule;
- a Need explains business necessity and does not itself grant permission;
- at most one current Required Need exists for the same `(BusinessProcessRef, InteractionRef)`;
- a Need may outlive one traffic-contract revision or one deployment;
- declaring a Need does not automatically create an Access Request;
- retirement or `NoLongerRequired` changes current necessity without rewriting earlier provenance.

## Operations

```text
RegisterBusinessProcess
DeclareConnectivityNeed
ChangeConnectivityNeedJustification
MarkConnectivityNeedNoLongerRequired
RetireBusinessProcess
```

## Published contract

```text
ProcessBackedNeed {
    connectivityNeedRef
    businessProcessRef
    interactionRef
    businessJustification
    currentState
    provenanceRef
}
```

Access Governance may correlate an explicit request with a current Required Need. Business Connectivity does not choose contract revision, deployments, approvers or Policy Rules.
