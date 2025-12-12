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
	@printf "$(BLUE)Color Scheme Generator - Orchestrator$(NC)\n"
	@printf "\n"
	@printf "$(GREEN)Available targets:$(NC)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install the package with uv
	@printf "$(BLUE)Installing color-scheme orchestrator...$(NC)\n"
	uv sync

install-dev: ## Install the package with development dependencies
	@printf "$(BLUE)Installing color-scheme orchestrator with dev dependencies...$(NC)\n"
	uv sync --all-extras --dev

venv: ## Create a new virtual environment
	@printf "$(BLUE)Creating virtual environment...$(NC)\n"
	uv venv

clean: clean-build clean-pyc clean-test ## Remove all build, test, coverage and Python artifacts

clean-build: ## Remove build artifacts
	@printf "$(BLUE)Cleaning build artifacts...$(NC)\n"
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## Remove Python file artifacts
	@printf "$(BLUE)Cleaning Python artifacts...$(NC)\n"
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test: ## Remove test and coverage artifacts
	@printf "$(BLUE)Cleaning test artifacts...$(NC)\n"
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

lint: ## Check code style with ruff
	@printf "$(BLUE)Running ruff linter...$(NC)\n"
	uv run ruff check src/ tests/

lint-fix: ## Fix code style issues with ruff
	@printf "$(BLUE)Fixing code style with ruff...$(NC)\n"
	uv run ruff check --fix src/ tests/

format: ## Format code with black and isort
	@printf "$(BLUE)Formatting code with black...$(NC)\n"
	uv run black src/ tests/
	@printf "$(BLUE)Sorting imports with isort...$(NC)\n"
	uv run isort src/ tests/

format-check: ## Check code formatting without making changes
	@printf "$(BLUE)Checking code format...$(NC)\n"
	uv run black --check src/ tests/
	uv run isort --check-only src/ tests/

type-check: ## Run type checking with mypy
	@printf "$(BLUE)Running mypy type checker...$(NC)\n"
	uv run mypy src/

test: ## Run tests with pytest
	@printf "$(BLUE)Running tests...$(NC)\n"
	uv run pytest

test-verbose: ## Run tests with verbose output
	@printf "$(BLUE)Running tests (verbose)...$(NC)\n"
	uv run pytest -vv

test-parallel: ## Run tests in parallel
	@printf "$(BLUE)Running tests in parallel...$(NC)\n"
	uv run pytest -n auto

coverage: ## Run tests with coverage report
	@printf "$(BLUE)Running tests with coverage...$(NC)\n"
	uv run pytest --cov=color_scheme --cov-report=html --cov-report=term

coverage-report: ## Open coverage report in browser
	@printf "$(BLUE)Opening coverage report...$(NC)\n"
	xdg-open htmlcov/index.html || open htmlcov/index.html

build: clean ## Build distribution packages
	@printf "$(BLUE)Building distribution packages...$(NC)\n"
	uv build

check: lint type-check test ## Run all checks (lint, type-check, test)
	@printf "$(GREEN)All checks passed!$(NC)\n"

dev: install-dev ## Setup development environment
	@printf "$(GREEN)Development environment ready!$(NC)\n"
	@printf "Run 'uv run color-scheme' to use the CLI\n"

run: ## Run the CLI (use ARGS="..." to pass arguments)
	@printf "$(BLUE)Running color-scheme $(ARGS)$(NC)\n"
	uv run color-scheme $(ARGS)

shell: ## Open a Python shell with the package loaded
	@printf "$(BLUE)Opening Python shell...$(NC)\n"
	uv run python

update: ## Update dependencies
	@printf "$(BLUE)Updating dependencies...$(NC)\n"
	uv sync --upgrade

lock: ## Update lock file without installing
	@printf "$(BLUE)Updating lock file...$(NC)\n"
	uv lock

# Docker targets
docker-build: docker-build-pywal docker-build-wallust docker-build-custom ## Build all Docker images

docker-build-pywal: ## Build pywal backend Docker image
	@printf "$(BLUE)Building pywal Docker image...$(NC)\n"
	cd .. && docker build -f orchestrator/docker/Dockerfile.pywal -t color-scheme-pywal:latest .

docker-build-wallust: ## Build wallust backend Docker image
	@printf "$(BLUE)Building wallust Docker image...$(NC)\n"
	docker build -f docker/Dockerfile.wallust -t color-scheme-wallust:latest .

docker-build-custom: ## Build custom backend Docker image (requires backend.py)
	@if [ -f backend.py ]; then \
		printf "$(BLUE)Building custom Docker image...$(NC)\n"; \
		docker build -f docker/Dockerfile.custom -t color-scheme-custom:latest .; \
	else \
		printf "$(YELLOW)Skipping custom backend build (backend.py not found)$(NC)\n"; \
	fi

docker-clean: ## Remove all Docker images
	@printf "$(BLUE)Removing Docker images...$(NC)\n"
	docker rmi color-scheme-pywal:latest color-scheme-wallust:latest color-scheme-custom:latest || true

docker-test: docker-build ## Build images and run a test
	@printf "$(BLUE)Testing Docker setup...$(NC)\n"
	uv run color-scheme --list-backends

