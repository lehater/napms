# UI presentation knowledge pilot

Status: research evidence  
Branch: `research/ui-presentation-knowledge-pilot`  
Pinned Harness runtime used by this pilot: `308a61f98ab569d694d3149192c92523c2bf3e45`; current Harness research branch head: `fad6ab83d89a9220b7cc04a3a4efe6367ba688aa` (`research/ui-presentation-coverage`).

## Question

Can the existing Harness Authority/Capability/Consumer model distinguish a frontend
that merely has UI design documents from one whose accepted engineering knowledge is
sufficient to reproduce material presentation and screen composition?

The pilot intentionally keeps modern First-MVP product/domain/API semantics authoritative.
Historical NAPMS UI material is used only as presentation evidence.

## Negative control

Pinning the presentation-coverage Harness experiment without changing NAPMS design
knowledge caused frontend Engineering Coverage to stop reporting complete while backend
coverage remained valid.

After adding only semantic-claim bindings, with no stronger design knowledge or
semantic evidence, the three new concerns remained:

- `interface.human.presentation-system` -> `MISSING / VALIDATE_SEMANTICS`
- `interface.human.screen-composition` -> `MISSING / VALIDATE_SEMANTICS`
- `verification.interface.presentation` -> `MISSING / VALIDATE_SEMANTICS`

The evaluator explicitly reported that provider existence alone is insufficient. This
falsifies the previous closure behavior where a present frontend artifact could indirectly
stand in for material presentation completeness.

## Canonical knowledge added by the pilot

### Presentation System

`docs/contracts/ui/mvp-presentation-system.yaml` now records:

- explicit precedence of modern semantic authority over historical presentation evidence;
- epistemic roles for PNG/SVG/documentation/executable reference sources;
- an immutable `main` reference commit for executable presentation evidence;
- material layout/geometry invariants;
- controlled implementation freedom;
- reusable AppShell, Catalogue, Detail and DataTable anatomy;
- canonical DTCG token source and generated-artifact boundary.

### Design tokens

`docs/contracts/ui/mvp-design-tokens.json` is a typed DTCG 2025.10 representation with:

- primitive color/spacing/radius values;
- semantic aliases;
- typography composites;
- component-level shell/control/table geometry for accepted material invariants.

It is an INTERFACE-DESIGN support artifact and does not create another public capability.

### Screen/View composition

`docs/contracts/ui/mvp-screen-view-design.yaml` now contains explicit ordered
composition for every First-MVP workspace.

The Resource Catalogue reference slice additionally records adopted and non-adopted
properties. In particular, legacy search/filter/sort/paging/selection/Resource-type
affordances are not imported because current `listResources` semantics do not authorize
them. The accepted reference still constrains shell geometry, hierarchy, density and
table-first visual language.

### Verification Design

`docs/plans/mvp-frontend-verification.yaml` now requires independent evidence for:

- canonical-token integrity;
- pattern/screen composition;
- geometry invariants;
- screenshot visual regression;
- deterministic rendering environment;
- responsive viewport matrix;
- interaction/focus states;
- reference-conformance dispositions.

A screenshot baseline is evidence of accepted presentation knowledge, not authority to
change that knowledge.

## Semantic acceptance

`tools/evaluate_frontend_presentation_semantics.py` provides deterministic project-native
semantic acceptance for:

- `engineering.frontend.presentation-system`;
- `engineering.frontend.screen-view-design`;
- `engineering.frontend.presentation-verification`.

The validator checks token references, material invariants, reference boundaries,
reusable pattern anatomy, all screen compositions and the presentation verification
contract.

The narrow `engineering.frontend.presentation-verification` capability was introduced
because presentation verification is independently provable. It is co-materialized by
the existing `FRONTEND-VERIFICATION` artifact and consumed by Test Design. This avoids
pretending that a presentation-specific semantic evaluation also proves every broad
verification claim.

## Positive control

After canonical presentation knowledge and deterministic semantic acceptance were added:

- Unified Harness Integration passed;
- `design-check` passed with presentation semantic acceptance enabled;
- Engineering Coverage passed with the generated semantic-evaluation set;
- the new presentation concerns no longer appeared in remaining work.

No new Harness Core entity or parallel frontend graph was required.

## Epistemic result

The pilot supports this boundary:

```text
modern product/domain/application/interface truth
        ↓ constrains
canonical Human Interface
        ↓
canonical Presentation System + typed tokens
        ↓
canonical Screen/View composition
        ↓
Verification/Test Design
        ↓
implementation
        ↓ evidenced by
browser/geometry/screenshot/accessibility results
```

Historical images and executable UI can be `EVIDENCED_BY` / derivation provenance for
presentation decisions. They do not become product/domain authority.

## What this pilot does not prove

The current `implementation/first-mvp-rebuild` WebUI has not been migrated to these
presentation contracts by this research branch.

Therefore this pilot does **not** claim:

- current React/CSS visually matches the Resource Catalogue references;
- canonical DTCG tokens are already materialized into production CSS;
- required screenshot/geometry/browser presentation tests already exist;
- all implementation evidence is green.

Those are the next implementation/materialization stage, not reasons to weaken design
knowledge closure.

## Next stage

1. Promote the generic Harness presentation concerns/strict-proof behavior after review.
2. Adopt the NAPMS canonical presentation knowledge without importing legacy domain semantics.
3. Generate CSS/TypeScript token materializations from canonical DTCG data.
4. Migrate AppShell, generic controls and Resource Catalogue/Detail presentation first.
5. Add deterministic geometry + screenshot + responsive + accessibility evidence.
6. Require those implementation checks before claiming the implemented frontend conforms
   to the accepted presentation intent.
