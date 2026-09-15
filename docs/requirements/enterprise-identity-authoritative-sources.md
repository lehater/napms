# External identity and authoritative-source extension requirements

## Purpose

Keep NAPMS local-first while defining the current compatibility rules for optional external identity and authoritative-source adapters.

## Local operation

NAPMS supports local username/password authentication as the primary runtime authentication path.

Normal operation does not require an external IdP, directory, CMDB, application catalogue, resource inventory or other enterprise system. Authority Management, Application Communication Catalogue and Resource Catalogue retain NAPMS-owned semantic state.

## External identity seam

An external authentication adapter may present a verified identity as a stable subject key qualified by provider/issuer identity.

NAPMS maps that verified external subject to exactly one NAPMS actor through a source-neutral mapping seam:

```text
Mapped | Unmapped | Ambiguous | Unknown
```

Only `Mapped` establishes an actor. `Unmapped`, `Ambiguous` and `Unknown` fail closed.

Provider/protocol mechanics remain outside Domain and application semantics.

## Authority separation

Authentication identifies an actor. Authority Management owns business authorization.

External claims, groups, roles or token scopes do not directly grant NAPMS business authority. Protected application actions evaluate the resulting NAPMS actor through Authority Management action/scope admission.

## Session behavior

Local authentication establishes the server-side NAPMS actor/session boundary. An external adapter, when configured, establishes the same boundary only after successful mapping.

Sessions do not encode a durable business-authority snapshot; protected use cases evaluate current Authority Management truth.

## External source seams

Authority Management, Application Communication Catalogue and Resource Catalogue remain semantic owners of their domain state.

Any external source adapter terminates at a context-owned import/projection boundary:

```text
external source
    -> source-specific adapter
    -> context-owned import/projection contract
    -> context application service
    -> context-owned state
```

Vendor transport models do not enter Domain. Contexts do not share mutable external-source tables. External identifiers remain source/correlation identifiers unless the owning bounded context explicitly defines a stronger identity relationship.

Synchronization, completeness, deletion and freshness semantics exist only when defined by the concrete source contract; absence of such a contract must not be replaced by assumptions.

## Acceptance rules

- local login succeeds without any external provider;
- a verified external identity with exactly one active mapping establishes the corresponding NAPMS actor;
- unmapped, ambiguous or unknown external identity establishes no actor;
- authentication mechanism does not change Authority Management ownership of protected-action admission;
- external source integration does not transfer semantic ownership out of the consuming bounded context.
