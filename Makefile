.PHONY: help dev lint format build install-core install-orchestrator test-all pipeline

# Variables
PYTHON_VERSION := 3.12
UV := uv
PACKAGES_DIR := packages
CORE_DIR := $(PACKAGES_DIR)/core
ORCHESTRATOR_DIR := $(PACKAGES_DIR)/orchestrator
SETTINGS_DIR := $(PACKAGES_DIR)/settings
TOOLS_DIR := tools

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m

##@ General
.DEFAULT_GOAL := help
help:
	@echo "$(BLUE)color-scheme - Development Makefile$(NC)"
	@echo ""
	@echo "$(GREEN)Usage:$(NC)"
	@echo "  make $(BLUE)<target>$(NC)"
	@echo ""
	@echo "$(GREEN)Targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

##@ Setup & Installation
dev: install-deps ## Set up development environment
	@echo "$(GREEN)✓ Development environment ready$(NC)"

install-deps: ## Install all dependencies for development
	@echo "$(BLUE)Installing settings package...$(NC)"
	cd $(SETTINGS_DIR) && $(UV) sync --dev
	@echo "$(BLUE)Installing core package...$(NC)"
	cd $(CORE_DIR) && $(UV) sync --dev
	@echo "$(BLUE)Installing orchestrator package...$(NC)"
	cd $(ORCHESTRATOR_DIR) && $(UV) sync --dev
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

install-core: ## Install color-scheme-core package
	@echo "$(BLUE)Installing color-scheme-core...$(NC)"
	cd $(CORE_DIR) && $(UV) sync --dev
	@echo "$(GREEN)✓ color-scheme-core installed$(NC)"

install-orchestrator: ## Install color-scheme-orchestrator package
	@echo "$(BLUE)Installing color-scheme-orchestrator...$(NC)"
	cd $(ORCHESTRATOR_DIR) && $(UV) sync --dev
	@echo "$(GREEN)✓ color-scheme-orchestrator installed$(NC)"

##@ Code Quality
lint: lint-core lint-settings lint-orchestrator ## Run linting on all packages

lint-core: ## Lint core package
	@echo "$(BLUE)Linting core package...$(NC)"
	cd $(CORE_DIR) && $(UV) run ruff check .
	cd $(CORE_DIR) && $(UV) run black --check .
	cd $(CORE_DIR) && $(UV) run isort --check .
	cd $(CORE_DIR) && $(UV) run mypy src/
	@echo "$(GREEN)✓ Core package linting passed$(NC)"

lint-settings: ## Lint settings package
	@echo "$(BLUE)Linting settings package...$(NC)"
	cd $(SETTINGS_DIR) && $(UV) run ruff check .
	cd $(SETTINGS_DIR) && $(UV) run black --check .
	cd $(SETTINGS_DIR) && $(UV) run isort --check .
	@echo "$(GREEN)✓ Settings package linting passed$(NC)"

lint-orchestrator: ## Lint orchestrator package
	@echo "$(BLUE)Linting orchestrator package...$(NC)"
	cd $(ORCHESTRATOR_DIR) && $(UV) run ruff check .
	cd $(ORCHESTRATOR_DIR) && $(UV) run black --check .
	cd $(ORCHESTRATOR_DIR) && $(UV) run isort --check .
	cd $(ORCHESTRATOR_DIR) && $(UV) run mypy src/
	@echo "$(GREEN)✓ Orchestrator package linting passed$(NC)"

format: format-core format-settings format-orchestrator ## Format all code in packages

format-core: ## Format core package
	@echo "$(BLUE)Formatting core package...$(NC)"
	cd $(CORE_DIR) && $(UV) run black .
	cd $(CORE_DIR) && $(UV) run isort .
	cd $(CORE_DIR) && $(UV) run ruff check --fix .
	@echo "$(GREEN)✓ Core package formatted$(NC)"

format-settings: ## Format settings package
	@echo "$(BLUE)Formatting settings package...$(NC)"
	cd $(SETTINGS_DIR) && $(UV) run black .
	cd $(SETTINGS_DIR) && $(UV) run isort .
	cd $(SETTINGS_DIR) && $(UV) run ruff check --fix .
	@echo "$(GREEN)✓ Settings package formatted$(NC)"

format-orchestrator: ## Format orchestrator package
	@echo "$(BLUE)Formatting orchestrator package...$(NC)"
	cd $(ORCHESTRATOR_DIR) && $(UV) run black .
	cd $(ORCHESTRATOR_DIR) && $(UV) run isort .
	cd $(ORCHESTRATOR_DIR) && $(UV) run ruff check --fix .
	@echo "$(GREEN)✓ Orchestrator package formatted$(NC)"

##@ Security
security: security-core security-settings security-orchestrator ## Run security scans on all packages

security-core: ## Security scan for core package
	@echo "$(BLUE)Running security scan on core package...$(NC)"
	cd $(CORE_DIR) && $(UV) run bandit -r src/ -f json -o bandit-report.json
	@echo "$(GREEN)✓ Core security scan complete$(NC)"

security-settings: ## Security scan for settings package
	@echo "$(BLUE)Running security scan on settings package...$(NC)"
	cd $(SETTINGS_DIR) && $(UV) run bandit -r src/ -f json -o bandit-report.json
	@echo "$(GREEN)✓ Settings security scan complete$(NC)"

security-orchestrator: ## Security scan for orchestrator package
	@echo "$(BLUE)Running security scan on orchestrator package...$(NC)"
	cd $(ORCHESTRATOR_DIR) && $(UV) run bandit -r src/ -f json -o bandit-report.json
	@echo "$(GREEN)✓ Orchestrator security scan complete$(NC)"

##@ Testing
test-all: ## Run all tests (matches tools/test-all-commands.sh)
	@echo "$(BLUE)Running comprehensive test suite...$(NC)"
	@bash $(TOOLS_DIR)/test-all-commands.sh

test-core: ## Test core package
	@echo "$(BLUE)Testing core package...$(NC)"
	cd $(CORE_DIR) && $(UV) run pytest -n auto --cov=src --cov-report=term
	cd $(CORE_DIR) && $(UV) run coverage report --fail-under=95

test-settings: ## Test settings package
	@echo "$(BLUE)Testing settings package...$(NC)"
	cd $(SETTINGS_DIR) && $(UV) run pytest -n auto --cov=src --cov-report=term
	cd $(SETTINGS_DIR) && $(UV) run coverage report --fail-under=95

test-orchestrator: ## Test orchestrator package
	@echo "$(BLUE)Testing orchestrator package...$(NC)"
	cd $(ORCHESTRATOR_DIR) && $(UV) run pytest -n auto --cov=src --cov-report=term

##@ Building
build: build-core build-settings build-orchestrator ## Build all packages

build-core: ## Build core package
	@echo "$(BLUE)Building core package...$(NC)"
	cd $(CORE_DIR) && $(UV) build
	@echo "$(GREEN)✓ Core package built$(NC)"

build-settings: ## Build settings package
	@echo "$(BLUE)Building settings package...$(NC)"
	cd $(SETTINGS_DIR) && $(UV) build
	@echo "$(GREEN)✓ Settings package built$(NC)"

build-orchestrator: ## Build orchestrator package
	@echo "$(BLUE)Building orchestrator package...$(NC)"
	cd $(ORCHESTRATOR_DIR) && $(UV) build
	@echo "$(GREEN)✓ Orchestrator package built$(NC)"

##@ CI/CD Pipeline
pipeline: ## Validate pipeline - simulate GitHub Actions workflows locally
	@echo "$(BLUE)Running pipeline validation...$(NC)"
	@echo ""
	@echo "$(BLUE)Step 1: Linting (Core)$(NC)"
	@cd $(CORE_DIR) && $(UV) run ruff check . && $(UV) run black --check . && $(UV) run isort --check . && $(UV) run mypy src/
	@echo "$(GREEN)✓ Linting passed$(NC)"
	@echo ""
	@echo "$(BLUE)Step 2: Security Scan (Core)$(NC)"
	@cd $(CORE_DIR) && $(UV) run bandit -r src/ -f json -o bandit-report.json
	@echo "$(GREEN)✓ Security scan passed$(NC)"
	@echo ""
	@echo "$(BLUE)Step 3: Testing (Core) - Python 3.12$(NC)"
	@cd $(CORE_DIR) && $(UV) run pytest -n auto --cov=src --cov-report=xml --cov-report=term
	@cd $(CORE_DIR) && $(UV) run coverage report --fail-under=95
	@echo "$(GREEN)✓ Tests passed with 95%+ coverage$(NC)"
	@echo ""
	@echo "$(GREEN)✓✓✓ Pipeline validation successful! $(NC)"
	@echo "$(GREEN)Your changes are safe to push to the cloud.$(NC)"
	@echo ""

##@ Cleanup
clean: ## Remove build artifacts and caches
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	rm -rf /tmp/color-scheme-test
	@echo "$(GREEN)✓ Cleanup complete$(NC)"
