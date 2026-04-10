.PHONY: install test lint check run status list clean

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff

## Setup
install:
	python3 -m venv $(VENV)
	$(PIP) install -q -e ".[dev]"
	@echo "✅ Virtual environment ready. Activate: source .venv/bin/activate"

## Quality
test:
	$(PYTEST) tests/ -v

lint:
	$(RUFF) check shaked_wg_agent/ tests/

lint-fix:
	$(RUFF) check --fix shaked_wg_agent/ tests/

check: lint test
	@echo "✅ All checks passed"

## Agent CLI
run:
	$(PYTHON) -m shaked_wg_agent run

status:
	$(PYTHON) -m shaked_wg_agent status

list:
	$(PYTHON) -m shaked_wg_agent list

## AOS Validation
validate-aos:
	bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

## Cleanup
clean:
	rm -rf $(VENV) .pytest_cache __pycache__ shaked_wg_agent/__pycache__ tests/__pycache__
	find . -name "*.pyc" -delete
