# Web UI interaction rules

## URL state

Shareable list/query state should be encoded in the URL where reasonable: page, sort, filters, search, selected scope/asOf when appropriate.

## Tables

- server-side pagination for potentially unbounded collections;
- server-side sort/filter when server-paginated;
- row click for a single dominant details destination;
- row action menus only for secondary actions.

## Forms

- validate obvious structural constraints client-side;
- server/domain remains authoritative;
- field errors appear near fields;
- request-level errors appear in a form alert;
- prevent duplicate submit while mutation is pending.

Composition selectors should prefer valid backend-provided choices over free-form IDs.

## Mutations

Safe/reversible admitted actions may execute directly with operation feedback. Security-significant/destructive actions require confirmation when accidental execution is plausible.

## Loading/refresh

- initial data: skeleton/table loading state;
- mutation: control-level loading;
- safe background refresh: retain old data and indicate refresh subtly.

## Empty states

Distinguish:
1. authorized collection genuinely empty;
2. current filters matched nothing;
3. no objects/actions are visible in the authenticated authority context.

## Errors and semantic outcomes

Transport/authentication presentation must not collapse domain outcomes:
- validation/invalid composition -> field/form/domain feedback;
- `401` -> login/session recovery;
- `403` -> explicit access denied;
- `404` -> not found;
- `409` or semantic stale/conflict -> explain current state/recovery where known;
- `5xx`/network -> retryable technical failure;
- `ConnectivityDecision.NotAllowed` -> valid business result, not an HTTP/security error.

## Accessibility

Target WCAG 2.2 AA for applicable behavior: keyboard navigation, visible focus, semantic labels, accessible overlays, sufficient contrast, no color-only status.
