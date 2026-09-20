# Blind greenfield backend reconstruction experiment — final result

Date: 2026-09-20  
Repositories: `lehater/harness`, `lehater/napms`  
Blind reconstruction frozen semantic snapshot: `ac6c2e1c17b50a62abd3320c4e4cb6cbbaf129ba`  
Replacement freeze marker commit: `dcfcfb5fac816f45b340e6a7a0ae987cef20106d`  
Harness repair merged to main: `536cb4e91b9e923673f82786e3662c73636fb081`

## Research question

Can current Harness, given only source problem/evidence/requirements/stakeholder/external constraints, independently construct a backend design sufficient for IMPLEMENTATION without forcing a coding agent to make substantial upstream decisions?

## Short answer

**Partially yes, but not yet reliably enough for an unconditional pass.**

Harness + agent reconstructed a substantially complete backend design and corrected several unsupported decisions in the prior NAPMS target. The frozen closure passed structural Harness evaluation and repeated Coding-Agent Challenges.

However post-freeze comparison discovered that one material accepted source requirement — effective request/export authority scoped by relevant scope/time — had been available in the original Wave-1 source but was dropped during source sanitization. Because downstream design saw an incomplete Source Corpus, the implementation closure falsely accepted instance-wide authorization.

That is a P1 experiment failure.

## What succeeded

### 1. Engineering Graph / Authority decomposition

The experiment successfully expressed the backend knowledge flow through ordinary Harness primitives:
- Authorities;
- Capability prerequisites;
- CanonicalArtifacts;
- Questions;
- IMPLEMENTATION consumer closure.

No new Core entity or evaluator rule was needed.

The frozen graph evaluates:
- `status = COMPLETE`;
- `create = []`;
- `wait = []`;
- `pending = []`;
- 28 capabilities in IMPLEMENTATION closure.

### 2. Blind design quality

Without opening old derived NAPMS design before freeze, reconstruction independently produced:
- strategic domain ownership;
- tactical models;
- application orchestration;
- modular-monolith/system topology;
- security architecture;
- HTTP API;
- PostgreSQL persistence;
- concurrency/idempotency/snapshot semantics;
- operability;
- engineering policy;
- component design;
- verification/test design;
- implementation plan/completion criteria.

### 3. Coding-agent closure pressure worked

Repeated Coding-Agent Challenges exposed material gaps after structural COMPLETE, including:
- source-vs-design confusion;
- cross-Application semantics;
- Access Rule identity/lifecycle;
- provenance completeness;
- traffic/address canonicalization;
- idempotency replay;
- materialization snapshot time;
- JWT/JWKS lifecycle;
- migration execution semantics;
- response commitment/stream failure.

This proves implementation-consumer challenge is a valuable semantic gate.

### 4. Blind reconstruction corrected old NAPMS design

Post-freeze comparison found multiple old target decisions unsupported or contradicted by original source:
- same-Application-only Interactions;
- one Interaction per directed Component pair;
- PolicyRule existing before Allowed permission;
- Rule identity by deployment pair with mutable effective revision;
- omission of reversible Active/Inactive;
- omission of effective-window semantics;
- omission of participant-attributed Needs;
- omission of multi-Need justification/reconciliation;
- compression of logical Resource endpoint identity;
- omission of domain-policy subset selection;
- weak self-contained export provenance.

So the blind process was not merely reproducing old design.

## What failed

### P1 — Source Corpus preservation/classification

The original Wave-1 baseline explicitly contains:
- request authority for relevant scope/time;
- read/export authority for selection;
- end-to-end provenance including effective authority scope/time.

The sanitized Source Corpus retained the distinction between request authority and permission decision, but discarded the scope/time part.

Result:
- Security Architecture selected instance-wide permissions;
- Coding-Agent Challenge saw a self-consistent but semantically incomplete input set;
- final blind freeze incorrectly claimed full semantic sufficiency.

Classification:
- `HARNESS_MISSED_CONCERN`;
- source-corpus under-classification;
- false semantic closure.

This is **not** `INSUFFICIENT_SOURCE_INPUT`: the source existed.

### P2 — Source answer about numeric quality targets was lost

External product input from 2026-09-19 explicitly states numeric latency/throughput/availability/scale targets are not required for first MVP.

Blind corpus did not admit it and left these as DEFERRED_NONBLOCKING.

No current coding decision was blocked, but the source corpus was still incomplete.

### P1 — Artifact Skill routing coverage

Unchanged Harness could structurally evaluate the graph COMPLETE but eight knowledge kinds were unrouted:
- strategic-domain-design;
- domain-use-case;
- application-design;
- quality-design;
- security-architecture;
- data-design;
- operability-design;
- security-analysis.

Five corresponding reusable Artifact Skills were absent; three existed but were not registered.

This defect was repaired and merged to `harness/main` without changing Core evaluator semantics.

## What did not fail

### No meaningful input contamination

No old derived NAPMS design was deliberately opened before replacement freeze.
The known repository-search snippet exposure was recorded and excluded unless independently supported by source provenance.

Post-freeze old design access remained comparison-only.

### No Core-model deficiency demonstrated

Authority/Capability/Artifact/Question + Engineering Graph were sufficient to represent all discovered backend knowledge dependencies.

The primary failures were:
- source classification procedure;
- Artifact Skill coverage;
- semantic completeness gating.

No new Core ontology is justified by this experiment.

## Harness changes already justified and merged

Merged:
- five missing Artifact Skills:
  - strategic-domain-design;
  - domain-use-case;
  - application-design;
  - quality-design;
  - data-design;
- registry routes for all eight missing knowledge kinds.

Validation:
- generic `make harness-check`: PASS;
- frozen NAPMS graph/Core: PASS;
- IMPLEMENTATION: COMPLETE;
- previously unrouted knowledge kinds: 8/8 routed.

## Harness changes still required before repeating the experiment

### P0/P1 — Source-preservation gate

Harness needs an explicit source-corpus audit procedure before design begins.

Required behavior:
1. enumerate all independently evidenced source artifacts;
2. classify at statement/granularity level, not whole-file level;
3. distinguish:
   - observable requirement;
   - design vocabulary embedded inside a requirement;
   - provenance metadata;
4. when sanitizing, preserve every independently observable constraint even if surrounding exact identity/model language is excluded;
5. generate a loss report:
   - source statement;
   - admitted sanitized statement or explicit exclusion reason;
6. require bidirectional traceability from admitted Source Corpus back to original source statements;
7. run a second independent source-loss review before final Source Corpus freeze.

The scope/time authority miss is exactly the class this gate must catch.

### P1 — Semantic closure must include source-coverage evidence

A target must not be called semantically implementation-ready solely because:
- Graph evaluates COMPLETE;
- all artifacts exist;
- Coding-Agent Challenge finds no downstream choices.

It must also establish:
- source corpus completeness for the selected scope;
- every accepted source statement has an admitted/routed disposition;
- no source-level constraint disappeared during sanitization.

### P1 — Final blind gate should be two-dimensional

Recommended final readiness condition:

```text
IMPLEMENTATION STRUCTURAL COMPLETE
AND
SOURCE COVERAGE COMPLETE
AND
CODING-AGENT SEMANTIC CHALLENGE PASS
```

Each gate catches a different failure class.

### P2 — Explicit evidence for DEFERRED_NONBLOCKING

When a source answer says a target is explicitly NOT_REQUIRED, preserve that answer.
Do not downgrade known negative product truth into generic unknown/deferred state.

## Recommended Harness model impact

Do **not** add a new Core entity.

Implement source preservation as:
- reusable Artifact Skill / analysis procedure;
- source-classification artifact contract;
- validator/lint over source-disposition mapping;
- optional Engineering Graph capability such as project-specific `source-coverage`, when the project requires blind/reconstruction assurance.

The Core model can already express that capability and make it a prerequisite for Product Requirements / terminal readiness where needed.

## Final experiment verdict

### Harness Core
PASS for representational sufficiency.

### Engineering Graph / prerequisite model
PASS with the important qualification that graph correctness cannot detect facts omitted before graph construction.

### Authority decomposition
PASS. No material ownership failure required a new Authority.

### Artifact Skills
FAIL at experiment start; repaired and merged.

### Backend design generation
STRONG PARTIAL PASS. The blind design is broad, coherent and in many areas better source-supported than the old target design.

### Source-corpus reconstruction
FAIL at P1 because available authorization scope/time semantics were lost.

### IMPLEMENTATION semantic sufficiency claim
FAIL as an unconditional claim for the frozen snapshot because of the source-corpus miss.

### Overall research result
**Harness is close to supporting blind greenfield backend reconstruction, but the missing source-preservation/coverage gate is a blocking methodological defect.**

The next high-value step is not more NAPMS backend design. It is to add and validate Source Coverage closure in Harness, then repeat the blind reconstruction from the original source corpus in a fresh branch/experiment and verify that scoped authorization is recovered without looking at this comparison result.
