# Web UI screen map

Canonical product semantics: `docs/requirements/web-ui-requirements.md`.

## Login

Input: login + password. Output: authenticated session or generic authentication failure.

Compact centered form; no external identity controls in I8.

## Compose Connectivity

Responsibility: produce one structurally valid `Access Rule Proposal` from trusted references.

Inputs:
- authorized scope/context;
- Source Component Deployment;
- Destination Component Deployment;
- compatible immutable DCS contract/revision.

The UI should progressively constrain destination/DCS choices using backend-provided valid options. Users do not enter firewall addresses/protocol/ports/vendor syntax.

I12 presentation:
- Source/Destination/DCS display labels are primary when available;
- stable UUIDs remain visible/fallback;
- bounded search is server-side;
- DCS options show decoded immutable protocol/service/port summary.

Submit result:
- `Allowed` -> authoritative Access Rule summary/link;
- `NotAllowed` -> explicit no-Rule business outcome;
- other semantic/transport failures -> dedicated error presentation.

## Access Rules

Responsibility: list authoritative Rules admitted for the authenticated actor/context.

Useful columns when available:
- Rule ID;
- source deployment;
- destination deployment;
- DCS revision/reference;
- governance scope;
- operational state;
- EffectiveWindow summary.

Source/Destination/DCS cells render optional catalogue labels first and stable technical IDs second. Row opens Rule Details.

## Access Rule Details

Responsibility: inspect identity, operational properties and traceability.

Sections:
- immutable semantic identity;
- Rule Governance Scope;
- `Active | Inactive`;
- EffectiveWindow with independent SetRuleEffectiveWindow admission;
- set/change/clear EffectiveWindow controls when permitted;
- EffectiveWindow business history;
- Connectivity Decision correlation/reference;
- proposal/authority/catalogue provenance;
- business history;
- admitted mutation actions.

Use progressive disclosure for low-frequency provenance detail. Semantic identity fields show catalogue labels first and stable IDs second; labels never replace identity.

## Effective Policy

Responsibility: run/view `SelectEffectiveDesiredPolicy(scope, asOf, actor)`.

Inputs: one Rule Governance Scope + explicit offset-aware `asOf`.

Scope discovery is evaluated for the same `asOf`; ambiguous scopes remain fail-closed. Denied/unknown authority returns no policy data and is presented distinctly from an authorized empty result. Rule rows use the same label-first catalogue presentation as Access Rules.

## Normalized Policy

Responsibility: present vendor-neutral normalized policy for an accepted export journey.

Preserve Rule/decision correlation, technical realization, DCS traffic alternatives, export `asOf` and required provenance. Presentation renders `Any`, `NotApplicable` and inclusive ranges distinctly and exposes Rule/Authority/ACC/RC provenance without flattening it. Optional catalogue labels supplement, but never replace, technical addresses and semantic IDs.

## Deferred

Dashboard, cross-entity Audit Log, portfolio administration and approval/review screens are not part of the first I8 UI increment.
