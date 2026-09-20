# Blind backend security architecture

Status: ACCEPTED candidate

## Trust model

External callers are untrusted until authenticated. The backend trusts identity only from a configured OpenID Connect issuer whose JWT signature, issuer, audience, expiry and not-before claims validate successfully.

The relational database and configured OIDC issuer are trusted infrastructure dependencies inside the deployment boundary. Caller-supplied actor/resource ownership fields never establish authorization.

## Identity

Authenticated principal:
- stable `sub` from trusted issuer;
- optional display attributes are non-authoritative;
- effective permission strings are read from a configured token claim.

No local password/account lifecycle is introduced by the MVP.

## Admission model

Protected operations require explicit permission. Missing/invalid identity, missing permission or authorization uncertainty fails closed.

Permission vocabulary:
- `resource.read`, `resource.write`
- `application.read`, `application.write`
- `deployment.read`, `deployment.write`
- `business.read`, `business.write`
- `access.request`
- `access.decide`
- `access.manage`
- `policy.read`, `policy.export`

The distinction between `access.request` and `access.decide` preserves the product rule that request authority is not permission to allow access. Resource Owner/Administrator and Business Process responsibility never create these permissions.

Current MVP permission scope is the whole backend instance. Per-Resource/Application scopes are not invented without product input. A future scoped model is a Product/Security extension.

### Canonical operation-to-permission matrix

| Operation class | Required permission |
| --- | --- |
| GET Site / ResponsibilityGroup / Resource / Resource history | `resource.read` |
| Create Site / ResponsibilityGroup / Resource / Endpoint; set/clear Resource address/Site/OWNER/ADMINISTRATOR | `resource.write` |
| GET Application / Interaction / InteractionRevision | `application.read` |
| Create/update Application / Component / Interaction / InteractionRevision | `application.write` |
| GET ComponentDeployment | `deployment.read` |
| Create ComponentDeployment | `deployment.write` |
| GET BusinessProcess / ConnectivityNeed | `business.read` |
| Create/update BusinessProcess / ConnectivityNeed, retire Need | `business.write` |
| Submit AccessRequest | `access.request` |
| Record ALLOWED/DENIED permission decision | `access.decide` |
| Change PolicyRule ACTIVE/INACTIVE or effective window | `access.manage` |
| Attach an additional current Need justification to PolicyRule | `access.manage` |
| GET AccessRequest / PolicyRule | `policy.read` |
| Materialize all current policy or an explicit PolicyRule subset | `policy.export` |

No permission implies another permission. In particular, `access.request`, `access.decide`, `access.manage` and `policy.export` are independent.

Health endpoints are not application-data operations. `/health/live` and `/health/ready` expose only minimal status and may be unauthenticated inside the deployment health-check boundary; deployment/network policy must prevent them from becoming an information-rich public interface.

## Decision authenticity

Recording ALLOWED/DENIED requires authenticated `access.decide`. The backend records principal subject, timestamp and optional external decision reference as provenance. The human/organizational process that caused the decision remains outside current ownership.

## Interface protection

- HTTPS is mandatory outside a trusted loopback/dev environment.
- Bearer tokens are accepted only in the Authorization header.
- No identity/permission override through request body/query/header aliases.
- Mutation responses never echo tokens/secrets.
- Error disclosure distinguishes authentication/authorization/domain failure without exposing internal stack/schema/secret data.

## Secrets/credentials

- OIDC issuer/audience metadata may be non-secret configuration.
- client credentials, database credentials and signing/private material are secret configuration.
- secrets are never logged and are redacted from diagnostic context.
- application does not persist bearer tokens.

## Data protection

Current admitted source contains business/resource/network information but no explicit regulated-personal-data class. Basic confidentiality/integrity controls apply. Encryption at rest is delegated to deployment/database capability; transport encryption is required for external calls. If regulated/sensitive classification is later accepted, Security/Data lifecycle must reopen.

## Security implementation freedoms

OIDC client/JWT library, TLS termination component and secret-store technology may vary while preserving this contract.
