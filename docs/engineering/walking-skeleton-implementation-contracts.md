# Walking Skeleton implementation contracts — PLAN-028 WP-03

Status: `accepted D2 contracts for first skeleton`.

Date: 2026-09-08.

## Application command

```text
SubmitAccessRuleProposal
  actorId
  authorityScope
  effectiveTime
  sourceComponentDeploymentId
  destinationComponentDeploymentId
  dcsContractRevisionId
```

Success result after Allowed materialization:

```text
AccessRuleMaterializationResult
  ruleId
  semanticIdentity
  operationalState = Active
  decisionReference
  created = true | false
```

`created=false` means the exact authoritative Rule already existed and was resolved idempotently.

## Ports

### AuthorityPort
`check(actorId, action=ProposeConnectivity, scope, effectiveTime) -> Permitted(authorityRef/effectiveValidity) | Denied | Unknown`

Denied/Unknown are fail-closed and no proposal proceeds.

### ApplicationCommunicationCataloguePort
`resolveDirectedInteraction(sourceDeploymentId, destinationDeploymentId, dcsRevisionId, effectiveTime) -> ValidExactInteraction(identity/provenance) | Invalid | Unknown`

Only ValidExactInteraction creates the immutable proposal subject.

### ConnectivityDecisionPort
`decideOrObtain(proposalSubject) -> Decision(subject, Allowed|NotAllowed, decisionRef?) | Unknown/Unavailable`

Returned subject must equal proposal subject exactly. NotAllowed is a valid business result with no Rule. Unknown/Unavailable is not NotAllowed and is not permission.

### AccessRuleRepository / UnitOfWork
Required operations:
- find by RuleSemanticIdentity;
- insert new AccessRule;
- commit with authoritative unique constraint over the three identity references;
- resolve uniqueness conflict/retry safely;
- load by RuleId for later increments.

## Initial transport

Expose the application command through a minimal HTTP API because the repository already contains a Python/FastAPI prototype/toolchain that can be reused as engineering scaffolding only, not business truth. The target API contract must be newly implemented from accepted G2/G3 semantics rather than extending historical `AccessRequest` API meaning.

Recommended first endpoint shape (implementation surface, not domain identity):

`POST /access-rule-proposals`

Responses:
- `200` existing Rule resolved idempotently;
- `201` new Active Rule materialized;
- `403` proposal authority denied;
- `409` structural/subject invariant conflict;
- `422` syntactically invalid command;
- `503` required authority/catalogue/decision dependency unknown/unavailable or persistence outcome cannot be established.

A `NotAllowed` decision should return a stable business non-materialization response distinct from infrastructure failure; exact HTTP status/body naming may be finalized during code implementation tests without changing domain semantics.

## Persistence contract

Use a relational transactional persistence mechanism for the first skeleton. Required schema semantics:
- opaque/stable RuleId primary key;
- sourceDeploymentId, destinationDeploymentId, dcsRevisionId stored as immutable identity references;
- unique constraint on their tuple;
- state constrained to Active/Inactive;
- decision reference/provenance;
- created/materialization audit timestamps/source metadata sufficient for first-slice acceptance.

Database/vendor choice is an engineering decision; existing MSSQL prototype is not automatically target truth. Prefer the simplest repository-supported local/test path unless deployment constraints require MSSQL.

## Versioning

No public backward-compatibility contract exists yet. Keep ports/application contracts explicit and internal so later transport evolution does not change domain semantics.