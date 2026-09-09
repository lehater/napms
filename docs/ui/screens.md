# Web UI screen map

Canonical product semantics:
- docs/requirements/web-ui-requirements.md
- docs/requirements/scoped-connectivity-inventory.md

## Login

Input: login + password. Output: authenticated session or generic authentication failure.

After successful login, default navigation goes to Connectivity.

## Connectivity

Primary product workspace.

Purpose: show the selected responsibility scope as a resource-centric connectivity landscape.

Hierarchy:

    Resource
      -> Component Deployment
        -> Connectivity Relationship

Primary row information:

- My Resource;
- current endpoint/address as secondary technical data;
- Component;
- direction relative to local side;
- Access/DCS label;
- optional protocol/ports;
- Remote Component;
- Remote Resource;
- Need summary;
- Decision summary;
- Policy summary;
- Realization later.

Resources/Components with zero connectivity remain visible.

The workspace does not use one generic status.

### Empty/no-connectivity row

Show an explicit state such as:

    No connectivity declared
    + Add connectivity

when the local Component has no relationship.

Do not confuse this with a known remote Component whose Resource realization is unresolved.

### Relationship details

Open in Drawer or bookmarkable route depending depth.

Sections:

- Need;
- Decision;
- Policy;
- Local side;
- Remote side;
- Technical details;
- provenance/history where separately admitted;
- Realization later.

Protected details remain subject to their own backend read contracts.

## Add Connectivity

Contextual workflow launched from a local Component/relationship, not primary navigation.

Known context is prefilled and not re-requested:

- selected scope;
- local Resource;
- local Component.

User selects/supplies:

- remote side;
- structurally valid access/DCS;
- applicability/validity where required;
- business reason/justification.

Trusted catalogue/backend discovery constrains remote/DCS choices.

The user-level action may be Request access or Add connectivity.

Do not show durable Waiting/Under review state until I16A/I16B accepts workflow semantics.

## Needs

Focused Connectivity Requirements workspace.

List:

- readable Source -> Destination;
- access/DCS label;
- dependent participant;
- scope;
- applicability;
- Active | Retired;
- justification summary;
- Covered | Uncovered | NotCurrent | Unknown.

Details:

- stable Requirement ID;
- immutable semantic interaction/dependent;
- scope;
- applicability;
- justification;
- provenance/history;
- independently admitted mutations.

Uncovered does not mean Denied.

## Decisions

Focused final Connectivity Decision workspace.

Purpose:

- inspect final Allowed | NotAllowed Decisions;
- later support decision-participant work only after I16B workflow semantics are accepted.

Decision reason/provenance/detail requires corresponding read authority.

Until implemented, sidebar entry is Planned.

## Rules

Focused Access Policy workspace.

Useful columns:

- readable source deployment;
- readable destination deployment;
- access/DCS;
- governance scope;
- Active | Inactive;
- effective-window summary;
- Rule ID as secondary technical information.

Row opens Rule Details.

## Access Rule Details

Sections:

- readable semantic identity first;
- canonical stable identity second;
- Rule Governance Scope;
- Active | Inactive;
- EffectiveWindow;
- Connectivity Decision correlation;
- proposal/authority/catalogue provenance;
- business history;
- independently admitted mutation actions.

## Effective

Purpose: inspect effective desired policy for one authorized scope and explicit asOf.

Show the user-facing meaning "what desired policy applies for this scope/time".

Authorized empty, denied/unknown and technical failure are distinct.

## Export / normalized policy

Technical/export view over the accepted normalized policy semantics.

Preserve:

- Rule/decision correlation;
- technical realization;
- DCS traffic alternatives;
- asOf;
- provenance.

This need not be a top-level sidebar item.

## Planned technical workspaces

The following may appear only as disabled Planned navigation until backed by implemented use cases:

- Realization;
- Evidence;
- Enforcement.

They must not show fabricated product data.

## Future presentation modes over Connectivity

Architecturally reserve:

    Resources | Services | Graph

Resources is the first implementation.

Services and Graph must reuse the same accepted composition semantics rather than create separate domain truth or incompatible APIs.
