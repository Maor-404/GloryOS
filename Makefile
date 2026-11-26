SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
GLORYOS := $(VENV)/bin/gloryos

.PHONY: setup preflight validate-contracts lint test audit check clean

setup:
	bash scripts/setup-dev-env.sh

preflight:
	$(GLORYOS) preflight --milestone M0
	$(GLORYOS) preflight --milestone M1

validate-contracts:
	$(GLORYOS) validate --contract distro-manifest configs/distro/gloryos-base.yaml

lint:
	$(VENV)/bin/ruff check src tests
	$(VENV)/bin/ruff format --check src tests
	$(VENV)/bin/mypy
	shellcheck scripts/*.sh

test:
	$(VENV)/bin/pytest

audit:
	$(VENV)/bin/pip-audit --skip-editable --progress-spinner off
	test -s LICENSE
	test -s THIRD_PARTY_NOTICES.md

check: lint validate-contracts test audit preflight

clean:
	rm -rf work out build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache
