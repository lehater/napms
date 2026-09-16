# Domain capability ownership map

Status: `S2 capability ownership and dependent Tactical DDD aligned; G2 PASS 2026-09-16`.

A capability is not automatically a Bounded Context, service or deployment unit. Canonical relationship map: `context-map.md`.

| Capability | Semantic owner / disposition |
|---|---|
| Business Process / Connectivity Need / attribution | **Business Connectivity** |
| Policy Rule lifecycle, RuleChange history, formal Accepted/Rejected decision, withdrawal, current effective revision | **Access Policy** |
| Effective Authority | **Authority Management** |
| Resource identity / effective HostAddress-or-Prefix realization | **Resource Catalogue** |
| Resource Scope Affiliation / Resource Responsibility | **Resource Catalogue** |
| Application / Component / Interaction / immutable traffic contract | **Application Communication Catalogue** |
| concrete ComponentDeployment -> ResourceRef | **Application Deployment** |
| Required Access Materialization | non-peer composition over Access Policy + ACC + AD + RC + NEP |
| Evidence-to-access candidate recognition | non-peer composition over TAE + RC + AD + ACC |
| Enforcement Target Relevance / policy locators | **Network Enforcement Placement** |
| Normalized Technical Access Evidence | **Technical Access Evidence** |
| Device/config evidence acquisition | non-peer application/integration capability producing TAE evidence |
| NetFlow/IPFIX/flow evidence acquisition | non-peer application/integration capability producing TAE evidence |
| Technical evidence import | non-peer application/integration capability producing TAE evidence |
| Provider configured-policy interpretation | adapter/integration capability; may consume provider material and/or selected TAE evidence |
| Policy realization assessment / delta / change design / verification | **Access Policy Realization** |
| Provider target rendering | adapter/integration capability |
| Provider/device mutation lifecycle | **Network Environment Operations** |
| Scoped Connectivity Inventory | current as-built/non-peer read composition where retained |
| Connectivity Impact Analysis | cross-context analysis; no peer BC accepted |

`Access Governance` is no longer a target peer Bounded Context. The minimum governance capability inside Access Policy is deliberately small: submit a RuleChange, record one formal `Accepted | Rejected` outcome, and preserve history/current effectiveness.

Customer-specific approval procedure is not a target capability of the first MVP. Bilateral approvers, quorum, CAB/ticket stages and Responsibility Scope-derived approval routing may be integrated later without changing the core RuleChange outcome model.

## Concrete deployment capability

```text
ACC Component
    -> AD ComponentDeployment(ComponentRef, ResourceRef)
        -> RC Resource
```

One target Component Deployment is one independently governed deployed Component instance on one Resource for the first MVP. A replica on another Resource is another Component Deployment, not another placement of one logical whole-Application deployment.

## Policy lifecycle capability

```text
Manual proposal --------------------\
                                     +--> Access Policy Rule lifecycle
Evidence Access Recognition --------/

Rule lifecycle
    RuleChange(Pending)
    -> Accepted | Rejected
    -> effective revision / unchanged revision
    -> optional explicit withdrawal
    -> current PolicyRule projection
```

Pending/Rejected changes coexist with current effective policy and cannot overwrite it. One Accepted applicable change may advance the effective revision.

Business Connectivity supplies Process-backed Need/business basis for deliberate submission. Authority Management may protect propose/decide/withdraw actions. Neither becomes part of Policy Rule ownership or defines customer approval workflow.

## Technical evidence acquisition and recognition

```text
source acquisition / collector
    -> faithful normalization into TAE contract
    -> TAE immutable source-qualified facts
    -> Evidence Access Recognition
        + RC/AD/ACC correlation
    -> RecognizedAccessCandidate
    -> normal Access Policy RuleChange lifecycle
```

TAE owns normalized evidence vocabulary/invariants. Recognition owns no authoritative policy or catalogue truth. Evidence does not become authorization merely because correlation succeeds.

Collection scheduling, polling cadence, credentials, retries and transport are not TAE domain capabilities. NEO remains controlled mutation owner.

## Current materialization chain

```text
Access Policy current effective Rule
+ ACC exact InteractionContractRevision
+ AD source/destination ComponentDeployment -> ResourceRef
+ RC Resource -> effective HostAddress | Prefix
+ NEP target relevance
-> RPM -> TargetRequiredPolicy
```

One Rule already identifies one concrete source/destination deployment pair; RPM does not expand a logical deployment's placement sets.

Provider interpretation/rendering remain outside APR core. NEO owns controlled mutation lifecycle. Apply success is not convergence proof.
