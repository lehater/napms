# Harness findings — blind backend reconstruction

## H-FIND-001 — P1 — incomplete Artifact Skill routing/coverage

### Failure

The blind Engineering Graph naturally requires the following knowledge kinds before IMPLEMENTATION closure:

- strategic-domain-design
- domain-use-case
- application-design
- quality-design
- security-architecture
- data-design
- operability-design
- security-analysis

Current Harness `skills/artifact-skill-registry-v0.yaml` has no routes for any of them.

Repository inspection shows:
- reusable Skills exist for `security-architecture`, `operability-design`, and `security-analysis`, but the registry does not route those kinds;
- no dedicated artifact Skill was found for `strategic-domain-design`, `domain-use-case`, `application-design`, `quality-design`, or physical `data-design`.

### Reproduction

Given the blind Engineering Graph and an empty/partial Core realization:
1. derive the IMPLEMENTATION target;
2. reach any CREATE frontier for one of the knowledge kinds above;
3. run the current agent router against the current registry.

Expected for a self-guided reusable Harness path: actionable CREATE is routed to the procedure that defines inputs/read boundary/stop conditions/output/acceptance.

Actual: `NO_REGISTERED_SKILL`.

### Why this is a Harness defect

Harness documentation explicitly allows manual fallback, so Core topology remains usable. However the experiment is testing whether Harness can independently reproduce backend design with reliable Authority/Capability/Artifact-Skill discipline. Major semantic/technical design classes fall out of the reusable skill path and therefore depend on ad-hoc agent judgment.

This is not NAPMS-specific:
- strategic/tactical/application/data/security/operability concerns recur across non-trivial backend products;
- three procedures already exist but are unreachable through the registry;
- the missing classes sit directly on the IMPLEMENTATION closure.

### Workaround used in this blind run

Use the current Engineering Graph production contract plus the current reference Authority catalog and any applicable analysis Skills manually. Do not modify Harness before freeze.

### Proposed post-failure experiment

After blind freeze, in a separate Harness research branch:
1. add missing registry routes where the Skill already exists;
2. develop the smallest dedicated Skills only for knowledge kinds whose blind-run work demonstrates repeatable inputs/stop/output semantics;
3. add router acceptance coverage over a non-trivial backend graph;
4. replay this same reconstruction frontier.

No Harness change is made during the blind run.
