# HCD requirements/task closure — NAPMS pilot

Status: research only; no semantics in this document are canonical product truth.

## Purpose

Apply the branch-only Harness HCD closure experiment to three representative NAPMS
subjects without repairing the UI or silently reconstructing missing User Needs.

Selected subjects:

1. Application / Component authoring;
2. Access Request;
3. Policy Export.

The executable fixture treats current Product Requirements, Human Interface and
Screen/View artifacts as already-materialized downstream providers. It then asks
whether those providers can satisfy a causal HCD consumer when Problem Evidence,
User Needs, Task Model and an Application-owned human journey are absent.

## Source-derived observations

### MVP-wide Discovery gap

Current canonical Discovery is `docs/discovery/resource-catalogue.yaml`, a
Resource Catalogue curation slice. It does not establish an MVP-wide user problem,
Context of Use or consolidated User Needs for the three pilot subjects.

The current Product Requirements artifact is therefore useful normative truth, but
it cannot by itself prove the problem/need chain that motivated all interactive work.

### FIRST-MVP-JOURNEY is not a human journey

`docs/model/use-cases/first-mvp-policy-export.yaml` declares
`kind: cross-context-use-case` and states that its purpose is to realize accepted
first-MVP backend requirements through cross-context composition.

The pilot deliberately does not bind it to `user-journey-design`. Treating that
artifact as the human journey would collapse backend/application composition and
human work into one semantic contract.

### Current UI knowledge is downstream-heavy

`docs/contracts/ui/mvp-human-interface.yaml` says its subjects are derived from
accepted product scope. `docs/contracts/ui/mvp-navigation.yaml` already chooses
workspaces/routes and embeds short journey narratives. These are useful downstream
decisions, but they are not evidence that the complete set of human tasks was
identified before view partitioning.

## Subject pilot

### 1. Application / Components

Accepted source facts:

- REQ-MVP-001 requires the end-to-end MVP to support describing Applications and
  Components.
- REQ-APP-001 requires reusable Application descriptions independent of concrete
  deployment realization.
- REQ-APP-002 defines Component as an application communication participant/role,
  not a network device.
- Current navigation chooses APPLICATION-CATALOGUE and APPLICATION-DETAIL and
  places Component authoring inside Application detail.

Missing accepted upstream knowledge:

- explicit user goal and Context of Use explaining why/when a person needs to
  create, locate or revisit an Application description;
- User Needs establishing which information must be available to recognize the
  correct existing Application or Component;
- intended task decomposition for create/select Application → maintain Components
  → proceed to Interaction work;
- evidence that a separate catalogue/detail split is required by human work rather
  than selected as an Interface Design convention.

Candidate research questions, not answers:

- What user outcome requires a reusable Application description?
- How does a user determine that an Application already exists and is the correct
  one to extend?
- Which information must be visible while adding/editing Components?
- Must Component authoring happen inside one Application context, or is that only
  the current interface partition?

### 2. Access Request

Accepted source facts:

- REQ-AUTH-001 requires effective request authority at the relevant scope/time.
- REQ-PERM-001..003 distinguish request permission, immutable request subject and
  Allowed/NotAllowed outcomes.
- Current navigation says the user selects an eligible Need/deployment subject,
  submits the request, then inspects the immutable subject and outcome.

Missing accepted upstream knowledge:

- explicit user goal/need that explains the human decision leading to request
  submission;
- task model for selecting the exact request subject from Connectivity Need,
  Interaction and Deployment semantics;
- required information for the user to judge that the intended subject is correct
  before an irreversible/auditable submission;
- recovery/alternate human work for denied authority, invalid subject or later
  NotAllowed decision.

Candidate research questions:

- What information must the requester compare before submitting?
- Which distinctions must remain visible between business justification,
  request authority and eventual connectivity decision?
- What should the user do after authority rejection versus a NotAllowed business
  decision?

### 3. Policy Export

Accepted source facts:

- REQ-AUTH-002 requires effective export authority.
- REQ-EXP-001 permits all-current-policy or explicit domain-policy subset selection.
- REQ-EXP-002..007 define effectiveness, evaluation-time coherence, completeness,
  unresolved output and normalization semantics.
- REQ-PROV-001 requires end-to-end explainable provenance.
- Current navigation chooses a POLICY-EXPORT workspace with scope selection,
  execution and completeness diagnostics.

This subject has the strongest normative downstream semantics of the three, but
still lacks:

- accepted user need explaining the human outcome/decision for which export exists;
- task model for identifying the correct subset and deciding whether diagnostics
  are sufficient to proceed;
- information requirements for subset selection, comparison and provenance review;
- explicit disposition of what human work follows an UNRESOLVED result.

Candidate research questions:

- Who consumes the vendor-neutral export and for what decision/action?
- How does the exporting user identify the intended policy subset?
- Which provenance/evaluation facts must be visible before and after execution?
- What human recovery task follows incomplete technical realization?

## Executable result expected from the fixture

Current downstream providers must not satisfy the pilot consumer immediately.

Expected frontiers:

```text
current NAPMS downstream knowledge
→ CREATE Problem Evidence

+ synthetic Problem Evidence
→ CREATE User Needs for the three subjects

+ synthetic User Needs
→ CREATE Task Models

+ synthetic Task Models
→ CREATE human User Journeys

+ synthetic human User Journeys
→ existing Human Interface + Screen/View providers can satisfy structural closure
```

The synthetic fixtures prove graph behavior only. They deliberately do not convert
the candidate questions above into accepted NAPMS semantics.

## Architectural interpretation

If the executable result passes, the pilot supports three conclusions:

1. existing Harness Core primitives are sufficient to enforce the missing causal
   predecessors;
2. NAPMS currently has real causal knowledge gaps upstream of its existing UI
   artifacts;
3. the first repair should be Discovery/User Needs and Task Model elicitation, not
   more navigation/screen redesign.


## Elicitation pass 1 — source-bounded User Needs candidate

A repository evidence pass found a stronger upstream source than the current UI:
`docs/horizontal/s0/problem-landscape.md` and
`docs/horizontal/s0/user-journeys.md`. These files are explicitly non-canonical,
but their source ledger states that they reconstruct problem/actor/goal material
from accepted `docs/**`. They are therefore useful as **candidate evidence**, not
as accepted User Needs.

Two research artifacts now materialize that distinction:

- `candidate-problem-evidence.yaml`;
- `candidate-user-needs.yaml`.

Neither is registered as a Discovery provider. The executable test uses them only
in a simulated promotion step after first proving that the real current model still
routes `CREATE problem-evidence`.

### Source precedence finding

The horizontal reconstruction is not safe to promote wholesale. Its application
communication S1 material contains the older rule that Interactions are
same-Application only, while current canonical `REQ-INT-001` explicitly rejects a
blanket cross-Application prohibition.

Therefore the candidate contract applies this precedence:

```text
current canonical first-MVP requirements
    > conflicting historical/horizontal candidate detail
```

Horizontal S0 is used only for actor/goal/problem framing.

### Candidate goals and User Needs

**Application / Components**

Goal candidate: capture reusable application communication intent so later
connectivity reasoning can use stable semantic meaning rather than reconstructing
intent from deployment placement/current addresses.

Candidate need:

- express reusable application participants and communication intent independently
  from concrete deployment and current network realization.

**Access Request**

Goal candidate: submit and later explain a concrete connectivity request without
confusing authority to request with the eventual permission outcome.

Candidate needs:

- understand the exact connectivity subject and business basis before submission;
- keep request-authority status and later permission outcome distinguishable and
  explainable for the exact submitted subject.

**Policy Export**

Goal candidate: obtain a complete explainable vendor-neutral projection of selected
current effective policy, or an explicit unresolved result.

Candidate needs:

- select intended current policy scope in domain-policy terms rather than
  vendor/device syntax;
- receive a coherent complete source-neutral result, or explicit unresolved
  diagnostics, with enough evaluation-time/provenance information to explain it.

### Why these are still not accepted

Six blocking questions remain:

1. how a user recognizes an existing Application/Component semantic object to reuse;
2. what information must be available together while defining/changing Components
   and communication intent;
3. what minimum information a requester must inspect before submission;
4. what human recovery differs between authority rejection and a later NotAllowed
   decision;
5. which concrete first-MVP human decision/action consumes the vendor-neutral export;
6. what human recovery follows an UNRESOLVED export and which diagnostics it needs.

These questions affect Task Model structure and information requirements. Treating
the current catalogue/detail/request/export screens as their answers would recreate
the causal inversion the experiment is intended to remove.

The candidate therefore has:

```yaml
status: CANDIDATE_REQUIRES_HUMAN_ACCEPTANCE
sufficiency_review:
  status: UNRESOLVED
```

The next semantic step is human disposition of these questions. Only after that
should the three `user-needs` capabilities be registered and Task Model work become
real rather than simulated.


## Elicitation pass 2 — move unresolved semantics to the correct layer

The first candidate pass classified all unresolved questions as if they blocked User
Needs acceptance. That was too strong.

A second upstream-only evidence pass used the revalidated target requirement
`docs-legacy/requirements/first-mvp-vendor-neutral-policy-export.md`. Its Purpose
states that the first application goal is to establish current effective policy,
inspect one complete vendor-neutral technical policy view and download the same
semantic result for downstream access-list processing.

This resolves the earlier question about the first-MVP human outcome of Policy
Export without reading current UI/navigation.

The remaining questions are all about **how work is performed**, not **why the user
needs the capability**:

- recognize/reuse an existing Application/Component semantic object;
- information required together during Application/Component authoring;
- information inspected before Access Request submission;
- recovery after authority rejection versus NotAllowed;
- recovery after an UNRESOLVED export.

Those are Task Model inputs. They no longer block the User Needs candidate.

The candidate state is therefore now:

```yaml
sufficiency_review:
  status: READY_FOR_HUMAN_ACCEPTANCE
  acceptance_required: explicit human review
task_model_questions: 5
```

This is an important layer correction: accepting User Needs must not require
prematurely deciding task decomposition, interaction grouping or recovery UI.

The candidate is still not registered in Harness. The next action remains a human
semantic review of the three actor/goal pairs and five User Needs. Only after that
acceptance should the Task Model capability become a real CREATE frontier.
