# NAPMS

**Network Access Policy Management System**

The repository working tree represents current project truth. Git history is the archive.

## Selected implementation MVP

The selected first implementation slice is the end-to-end vendor-neutral policy export journey defined by:

- `docs/requirements/first-mvp-policy-export.yaml` — accepted product intent, scope and acceptance;
- `docs/model/use-cases/first-mvp-policy-export.yaml` — canonical cross-context journey.

It combines current effective Access Policy rules with the accepted Application Communication Catalogue, Application Deployment, Business Connectivity, Resource Catalogue and Authority Management semantics to materialize the current vendor-neutral policy as a table and CSV data.

The export contains access-list-oriented source/destination address, protocol and port/range semantics without firewall, device, ACL or provider-specific context.

Implementation readiness is defined by `docs/plans/first-mvp-implementation-readiness.yaml`. It describes an implementable slice but does not by itself authorize product implementation.

## Design and architecture

`docs/` is the sole canonical current design/documentation authority. Generated views are projections and are not sources of truth.

For non-trivial design, architecture or implementation-planning work:

1. read `AGENTS.md`;
2. read `docs/canonical-graph.yaml` to locate the semantic owner and direct dependencies;
3. read `docs/meta/current-workstream.yaml`; follow a referenced workstream only when one is active;
4. load only the affected canonical artifacts.

Current major owners include:

- `docs/requirements/` — accepted product intent;
- `docs/discovery/` — current discovery evidence;
- `docs/model/` — strategic, tactical and use-case semantics;
- `docs/architecture/structurizr/workspace.dsl` — canonical C4 structural/deployment architecture;
- `docs/architecture/` — system, security, module, persistence, quality, threat and observability design;
- `docs/contracts/` — application/interface contracts;
- `docs/plans/` — implementation-readiness and verification intent;
- `docs/canonical-graph.yaml` — routing and dependency metadata.

Validate current canonical design:

```bash
make harness-bootstrap
make design-check
```

`make harness-bootstrap` checks out the immutable Harness commit declared in `.harness-version`; design tooling rejects a mismatched local Harness checkout.

Regenerate disposable projections:

```bash
make design-sync
```

Build the generated human-readable implementation context package:

```bash
make human-implementation-package
```

Run the local Structurizr architecture viewer:

```bash
make architecture
```

Validate the Structurizr workspace:

```bash
make architecture-check
```

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
backend/src/napms/                 product code
backend/tests/                     executable specifications and integration tests
web/                               React Web UI
docs/requirements/                 accepted product intent
docs/discovery/                    current discovery evidence
docs/model/                        canonical domain and use-case model
docs/architecture/                 canonical architecture and persistence design
docs/contracts/                    application/interface contracts
docs/plans/                        implementation-readiness and verification intent
docs/meta/current-workstream.yaml  current workstream pointer
docs/canonical-graph.yaml          canonical routing/dependency graph
docs-generated/                    generated, disposable non-canonical views
docs-legacy/                       retired frozen migration evidence
tools/                             repository validation/generation tooling
```

See `AGENTS.md` and `docs/README.md` before changing product, domain or architecture semantics.
