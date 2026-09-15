# NAPMS

**Network Access Policy Management System**

The repository working tree represents current project truth. Git history is the archive.

## Selected implementation MVP

The selected first implementation slice is defined by `docs/requirements/first-mvp-vendor-neutral-policy-export.md`:

```text
AP current effective Policy Rules
        +
ACC InteractionContractRevision
        +
AD ApplicationDeployment + ComponentPlacement
        +
RC Resource + AddressSpace
        |
        v
Full Vendor-Neutral Policy Export
        |
        +--> table
        `--> CSV/vendor-neutral data
```

The export contains access-list-oriented source/destination address, protocol and port/range semantics without firewall, device, ACL or provider context.

The complete target domain remains defined by `docs/domain/strategic-model.md`. Current execution state is `docs/plans/active/README.md`.

## Local Docker start

Prerequisites: Docker Engine/Desktop with Docker Compose v2 and Python 3.

```bash
make dev-up
```

Useful commands:

```bash
make dev-status
make dev-logs
make dev-down
make dev-reset
```

`dev-down` preserves the database volume. `dev-reset` deletes local database state.

## Local backup and recovery

Create a validated PostgreSQL custom-format logical backup:

```bash
make dev-backup BACKUP=backups/napms.napms.dump
```

Restore into a clean replacement PostgreSQL volume:

```bash
make dev-restore BACKUP=backups/napms.napms.dump CONFIRM_RESET=yes
```

See `docs/engineering/local-backup-recovery.md` and `docs/engineering/local-upgrade-procedure.md` for current operational contracts.

## Native development

```bash
python -m pip install -e "backend[dev,postgres,runtime]"
make test
```

PostgreSQL integration tests use `NAPMS_TEST_POSTGRES_DSN` and `make postgres-test`.

Web build:

```bash
cd web
npm ci
npm run build
```

## Repository layout

```text
backend/src/napms/         product code
backend/tests/             executable specifications and integration tests
web/                       React Web UI
docs/requirements/         current product contracts
docs/domain/               current DDD model
docs/architecture/         current architecture contracts
docs/engineering/          current runtime/operational contracts
docs/ui/                   current reusable UI guidance
docs/plans/active/         current execution state
docs/process/              repository working protocols
```

See `AGENTS.md` and `docs/README.md` before changing product/domain/architecture semantics.
