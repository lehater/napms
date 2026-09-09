# Web UI screen map

Canonical product semantics and desktop-first viewport contract: `docs/requirements/web-ui-requirements.md`.

Operational collection screens are table-first at desktop widths. Narrow-screen compatibility preserves the same IA and may use bounded table overflow; it does not require card-per-object redesign.

## Login

Input: login + password. Output: authenticated session or generic authentication failure.

Compact centered form; no external identity controls in I8.

## My Connectivity Needs

Responsibility: list, declare and manage Connectivity Requirements for the authenticated actor's admitted scopes.

List:
- Source -> Destination label-first interaction;
- DCS label;
- Dependent participant;
- Governance Scope;
- Applicability;
- `Active | Retired`;
- justification summary.

Declare:
- server-backed declaration scope;
- bounded ACC interaction search;
- Dependent choice constrained to Source or Destination;
- Ongoing or absolute half-open time window;
- mandatory justification.

Details:
- stable Requirement ID;
- immutable Dependent + Required Semantic Interaction;
- stored Governance Scope;
- Applicability and business history;
- Justification and business history;
- declaration provenance;
- independent Set Applicability / Set Justification / Retire controls when backend capabilities are Permitted.

I14 alignment:
- list and details show `Covered | Uncovered | NotCurrent | Unknown`;
- one explicit `asOf` controls Requirement applicability and Access Rule effective contribution;
- current Retired lifecycle remains `NotCurrent`; I14 does not reconstruct historical aggregate lifecycle;
- `Uncovered` explicitly does not mean `Denied`;
- Rule details/provenance remain hidden in the first slice;
- no configured/observed-access claim is shown.

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

## Connectivity Decisions — planned in I16 after UI quality gate

Responsibility: list/read and directly record final durable Connectivity Decisions admitted for the authenticated actor.

List:
- readable Source -> Destination + DCS subject;
- Decision Governance Scope;
- `Allowed | NotAllowed`;
- validity;
- reason summary;
- deciding principal/time;
- stable Decision ID.

Details:
- immutable Decision identity;
- exact subject and Governance Scope;
- final outcome;
- validity;
- reason/evidence references;
- deciding provenance;
- superseded/superseding Decision relationship where present.

Record:
- admitted Decision Governance Scope;
- exact admitted subject;
- final `Allowed | NotAllowed`;
- required reason and validity;
- optional accepted evidence references;
- backend-owned actor/time/Authority provenance.

No Pending/Approved/Rejected state, approval queue or generic Access Request is shown.

## Planned capability previews

These screens are structural previews only until their owning increments become executable. Every page shows `Preview · Planned Ixx`; unknown semantics remain unspecified.

### Technical Access Evidence — I17

Preview may show:
- evidence collection table;
- source/provenance/time columns;
- accepted evidence kind labels only when already canonical;
- evidence details region.

No ingestion/mutation action is enabled before I17 runtime exists.

### Technical-to-Domain Access Resolution — I18

Preview may show:
- technical predicate input/evidence context;
- resolved domain-interaction result area;
- unresolved/ambiguous explanation region only using statuses accepted by I18 semantics.

Do not pre-invent the resolution algebra.

### Network Enforcement Placement — I19

Preview may show:
- domain traffic context;
- logical firewall/enforcement placement result region;
- path/placement provenance sections whose exact content follows I19 semantics.

No vendor/device identity is substituted for Logical Firewall meaning.

### Reconciliation / Enforcement Policy — I20

Preview may show a desktop comparison workspace:
- desired policy region;
- configured technical evidence region;
- reconciliation result/delta region;
- provenance/explanation region.

Do not invent add/remove/replace classifications before I20 accepts them.

### Configuration Rendering — I21

Preview may show:
- accepted vendor-neutral enforcement intent input;
- target selection area;
- rendered artifact/code region;
- provenance/equivalence result region.

Render/apply actions remain unavailable before concrete adapters exist.

### Network Operations — I22

Preview may show:
- target/current-state context;
- pre-check/apply/post-check execution structure;
- execution result/audit area.

No fake successful execution or rollback semantics are displayed.

### Enterprise Sources — I23

Do not expose a generic administration screen merely because I23 exists. Add a preview only when the concrete enterprise identity/catalogue/source integration produces an accepted human/operator workflow.

### Product completion surfaces — I25

Potential preview targets:
- global explainability/audit navigation;
- mature search/filtering;
- bounded bulk operations;
- role-appropriate workspaces;
- Dashboard only after real aggregate/read-model semantics exist.

## Deferred

Dashboard, cross-entity Audit Log, portfolio administration and approval/review queue screens remain deferred until concrete product use cases/canonical semantics require them.
