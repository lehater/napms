# Catalogue Curation requirements

Status: `accepted product requirement for I27 planning`.

Date: 2026-09-10.

## Purpose

Make the local NAPMS product self-service for the access-domain catalogue data that its existing Connectivity, Checker, Requirement, Decision, Rule and Realization workflows already consume.

The product shall provide user-facing curation workflows for:

- Resource Catalogue data needed to identify access-relevant Resources, their technical endpoints/realizations, responsibility-scope affiliations and operational responsibility/contact facts;
- Application Communication Catalogue data needed to identify Applications, Components, Component Deployments, deployment-to-Resource bindings and immutable Directed Communication Specification revisions used by governed connectivity.

This requirement closes the current gap where catalogue truth is persisted and consumed by the product but normal local users cannot create or maintain that truth through supported application/UI workflows.

## Product problem

The current supported local runtime seeds catalogue records directly into PostgreSQL. Human-facing workspaces consume those records, but the user cannot onboard a new Resource/Application structure end to end without out-of-band database/seed changes.

That prevents the local product from supporting the normal workflow:

```text
responsible user
    -> register access-relevant Resources
    -> register application/deployment structure
    -> bind deployments to Resources
    -> describe valid directed communication
    -> use Connectivity / Needs / Decisions / Rules / Checker / Realization
```

The solution is not a generic CMDB or application-portfolio database. Catalogue curation exists only to maintain identities and relations required by NAPMS access outcomes.

## Existing semantic ownership

This requirement preserves current Strategic DDD ownership.

### Resource Catalogue

Resource Catalogue owns:

- Resource identity;
- Resource Endpoint/current and historical realization facts;
- Resource Scope Affiliation;
- Resource Responsibility/contact facts required by access-domain workflows.

### Application Communication Catalogue

Application Communication Catalogue owns:

- Application identity;
- Component identity;
- Component Deployment identity;
- structurally valid directed communication/DCS identity and immutable revision semantics;
- Deployment Resource Binding.

### Authority Management

Authority Management owns actor/action admission for catalogue mutation. Resource ownership, Resource Responsibility, Resource Scope Affiliation and catalogue visibility do not themselves grant mutation authority.

## Primary user model

The normal product navigation gains a catalogue area:

```text
CATALOGS
  Applications
  Resources
```

These workspaces are responsibility-aware but remain catalogue-owner surfaces. They do not copy catalogue truth into Web state or into another bounded context.

The selected Responsibility Scope may be used to focus local work and discover relevant Resources, but the current opaque Responsibility Scope reference does not imply a new Company/Organization aggregate or hierarchy.

## Resource curation workflow

### Purpose

Allow an admitted user to onboard and maintain one access-relevant Resource and the Resource Catalogue facts needed by downstream NAPMS workflows.

### Required capabilities

The supported workflow shall allow an admitted user to:

1. create/register a Resource identity with required provenance;
2. inspect Resource details;
3. add a new endpoint/realization version with one or more technical addresses;
4. end/replace time-qualified realization facts without rewriting historical facts;
5. affiliate the Resource with one or more Responsibility Scopes using the existing time-qualified Resource Scope Affiliation semantics;
6. end/replace an affiliation without changing Resource identity;
7. maintain Resource Responsibility assignments for supported person/team references and roles;
8. inspect the effective/current projection needed for ordinary workflows while retaining access to technical identifiers and provenance.

### Resource list

The Resources workspace shall support at least:

- server-backed paging;
- search/filter by Resource reference and available display/contact information;
- scope-focused filtering using effective Resource Scope Affiliation;
- clear indication of resources with missing current endpoint realization, missing scope affiliation or missing operational responsibility/contact information when those facts are relevant to the current workflow;
- navigation to Resource details and contextual create/edit actions admitted by the backend.

A Resource remains a Resource when no effective scope affiliation or endpoint realization exists. The UI shall represent missing relations explicitly instead of hiding or fabricating them.

### Resource history

Time-qualified facts are maintained by adding/ending versions/relations according to their owning semantics. The UI shall not silently rewrite historical realization, affiliation or responsibility facts as if they were non-temporal scalar fields.

## Application catalogue curation workflow

### Purpose

Allow an admitted user to describe the minimum application structure required to express governed communication and bind it to Resource Catalogue identities.

### Required structure

The user-facing conceptual hierarchy is:

```text
Application
  -> Component
      -> Component Deployment
          -> Deployment Resource Binding
          -> participates in Directed Communication Specifications
```

The implementation shall restore/complete the missing tactical and persistence representation required to support the already accepted Application/Component/Deployment strategic identities. Exact aggregate boundaries, lifecycle rules and identifiers must be resolved in the I27 domain stage before persistence/UI implementation.

### Applications workspace

The Applications workspace shall support at least:

- list/search of Applications;
- drill-down from Application to Components and Component Deployments;
- creation and maintenance of catalogue structure admitted by backend use cases;
- binding/unbinding or effective replacement of Component Deployments to existing Resources using Deployment Resource Binding semantics;
- inspection of communication specifications involving a selected Component/Deployment;
- creation of new immutable DCS revisions through a user workflow that captures supported source/destination and traffic semantics without requiring the user to enter arbitrary internal UUID combinations.

### DCS authoring

DCS is a domain/application communication contract, not a raw firewall rule editor.

The authoring workflow shall expose supported communication meaning such as service/protocol/port constraints through validated fields. The backend owns structural validity and serialization into the immutable DCS projection contract.

Editing an existing immutable DCS revision means creating a new revision/identity according to the accepted ACC tactical model; the UI shall not rewrite a revision already referenced by Requirements, Decisions or Rules.

## Deployment Resource Binding

A Component Deployment may bind to one or more Resource references according to the existing time-qualified binding model.

The curation workflow shall:

- select Resources from backend catalogue discovery rather than accept unchecked opaque references as the normal path;
- preserve validity/provenance;
- make current versus historical bindings distinguishable;
- avoid treating the binding as Resource identity, Resource realization or application ownership.

## Mutation authority

Catalogue mutation is a separately authorized product capability.

I27 shall define explicit Authority Management actions for the Resource Catalogue and Application Communication Catalogue mutation use cases. The exact action granularity is a domain-stage decision and shall be selected before HTTP/UI implementation.

Required properties regardless of final action names:

- the authenticated session supplies actor identity;
- the backend evaluates authority for every mutation;
- UI visibility/enabled state is presentation only;
- `ReadScopedConnectivity` does not grant catalogue mutation;
- Resource Responsibility does not grant catalogue mutation;
- catalogue read visibility does not grant catalogue mutation;
- a mutation's scope/subject context cannot be caller-substituted to bypass stored or selected authority semantics.

## Catalogue visibility

The current catalogue-read visibility baseline remains unchanged for I27 unless a separate accepted visibility requirement changes it.

Authenticated users may continue to read catalogue information needed to understand connectivity. Foreign catalogue objects may therefore be visible as remote context while remaining non-editable when mutation authority is absent.

I27 must distinguish:

```text
visible/readable
!= local/in selected scope
!= operationally responsible
!= authorized to curate
```

Fine-grained foreign catalogue discover/read visibility is outside this increment unless required to safely implement mutation discovery.

## Validation and consistency

All catalogue mutation use cases shall validate in the owning backend application/domain layer.

The Web UI may perform obvious structural validation for usability but is not authoritative.

At minimum:

- required identifiers/references and provenance are non-empty;
- temporal intervals are offset-aware and valid;
- overlapping effective facts that violate existing catalogue invariants fail explicitly;
- bindings reference existing Component Deployments and Resources;
- DCS source/destination and traffic semantics satisfy the accepted ACC contract;
- immutable identities/revisions already referenced by downstream business truth are not silently rewritten;
- duplicate submission is idempotent where a natural command identity/idempotency contract exists, or otherwise prevented and reported safely.

## HTTP/API boundary

HTTP routes shall expose task-oriented application use cases and read models rather than generic table CRUD.

Expected API families are conceptually:

```text
/api/v1/catalogue/resources/...
/api/v1/catalogue/applications/...
```

Exact route names are engineering contract decisions, but transport DTOs must preserve owner semantics and must not expose database-row mutation as the domain API.

The API shall provide backend-owned discovery lists required by forms so that the Web client does not construct arbitrary cross-context stable-ID combinations.

## UI behavior

### Resources

Primary presentation should be a dense operational list with drill-down details and contextual mutations. Detail should group:

- identity/provenance;
- effective endpoints/technical addresses;
- Responsibility Scope affiliations;
- Resource Responsibility/contact assignments;
- bound Component Deployments where a read composition already safely supports it.

### Applications

Primary presentation should make the hierarchy visible without forcing bounded-context terminology on ordinary users:

```text
Application
  Component
    Deployment
```

Details should progressively expose stable IDs, Resource bindings, DCS revisions and provenance.

### Mutation UX

Forms shall:

- use backend discovery for references;
- distinguish create-new-version/end-relation behavior from in-place scalar edits;
- prevent accidental duplicate submission;
- show domain validation errors near the relevant fields;
- distinguish authorization, domain conflict/validation and transport failures;
- confirm destructive or history-ending actions when accidental execution is plausible.

## Local-first target

I27 targets the supported local product:

- PostgreSQL remains the authoritative current catalogue persistence;
- local username/password sessions remain primary;
- no external CMDB, application registry, directory or enterprise IdP is required;
- deterministic local demo data remains available, but normal catalogue onboarding no longer depends on editing seed SQL;
- no real network lab/device transport is required for catalogue curation.

## Non-goals

I27 does not introduce:

- a generic CMDB/asset inventory;
- a generic application portfolio management system;
- a Company/Legal Entity/Organization bounded context solely to display Responsibility Scope references;
- automatic import/synchronization from ServiceNow, NetBox, Kubernetes, cloud providers, LDAP/AD or other external sources;
- fine-grained foreign-object visibility policy unless selected by a separate requirement;
- bulk import/edit as the first slice;
- arbitrary database CRUD screens;
- deletion semantics that erase identities/facts already referenced by Requirements, Decisions, Rules or historical evidence;
- changes to Access Rule semantic identity;
- ownership/responsibility implying mutation authority.

## I27 acceptance journey

The increment is complete only when an authenticated admitted user can perform a fresh local journey without direct SQL/seed edits:

```text
create Resource A and Resource B
    -> add effective endpoints/addresses
    -> affiliate relevant Resource(s) with Responsibility Scope
    -> add responsibility/contact facts
    -> create Application(s) / Component(s) / Component Deployment(s)
    -> bind deployments to Resources
    -> create a structurally valid directed communication/DCS revision
    -> observe the resulting catalogue structure in Applications/Resources
    -> use it from Connectivity
    -> declare/request the connectivity through existing product workflow
```

The acceptance proof must also demonstrate that an authenticated actor without the selected catalogue mutation authority can still receive the allowed catalogue read projection while mutation is denied by the backend.

## Blocking domain decisions for implementation

The requirement is sufficient to select I27, but implementation infrastructure remains closed until the following are resolved in canonical domain/architecture truth:

1. ACC tactical model for Application, Component and Component Deployment identities/relationships and their lifecycle rules;
2. whether catalogue entities support retirement/inactivation and how downstream references behave, instead of hard deletion;
3. exact Authority Management action granularity and scope correlation for Resource and ACC mutations;
4. supported user-authored DCS traffic-semantics input model and immutable revision rule;
5. command/idempotency/provenance rules for locally curated catalogue facts.

These are owner decisions, not UI implementation details.