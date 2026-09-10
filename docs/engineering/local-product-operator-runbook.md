# Local product operator runbook

Status: `accepted supported-local operator workflow`.

Date: 2026-09-10.

## Purpose

Describe the supported local NAPMS operator path from startup through policy inspection and realization evidence. This runbook does not add product semantics and does not imply enterprise deployment or real-device integration.

## Start and verify the local product

Start the supported Compose topology:

```bash
make dev-up
```

Use the generated local UI credentials printed by the command and open the printed loopback URL.

Check runtime health when needed:

```bash
make dev-status
make dev-logs
```

`dev-status` is the supported local liveness/readiness/PostgreSQL diagnostic path. Startup/status probes do not create or mutate business state.

## Supported product journey

The primary local browser journey is:

```text
Connectivity
  -> declare/reuse Connectivity Requirement
  -> inspect Needs
  -> inspect/record Connectivity Decision
  -> inspect authoritative Access Rule
  -> inspect Effective Desired Policy / Normalized Policy
  -> inspect Realization
```

`Realization` is a read-only network/security operator projection. It may show desired policy/enforcement placement/rendered configuration as `Available` while reconciliation or controlled-operation evidence remains `NotAvailable` when the runtime has no selected configured-evidence/managed-scope input or actual NEO operation result. `Unknown` is preserved when required semantic input is ambiguous or incomplete. These states must not be reinterpreted as success.

Explainability navigation follows existing owner pages:

```text
Realization -> Access Rule -> Connectivity Decision -> Connectivity Requirement
```

Each owner page performs its own read authorization. The projection does not create copied authoritative state.

## Recovery and upgrade

Create a validated logical backup before destructive recovery or forward upgrade:

```bash
make dev-backup BACKUP=backups/napms.napms.dump
```

Restore into a clean replacement volume only with explicit confirmation:

```bash
make dev-restore BACKUP=backups/napms.napms.dump CONFIRM_RESET=yes
```

Forward upgrade ordering and recovery rules are defined in `docs/engineering/local-upgrade-procedure.md`. Backup/restore details are defined in `docs/engineering/local-backup-recovery.md`.

## Web dependency reproducibility

The repository owns `web/package-lock.json`. Supported CI and Docker builds install the locked graph with `npm ci`; update the lockfile with the package manager whenever `web/package.json` dependency intent changes.

## Explicit exclusions

The supported local product does not claim:
- real Cisco/device transport or lab compatibility;
- crash-durable NEO operation history or production rollback;
- externally sourced configured-evidence selection unless a concrete source is added;
- external IdP, directory, CMDB, catalogue, Authority or MSSQL dependencies;
- enterprise HA, public TLS automation, external secret stores or multi-node topology;
- performance/SLA guarantees without an accepted workload target;
- generic dashboard, global search, bulk mutation or additional export surfaces without a demonstrated operator requirement.

The deterministic NEO target stub proves controlled-execution orchestration semantics only. Full-chain acceptance evidence exists in the PostgreSQL integration suite; the interactive runtime must still report unavailable stages truthfully when their actual owning inputs/results do not exist.
