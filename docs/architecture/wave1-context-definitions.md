# Wave-1 context definitions — PLAN-027 WP-01

Status: `accepted architecture input — design-relevant D1 context definitions`.

Date: 2026-09-08.

## Purpose

Define only the Bounded Context responsibilities required by the accepted Wave-1 value slice. These are semantic/model boundaries, not service, database, team or deployment boundaries.

## Participating contexts

### Access Policy

**Purpose:** own what network access is authorized to exist as authoritative desired policy.

**Wave-1 responsibilities:**
- own Access Rule ID and immutable semantic identity;
- enforce one authoritative Rule per semantic identity and idempotent Allowed materialization;
- consume ConnectivityDecision result without owning its reasons/process;
- first materialization from Allowed starts Active;
- own Active/Inactive and supported declarative operational properties;
- select effective desired-policy Rules for an authorized scope/as-of;
- preserve decision/business provenance needed downstream.

**Owned language/state:** Access Rule, Rule ID, semantic identity, Active, Inactive, effective desired policy.

**Decisions:** whether an Allowed subject resolves an existing Rule or creates the unique Rule; whether a Rule contributes desired effect at an as-of from its authoritative state/properties.

**Inbound dependencies:** exact proposal/decision subject; Authority Management for permitted actions; Application Communication Catalogue for structural semantic identity; Resource Catalogue and Application Communication Catalogue facts for projection.

**Outbound:** authoritative Rule semantics/effective desired-policy selection and provenance required by normalized projection.

**Not owned:** reasons behind Allowed/NotAllowed; resource/application catalogue truth; technical enforcement placement; configured reality; vendor rendering/execution.

### Authority Management

**Purpose:** answer who may perform a domain action for a scope/effective time.

**Wave-1 responsibilities:** provide effective permission for proposal, Rule mutation and read/export actions; retain sufficient authority provenance for explainability.

**Owned language/state:** authority/eligibility, scope, effective time, Responsibility Assignment/delegation where relevant.

**Decision:** whether actor is permitted to perform the requested domain action for scope/time.

**Outbound:** permitted/not-permitted authority fact plus effective/provenance context.

**Not owned:** connectivity permission reason, Access Rule state/identity, NEED, application/resource truth.

### Application Communication Catalogue

**Purpose:** define valid application/component/deployment structure and communication contracts.

**Wave-1 responsibilities:**
- own Application/Component roles, Component Deployment and DCS identity;
- expose structurally valid directed interactions;
- provide immutable decision-relevant DCS contract/revision semantics;
- provide protocol/service/port facts required by normalized projection.

**Decision:** whether selected source/destination deployments are compatible under an explicitly described DCS interaction.

**Outbound:** valid Rule-subject facts and DCS projection facts with identity/provenance/effective validity where applicable.

**Not owned:** authorization to create policy, Rule lifecycle, technical endpoint realization, vendor syntax.

### Resource Catalogue

**Purpose:** own access-domain Resource/Endpoint identity and current/historical technical realization.

**Wave-1 responsibilities:** resolve technical source/destination realization required for normalized export at one logical as-of; expose validity/provenance sufficient to establish temporal coherence.

**Decision:** what technical realization is authoritative/valid for a Resource/Endpoint at the requested as-of.

**Outbound:** endpoint/address realization plus correlation, effective validity and provenance.

**Not owned:** Access Rule semantic identity, connectivity permission, DCS semantics, normalized policy meaning.

## Participating application composition — not a peer BC

### Access Rule Proposal composition

Combines:
- effective proposal authority from Authority Management;
- valid Source/Destination Component Deployments + DCS from Application Communication Catalogue;
- current Access Policy knowledge where required to derive/compose the proposal.

Produces one immutable proposed Rule semantic identity. It owns no authoritative Rule ID/state and does not decide Allowed/NotAllowed.

### Normalized Policy Export composition

Combines:
- selected effective desired Rules from Access Policy;
- technical realization from Resource Catalogue;
- DCS technical semantics from Application Communication Catalogue;
- read/export authority from Authority Management.

Produces a complete explainable vendor-neutral projection for one logical as-of. It is application composition/output, not a new Bounded Context in current evidence.

## External/deferred semantic participant

### Connectivity Decision Domain

Current Wave-1 contract only:

`AccessRuleProposal -> ConnectivityDecision(subject exact semantic identity, result Allowed|NotAllowed, opaque provenance/reason reference where available) -> Access Policy`.

Internal policy, reasons, workflow, actors, exceptions, review and supersession remain D0. Architecture must treat this as an external/deferred semantic dependency and must not invent its model.

## Strategic contexts not elaborated for Wave 1

Connectivity Requirements, Network Enforcement Placement, Technical Access Evidence and Access Policy Realization remain accepted Strategic DDD contexts but are not promoted to Wave-1 D1 architecture merely because they exist in DDD-BDM-010. Their later participation follows explicit deferral/revisit triggers.

## WP-01 result

Wave-1 architecture must preserve four directly participating semantic owners — Access Policy, Authority Management, Application Communication Catalogue and Resource Catalogue — plus the deferred Connectivity Decision seam and application-level Proposal/Export compositions. No service/database/deployment topology follows from this definition.