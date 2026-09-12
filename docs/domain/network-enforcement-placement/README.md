# Network Enforcement Placement domain

## Accepted MVP target

The accepted MVP NEP boundary is defined by:

- `../../decisions/ADR-017-nep-candidate-policy-attachment-contract.md` — normative candidate/device/interface/policy-attachment contract;
- `network-context.md` — canonical MVP query/output semantics;
- `../../requirements/network-enforcement-placement-core.md` — observable target requirements and acceptance examples.

The MVP contract is:

```text
TrafficRelation(sourceAddress, destinationAddress, asOf)
    -> unordered EnforcementCandidate[]
        -> provider device
        -> optional source-supported ingress/egress interfaces
        -> PolicyAttachment[0..N]
```

Candidate membership means relevance-to-inspect, not proven traversal. The candidate set is not a route.

NEP returns policy/ACL locators and attachment location; Technical Access Evidence owns configured policy contents.

## Current/stronger runtime capability

`tactical-model.md` documents the implemented I19 stronger proven-path model. It remains valid current-runtime/history for sources that can truthfully prove a path, but it is not an MVP prerequisite and must not be inferred from candidate evidence.

The MVP target may therefore differ from current persistence/code until the NEP migration review is completed.
