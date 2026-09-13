# Local product operator runbook

Status: `accepted supported-local operator workflow; APR operator workflow under revalidation`.

Date: 2026-09-13.

## Purpose

Describe the supported local NAPMS operator path for current accepted product capabilities. This runbook does not add product semantics and does not imply enterprise deployment or real-device integration.

Access Policy Realization target semantics and its future operator workflow are currently defined only by the problem framing in `docs/domain/access-policy-realization/README.md`. The existing legacy Realization runtime must not be used as a target specification.

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

## Supported current product journey

The current non-APR browser journey includes:

```text
Connectivity
  -> declare/reuse Connectivity Requirement
  -> inspect Needs
  -> inspect/record Connectivity Decision
  -> inspect authoritative Access Rule
  -> inspect Effective Desired Policy / Normalized Policy
```

APR-specific realization assessment, semantic delta, policy-change design, pre-change verification and rendering will receive a new operator workflow only after their target contracts are accepted.

The runtime may still contain an older read-only `Realization` screen while migration is pending. Its stage/status vocabulary is legacy implementation behavior and is not normative documentation.

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

The deterministic NEO target stub proves its currently implemented operation mechanics only. It does not establish the redesigned APR semantic model or a real device-integration claim.
