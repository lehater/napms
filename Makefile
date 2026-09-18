.PHONY: test postgres-test web-check journey-e2e docker-build dev-up dev-status dev-down dev-logs dev-reset dev-backup dev-restore harness-check docs-v2-harness-check skill-routing-eval knowledge-check architecture architecture-check canonical-model-sync canonical-model-check check

STRUCTURIZR_IMAGE ?= structurizr/structurizr:2026.06.28-noble
STRUCTURIZR_DIR := $(CURDIR)/docs/architecture/structurizr

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

architecture:
	docker run --rm -it -p 8080:8080 -v "$(STRUCTURIZR_DIR):/usr/local/structurizr" $(STRUCTURIZR_IMAGE) local

architecture-check:
	docker run --rm -v "$(STRUCTURIZR_DIR):/usr/local/structurizr:ro" $(STRUCTURIZR_IMAGE) validate -workspace /usr/local/structurizr/workspace.dsl

canonical-model-sync:
	python tools/check_cm1_strategic_equivalence.py
	python tools/check_cm2_resource_catalogue_equivalence.py
	python tools/generate_strategic_views.py
	python tools/generate_resource_catalogue_views.py

canonical-model-check:
	python tools/check_cm1_strategic_equivalence.py
	python tools/check_cm2_resource_catalogue_equivalence.py
	python tools/generate_strategic_views.py --check
	python tools/generate_resource_catalogue_views.py --check

harness-check:
	python tools/validate_harness.py
	python tools/validate_plans.py
	python tools/validate_plan_capsule_sync.py
	python tools/validate_skill_routing.py
	python tools/validate_lifecycle_transitions.py

docs-v2-harness-check:
	python tools/test_docs_v2_harness.py
	python tools/test_docs_v2_harness_resume_refs.py
	python tools/test_docs_v2_harness_frontmatter.py
	python tools/docs_v2_harness.py --root . validate

skill-routing-eval:
	@test -n "$(ROUTING_RESULTS)" || (echo "Usage: make skill-routing-eval ROUTING_RESULTS=path/to/results.json [ROUTING_BASELINE=path/to/baseline.json]" >&2; exit 2)
	python tools/evaluate_skill_routing_results.py "$(ROUTING_RESULTS)" $(if $(ROUTING_BASELINE),--baseline "$(ROUTING_BASELINE)")

knowledge-check:
	python tools/validate_domain_model.py

check: test harness-check knowledge-check
