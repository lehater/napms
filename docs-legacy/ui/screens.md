# Web UI screen map

Status: `current non-APR screens through I27 Catalogue Curation; APR operator surface under revalidation`.

Canonical product semantics:
- `docs/requirements/web-ui-requirements.md`;
- feature requirements under `docs/requirements/`;
- feature boundaries under `docs/architecture/`.

APR target framing:
- `docs/domain/access-policy-realization/README.md`.

## Login

Input: login + password. Output: authenticated session or generic authentication failure. Successful login enters the normal product shell.

## Connectivity

Primary resource-centric workspace for one selected Responsibility Scope.

```text
Resource
  -> Component Deployment
      -> Connectivity Relationship
```

Show local/remote participants, direction, access/DCS, Need, Decision and Policy independently. Empty Resources/Deployments remain visible. Relationship detail progressively exposes owner-protected details and technical identifiers.

Contextual Add connectivity uses backend discovery and reuses known local context.

## Checker

Technical traffic analysis and attribution entry point.

Input: source/destination address, protocol/port semantics and `asOf`. Output groups:
- Overview/address/resource attribution;
- Network Context information;
- policy/governance matches;
- Ownership/Resource Responsibility;
- stored configured Evidence.

Ambiguous/historical/unknown attribution and missing evidence remain explicit. Checker-specific network-context presentation does not define APR target-selection semantics.

## Applications

Catalogue list/search plus create Application.

Application detail exposes:

```text
Application
  Component
    Component Deployment
      Resource Bindings
      DCS revisions
```

Supported actions include:
- Application/Component/Deployment rename without changing stable identity;
- leaf-to-parent retirement rather than hard delete, with blocked parent retirement surfaced explicitly;
- Component/Deployment creation;
- backend Resource discovery and bind/unbind through temporal end semantics;
- immutable DCS authoring using Active participant discovery;
- saved DCS inspection after reload/reopen with readable source/destination and protocol/port/service alternatives.

Communication correction creates another immutable DCS revision; the UI does not rewrite historical revisions or downstream references.

Readable names lead; stable IDs, versions and provenance are available in technical detail.

## Resources

Paged/searchable Resource catalogue with effective Responsibility Scope filtering and current completeness diagnostics.

Resource detail groups:
- identity/lifecycle/provenance;
- endpoint realization history/current technical addresses;
- Responsibility Scope affiliations;
- Resource Responsibility/contact assignments.

Supported actions include create, rename/retire, realization create/replace, scope-affiliation create/end and responsibility create/end. Missing current facts are shown explicitly.

## Needs

Connectivity Requirement workspace: readable interaction, scope/applicability, `Active | Retired`, justification and derived `Covered | Uncovered | NotCurrent | Unknown` alignment. Protected mutations remain independently admitted.

## Decisions

Final Decision workspace for `Allowed | NotAllowed`: list/detail, direct admitted recording and explicit immutable supersession. No Pending/approval lifecycle.

## Rules

Access Rule list/detail with readable participants/DCS first, governance scope, `Active | Inactive`, effective-window state, Decision correlation and provenance.

## Effective

Read effective desired policy for one authorized scope and `asOf`. Authorized empty, denied/unknown and technical failure are distinct.

## Export

Normalized technical policy view preserving semantic correlation, DCS traffic alternatives, realization, `asOf` and provenance.

## Access Policy Realization

No target APR screen contract is currently accepted. The existing runtime `Realization` screen is legacy implementation/migration material and must not be used as the specification for the redesigned APR bounded context.

The target screen model will be defined only after APR realization assessment, semantic delta, policy-change design, verification and rendering contracts are accepted.

## Navigation

Accepted non-APR navigation:

```text
OVERVIEW
  Connectivity
  Checker

CATALOGUES
  Applications
  Resources

POLICY
  Needs
  Decisions
  Rules
  Effective
  Export
```

A legacy runtime may still expose `OPERATIONS -> Realization` until implementation migration. Its current contents are not target semantics.

Future screens may be added only when backed by accepted scope and must not expose fake actions/data.
