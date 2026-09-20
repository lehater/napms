# Blind backend reconstruction V2 protocol

Status: READY_FOR_FRESH_CONTEXT
Reason: V1 comparison has been opened in the current context; V2 semantic reconstruction must run in a fresh agent/chat context to remain blind.

## Purpose

Repeat the NAPMS backend greenfield reconstruction using Harness main after:
- Artifact Skill routing repair `536cb4e91b9e923673f82786e3662c73636fb081`;
- Source Coverage gate `df1c1c2d53a822d01f2c61a7894eab0dab6e5eae`.

The V2 question is narrower than V1:

> Does mandatory statement-level Source Coverage prevent the source-loss failure observed in V1 while preserving the ability to reach IMPLEMENTATION closure independently?

## Contamination boundary

The V2 executing context MUST NOT read:
- `experiments/blind-backend-2026-09-20/comparison/**`;
- `experiments/blind-backend-2026-09-20/final-experiment-summary.md`;
- any V1 post-freeze findings that reveal old-vs-new differences;
- current canonical/legacy derived NAPMS domain, architecture, API, persistence, security, operability, implementation or verification design.

The current conversation/context is therefore not eligible to execute V2 semantics.

## Allowed source classes

Rebuild the source corpus only from independently evidenced inputs:
- original accepted product/stakeholder requirements and acceptance examples whose provenance establishes source-level status;
- raw stakeholder/discovery evidence;
- explicit current stakeholder instructions;
- externally imposed constraints;
- explicit negative product answers (including NOT_REQUIRED decisions) whose provenance is source-level.

Do not import old solution nouns merely because they appear in mixed documents.

## Mandatory statement-level Source Coverage

Before Product Requirements may be accepted:

1. enumerate every in-scope independently evidenced source statement;
2. split mixed requirement/design sentences when necessary;
3. assign exact-one disposition using Harness `source-coverage-audit`;
4. run `source_coverage.py validate`;
5. require `coverage_status: COMPLETE`;
6. independently reverse-audit original source -> ledger;
7. register project capability `napms.backend.source-coverage`.

Any QUESTION makes downstream product/design work WAIT/PENDING.

## Required Engineering Graph change

Add production:

```yaml
- capability: napms.backend.source-coverage
  knowledge_kind: source-coverage-audit
  requires: []
```

owned by the source/discovery boundary selected for the experiment.

Change product requirement production so:

```yaml
napms.backend.product-requirements:
  requires:
    - napms.backend.problem-evidence
    - napms.backend.source-coverage
```

The exact Authority may be DISCOVERY or PRODUCT-REQUIREMENTS according to the project graph, but source coverage must remain assurance evidence rather than re-own product semantics.

## Final V2 readiness gate

Do not freeze on structural COMPLETE alone.

Required conjunction:

```text
SOURCE COVERAGE COMPLETE
AND
IMPLEMENTATION STRUCTURAL COMPLETE
AND
CODING-AGENT CHALLENGE PASS
```

Additionally:
- no blocking Questions;
- no unrouted CREATE work;
- all implementation-required knowledge kinds have registered Artifact Skills or explicitly justified manual production;
- source-coverage ledger has exact-one disposition for every enumerated source statement.

## Comparison rule

Only after exact V2 freeze may prior NAPMS design and V1 comparison artifacts be opened.

Comparison must classify:
- NEW_BETTER_SUPPORTED
- OLD_BETTER_SUPPORTED
- VALID_DESIGN_FREEDOM
- HARNESS_MISSED_CONCERN
- OLD_UNJUSTIFIED_DECISION
- INPUT_CONTAMINATION
- INSUFFICIENT_SOURCE_INPUT

## Success criterion

V2 succeeds only if the implementation consumer can proceed without substantial upstream semantic decisions **and** post-freeze source comparison finds no available source statement that disappeared during corpus sanitization.

## Execution handoff

Run V2 in a new context with:
- Harness main at or after `df1c1c2d53a822d01f2c61a7894eab0dab6e5eae`;
- NAPMS source access;
- this protocol only as experiment mechanics;
- V1 comparison/final-result artifacts explicitly forbidden until V2 freeze.
