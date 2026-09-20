# Tactical domain — Access Policy

Status: ACCEPTED candidate

## Aggregate: AccessRequest

Identity: `AccessRequestRef`.

Immutable subject:
- sourceDeploymentRef;
- destinationDeploymentRef;
- interactionRevisionRef;
- needRef.

State:
- submittedAt;
- submitterActorRef;
- permissionDecision?: ALLOWED | DENIED with decisionRef/provenance/decidedAt.

Invariants:
- Need must be current at submission and its InteractionRef must match the Interaction owning the exact InteractionRevision.
- source/destination Deployment Components must match the revision's source/destination Components.
- request subject is immutable after submission.
- one request receives at most one final permission decision; a new materially different attempt is a new AccessRequest.
- request submission authority is checked outside the aggregate through the accepted security/application admission contract.

## Aggregate: PolicyRule

Identity: `PolicyRuleRef`.

Immutable semantic subject/provenance:
- originatingAccessRequestRef;
- sourceDeploymentRef;
- destinationDeploymentRef;
- interactionRevisionRef;
- needRef;
- allowedDecisionRef.

State:
- effectState: ACTIVE | INACTIVE;
- version/history.

Invariants:
- PolicyRule exists only for an ALLOWED request.
- one AccessRequest can establish at most one PolicyRule; repeated allowed materialization resolves the same rule.
- technical Resource/address realization is not part of PolicyRule identity.
- changing ACTIVE/INACTIVE never rewrites the request/decision subject or provenance.
- DENIED request never produces a Rule.

Operations:
- SubmitAccessRequest
- RecordPermissionDecision
- MaterializeAllowedRule
- SetRuleEffectState
- ReadCurrentEffectiveRules
- ReadRuleHistory

## Consistency boundary

Recording one permission decision and first-time PolicyRule establishment must be atomic with respect to that request identity. Rule effect-state mutation is atomic per PolicyRule. External domain references are validated before committing a request; no cross-context write transaction is required.
