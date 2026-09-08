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

## I1 core realization notes

The executable core maps the accepted contracts as follows:

- a permitted `AuthorityCheck.authority_reference` is the opaque reference to the authority evidence for the requested actor/action/scope/effective time; absence fails closed before catalogue or decision calls. Concrete Authority-provider validity payloads remain adapter-specific and are not invented in I1;
- a valid catalogue answer carries the exact resolved `RuleSemanticIdentity` plus provenance; the application rejects a valid-labelled answer whose identity differs from the requested proposal subject;
- the authoritative Rule preserves proposal authority/catalogue provenance and the explicit `Allowed` decision result/reference;
- `AccessRuleRepository` exposes find, insert, load-by-RuleId and operation commit semantics; a typed semantic-identity conflict lets the application resolve the authoritative winner. I1 proves this port behavior with an in-memory fake, while I2 must prove the same guarantee under real relational concurrency/rollback semantics.

## I1 transport boundary

I1 has no required transport. The application command is exercised directly through Domain/Application tests with fake/in-memory ports.

An HTTP adapter may be introduced only after the I1 core gate passes. If selected, it maps transport syntax/statuses to the stable application outcomes without redefining domain semantics.

## Post-I1 persistence contract

I2 must implement the accepted repository semantics using a relational transactional persistence mechanism:
- opaque/stable RuleId primary key;
- sourceDeploymentId, destinationDeploymentId and dcsRevisionId stored as immutable identity references;
- authoritative unique constraint on their tuple;
- state constrained to Active/Inactive;
- decision/provenance required by the accepted model;
- concurrency/rollback behavior proven against the selected deployment engine.

Database/vendor choice remains an engineering decision. No Legacy schema/procedure is target truth.

## Versioning

No public backward-compatibility contract exists yet. Keep ports/application contracts explicit and internal so later transport evolution does not change domain semantics.