# Tactical domain — Access Policy

Status: ACCEPTED after Source Corpus amendment 01

## Value object: AccessSubject

An `AccessSubject` is the semantic identity of concrete desired connectivity for this MVP:

- `sourceDeploymentRef`;
- `destinationDeploymentRef`;
- `interactionRevisionRef`.

Rationale:
- concrete Deployments identify the participating deployed Component instances;
- exact InteractionRevision identifies independently meaningful directed traffic semantics;
- Resource/address realization is deliberately excluded because it may change without changing access meaning;
- NeedRef is deliberately excluded because business justification can be added/retired independently and must not duplicate current access.

Two AccessSubjects are equal only when all three refs are equal.

## Aggregate: AccessRequest

Identity: `AccessRequestRef`.

Immutable state:
- `subject: AccessSubject`;
- `initialNeedRef`;
- `validatedBusinessProcessVersion` at submission;
- `submitterSubject`;
- `submittedAt`.

Final state:
- `permissionDecision?: PermissionDecision`.

`PermissionDecision`:
- `result: ALLOWED | DENIED`;
- optional opaque `externalDecisionRef`;
- `decidedBySubject`;
- `decidedAt`.

Invariants:
- initialNeedRef is current under the accepted current-Need validation lock through submission commit;
- initial Need's InteractionRef matches the Interaction owning subject.interactionRevisionRef;
- source/destination Deployment Components match revision direction;
- AccessSubject/initialNeed/provenance are immutable after submission;
- one AccessRequest receives at most one final decision;
- DENIED never creates permission evidence or a PolicyRule by itself.

## Aggregate: PolicyRule

Identity: `PolicyRuleRef`.

Unique semantic key:
- exactly one PolicyRule exists per `AccessSubject`.

Immutable:
- `subject: AccessSubject`;
- `createdAt`.

Operational state:
- `effectState: ACTIVE | INACTIVE`;
- `effectiveWindow?: EffectiveWindow`;
- aggregate `version`.

`EffectiveWindow`:
- optional `effectiveFrom` inclusive;
- optional `effectiveUntil` exclusive;
- if both exist: `effectiveFrom < effectiveUntil`;
- absent bounds mean unbounded on that side.

Children/history:

### AuthorizationEvidence

One entry per ALLOWED AccessRequest associated with this Rule:
- `accessRequestRef` unique;
- `submittedBySubject`;
- `submittedAt`;
- `initialNeedRef`;
- optional `externalDecisionRef`;
- `decidedBySubject`;
- `decidedAt`.

The request fields are projected from immutable AccessRequest owner state; they are not independently mutable evidence fields.

It proves accepted permission provenance. Multiple ALLOWED requests for the same AccessSubject can contribute multiple evidence entries without duplicating the Rule.

### JustificationAssociation

One entry per associated NeedRef:
- `needRef` unique within Rule;
- `attachedAt`;
- `attachedBySubject`;
- optional `sourceAccessRequestRef`.

Association history is append-only in the MVP. Current/retired Need status is not stored as Access Policy truth; Business Connectivity owns it.

### OperationalHistory

Append-only accepted changes to:
- ACTIVE/INACTIVE;
- effectiveWindow.

History records changedBySubject/changedAt and before/after accepted operational values.

## Invariants

- PolicyRule may exist only after at least one ALLOWED AccessRequest for its exact AccessSubject.
- first creation is ACTIVE with no restricting effectiveWindow;
- ALLOWED resolution is atomic: final AccessRequest decision + resolve/create Rule + AuthorizationEvidence + initial JustificationAssociation commit together;
- concurrent ALLOWED requests for the same AccessSubject converge on one PolicyRule;
- processing another ALLOWED request for an existing Rule does not reset ACTIVE/INACTIVE or effectiveWindow;
- AuthorizationEvidence AccessRequestRef is unique and append-only;
- JustificationAssociation NeedRef is unique and append-only;
- attaching Need requires it to be current at that transaction snapshot and its InteractionRef must match the Rule Interaction;
- Need currentness/retirement later does not mutate PolicyRule;
- zero current Needs does not alter effectState/effectiveWindow;
- semantic identity and permission evidence never include current Resource address realization;
- same-state/same-window operational update is a semantic no-op: version/history unchanged.

## Effective contribution

At evaluation time `t`, Rule is operationally effective iff:

`effectState == ACTIVE`
AND (`effectiveFrom` absent OR `t >= effectiveFrom`)
AND (`effectiveUntil` absent OR `t < effectiveUntil`).

Current business justification status is reported separately and does not enter this boolean in the MVP.

## Operations

- SubmitAccessRequest
- RecordPermissionDecision
- ResolveOrCreateAllowedPolicyRule
- SetPolicyRuleOperationalState
- AttachPolicyRuleJustification
- ReadAccessRequest
- ReadPolicyRule
- ReadCurrentPolicyRules
- ReadPolicyRuleHistory

## Consistency boundaries

- AccessRequest finalization is atomic per AccessRequest version.
- ALLOWED finalization plus unique-subject Rule resolve/create, evidence and initial justification association is one database transaction.
- PolicyRule operational mutation and justification attachment are atomic per PolicyRule version.
- mutable Need currentness uses the Business Connectivity owner-provided validation lock held through Access Policy commit; immutable Interaction/Deployment facts are read-only peer facts; no peer owner state is written.
