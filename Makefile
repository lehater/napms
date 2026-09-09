.PHONY: test postgres-test web-check docker-build dev-up dev-down dev-logs dev-reset harness-check knowledge-check check

test:
	python -m pytest -q -m "not postgres"

postgres-test:
	python -m pytest -q -m postgres tests/integration/postgres

web-check:
	cd web && npm run build

docker-build:
	NAPMS_POSTGRES_PASSWORD=local-build-placeholder docker compose build

dev-up:
	@NAPMS_POSTGRES_PASSWORD="$$(python -c 'import secrets; print(secrets.token_urlsafe(24))')" sh -c 'python tools/dev_compose.py up && python tools/verify_local_postgres_auth.py'

dev-down:
	NAPMS_POSTGRES_PASSWORD=local-command-placeholder docker compose down --remove-orphans

dev-logs:
	NAPMS_POSTGRES_PASSWORD=local-command-placeholder docker compose logs --follow --tail=200

dev-reset:
	NAPMS_POSTGRES_PASSWORD=local-command-placeholder docker compose down --volumes --remove-orphans

harness-check:
	python tools/validate_harness.py
	python tools/validate_plans.py
	python tools/validate_skill_routing.py

knowledge-check:
	python tools/validate_domain_model.py

check: test harness-check knowledge-check
