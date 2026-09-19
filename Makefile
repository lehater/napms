.PHONY: test postgres-test web-check journey-e2e docker-build dev-up dev-status dev-down dev-logs dev-reset dev-backup dev-restore design-sync design-check authority-context human-implementation-package architecture architecture-check check

STRUCTURIZR_IMAGE ?= structurizr/structurizr:2026.06.28-noble
STRUCTURIZR_DIR := $(CURDIR)/docs/architecture/structurizr
GENERATED_ARCH_DIR := $(CURDIR)/docs-generated/architecture
PLANTUML_SERVER_IMAGE ?= plantuml/plantuml-server:jetty
PLANTUML_CONTAINER ?= napms-plantuml

test:
	cd backend && python -m pytest -q -m "not postgres"

postgres-test:
	cd backend && python -m pytest -q -m postgres tests/integration/postgres

web-check:
	cd web && npm run build

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

design-sync:
	python tools/check_canonical_graph.py
	python tools/check_harness_vertical.py
	python tools/generate_strategic_views.py
	python tools/generate_resource_catalogue_views.py
	python tools/generate_acc_view.py
	python tools/generate_ad_view.py
	python tools/generate_bc_view.py
	python tools/generate_ap_view.py
	python tools/generate_mvp_journey_view.py
	python tools/generate_persistence_erd.py

design-check:
	python tools/check_canonical_graph.py
	python tools/check_harness_vertical.py
	python tools/test_harness_vertical.py
	python tools/test_authority_execution.py
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

authority-context:
	@test -n "$(AUTHORITY)" || (echo "Usage: make authority-context AUTHORITY=SYSTEM-ARCHITECTURE" >&2; exit 2)
	python tools/prepare_authority_execution.py "$(AUTHORITY)"

architecture: design-sync
	@docker rm -f $(PLANTUML_CONTAINER) >/dev/null 2>&1 || true
	@docker run -d --rm --name $(PLANTUML_CONTAINER) -p 127.0.0.1:8081:8080 $(PLANTUML_SERVER_IMAGE) >/dev/null
	@trap 'docker rm -f $(PLANTUML_CONTAINER) >/dev/null 2>&1 || true' EXIT INT TERM; 		docker run --rm -it -p 127.0.0.1:8080:8080 		-v "$(STRUCTURIZR_DIR):/usr/local/structurizr" 		-v "$(GENERATED_ARCH_DIR):/usr/local/structurizr/generated:ro" 		$(STRUCTURIZR_IMAGE) local

architecture-check: design-sync
	docker run --rm 		-v "$(STRUCTURIZR_DIR):/usr/local/structurizr" 		-v "$(GENERATED_ARCH_DIR):/usr/local/structurizr/generated:ro" 		$(STRUCTURIZR_IMAGE) validate -workspace /usr/local/structurizr/workspace.dsl

check: test design-check
