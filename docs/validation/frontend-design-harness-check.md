# Frontend Design Validation — NAPMS

Status: validation evidence only; not canonical product/design truth.

Branch purpose: test the current Harness frontend-design model against NAPMS without changing `main`.

## Validation method

The frontend was reconstructed first from current canonical product/domain/application/security/machine-interface knowledge.

Existing UI contracts, legacy UI requirements and frontend implementation were treated only as comparison evidence after the blind design boundary was established.

Primary upstream inputs:
- `docs/requirements/first-mvp-product-requirements.yaml`;
- `docs/model/use-cases/first-mvp-policy-export.yaml`;
- selected tactical domain models;
- `docs/architecture/mvp-module-contracts.yaml`;
- `docs/architecture/mvp-security-architecture.yaml`;
- `docs/architecture/mvp-quality-requirements.yaml`;
- `docs/contracts/http/napms.openapi.yaml`.

## Blind user-facing journey

The first-MVP frontend can be derived as one main end-to-end journey:

1. **Describe Resources**
   - create Resource with stable identity and immutable AuthorityScopeRef;
   - add logical Endpoints;
   - set/replace/clear current HostAddress or Prefix;
   - preserve current/history distinction.

2. **Describe application communication**
   - create Applications and Components;
   - create directed Interactions;
   - publish immutable InteractionRevisions with exact traffic semantics.

3. **Describe deployment**
   - create concrete ComponentDeployments binding Components to Resources.

4. **Describe business justification**
   - create BusinessProcess;
   - create participant-attributed ConnectivityNeed;
   - keep Need/business justification distinct from permission/authority.

5. **Submit and decide access request**
   - select exact source/destination deployments, immutable interaction revision and Need;
   - submit under scoped `access.request` authority;
   - record ALLOWED or DENIED;
   - DENIED creates no PolicyRule.

6. **Manage current desired access**
   - inspect the resulting PolicyRule;
   - set ACTIVE/INACTIVE and optional EffectiveWindow;
   - attach additional current Needs without duplicating the Rule.

7. **Materialize/export policy**
   - select all Rules or an explicit subset;
   - backend evaluates scoped `policy.export` authority;
   - receive one coherent `COMPLETE` or `UNRESOLVED` result;
   - table/CSV are projections of the same backend-owned materialization result.

## Blind information architecture

Six top-level workspaces are sufficient for the selected first-MVP scope:

1. **Resources**
2. **Applications**
3. **Business Connectivity**
4. **Access Requests**
5. **Current Access**
6. **Policy Export**

Concrete deployments are subordinate to Application/Component context in the first slice rather than requiring an independent top-level workspace.

Resource history remains subordinate to Resource Detail rather than becoming a separate business workspace.

## Required interface states

At minimum the Human Interface Design must preserve:

- loading;
- loaded;
- genuine empty;
- filtered empty when filtering exists;
- submitting;
- accepted success;
- validation/reference rejection;
- authentication rejection;
- authorization rejection;
- stale/concurrency conflict;
- dependency unavailable;
- not found;
- unexpected technical failure;
- retry/recovery;
- COMPLETE materialization;
- UNRESOLVED materialization.

Semantic distinctions that must remain visible:

- Resource exists with no current address != Resource not found;
- Site/OWNER/ADMINISTRATOR != authorization authority;
- Need/business justification != permission decision;
- AccessRequest admission != final ALLOWED/DENIED decision;
- ALLOWED decision != currently ACTIVE/effective Rule;
- current Rule != effective materialized row;
- COMPLETE != UNRESOLVED;
- dependency failure != successful UNRESOLVED result.

## Comparison with current canonical UI design

### What is already correct

`docs/contracts/ui/mvp-navigation.yaml` and `docs/contracts/ui/resource-detail.yaml` are consistent with the blind reconstruction for Resource Catalogue:

- stable Resource identity drives navigation;
- Resource history is subordinate to Resource Detail;
- current facts are primary;
- explicit absence is not not-found;
- loading/not-found/error remain distinct;
- ended/replaced facts preserve validity/provenance.

This is valid Interface Design, but only for the Resource-history pilot.

### What is missing

The current canonical UI layer does not define the complete first-MVP frontend closure.

There is no canonical Human Interface Design for:
- Applications/Components/Interactions/Revisions;
- ComponentDeployments;
- BusinessProcess/ConnectivityNeed;
- AccessRequest submission and decision;
- PolicyRule management;
- Policy materialization/export.

## P0 gaps

### P0-1 — No frontend consumer/readiness boundary

`docs/harness-core.yaml` has only the backend `IMPLEMENTATION` consumer.

`docs/plans/first-mvp-implementation-readiness.yaml` explicitly excludes frontend implementation.

Therefore the project can correctly report backend design COMPLETE while saying nothing about frontend completeness.

Required repair:
- introduce a separate frontend implementation consumer/closure;
- do not make backend implementation depend on frontend knowledge.

### P0-2 — Browser authentication/session lifecycle is not designed

Current Security Architecture defines backend OIDC bearer-JWT validation, but not how the separate browser client obtains and maintains authentication.

Missing decisions include:
- browser authentication flow;
- redirect/callback responsibility;
- PKCE or equivalent accepted mechanism;
- token/session storage boundary;
- refresh/re-authentication behavior;
- logout/invalidation behavior;
- whether a BFF/session-cookie pattern is used or excluded.

These are SECURITY-ARCHITECTURE decisions.

Frontend System Architecture must be BLOCKED until this is resolved.

### P0-3 — Current HTTP contract is command-heavy and insufficient for the full UI

The canonical OpenAPI exposes the required write operations and selected reads, but does not provide a complete discovery/read model for user-facing selection/list/detail flows across Applications, Components, Interactions/Revisions, Deployments, Processes/Needs, Access Requests and current Rules.

A browser UI must not:
- invent identifiers;
- query persistence directly;
- reconstruct owner truth client-side.

Required repair:
- derive explicit UI-required read/query application contracts;
- then expose the necessary external API representations under INTERFACE-DESIGN.

This gap belongs first to APPLICATION/SYSTEM ownership for owner read contracts and then INTERFACE-DESIGN for HTTP realization.

### P0-4 — Complete Human Interface Design is absent

The current canonical UI contracts define a Resource pilot, not first-MVP interface closure.

Required canonical knowledge:
- task/journey coverage;
- information architecture;
- navigation;
- view boundaries;
- visible state model;
- transitions;
- error/recovery semantics;
- permission-sensitive behavior;
- export/result semantics.

## P1 gaps

### P1-1 — Frontend System Architecture

The C4 model declares a separate browser Web Application, but there is no implementation-independent frontend architecture contract covering:
- browser runtime/module topology;
- frontend/backend responsibility;
- state ownership/lifetime;
- API adapter boundary;
- caching/invalidation policy if any;
- authentication integration;
- dependency direction.

### P1-2 — Frontend Component Design

No code-facing component/port/dependency contract exists for the Web Application.

Required only after Human Interface Design + frontend architecture/security are accepted.

### P1-3 — Frontend Test Design and Verification Design

The current verification/readiness model is backend-oriented.

Frontend requires executable contracts for:
- journeys;
- view-state transitions;
- validation/recovery;
- permission/auth states;
- COMPLETE/UNRESOLVED mapping;
- keyboard/focus behavior;
- architectural dependency boundaries;
- browser security.

### P1-4 — Frontend Implementation Design

No terminal pre-code frontend realization contract exists.

Framework choice, routing/state mechanics and implementation slicing remain undecided and must not be invented by coding agents before upstream closure.

## Legacy UI comparison

`docs-legacy/requirements/web-ui-requirements.md` contains useful historical requirements such as:

- desktop-first dense control-plane UI;
- WCAG 2.2 AA target;
- server-side paging/filter/search for potentially unbounded data;
- explicit responsive bands;
- Connectivity/Checker-centric navigation.

These are not current canonical inputs.

Therefore Harness must not silently promote them into the new frontend design. If they are still required, their accepted semantics must be reintroduced into current canonical Product/Interface/Quality ownership.

`docs-legacy/ui/screens.md` also contains broader historical screens than the selected first-MVP journey. They are comparison evidence, not authority.

## Harness behavior assessment

The current Harness frontend model is sufficient to diagnose NAPMS correctly:

1. User Journey Design can be derived from current accepted product/domain/application semantics.
2. Human Interface Design can recover the six-workspace model and required visible semantic distinctions.
3. The Resource Detail pilot validates the Interface Design boundary.
4. Frontend System Architecture must stop on the missing browser-authentication decision.
5. The coding boundary exposes missing owner read/query contracts rather than allowing the browser to reach persistence.
6. No new FRONTEND-DESIGN/UI-DESIGN/UX-DESIGN Authority is required.

What NAPMS lacks is project engineering knowledge, not a new Harness Core mechanism.

## Validation verdict

Frontend design status for the full selected NAPMS first-MVP journey: **BLOCKED / INCOMPLETE**.

Backend implementation readiness remains valid and independent.

Blocking owners:
- SECURITY-ARCHITECTURE: browser authentication/session lifecycle;
- APPLICATION/SYSTEM + INTERFACE-DESIGN: UI-required read/query contracts;
- INTERFACE-DESIGN: complete Human Interface Design.

After those P0 repairs, produce frontend System Architecture, Component Design, Verification/Test Design and terminal Implementation Design through the existing Harness producer/consumer model.


## Post-design comparison with current Web implementation

The existing `web/` implementation was inspected only after the blind design result above.

### Useful implementation evidence

The current React frontend already demonstrates several sound implementation patterns:

- feature-oriented source structure;
- a reusable design-system layer;
- explicit Resource/Application/Rule/etc. pages;
- visible loading/error/domain-status components;
- responsive desktop/mobile shell mechanics;
- Resource detail/history implementation material consistent with the current Resource UI pilot.

These facts show implementation capability, not canonical target semantics.

### Material mismatch — authentication

Current Web code implements a local username/password session flow:

- `POST /api/v1/session`;
- `GET /api/v1/session`;
- `DELETE /api/v1/session`;
- browser-visible login/password form.

Current canonical Security Architecture instead requires OIDC bearer JWT validation and defines no username/password session API.

Therefore current Web authentication is legacy/non-canonical relative to the selected target architecture.

This independently confirms P0-2: browser authentication/session architecture must be decided before target frontend implementation can be considered ready.

### Material mismatch — navigation/domain vocabulary

Current Web navigation exposes legacy/current-runtime surfaces including:

- Connectivity;
- Checker;
- Needs/requirements;
- Decisions;
- Rules;
- Effective;
- Export;
- Realization.

Some of these are useful historical/product directions, but several belong to broader or superseded models described in `docs-legacy/**`, not to the narrow selected first-MVP canonical journey.

They must not be promoted wholesale into target navigation merely because code exists.

### Machine-interface mismatch

Current Web feature APIs rely on a broader `/api/**` surface than the selected canonical OpenAPI shown in `docs/contracts/http/napms.openapi.yaml`.

This is implementation evidence that a usable UI needs richer read/discovery contracts.

It does not authorize keeping undocumented endpoints. The correct repair is to promote required application/read semantics and then canonicalize the external interface.

## Final validation result

The experiment validates both positive and negative Harness behavior.

Positive:
- blind journey/interface reconstruction is possible from accepted NAPMS knowledge;
- the Resource Detail pilot matches the reconstructed semantics;
- the existing Authority model is sufficient;
- no frontend-specific Core/Authority is needed.

Negative/gap detection:
- no frontend consumer exists;
- browser auth/session architecture is missing and current implementation contradicts target security;
- read/discovery contracts are incomplete for the full UI;
- complete Human Interface Design is absent;
- downstream frontend architecture/component/test/implementation design therefore cannot yet be accepted.

The correct target-state result for a dedicated frontend consumer is **BLOCKED**, not COMPLETE.


## Development authentication decision

Development is a distinct deployment/runtime mode, but it does not introduce a second authentication model.

### Development

Use a local/mock OIDC issuer that produces JWT bearer tokens compatible with the canonical backend validation contract.

Development tokens must exercise the same backend path as production tokens, including:
- configured issuer validation;
- audience validation;
- expiry/time validation;
- subject extraction;
- instance-permission claims;
- AuthorityGrant claims;
- asymmetric signature verification according to the accepted backend security contract.

Developer convenience may simplify token issuance and local sign-in, but must not bypass JWT validation or introduce trusted caller-supplied identity/authority fields.

### Production

Use the real configured OIDC provider with the same backend bearer-token validation path.

### Explicitly rejected development shortcut

Do not preserve a separate username/password + `/api/v1/session` authentication model as the target development architecture.

The environment may simplify **how a token is obtained**, not **how identity/authority is validated by NAPMS**.

### Remaining browser-security question

This decision resolves the development-vs-production authentication mechanism distinction, but browser Security Architecture still needs to define the supported browser flow itself:

- authorization-code/PKCE or another accepted browser OIDC flow;
- callback/redirect ownership;
- browser token/session storage boundary;
- refresh/re-authentication behavior;
- logout/invalidation behavior;
- whether a BFF/session-cookie pattern is used or explicitly excluded.

Therefore the full frontend Security Architecture remains BLOCKED until that browser lifecycle is accepted.
