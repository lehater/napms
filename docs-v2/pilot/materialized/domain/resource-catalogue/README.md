# Resource Catalogue — pilot domain glossary

Status: M7 PILOT CANDIDATE / non-canonical.

This glossary accompanies the candidate `domain-model.puml`. It defines only terminology needed for the selected catalogue-curation slice.

| Term | Meaning |
|---|---|
| Resource | Stable Resource Catalogue-owned identity of an access-relevant resource. |
| ResourceRef | Opaque cross-context reference to Resource identity; not a persistence key or private realization-fact identity. |
| AddressSpace | Value object containing exactly one HostAddress or Prefix when resolved. |
| ResourceAddressFact | Temporal authoritative fact that a Resource has an AddressSpace for a validity interval, with provenance. |
| CurrentResourceRealization | Derived published semantic projection resolving a ResourceRef at a logical time to optional AddressSpace plus completeness/provenance information. |
| ResourceScopeAffiliation | Temporal RC fact associating a Resource with a Responsibility Scope. It does not grant actor authority. |
| ResourceResponsibility | Temporal RC fact describing responsible person/team and role/contact data. It neither establishes scope membership nor grants actor authority. |
| unresolved realization | Valid state in which no effective AddressSpace resolves for a Resource at the requested logical time. |

## Boundary

Resource Catalogue owns Resource identity and the RC facts above. Application Communication Catalogue owns application/component/deployment semantics and bindings. Authority Management owns actor authority. HTTP DTOs, persistence rows and UI projections are realizations of these semantics, not alternative semantic owners.

Product code is read-only evidence during this documentation-system pilot.