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
