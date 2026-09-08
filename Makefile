.PHONY: test harness-check knowledge-check check

test:
	python -m pytest -q

harness-check:
	python tools/validate_harness.py
	python tools/validate_plans.py
	python tools/validate_skill_routing.py

knowledge-check:
	python tools/validate_domain_model.py

check: test harness-check knowledge-check
