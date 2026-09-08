# Wave-1 minimal architecture views — PLAN-027 WP-06

Status: `accepted G3 structural/runtime views`.

Date: 2026-09-08.

## System context

```text
[Business / Resource actors]
        |
        v
[NAPM Wave-1 Product]
  |     |       |       |
  |     |       |       +--> [Deferred Connectivity Decision provider]
  |     |       +----------> [Application Communication authoritative source]
  |     +------------------> [Resource authoritative source]
  +------------------------> [Authority / responsibility authoritative source]
        |
        +--> Normalized Policy Export --> [human/downstream future renderer]

[Legacy SSSR_XLAM] --temporary adapters/transition evidence--> [NAPM]
```

Legacy is not a semantic owner of the target model merely because it is a transition source.

## Initial container / deployment-unit view

```text
+-----------------------------------------------------------+
| NAPM Wave-1 Application                                  |
|                                                           |
| Application/use-case layer                               |
|  - Proposal composition                                  |
|  - Rule materialization/state use cases                  |
|  - Export snapshot assembly + normalization              |
|                                                           |
| Semantic modules / ports                                 |
|  - Access Policy                                         |
|  - Authority port/model                                  |
|  - Application Communication Catalogue port/model        |
|  - Resource Catalogue port/model                         |
|  - Connectivity Decision port                            |
|                                                           |
| Adapters                                                  |
|  - enterprise/Legacy/manual integrations as required     |
|  - normalized export serialization                       |
+-----------------------------------------------------------+
             |
             +--> primary transactional persistence
                  (physical sharing permitted; module-owned access)
```

Separate adapter/process deployment is allowed only when integration/runtime constraints justify it. It does not create a new domain owner.

## Runtime view — Allowed proposal

```text
Actor
 -> Proposal use case
 -> Authority port: permitted?
 -> App Communication Catalogue: validate exact interaction
 -> Connectivity Decision port: exact subject -> Allowed
 -> Access Policy: materialize-or-resolve
 -> persistence consistency boundary: unique semantic identity
 <- same/new Rule ID, Active
```

## Runtime view — export

```text
Actor -> Export use case
  -> Authority: export permitted?
  -> Access Policy: selected effective Rules(asOf)
  -> Resource Catalogue: realizations valid at asOf
  -> App Communication Catalogue: DCS facts/provenance
  -> assemble immutable logical Export Snapshot
     [fail if any selected effective Rule cannot be proven complete/coherent]
  -> normalize snapshot
  -> serialize successful vendor-neutral export
```

## Runtime view — identity vs realization change

```text
identity-defining change
 -> new proposal subject -> new Connectivity Decision -> possible new Rule

technical realization change
 -> Resource Catalogue version/effective fact changes
 -> existing Rule unchanged
 -> later Export Snapshot resolves new valid realization
```

## Architecture boundary rules

- module calls may initially be in-process; semantic contracts remain explicit;
- no module reads another module's persistence as a substitute for its semantic contract;
- external adapters translate source-specific representations and preserve provenance/effective-time evidence;
- successful export normalization never performs uncontrolled live lookups after snapshot assembly;
- vendor rendering/device execution are outside this container view for Wave 1.