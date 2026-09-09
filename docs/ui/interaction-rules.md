# Web UI interaction rules

Canonical product/viewport contract: `docs/requirements/web-ui-requirements.md`.

## Operator-efficiency baseline

NAPMS is optimized for repeated desktop operational work.

Therefore:
- keep high-frequency navigation/actions visible on desktop;
- prefer compact list/detail workflows over wizard-heavy interaction when the domain does not require a wizard;
- avoid unnecessary modal hops for ordinary read/navigation tasks;
- preserve stable screen locations for repeated controls;
- use readable names first while keeping stable technical IDs/provenance available;
- do not inflate spacing/cards at the cost of useful comparison density.

No mandatory keyboard-shortcut scheme is required yet, but all primary workflows must be keyboard operable.

## URL state

Shareable list/query state should be encoded in the URL where reasonable:
- page;
- sort;
- filters;
- search;
- selected scope/asOf;
- stable detail identity.

Reload/back/forward should not silently lose meaningful read-context state where a bookmarkable URL is practical.

## Tables

- server-side pagination for potentially unbounded collections;
- server-side sort/filter when server-paginated;
- use a table as the default when multiple objects are compared across multiple attributes;
- one dominant row/details destination;
- secondary actions use explicit row controls/menus;
- contain horizontal overflow inside the table region;
- do not convert dense operational tables into card grids solely for mobile;
- never hide an admitted critical action without providing another reachable control.

## Forms

- validate obvious structural constraints client-side;
- server/domain remains authoritative;
- field errors appear near fields;
- request-level errors appear in a form alert;
- prevent duplicate submit while mutation is pending;
- labels remain visible; placeholder-only labelling is insufficient.

Composition selectors should prefer valid backend-provided choices over free-form IDs.

## Mutations

Safe/reversible admitted actions may execute directly with operation feedback. Security-significant/destructive actions require confirmation when accidental execution is plausible.

After successful mutation, the durable resulting state must remain correct after page reload.

## Loading/refresh

- initial data: skeleton/table loading state;
- mutation: control-level loading;
- safe background refresh: retain old data and indicate refresh subtly;
- loading states must not cause major layout shifts that obscure the user's working context.

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

## Responsive compatibility

- desktop layout is authoritative for information architecture;
- tablet/mobile preserve the same destinations and semantics;
- narrow navigation uses an off-canvas/collapsed shell, not a second mobile taxonomy;
- document-level horizontal overflow is prohibited;
- dense table/technical regions may scroll horizontally inside their own bounds;
- mobile compatibility does not require complex operational analysis/bulk workflows to become card-first.

## Accessibility and browser quality

Target WCAG 2.2 AA:
- keyboard navigation;
- visible focus;
- semantic labels/names;
- accessible overlays;
- sufficient contrast;
- no color-only status.

Quality checks include default/hover/focus/active and animated/intermediate visual states.

Playwright should use roles/labels for primary interaction. Missing accessible names are UI defects, not reasons to add opaque test IDs.
