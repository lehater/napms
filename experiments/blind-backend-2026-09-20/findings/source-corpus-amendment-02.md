# Source Corpus amendment 02 — no blanket same-Application invariant

Priority: P1  
Status: CLOSED BY RECLASSIFICATION / downstream repaired

## Failure

The first blind sanitization retained the existence of Application, Component and directed Interaction, but omitted a negative acceptance constraint from the admitted pre-implementation Wave-1 acceptance baseline:

> structural validity follows the explicitly described directed interaction and valid Component references; no additional blanket same-Application invariant is introduced.

The blind Tactical/API/Data design then incorrectly made Interaction a child of one Application and rejected source/destination Components from different Applications.

## Evidence

Allowed source:
- bootstrap commit `c403ceeda2837d8956e3d093fef95c1bd69d0c6f`;
- `docs/requirements/wave1-acceptance-examples.md`;
- accepted specification-by-example baseline, example E1.

Only the observable negative constraint was re-admitted. Existing NAPMS domain/architecture/API implementation was not inspected or used.

## Repair

Application Communication now contains two independent aggregates:

- Application -> Components;
- Interaction -> immutable InteractionRevisions.

Interaction references two valid ComponentRefs and may cross Application boundaries.

Consequences:
- Interaction creation writes no Application aggregate;
- Application ETag guards Component creation only;
- Interaction ETag guards revision publication;
- persistence has no `interaction.application_ref` and no same-Application constraint;
- API uses `POST /v1/interactions` rather than nesting Interaction below Application;
- coding/tests must prove cross-Application Interaction succeeds.

## Prevention rule

Negative acceptance constraints such as “must not require X” are SOURCE_INPUT when they constrain observable valid/invalid behavior, even if they mention nouns later used in domain modeling.
