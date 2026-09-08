.PHONY: test postgres-test web-check harness-check knowledge-check check

test:
	python -m pytest -q -m "not postgres"

postgres-test:
	python -m pytest -q -m postgres tests/integration/postgres

web-check:
	cd web && npm run build

harness-check:
	python tools/validate_harness.py
	python tools/validate_plans.py
	python tools/validate_skill_routing.py

knowledge-check:
	python tools/validate_domain_model.py

check: test harness-check knowledge-check
