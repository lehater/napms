# Catalogue curation — acceptance scenarios

Status: M7 PILOT CANDIDATE / non-canonical.

These scenarios preserve acceptance intent for the selected Resource Catalogue slice. They are not implementation tests and do not authorize writing or changing tests.

## ACC-CAT-001 — Resource onboarding

Given an admitted catalogue curator, when the curator creates a Resource, establishes its current endpoint/realization and scope affiliation through supported authoring, then the Resource has a stable identity, the accepted temporal facts are visible, and authoring does not require caller-selected internal identifiers.

## ACC-CAT-006 — Address replacement

Given an existing Resource with an effective realization, when an admitted curator replaces the Resource address at an accepted logical time, then Resource identity is unchanged, the previous realization remains historical truth, and the successor realization becomes effective according to temporal semantics.

## ACC-CAT-007 — Responsibility is not authority

Given a person or team recorded as operationally responsible for a Resource, when that actor has no catalogue-curation authority assignment, then the responsibility record alone does not admit a catalogue mutation.

## ACC-CAT-008 — Resource retirement preserves history

Given a Resource referenced by historical catalogue or downstream truth, when it is retired, then it is no longer treated as a new active selection while its stable identity and historical facts remain preservable/readable subject to the applicable read authorization.

## ACC-CAT-009 — Concurrent stale mutation

Given two mutations based on the same current version, when one mutation is accepted first and the other later submits a stale expected version, then the later mutation receives an explicit conflict rather than silently overwriting the accepted change.

## Pilot exclusions

Application/Component/Deployment onboarding, DCS authoring, hierarchy replacement and legacy compatibility migration scenarios remain outside this bounded RC materialization. Their omission here is scope exclusion, not deletion of canonical product truth.