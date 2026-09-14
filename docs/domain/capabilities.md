# Domain capability ownership map

Status: `S2 globally revalidated at Strategic level; Tactical work remains active where recorded`.

A capability is not automatically a Bounded Context, service or deployment unit. Current target ownership follows the 2026-09-14 G1 revalidation, ADR-019, ADR-020, ADR-021 and the global Strategic convergence pass.

Canonical relationship map: `context-map.md`.

## Current target capabilities

| Capability | Semantic owner / disposition |
|---|---|
| Business Process / Connectivity Need / business attribution | **Business Connectivity** |
| Access Request / bilateral approval / grant / withdrawal / history | **Access Governance** |
| Effective Authority / group-role-scope assignment | **Authority Management** |
| Current Policy Rule / effective semantic authorization | **Access Policy** |
| Resource / Endpoint / corporate-visible address realization | **Resource Catalogue** |
| Resource Scope Affiliation / Resource Responsibility | **Resource Catalogue** |
| ComponentDeployment / Interaction / immutable traffic contract | **Application Communication Catalogue** |
| Required Access Materialization | **non-peer derived composition** over Access Policy + ACC + Resource Catalogue |
| Enforcement Target Relevance / policy locators | **Network Enforcement Placement** |
| Target Required Policy Projection | **non-peer derived composition** using materialization + NEP |
| Technical Access Evidence Management | **Technical Access Evidence** |
| Provider Configured-Policy Interpretation | **adapter/integration capability** publishing `ConfiguredEffectivePolicySnapshot` |
| Policy Realization Assessment / common-missing-excess | **Access Policy Realization** |
| Vendor-neutral Policy Change Design / Proposed Result Verification | **Access Policy Realization** |
| Provider Target Rendering | **adapter/integration capability** consuming `VerifiedChangeIntent` and publishing `TargetPolicyArtifact` |
| Provider/device mutation lifecycle | **Network Environment Operations** Bounded Context |
| Scoped Connectivity Inventory | non-peer application/read composition |
| Connectivity Impact Analysis | cross-context analysis; no peer BC accepted |

## Responsibility-scope correlation

Resource Catalogue and Authority Management use the same stable `ResponsibilityScopeRef` for independent truths:

```text
Resource Catalogue: Resource -> effective scope affiliation
Authority Management: Actor + Action + Scope + Time -> effective authority
```

Access Governance consumes these facts for different purposes: Resource Catalogue supplies the side responsibility-scope context, while Authority Management supplies actor/action admission. Neither fact implies the other, and Resource responsibility/contact metadata is not approval authority.

The exact product rule for selecting among legitimately overlapping Resource Scope Affiliations remains an Access Governance behavior/Tactical question, not a reason to move scope-affiliation ownership out of Resource Catalogue.

## Provider configured-policy interpretation

ADR-021 places provider-specific interpretation outside APR core and outside TAE domain ownership.

```text
provider policy/configuration
+ provider semantics
+ explicit comparison scope
    -> ConfiguredEffectivePolicySnapshot
```

The interpreter resolves source-specific rule ordering, deny/default behavior, objects/groups, aliases and other supported provider semantics into source-neutral effective permit space.

The published projection must carry target/policy correlation, provenance/time, explicit completeness (`Complete | Incomplete | Unknown`), interpreter identity/version and unsupported-semantics outcome. Unsupported/incomplete semantics fail closed for a complete realization conclusion.

TAE may persist normalized source-qualified evidence but does not choose the current capture or assert APR comparison completeness.

## APR

APR consumes source-neutral comparable inputs:

```text
TargetRequiredPolicy
ConfiguredEffectivePolicySnapshot
```

and owns exact effective-policy algebra, realization assessment, semantic delta, vendor-neutral change design and semantic verification of the proposed result.

APR core does not own provider syntax, ordering, object expansion, default behavior or renderer implementation.

## Provider rendering

ADR-021 places provider-specific rendering downstream of APR semantic verification and upstream of NEO execution:

```text
VerifiedChangeIntent
+ target/provider capabilities
+ base revision/correlation
    -> TargetPolicyArtifact
```

Rendering is an adapter/integration capability. It translates representation only and must preserve verified semantics. Failure to establish semantic equivalence is a fail-closed outcome; no executable artifact is handed to NEO.

## NEO

Network Environment Operations is a target Bounded Context because controlled mutation has independent operation identity, authority admission, concurrency/preconditions, failure/outcome semantics and audit lifecycle.

NEO owns controlled target mutation lifecycle, mutation authority admission, concurrency/pre-check, apply outcome and operation provenance for a supplied target artifact. It does not reinterpret provider policy semantics, repair renderer output or re-decide placement.

Apply success is not convergence proof. Subsequent provider state must be interpreted again and compared through APR.

## Strategic consequences

No new Bounded Context is introduced for provider interpretation or rendering. Provider-specific interpreter/renderer implementations may share libraries or adapter infrastructure, but this does not create a shared semantic owner.

Required Policy Materialization, Scoped Connectivity Inventory and cross-context analysis remain compositions, not peer Bounded Contexts merely because they combine several published contracts.
