# Coding-Agent Challenge 02

Status: FAILED — repair required before blind freeze

## CAC-004 — P1 — ConnectivityNeed lost participant-side attribution

Source evidence explicitly requires:
- Need is stated from a dependent participant/component perspective;
- source and destination participants can contribute attribution independently.

Current blind model stored only Process -> Interaction + business basis. A coding agent could not represent two independent Process Needs for the same Interaction distinguished by which participant/component the business process depends on.

Classification: incomplete Product/Tactical/Data/Interface closure caused by source coverage loss, not implementation freedom.

Required repair:
- Need includes `participantComponentRef`;
- it must be either the Interaction source or destination Component;
- Need identity remains independent of Deployment/IP;
- source-side and destination-side Needs can coexist independently;
- Rule justification output preserves participantComponentRef.

## CAC-005 — P1 — operational Rule audit is durable but not externally queryable

Accepted product behavior requires ACTIVE/INACTIVE state transition to be auditable at business level.

Persistence contains operational history, but Interface Design exposes only current PolicyRule. Coding agent would have to decide whether/how audit is observable.

Classification: incomplete Interface Design / Verification closure.

Required repair:
- add canonical PolicyRule history read contract under `policy.read`;
- expose operational state/effective-window changes with actor/time and before/after state;
- bounded pagination;
- test transition history and no-op non-history.

## CAC-006 — P2 — OIDC permission claim representation underspecified

Security Architecture defines a configurable permission-claim name but not the accepted claim representation or missing/type behavior. Different JWT libraries could therefore produce materially different authorization outcomes.

Required repair:
- trusted `sub` must be non-empty;
- configured permission claim, when present, is an array of strings;
- missing claim means authenticated principal with empty permissions;
- wrong claim type means invalid credential/security-token format rather than implicit grant;
- duplicate strings collapse; unknown strings grant nothing because Authorizer checks only known exact permissions;
- no caller-controlled alternative header/body permission source.

## Result

Structural Harness COMPLETE from the earlier checkpoint is still not semantic closure. Freeze remains prohibited until repairs and Coding-Agent Challenge 03 pass.
