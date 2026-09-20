# Coding-Agent Challenge 03

Status: FAILED — two P1 repairs required

## CAC-007 — P1 — PolicyRule version semantics incomplete for ALLOWED evidence append

An existing PolicyRule may receive a new AuthorizationEvidence when another AccessRequest with the same AccessSubject becomes ALLOWED.

The closure defines PolicyRule ETag/version for operational and justification mutation, but did not say whether adding authorization evidence changes the Rule aggregate version.

A coding agent therefore had to choose between:
- leaving ETag unchanged while the Rule representation/evidence set changed; or
- incrementing Rule version without an explicit concurrency contract.

Required repair:
- PolicyRule version represents mutation of the entire Rule aggregate, including authorization evidence and justification association sets;
- new Rule with initial evidence/justification starts at version 1;
- adding new AuthorizationEvidence to existing Rule increments Rule version exactly once for that ALLOWED transaction, regardless of whether initial Need association was already present;
- attaching a new justification also increments version;
- actual operational change increments version + operational-history row;
- semantic no-op operational/duplicate association does not increment;
- ALLOWED append never resets operational state/window;
- concurrency test covers ALLOWED evidence racing access.manage.

## CAC-008 — P1 — public/source-fact provenance shape underspecified

Several accepted artifacts used an untyped `provenance` / `realizationProvenance` field. A coding agent had to invent its JSON/data representation and which actor/time is preserved.

Required repair for API-created MVP facts:
- Resource address history: explicit `effectiveFrom/effectiveTo` + `changedBySubject`;
- InteractionRevision: explicit `createdAt + createdBySubject`;
- ConnectivityNeed: explicit `createdAt + createdBySubject`, plus retiredAt when retired;
- current policy realization rows: explicit address effectiveFrom + addressChangedBySubject;
- AccessRequest/decision/Rule evidence/history already have explicit actor/time and remain unchanged;
- remove generic free-form provenance fields from external/persistence contracts.

No generic extensible provenance JSON is introduced without an accepted external-source/import requirement.

## Result

Freeze remains prohibited until these repairs propagate through Data/Interface/Component/Verification/Test/Implementation and Challenge 04 finds no P0/P1 residual design decision.
