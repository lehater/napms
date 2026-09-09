# Web UI interaction rules

## URL state

Shareable workspace/query state should be encoded in the URL where reasonable:

- selected responsibility scope;
- search;
- filters;
- sort;
- page;
- explicit asOf;
- optional selected relationship.

Do not encode trusted actor identity or authority claims in client state.

## Scope switching

Changing the selected responsibility scope changes the local/my-side context for Connectivity.

Requirements:

- current scope remains visible;
- switching scope is deliberate;
- stale rows from the previous scope are not presented as current data;
- the backend re-evaluates all relevant admissions;
- scope switching does not imply global visibility changes for remote catalogue data in the current baseline.

## Connectivity tree-grid

- Resource -> Component -> Connectivity hierarchy;
- Resource/Component rows remain visible even when no relationship exists;
- expansion/collapse is keyboard accessible;
- group rows are not duplicated merely to satisfy a flat table abstraction;
- potentially unbounded data uses server-side paging/search/filter as required;
- background refresh retains current data and indicates refresh subtly;
- row selection/detail navigation does not interfere with expand/collapse controls.

## Direction

Direction is presented relative to local/my side.

Canonical Source/Destination identities are available in details but are not required primary columns.

## Technical columns

Default view favors semantic access labels.

Protocol, ports, stable IDs and additional endpoint details are exposed through secondary text/details/column chooser.

Column preferences are presentation state and may be stored locally.

## Add Connectivity

Launch from the local Component/relationship context.

Known context must not be re-entered:

- selected scope;
- local Resource;
- local Component.

The user chooses missing intent only:

- remote side;
- structurally valid DCS/access;
- applicability/validity where required;
- reason/justification.

Trusted remote/DCS choices come from backend discovery/validation.

Prevent duplicate submit while a mutation is in flight.

Do not persist/display Waiting/Under review as business state until accepted workflow semantics exist.

## Empty and unresolved states

Distinguish:

1. local Resource with no Components;
2. local Component with no connectivity;
3. known interaction with unresolved remote Resource realization;
4. known Requirement with Uncovered policy;
5. authorized collection genuinely empty;
6. current filters matching nothing;
7. authorization-limited/protected detail;
8. retryable technical failure.

A known remote Component with unresolved Resource realization is not "no connectivity".

## Protected details

Global catalogue visibility does not grant global Requirement/Decision/Rule detail access.

When the overview exposes a coarse status:

- show only the accepted coarse result;
- do not reveal protected reason/provenance/IDs unless the corresponding read use case admits it;
- use explicit unavailable/restricted presentation where needed rather than silently leaking data.

## Forms

- validate obvious structural constraints client-side;
- server/domain remains authoritative;
- field errors appear near fields;
- request/domain errors appear in a form alert;
- transport/authentication errors remain distinct;
- prevent duplicate mutation submission.

## Mutations

Safe/reversible admitted actions may execute directly with operation feedback.

Security-significant or destructive actions require confirmation when accidental execution is plausible.

Ownership/responsibility display never substitutes for backend action admission.

## Loading/refresh

- initial inventory: hierarchical skeleton/loading state;
- mutation: control-level loading;
- safe refresh: retain previous data and indicate refresh;
- scope change: do not present old-scope data as current.

## Errors and semantic outcomes

Do not collapse business outcomes into transport status:

- invalid composition -> form/domain feedback;
- 401 -> login/session recovery;
- 403 -> explicit access denied;
- 404 -> not found;
- stale/conflict -> explain recovery where known;
- 5xx/network -> retryable technical failure;
- ConnectivityDecision.NotAllowed -> valid business result;
- Alignment.Uncovered -> policy coverage gap, not denial;
- unresolved remote realization -> catalogue/resource uncertainty, not missing connectivity.

## Accessibility

Target WCAG 2.2 AA:

- keyboard-operable tree-grid and overlays;
- visible focus;
- semantic labels;
- accessible expanded/collapsed state;
- sufficient contrast;
- status text/icons in addition to color;
- directional meaning not encoded by icon alone.
