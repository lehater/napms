# NAPMS Strategic DDD model

Status: `current target`.

## Bounded Contexts

| Bounded Context | Semantic center | Responsibility |
|---|---|---|
| Business Connectivity | why connectivity is needed | Business Process, Connectivity Need and current business justification |
| Access Governance | whether required consent exists | request history, bilateral obligations/decisions and current grant/withdrawal |
| Access Policy | what semantic access is authorized | authoritative current Policy Rule truth |
| Authority Management | who may act for scope/time | effective actor/action/scope authority |
| Resource Catalogue | what access-domain resources exist | Resource identity/lifecycle, current AddressSpace, scope affiliation/responsibility |
| Application Communication Catalogue | what applications/components communicate | Application, Component, Interaction and immutable InteractionContractRevision |
| Application Deployment | where application components are placed | ApplicationDeployment and current Component-to-Resource placement set |
| Network Enforcement Placement | where a technical pair may be enforced | candidate Firewall/policy-locator relevance |
| Technical Access Evidence | what technical material was observed/reported/imported | normalized immutable source-qualified evidence |
| Access Policy Realization | required versus configured effective access | assessment, semantic delta and verified additive change intent |
| Network Environment Operations | how a verified target mutation is executed | controlled mutation identity, authority, preconditions and outcome |

Provider Policy Interpreter, Provider Policy Renderer and Technical Evidence Acquisition/Collectors are integration/application capabilities, not Bounded Contexts. Required Policy Materialization is a derived composition, not a Bounded Context.

No Shared Kernel is accepted between target BCs. Cross-context references are opaque semantic references rather than persistence foreign keys.

## Selected first implementation slice

```text
ACC InteractionContractRevision
        +
AD ApplicationDeployment + ComponentPlacement
        +
RC Resource + AddressSpace
        |
        v
Required Access Matrix
        |
        +--> table
        `--> vendor-neutral export
```

This slice consumes an explicit selection of `InteractionContractRevisionRef + sourceApplicationDeploymentRef + destinationApplicationDeploymentRef`. It derives technical connectivity only; it does not claim authorization, enforcement placement or configured-state convergence.

## ACC / AD / RC ownership

```text
ACC
  Application / Component / Interaction
  immutable InteractionContractRevision
          |
          | ApplicationRef / ComponentRef
          v
AD
  ApplicationDeployment
  current Set<(ComponentRef, ResourceRef)>
          |
          v
RC
  Resource
  AddressSpace [0..1] = HostAddress | Prefix
```

Interaction traffic changes create a new immutable revision while preserving Interaction identity. ApplicationDeployment identity survives ordinary scaling and placement replacement while logical deployment continuity is preserved. AD retains every applicable placement. RC owns address realization; address changes do not redefine Resource, deployment or interaction identity.

## Authorization path

```text
Business Connectivity -> Access Governance -> Access Policy
```

A governed subject is:

```text
InteractionContractRevisionRef
+ sourceApplicationDeploymentRef
+ destinationApplicationDeploymentRef
```

Access Governance owns bilateral consent/grant/withdrawal. Access Policy owns the resulting current semantic authorization. Authority Management owns actor/action/scope/time authority; Resource responsibility metadata does not grant authority.

## Target realization path

```text
Access Policy
+ ACC
+ AD
+ RC
+ NEP
    -> Required Policy Materialization
    -> Access Policy Realization
    -> Provider Policy Renderer
    -> Network Environment Operations
```

Required Policy Materialization preserves every applicable placement combination and candidate target. Missing required input is explicit unresolved state, never an empty policy.

APR compares complete comparable required/configured effective permit spaces:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

`Realized` requires empty missing and excess. Incomplete/unsupported correlation is `Uncomparable`. The accepted remediation boundary is additive `ENSURE-PERMIT` for missing access; excess is evidence, not automatic removal authority.

Provider-native syntax remains at interpretation/rendering boundaries. NEO executes a verified rendered artifact but does not recompute authorization, target selection or APR intent. Execution success is not semantic convergence; convergence requires later observation and comparison.

## Evidence boundary

Technical Evidence Acquisition/Collectors initiate source-specific collection and translate into the TAE contract. TAE owns normalized evidence meaning and provenance, not polling/scheduling/credentials/transport. Evidence alone never creates authorization, desired policy or mutation intent.

## Strategic invariants

- each authoritative semantic fact/decision has one owner;
- unknown/incomplete information never silently becomes absence, denial, empty policy or success;
- workflows may derive values but gain no business authority merely by orchestrating owners;
- provider-native semantics stay at integration boundaries;
- current-state and time-qualified semantics are explicit in their owning contracts.
