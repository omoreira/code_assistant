.PHONY: help install install-dev test test-cov lint format clean venv

help:
	@echo "code-assistant - Available targets:"
	@echo ""
	@echo "  make venv          Create virtual environment"
	@echo "  make install       Install package in development mode"
	@echo "  make install-dev   Install package with development dependencies"
	@echo "  make test          Run unit tests"
	@echo "  make test-cov      Run tests with coverage report"
	@echo "  make lint          Run linting (flake8 + pylint)"
	@echo "  make format        Format code with black"
	@echo "  make clean         Clean up generated files and cache"
	@echo "  make help          Show this help message"

venv:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip setuptools wheel

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	PYTHONPATH=src pytest tests/ -v

test-cov:
	PYTHONPATH=src pytest tests/ -v --cov=code_starter --cov=code_debugger --cov=code_patcher --cov=code_refractor --cov=shared --cov-report=html --cov-report=term

lint:
	flake8 src/code_starter src/code_debugger src/code_patcher src/code_refractor src/shared src/tools src/db_master_handler src/assistant_contracts tests --max-line-length=88
	PYTHONPATH=src pylint code_starter code_debugger code_patcher code_refractor shared --disable=R0913,R0914,C0114,C0115,C0116

format:
	black src/code_starter src/code_debugger src/code_patcher src/code_refractor src/shared src/tools src/db_master_handler src/assistant_contracts tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov
	rm -rf .tox

.DEFAULT_GOAL := help
