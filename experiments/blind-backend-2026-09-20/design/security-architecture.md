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

Protected operations require explicit permission. Missing/invalid identity, missing permission, malformed scope or authorization uncertainty fails closed.

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

Current MVP permission scope is whole backend instance. Per-Resource/Application scopes are not invented without product input. A future scoped model is a Security/Product extension.

## Decision authenticity

Recording ALLOWED/DENIED requires authenticated `access.decide`. The backend records principal subject, timestamp and optional external decision reference as provenance. The human/organizational process that caused the decision remains outside current ownership.

## Interface protection

- HTTPS is mandatory outside a trusted loopback/dev environment.
- Bearer tokens accepted only in Authorization header.
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
