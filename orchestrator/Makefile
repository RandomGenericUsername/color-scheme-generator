.PHONY: help install install-dev clean test lint format type-check build run-tests coverage clean-build clean-pyc clean-test docker-build docker-clean

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Color Scheme Generator - Orchestrator$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install the package with uv
	@echo "$(BLUE)Installing color-scheme orchestrator...$(NC)"
	uv sync

install-dev: ## Install the package with development dependencies
	@echo "$(BLUE)Installing color-scheme orchestrator with dev dependencies...$(NC)"
	uv sync --all-extras --dev

venv: ## Create a new virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	uv venv

clean: clean-build clean-pyc clean-test ## Remove all build, test, coverage and Python artifacts

clean-build: ## Remove build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## Remove Python file artifacts
	@echo "$(BLUE)Cleaning Python artifacts...$(NC)"
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test: ## Remove test and coverage artifacts
	@echo "$(BLUE)Cleaning test artifacts...$(NC)"
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

lint: ## Check code style with ruff
	@echo "$(BLUE)Running ruff linter...$(NC)"
	uv run ruff check src/ tests/

lint-fix: ## Fix code style issues with ruff
	@echo "$(BLUE)Fixing code style with ruff...$(NC)"
	uv run ruff check --fix src/ tests/

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code with black...$(NC)"
	uv run black src/ tests/
	@echo "$(BLUE)Sorting imports with isort...$(NC)"
	uv run isort src/ tests/

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code format...$(NC)"
	uv run black --check src/ tests/
	uv run isort --check-only src/ tests/

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running mypy type checker...$(NC)"
	uv run mypy src/

test: ## Run tests with pytest
	@echo "$(BLUE)Running tests...$(NC)"
	uv run pytest

test-verbose: ## Run tests with verbose output
	@echo "$(BLUE)Running tests (verbose)...$(NC)"
	uv run pytest -vv

test-parallel: ## Run tests in parallel
	@echo "$(BLUE)Running tests in parallel...$(NC)"
	uv run pytest -n auto

coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	uv run pytest --cov=color_scheme --cov-report=html --cov-report=term

coverage-report: ## Open coverage report in browser
	@echo "$(BLUE)Opening coverage report...$(NC)"
	xdg-open htmlcov/index.html || open htmlcov/index.html

build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	uv build

check: lint type-check test ## Run all checks (lint, type-check, test)
	@echo "$(GREEN)All checks passed!$(NC)"

dev: install-dev ## Setup development environment
	@echo "$(GREEN)Development environment ready!$(NC)"
	@echo "Run 'source .venv/bin/activate' to activate the virtual environment"

run: ## Run the CLI (use ARGS="..." to pass arguments)
	@echo "$(BLUE)Running color-scheme $(ARGS)$(NC)"
	uv run color-scheme $(ARGS)

shell: ## Open a Python shell with the package loaded
	@echo "$(BLUE)Opening Python shell...$(NC)"
	uv run python

update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	uv sync --upgrade

lock: ## Update lock file without installing
	@echo "$(BLUE)Updating lock file...$(NC)"
	uv lock

# Docker targets
docker-build: docker-build-pywal docker-build-wallust docker-build-custom ## Build all Docker images

docker-build-pywal: ## Build pywal backend Docker image
	@echo "$(BLUE)Building pywal Docker image...$(NC)"
	docker build -f docker/Dockerfile.pywal -t colorscheme-generator:pywal .

docker-build-wallust: ## Build wallust backend Docker image
	@echo "$(BLUE)Building wallust Docker image...$(NC)"
	docker build -f docker/Dockerfile.wallust -t colorscheme-generator:wallust .

docker-build-custom: ## Build custom backend Docker image (requires backend.py)
	@if [ -f backend.py ]; then \
		echo "$(BLUE)Building custom Docker image...$(NC)"; \
		docker build -f docker/Dockerfile.custom -t colorscheme-generator:custom .; \
	else \
		echo "$(YELLOW)Skipping custom backend build (backend.py not found)$(NC)"; \
	fi

docker-clean: ## Remove all Docker images
	@echo "$(BLUE)Removing Docker images...$(NC)"
	docker rmi colorscheme-generator:pywal colorscheme-generator:wallust colorscheme-generator:custom || true

docker-test: docker-build ## Build images and run a test
	@echo "$(BLUE)Testing Docker setup...$(NC)"
	uv run color-scheme --list-backends

