.PHONY: test postgres-test backend-format backend-lint backend-type backend-architecture backend-quality backend-security web-check web-security repository-quality journey-e2e docker-build dev-up dev-status dev-down dev-logs dev-reset dev-backup dev-restore harness-bootstrap harness-pin-check design-sync design-check authority-context human-implementation-package architecture architecture-check check

STRUCTURIZR_IMAGE ?= structurizr/structurizr:2026.06.28-noble
STRUCTURIZR_DIR := $(CURDIR)/docs/architecture/structurizr
GENERATED_ARCH_DIR := $(CURDIR)/docs-generated/architecture
PLANTUML_SERVER_IMAGE ?= plantuml/plantuml-server:jetty
PLANTUML_CONTAINER ?= napms-plantuml
HARNESS_ROOT ?= $(CURDIR)/.harness-tool

test:
	cd backend && python -m pytest -q -m "not postgres"

postgres-test:
	cd backend && python -m pytest -q -m postgres tests/integration/postgres

backend-format:
	python -m ruff format --check backend/src backend/tests

backend-lint:
	python -m ruff check backend/src backend/tests

backend-type:
	cd backend && python -m mypy src/napms

backend-architecture:
	cd backend && lint-imports --config .importlinter
	cd backend && python -m pytest -q tests/architecture

backend-quality: backend-format backend-lint backend-type backend-architecture test

backend-security:
	python -m pip_audit -r backend/requirements.lock

web-check:
	cd web && npm run check && npm run build

web-security:
	cd web && npm audit --audit-level=high

repository-quality: backend-quality backend-security web-check web-security

journey-e2e:
	python -m pytest -q e2e

docker-build:
	NAPMS_POSTGRES_PASSWORD=local-build-placeholder docker compose build

dev-up:
	@NAPMS_POSTGRES_PASSWORD="$$(python -c 'import secrets; print(secrets.token_urlsafe(24))')" sh -c 'python tools/prepare_local_postgres.py && python tools/local_start.py up && python tools/verify_local_postgres_auth.py'

dev-status:
	NAPMS_POSTGRES_PASSWORD=local-status-placeholder python tools/local_status.py

dev-down:
	NAPMS_POSTGRES_PASSWORD=local-command-placeholder docker compose down --remove-orphans

dev-logs:
	NAPMS_POSTGRES_PASSWORD=local-command-placeholder docker compose logs --follow --tail=200

dev-reset:
	NAPMS_POSTGRES_PASSWORD=local-command-placeholder docker compose down --volumes --remove-orphans

dev-backup:
	@test -n "$(BACKUP)" || (echo "Usage: make dev-backup BACKUP=backups/napms.napms.dump" >&2; exit 2)
	NAPMS_POSTGRES_PASSWORD=local-command-placeholder python tools/local_postgres_backup.py backup "$(BACKUP)"

dev-restore:
	@test -n "$(BACKUP)" || (echo "Usage: make dev-restore BACKUP=backups/napms.napms.dump CONFIRM_RESET=yes" >&2; exit 2)
	@test "$(CONFIRM_RESET)" = "yes" || (echo "Restore replaces the local PostgreSQL volume; rerun with CONFIRM_RESET=yes" >&2; exit 2)
	python tools/local_postgres_backup.py restore-clean "$(BACKUP)" --confirm-reset

harness-bootstrap:
	rm -rf "$(HARNESS_ROOT)"
	git clone --filter=blob:none --no-checkout https://github.com/lehater/harness.git "$(HARNESS_ROOT)"
	git -C "$(HARNESS_ROOT)" checkout --detach "$$(cat .harness-version)"

harness-pin-check:
	@test -d "$(HARNESS_ROOT)/.git" || (echo "Pinned Harness checkout missing; run 'make harness-bootstrap'" >&2; exit 2)
	@test "$(git -C "$(HARNESS_ROOT)" rev-parse HEAD)" = "$(cat .harness-version)" || (echo "Harness checkout does not match .harness-version; run 'make harness-bootstrap'" >&2; exit 2)

design-sync: harness-pin-check
	python tools/check_canonical_graph.py
	HARNESS_ROOT="$(HARNESS_ROOT)" python tools/check_harness_integration.py
	HARNESS_ROOT="$(HARNESS_ROOT)" python tools/check_design_closure.py
	python tools/check_knowledge_completeness.py
	python tools/generate_strategic_views.py
	python tools/generate_resource_catalogue_views.py
	python tools/generate_acc_view.py
	python tools/generate_ad_view.py
	python tools/generate_bc_view.py
	python tools/generate_ap_view.py
	python tools/generate_mvp_journey_view.py
	python tools/generate_persistence_erd.py

design-check: harness-pin-check
	python $(HARNESS_ROOT)/repository_realization.py docs/plans/mvp-repository-realization.yaml
	python $(HARNESS_ROOT)/architecture_driver_closure.py docs/requirements/first-mvp-architecture-driver-closure.yaml
	python tools/check_canonical_graph.py
	HARNESS_ROOT="$(HARNESS_ROOT)" python tools/check_harness_integration.py
	HARNESS_ROOT="$(HARNESS_ROOT)" python tools/check_requirements_semantic_admission.py
	python tools/check_knowledge_completeness.py
	python tools/check_frontend_design_closure.py
	HARNESS_ROOT="$(HARNESS_ROOT)" python tools/check_frontend_provider_mapping.py
	python tools/evaluate_frontend_presentation_semantics.py --require-accepted
	python tools/evaluate_security_identity_semantics.py --require-accepted
	python tools/check_openapi_contract.py
	python tools/check_persistence_model.py
	python tools/check_design_control.py
	python tools/validate_skill_routing.py
	python tools/generate_strategic_views.py --check
	python tools/generate_resource_catalogue_views.py --check
	python tools/generate_acc_view.py --check
	python tools/generate_ad_view.py --check
	python tools/generate_bc_view.py --check
	python tools/generate_ap_view.py --check
	python tools/generate_mvp_journey_view.py --check
	python tools/generate_persistence_erd.py --check

authority-context: harness-pin-check
	@test -n "$(AUTHORITY)" || (echo "Usage: make authority-context AUTHORITY=SYSTEM-ARCHITECTURE CAPABILITY=engineering.architecture.rules" >&2; exit 2)
	@test -n "$(CAPABILITY)" || (echo "CAPABILITY is required; Authority contexts are capability-scoped" >&2; exit 2)
	HARNESS_ROOT="$(HARNESS_ROOT)" python tools/prepare_authority_execution.py "$(AUTHORITY)" --capability "$(CAPABILITY)"

human-implementation-package: harness-pin-check
	HARNESS_ROOT="$(HARNESS_ROOT)" python tools/generate_human_context_package.py --consumer BACKEND-IMPLEMENTATION

architecture: design-sync
	@docker rm -f $(PLANTUML_CONTAINER) >/dev/null 2>&1 || true
	@docker run -d --rm --name $(PLANTUML_CONTAINER) -p 127.0.0.1:8081:8080 $(PLANTUML_SERVER_IMAGE) >/dev/null
	@trap 'docker rm -f $(PLANTUML_CONTAINER) >/dev/null 2>&1 || true' EXIT INT TERM; docker run --rm -it -p 127.0.0.1:8080:8080 -v "$(STRUCTURIZR_DIR):/usr/local/structurizr" -v "$(GENERATED_ARCH_DIR):/usr/local/structurizr/generated:ro" $(STRUCTURIZR_IMAGE) local

architecture-check: design-sync
	docker run --rm -v "$(STRUCTURIZR_DIR):/usr/local/structurizr" -v "$(GENERATED_ARCH_DIR):/usr/local/structurizr/generated:ro" $(STRUCTURIZR_IMAGE) validate -workspace /usr/local/structurizr/workspace.dsl

check: design-check repository-quality
