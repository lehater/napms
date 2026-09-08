.PHONY: test postgres-test web-check docker-build dev-up dev-down dev-logs dev-reset harness-check knowledge-check check

test:
	python -m pytest -q -m "not postgres"

postgres-test:
	python -m pytest -q -m postgres tests/integration/postgres

web-check:
	cd web && npm run build

docker-build:
	docker compose build

dev-up:
	python tools/dev_compose.py up

dev-down:
	docker compose down --remove-orphans

dev-logs:
	docker compose logs --follow --tail=200

dev-reset:
	docker compose down --volumes --remove-orphans

harness-check:
	python tools/validate_harness.py
	python tools/validate_plans.py
	python tools/validate_skill_routing.py

knowledge-check:
	python tools/validate_domain_model.py

check: test harness-check knowledge-check
