# Blind domain use-case contracts

Status: ACCEPTED after Source Corpus amendment 01

## Resource Description

- Register immutable Site and organizational ResponsibilityGroup records.
- Register Resource with stable ResourceRef and human-recognizable name.
- Register logical ResourceEndpoint independently of address assignment.
- Set/change/clear current endpoint address while preserving history.
- Set/clear current Site while preserving Site-assignment history.
- Set/clear one current OWNER group and one current ADMINISTRATOR group, closing prior assignment history when replaced.
- Read current Resource realization and basic history.
- Missing current address is explicit, not an empty/denied address.

## Application Communication

- Register Application and Components.
- Define a directed Interaction for one independently meaningful communication reason.
- Publish immutable InteractionRevision with complete minimal supported traffic semantics.
- Publish a new revision when decision-relevant traffic meaning changes; prior revisions remain resolvable.
- Read Application/Interaction and exact revision.

## Application Deployment

- Register immutable ComponentDeployment referencing one Component and one Resource.
- Read Deployment without depending on Resource current address.
- Different concrete deployments have different DeploymentRefs.
- Move/retire/delete semantics are outside current MVP.

## Business Connectivity

- Register Business Process with optional descriptive responsible organization.
- Declare active ConnectivityNeed from Process to one Interaction.
- Retire Need terminally while preserving historical provenance.
- Resolve Need currentness and Process/Interaction/business provenance.
- Need does not grant connectivity permission.
- Business criticality/propagation remains outside current MVP.

## Access Policy

### Submit access

- Submit AccessRequest for source Deployment, destination Deployment and exact InteractionRevision, using one current Need for that Interaction as submission justification.
- Reject mismatched direction/revision or non-current Need.
- AccessRequest captures immutable semantic access subject plus initial Need justification/provenance; Need does not become part of semantic current-access identity.

### Record permission

- Consume one final ALLOWED or DENIED decision for exact AccessRequest.
- DENIED creates no new PolicyRule/current access.
- ALLOWED atomically resolves or creates the one PolicyRule for the request's semantic access.
- First creation starts ACTIVE with no restricting effective window unless explicitly supplied later.
- If Rule already exists, ALLOWED adds authorization evidence and initial Need justification if not already associated; it does not create a duplicate or reset Rule operational state/effective window.

### Manage current access

- Change Rule ACTIVE <-> INACTIVE without changing identity or requiring a new permission decision.
- Set/clear an optional absolute effective window without changing identity/permission evidence.
- Attach an additional **current** Need whose Interaction matches the Rule's Interaction to an existing Rule; attaching justification does not grant or refresh permission.
- Preserve every attached justification historically when its Need later retires; no detach/delete use case exists in MVP.
- Read Rule including authorization evidence, justification references, operational/effective history.

### Current justification status

- For read/materialization, resolve attached NeedRefs through Business Connectivity.
- Distinguish current and retired justifications.
- If none are current, expose reconciliation condition `NO_CURRENT_BUSINESS_JUSTIFICATION`.
- Do not automatically revoke/deactivate Rule solely because current justification count reaches zero.

## Policy Materialization composition

1. establish one server-owned current evaluation instant and coherent read snapshot;
2. select all current PolicyRules or an explicit domain-policy subset by PolicyRuleRef;
3. evaluate each selected Rule's operational state/effective window;
4. skip INACTIVE or conditionally non-effective Rules before requiring technical realization;
5. for each selected effective Rule resolve authorization evidence, current/historical Need justification status, exact InteractionRevision, source/destination Deployments and current Resource endpoints;
6. expand exact traffic semantics over current endpoint combinations;
7. preserve Rule/access/permission/justification/interaction/deployment/resource provenance and reconciliation flags;
8. if an effective Rule lacks required technical/semantic realization, return overall UNRESOLVED rather than complete success;
9. absence of current Need alone is a reconciliation flag, not materialization incompleteness or automatic revocation.

Historical/time-travel policy export is outside this MVP.
