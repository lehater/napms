# Domain capability ownership map

Status: `S2 affected-edge aligned with TAE acquisition boundary 2026-09-15`.

A capability is not automatically a Bounded Context, service or deployment unit. Canonical relationship map: `context-map.md`.

| Capability | Semantic owner / disposition |
|---|---|
| Business Process / Connectivity Need / attribution | **Business Connectivity** |
| Access Request / bilateral consent / grant / withdrawal | **Access Governance** |
| Effective Authority | **Authority Management** |
| Current Policy Rule / effective semantic authorization | **Access Policy** |
| Resource identity / effective HostAddress-or-Prefix realization | **Resource Catalogue** |
| Resource Scope Affiliation / Resource Responsibility | **Resource Catalogue** |
| Application / Component / Interaction / immutable traffic contract | **Application Communication Catalogue** |
| ApplicationDeployment / ComponentPlacement | **Application Deployment** |
| Required Access Materialization | non-peer composition over AP + ACC + AD + RC + NEP |
| Enforcement Target Relevance / policy locators | **Network Enforcement Placement** |
| Normalized Technical Access Evidence | **Technical Access Evidence** |
| Device/config evidence acquisition | non-peer application/integration capability producing TAE evidence |
| NetFlow/IPFIX/flow evidence acquisition | non-peer application/integration capability producing TAE evidence |
| Technical evidence import | non-peer application/integration capability producing TAE evidence |
| Provider configured-policy interpretation | adapter/integration capability; may consume provider material and/or selected TAE evidence |
| Policy realization assessment / delta / change design / verification | **Access Policy Realization** |
| Provider target rendering | adapter/integration capability |
| Provider/device mutation lifecycle | **Network Environment Operations** |
| Scoped Connectivity Inventory | non-peer read composition |
| Connectivity Impact Analysis | cross-context analysis; no peer BC accepted |

## Technical evidence acquisition

```text
source acquisition / collector
    -> faithful normalization into TAE contract
    -> TAE immutable source-qualified facts
    -> downstream interpretation
```

TAE owns the normalized evidence vocabulary and invariants. Acquisition capabilities own when/how source material is collected and translated into that vocabulary.

Collection scheduling, polling cadence, credentials, retries and transport are not TAE domain capabilities. NEO is not the evidence-read gateway; it remains the controlled-mutation owner.

Whether acquisition and NEO share concrete provider/device clients or adapter infrastructure is deferred to Architecture.

## Current deployment/materialization chain

```text
ACC InteractionContractRevision
+ AD ApplicationDeployment / ComponentPlacement -> ResourceRef
+ RC Resource -> effective HostAddress | Prefix
+ AP authorization
+ NEP target relevance
-> RPM -> TargetRequiredPolicy
```

`ResourceEndpoint`, endpoint purpose, multiple simultaneous Resource addresses/interfaces and deployment-specific exposure are not current target capabilities. They require a confirmed future use case.

Provider interpretation/rendering remain outside APR core. NEO owns controlled mutation lifecycle. Apply success is not convergence proof.
