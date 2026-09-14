# Capability Revalidation Checkpoint — 2026-09-14

Status: `stakeholder-confirmed discovery / G1 revalidation checkpoint`.

Author/source: project stakeholder discussion, 2026-09-14. This checkpoint preserves accepted product semantics and explicitly separates them from still-open S2/architecture choices. Existing CR/CD documents predate this revalidation and must not override the statements below merely because they are older or more detailed.

## Revalidation intent

The current work is capability-first. Do not preserve `Connectivity Requirements` or `Connectivity Decision` as Bounded Contexts merely because those names exist in the strategic model. Recompose capabilities after G1; choose BC boundaries only later.

The semantic ladder is:

```text
Observed != Recognized != Needed != Authorized != Realized
```

- Observed: traffic was seen.
- Recognized: the application/component interaction is known.
- Needed: a business process is known to require the interaction.
- Authorized: responsible sides have permitted the concrete deployed interaction.
- Realized: the network currently implements the required effective access.

`Unjustified` does not automatically mean `forbidden`; `authorized` does not automatically mean `realized`.

## Distributed self-service journey

The product is intended to distribute maintenance and access governance to interested/responsible employees rather than rely on one central catalogue or one central approver.

MVP behavior currently accepted:

- all Resources are visible to users;
- only Resources in the user's effective responsibility/authority scope are manageable;
- a user may initiate an access request for an in-scope source Resource;
- the destination Resource may be globally visible and outside the requester's scope;
- useful personal views include managed Resources, submitted/current access requests and effective access;
- Resource visibility, Resource management authority and authority to request access are separate concerns.

Resource `owner`/`administrator` facts do not themselves grant security actions.

## Business process and connectivity need

A Business Process supplies structured business justification for deliberate connectivity. NAPMS does not need to become a BPM/workflow engine merely to model this justification.

Confirmed behavior/meaning:

- deliberate known access requests must be backed by a Business Process through a Connectivity Need;
- a Process has a stable human-recognizable meaning and organizational responsibility;
- business importance/criticality is meaningful for impact analysis, but the exact scale/algorithm is not yet fixed;
- monetary value, downtime cost, process hierarchy and similar richer attributes are candidates only;
- Organizational Unit and NAPMS Responsibility Scope are not assumed to be the same object;
- a Process may require many Interactions and the same Interaction may support many Processes;
- the destination side does not have to invent a mirror Process/Need for every client request;
- a Connectivity Need is application-semantic, not IP- or Deployment-level;
- a Need identifies a Process-backed dependency on a required Interaction and the dependent participant/role;
- Need lifetime follows business need, not address or deployment lifetime;
- one Need may lead to several concrete Requests over time or across deployments;
- one Policy Rule may satisfy several Needs;
- losing one Need does not remove a Rule when other current Needs still justify the same authorized subject;
- loss of all known current Needs is a reconciliation finding, not automatic revocation unless a later explicit policy says so.

Working semantic shape, not a frozen persistence model:

```text
Business Process
    -> Connectivity Need
        -> required Application Interaction
        -> dependent Component/participant role
```

## Recognition / brownfield discovery

Observed traffic may initially have no Process or Need. Do not force fake business attribution merely to ingest/recognize brownfield traffic.

Recognition can be incrementally enriched:

```text
Observed Traffic
    -> Resource attribution
    -> Deployment/Component attribution
    -> Interaction recognition
    -> Process / Connectivity Need attribution
    -> authorization reconciliation
```

The enrichment steps need not be one strict sequence. Source and destination sides may contribute independently. Unknown source/destination Resource, Deployment/Component, Interaction, Process/Need and authorization states may coexist.

When an observed deployed interaction becomes recognized and justified but is not authorized, it converges into the same Access Request workflow used for deliberate access. If it is already authorized but lacks business attribution, the task is attribution/reconciliation, not a second approval workflow.

A recognition workspace is currently a composition/work-queue capability candidate, not a proven Bounded Context.

## Deployment and Resource realization

For MVP:

```text
ComponentDeployment -> exactly one Resource
```

A Deployment means the concrete deployment of a concrete Component on a concrete Resource. Resource association is mandatory at Deployment creation. A Deployment without a Resource is not valid in this MVP model.

A Resource may have zero or more Endpoints; an Endpoint may temporarily have no current address. A Deployment and semantic Policy Rule may therefore exist while technical realization is unresolved.

IP/address changes and Endpoint additions/removals on the same Resource do not change Deployment identity or semantic authorization. Moving the Component to another Resource must not silently transfer existing authorization. The current preferred interpretation is a new Deployment/new concrete authorization subject; exact S2 lifecycle mechanics remain to be fixed.

## Access request subject

A deliberate Access Request asks permission for a concrete deployed realization of an already known Process-backed Need.

Authorization subject is conceptually:

```text
source Deployment
+ destination Deployment
+ stable Interaction meaning
```

Business justification is conceptually:

```text
Connectivity Need
+ Business Process
```

The Request must not be rewritten historically when later business justification changes. Deployment replacement or material Interaction expansion/change requires renewed approval. Address changes, Endpoint address changes and Resource metadata changes do not.

## Bilateral approval — no centralized approver

Access approval is distributed between the responsible sides of the concrete interaction. There is no mandatory central approver deciding ordinary access on behalf of both sides.

Every Request requires independent approval obligations for:

```text
source side
AND
destination side
```

Overall authorization is granted only when both required sides approve. Either side may reject. Approvals may arrive in any order. The same human may satisfy both obligations only if effective authority independently permits that actor to act for both sides; two distinct people are not currently required.

Approval is not derived from Resource ownership or technical administration. The approving employee must receive effective authority through role/group/scope assignments.

Conceptually:

```text
Actor -> member of Group
Group -> assigned Role within Scope
Role -> permits Action
```

Access Governance asks Authority Management whether an actor currently may perform the relevant action in the corresponding Scope. It must not infer permission from `ownerGroup` or `administratorGroup`.

Request initiation, source-side approval, destination-side approval and network execution are distinct permissions even when one actor happens to hold several of them.

Approval provenance must preserve enough information to explain who decided, which side was represented, when, outcome/reason and the authority basis/scope valid at decision time. Later loss of a role does not rewrite a historically valid decision.

## Revocation / withdrawal of consent

Grant and revocation are intentionally asymmetric:

```text
Grant  = source consent AND destination consent
Revoke = source withdrawal OR destination withdrawal
```

Either authorized side must be able to withdraw its consent for current access without obtaining consent from the other side. This prevents one side from blocking termination of access to/from its Resource.

Rejecting a pending Request and withdrawing consent from an existing authorization are different actions. Historical approvals remain historical facts after revocation; the original Request does not become `Rejected` retroactively.

A Need survives revocation when the business need still exists. A new explicit bilateral authorization action is required before revoked access can become authorized again; removal of the revocation cause must not silently restore access.

The exact aggregate/entity representation of side consent, grant and revocation is intentionally left to S2.

## Policy Rule lifecycle and deduplication

Policy Rule is current authorization truth, not the request/approval journal.

One semantic subject should have one authoritative current Policy Rule meaning. Multiple Needs and multiple approved Requests may provide provenance/business justification for the same semantic authorization. A rejected Request does not create a deny Policy Rule.

Policy Rule lifecycle is independent of Request history. A Rule may become ineffective after withdrawal and may later become effective again only after a new explicit valid authorization. Whether this is represented by one long-lived Rule, revisions or another S2 mechanism is unresolved.

Time-bounded authorization is a valid behavior candidate: effective policy should exist only while a valid authorization basis covers the subject. Do not freeze one `effectiveFrom/effectiveTo` storage shape before S2.

## Semantic-to-technical realization

The required realization chain is currently:

```text
Effective semantic Policy Rules
    -> Deployment -> Resource
    -> all current ResourceEndpoints
    -> current corporate-visible prefixes
    -> Interaction required traffic
    -> normalized required technical predicates
    -> NEP candidate enforcement locations/policy locators
    -> target-specific required effective policy
    -> APR comparison/change design
    -> NEO execution/post-check
```

Technical predicates may be shared by several semantic Policy Rules. Deduplication must preserve many-to-one provenance. Revoking one Policy Rule must not remove a technical predicate still required by another effective authorization.

Do not translate revocation into `delete the ACL line that was created for this Rule`; recompute aggregate required effective policy and compare it with observed effective policy.

## Normalized network truth

Vendor-specific configuration belongs at integration boundaries. Internal reasoning should use normalized effective permit semantics rather than vendor ACL syntax/rows.

Conceptual normalized predicate includes source prefix/range, destination prefix/range, protocol and relevant port ranges. `deny` is not an internal desired-access action; provider ordering/deny/default semantics are interpreted into effective allowed space at normalization boundaries.

TAE/APR documents that imply internal vendor-row semantics or provider rendering inside APR are dirty candidates for later correction.

## Required vs observed realization

Authorization state and network state are independent truths:

```text
Authorized=true,  Realized=true   -> desired access satisfied
Authorized=true,  Realized=false  -> missing required access
Authorized=false, Realized=true   -> excess/unauthorized technical access
Authorized=false, Realized=false  -> desired absence satisfied
```

The binary table is explanatory only. Actual reconciliation is set/space based:

```text
common  = required ∩ observed
missing = required - observed
excess  = observed - required
```

A semantic Rule may be authorized but not yet materializable because Resource/Endpoint/address/placement/policy-locator evidence is missing. Such cases are `unresolved`, not silently omitted and not mislabeled as firewall drift.

Observed network truth must carry freshness/provenance. After revocation, stale last-known device state may show that access was previously present; it must not be presented as a fresh certainty until reacquired.

NEO execution success is not the same as convergence. Post-check must confirm normalized observed effective state against desired state.

## Capability clues after revalidation

These are cohesion candidates, not final BC names:

```text
Business connectivity
    Business Process Management
    Connectivity Need Management
    Business Attribution
    Business Impact / justification reconciliation

Access governance
    Access Request Submission
    Approval Obligation Determination
    Side Approval
    Composite/Bilateral Approval Evaluation
    Authorization Grant
    Authorization Revocation
    Governance History

Authority management
    Group Membership
    Role Definition
    Role Assignment
    Scope Binding
    Effective Authority Evaluation

Access policy
    Current Policy Rule Governance
    Effective Authorized Policy

Recognition / reconciliation
    Observed Traffic Enrichment
    Policy Realization Reconciliation
    Business Justification Reconciliation
```

Do not infer one Bounded Context per group or capability.

## Existing CR/CD reclassification

Old `Connectivity Requirements` contains useful Need semantics but mixes them with deployment-level subject, lifecycle, authority and tactical identity choices. The useful core is being reinterpreted as Process-backed application-semantic Connectivity Need. Stable Requirement ID, Active/Retired state machine, active uniqueness and redeclaration rules are not automatically carried forward.

Old `Connectivity Decision` contains useful decision authority, approve/reject, reason, actor/time and provenance behavior. A single global `Allowed/NotAllowed` decision, standalone durable Decision identity, validity interval and supersession chain are not currently justified. Bilateral side decisions and current authorization lifecycle supersede the old single-decision assumption at G1.

ADR-016 and the strategic model must therefore be revalidated before being used to exclude request/approval capabilities from the product.

## Explicit unknowns retained for later stages

- final Bounded Context grouping and Context Map;
- exact Process identity/lifecycle and criticality scale;
- Organizational Unit to Responsibility Scope mapping;
- exact authority role names and whether approve/revoke share a role;
- how overlapping scopes resolve an applicable approval authority;
- whether a responsibility-scope change requires warning, reapproval or automatic revocation;
- exact entity/aggregate/storage representation of Need realization, Approval Obligation, side consent, Authorization Grant and revocation;
- exact Rule revision/reactivation mechanics;
- exact time-bounded authorization model;
- ownership of semantic-to-technical materialization and target-specific policy projection;
- exact normalization schema and provider boundary ownership;
- whether future Deployment-to-Endpoint binding is needed beyond the MVP Resource binding.
