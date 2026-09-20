# Blind backend security architecture

Status: ACCEPTED after Source Corpus amendments 01–02

## Trust model

External callers are untrusted until authenticated. The backend trusts identity only from a configured OpenID Connect issuer under the exact validation contract below.

JWT validation:
- token must be signed; `alg=none` is always rejected;
- `alg` must be in startup-configured `NAPMS_OIDC_ALLOWED_ALGS`, a non-empty subset of `RS256,RS384,RS512,PS256,PS384,PS512,ES256,ES384,ES512,EdDSA`;
- HMAC `HS*` algorithms are never accepted because this MVP configures no shared JWT verification secret;
- selected JWKS public key type/curve must be compatible with the token algorithm;
- configured issuer is an absolute HTTPS URL;
- OIDC discovery metadata `issuer` must exactly equal that configured issuer;
- discovered `jwks_uri` must be an absolute HTTPS URL;
- redirects from OIDC metadata/JWKS fetches to non-HTTPS locations are rejected;
- `iss` is required and exactly equals configured issuer;
- `aud` is required and is either string or array<string> containing the exact configured audience;
- `exp` is required NumericDate; token is acceptable only while current time <= exp + configured clock skew;
- `nbf`, when present, is NumericDate and requires current time + configured clock skew >= nbf;
- `sub` is required non-empty string;
- `iat` is not an authorization criterion.

The relational database and configured OIDC issuer are trusted infrastructure dependencies inside the deployment boundary. Caller-supplied actor/resource ownership fields never establish authorization.

## Identity

Validation clock skew is fixed for process lifetime by `NAPMS_OIDC_CLOCK_SKEW` and is applied only to exp/nbf comparisons above.

Authenticated principal:
- `sub` is required and must be a non-empty string from the validated token;
- optional display attributes are non-authoritative;
- the configured permission claim, when present, must be a JSON array of strings;
- the configured authority claim, when present, must be a JSON array of objects `{action,scope,effectiveFrom?,effectiveUntil?}`;
- authority `action` and `scope` are required non-empty strings;
- `effectiveFrom`/`effectiveUntil`, when present, are NumericDate values with half-open semantics `[effectiveFrom,effectiveUntil)`; when both exist, effectiveFrom < effectiveUntil;
- missing authority claim yields an authenticated Principal with an empty AuthorityGrant set;
- duplicate authority objects collapse by exact action/scope/bounds tuple;
- unknown authority actions grant nothing because ScopedAuthorizer recognizes only `access.request` and `policy.export`;
- malformed authority claim/object/bounds is an invalid credential/token-format failure (401);
- missing permission claim yields an authenticated Principal with an empty permission set;
- wrong permission-claim type or non-string element is an invalid credential/token-format failure (401);
- duplicate permission strings collapse to a set;
- unknown permission strings grant nothing by themselves because Authorizer recognizes only the exact canonical permission vocabulary;
- no alternative body/query/header permission or authority-grant source exists.

No local password/account lifecycle is introduced by the MVP.

## Admission model

Protected operations require explicit permission. Missing/invalid identity, missing permission or authorization uncertainty fails closed.

Instance permission vocabulary:
- `resource.read`, `resource.write`
- `application.read`, `application.write`
- `deployment.read`, `deployment.write`
- `business.read`, `business.write`
- `access.decide`
- `access.manage`
- `policy.read`

Scoped authority actions:
- `access.request`
- `policy.export`

`access.request` and `policy.export` are **not** granted by instance permission strings. They require effective scoped AuthorityGrants.

An AuthorityGrant is effective for action A, scope S and time T iff action/scope exactly match and T is inside its optional half-open effective bounds.

Request admission:
- resolve source and destination Deployments to Resources and their explicit Resource-owned AuthorityScopeRefs;
- deduplicate those scope refs;
- at server-owned request `admissionAt`, require an effective `access.request` grant for every distinct participating scope;
- record the exact actor/action/scope/grant-bounds/admissionAt evidence used.

Export admission:
- from the selected PolicyRules resolve the distinct participating Resource AuthorityScopeRefs;
- at the same database-owned `evaluationAt` used for materialization, require an effective `policy.export` grant for every distinct selected scope;
- record that export authority evidence in the materialization result.

The distinction between scoped request authority and `access.decide` preserves the product rule that authority to request is not permission to allow. `access.manage` changes already-authorized current-access operational/justification metadata but never creates permission evidence.

Resource Site/OWNER/ADMINISTRATOR, Business Process responsible organization and Connectivity Need existence never create or imply an AuthorityGrant.

### Canonical operation-to-permission matrix

| Operation class | Required permission |
| --- | --- |
| GET Site / ResponsibilityGroup / Resource / Resource history | `resource.read` |
| Create Site / ResponsibilityGroup / Resource / Endpoint; set/clear Resource address/Site/OWNER/ADMINISTRATOR | `resource.write` |
| GET Application / Interaction / InteractionRevision | `application.read` |
| Create Application/Component/Interaction and publish InteractionRevision | `application.write` |
| GET ComponentDeployment | `deployment.read` |
| Create ComponentDeployment | `deployment.write` |
| GET BusinessProcess / ConnectivityNeed | `business.read` |
| Create BusinessProcess/ConnectivityNeed, set/clear responsible organization, retire Need | `business.write` |
| Submit AccessRequest | effective scoped `access.request` AuthorityGrant for every participating Resource AuthorityScopeRef at admissionAt |
| Record ALLOWED/DENIED permission decision | `access.decide` |
| Change PolicyRule ACTIVE/INACTIVE/effective window | `access.manage` |
| Attach an additional current Need justification to PolicyRule | `access.manage` |
| GET AccessRequest / PolicyRule | `policy.read` |
| Materialize all current policy or an explicit PolicyRule subset | effective scoped `policy.export` AuthorityGrant for every selected Resource AuthorityScopeRef at evaluationAt |

No permission/grant implies another. In particular, scoped `access.request`, `access.decide`, `access.manage`, `policy.read` and scoped `policy.export` are independent.

Health endpoints are not application-data operations. `/health/live` and `/health/ready` expose only minimal status and may be unauthenticated inside the deployment health-check boundary; deployment/network policy must prevent them from becoming an information-rich public interface.

## Decision authenticity

Recording ALLOWED/DENIED requires authenticated instance permission `access.decide`. The backend records principal subject, timestamp and optional external decision reference as provenance. The human/organizational process that caused the decision remains outside current ownership.

## Interface protection

- external caller traffic is HTTPS to deployment ingress/reverse proxy/load balancer; the application-owned listener is plaintext only inside the trusted deployment boundary and must not be exposed directly to an untrusted network; application TLS certificates/keys are not an MVP responsibility.
- Bearer tokens are accepted only in the Authorization header.
- No identity/permission override through request body/query/header aliases, including `X-Forwarded-User`, `X-Remote-User`, or proxy-supplied permission headers. Forwarded network metadata never establishes application identity.
- Mutation responses never echo tokens/secrets.
- Error disclosure distinguishes authentication/authorization/domain failure without exposing internal stack/schema/secret data.

## Secrets/credentials

- OIDC issuer/audience/permission-claim/authority-claim/allowed-algorithms/clock-skew metadata are non-secret configuration. In serve mode the configured OIDC issuer is always an absolute HTTPS URL.
- client credentials, database credentials and signing/private material are secret configuration.
- secrets are never logged and are redacted from diagnostic context.
- application does not persist bearer tokens.

## Data protection

Current admitted source contains business/resource/network information but no explicit regulated-personal-data class. Basic confidentiality/integrity controls apply. Encryption at rest is delegated to deployment/database capability; transport encryption is required for external calls. If regulated/sensitive classification is later accepted, Security/Data lifecycle must reopen.

## Security implementation freedoms

OIDC client/JWT library, TLS termination component and secret-store technology may vary while preserving this contract.
