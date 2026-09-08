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

Row opens Rule Details.

## Access Rule Details

Responsibility: inspect identity, operational properties and traceability.

Sections:
- immutable semantic identity;
- Rule Governance Scope;
- `Active | Inactive`;
- EffectiveWindow;
- Connectivity Decision correlation/reference;
- proposal/authority/catalogue provenance;
- business history;
- admitted mutation actions.

Use progressive disclosure for low-frequency provenance detail.

## Effective Policy

Responsibility: run/view `SelectEffectiveDesiredPolicy(scope, asOf, actor)`.

Inputs: one Rule Governance Scope + explicit offset-aware `asOf`.

Denied/unknown authority returns no policy data and is presented distinctly from an empty authorized result.

## Normalized Policy

Responsibility: present vendor-neutral normalized policy for an accepted export journey.

Preserve Rule/decision correlation, technical realization, DCS traffic alternatives, export `asOf` and required provenance. Presentation must not silently flatten `Any`, `NotApplicable`, ranges or provenance distinctions.

## Deferred

Dashboard, cross-entity Audit Log, portfolio administration and approval/review screens are not part of the first I8 UI increment.
