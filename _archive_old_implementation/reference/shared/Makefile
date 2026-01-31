.PHONY: help install install-dev clean test lint format type-check build coverage

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@printf "$(BLUE)Color Scheme Shared Library$(NC)\n"
	@printf "\n"
	@printf "$(GREEN)Available targets:$(NC)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install the package
	@printf "$(BLUE)Installing colorscheme-shared...$(NC)\n"
	pip install -e .

install-dev: ## Install with development dependencies
	@printf "$(BLUE)Installing with dev dependencies...$(NC)\n"
	pip install -e ".[dev]"

clean: ## Remove build and test artifacts
	@printf "$(BLUE)Cleaning artifacts...$(NC)\n"
	rm -rf build dist .eggs
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache

test: ## Run tests
	@printf "$(BLUE)Running tests...$(NC)\n"
	pytest -q

test-verbose: ## Run tests with verbose output
	@printf "$(BLUE)Running tests (verbose)...$(NC)\n"
	pytest -vv

coverage: ## Run tests with coverage report
	@printf "$(BLUE)Running tests with coverage...$(NC)\n"
	pytest --cov=colorscheme_shared --cov-report=html --cov-report=term

lint: ## Check code style with ruff
	@printf "$(BLUE)Running ruff linter...$(NC)\n"
	ruff check src tests

lint-fix: ## Fix code style issues
	@printf "$(BLUE)Fixing code style...$(NC)\n"
	ruff check --fix src tests

format: ## Format code with black
	@printf "$(BLUE)Formatting code...$(NC)\n"
	black src tests

format-check: ## Check code formatting
	@printf "$(BLUE)Checking code format...$(NC)\n"
	black --check src tests

type-check: ## Run type checking with mypy
	@printf "$(BLUE)Running mypy...$(NC)\n"
	mypy src

check: lint type-check test ## Run all checks
	@printf "$(GREEN)All checks passed!$(NC)\n"

build: clean ## Build distribution packages
	@printf "$(BLUE)Building...$(NC)\n"
	python -m build
