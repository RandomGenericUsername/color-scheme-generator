.PHONY: help dev lint format build install-core install-orchestrator install-settings install-templates test-all test-run pipeline lint-templates format-templates security-templates test-templates push clean

# Variables
PYTHON_VERSION := 3.12
UV := uv
PACKAGES_DIR := packages
CORE_DIR := $(PACKAGES_DIR)/core
ORCHESTRATOR_DIR := $(PACKAGES_DIR)/orchestrator
SETTINGS_DIR := $(PACKAGES_DIR)/settings
TEMPLATES_DIR := $(PACKAGES_DIR)/templates
TOOLS_DIR := tools
DEV_DIR := $(TOOLS_DIR)/dev

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m

##@ General
.DEFAULT_GOAL := help
help:
	@echo -e "$(BLUE)color-scheme - Development Makefile$(NC)"
	@echo -e ""
	@echo -e "$(GREEN)Usage:$(NC)"
	@echo -e "  make $(BLUE)<target>$(NC)"
	@echo -e ""
	@echo -e "$(GREEN)Targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-25s$(NC) %s\n", $$1, $$2}'

##@ Setup & Installation
dev: install-deps ## Set up development environment
	@echo -e "$(GREEN)✓ Development environment ready$(NC)"

install-deps: ## Install all dependencies for development
	@echo -e "$(BLUE)Installing all packages in workspace...$(NC)"
	$(UV) sync --dev --all-packages
	@echo -e "$(GREEN)✓ All dependencies installed$(NC)"

install-core: ## Install color-scheme-core package
	@echo -e "$(BLUE)Installing color-scheme-core...$(NC)"
	cd $(CORE_DIR) && $(UV) sync --dev
	@echo -e "$(GREEN)✓ color-scheme-core installed$(NC)"

install-orchestrator: ## Install color-scheme-orchestrator package
	@echo -e "$(BLUE)Installing color-scheme-orchestrator...$(NC)"
	cd $(ORCHESTRATOR_DIR) && $(UV) sync --dev
	@echo -e "$(GREEN)✓ color-scheme-orchestrator installed$(NC)"

install-settings: ## Install color-scheme-settings package
	@echo -e "$(BLUE)Installing color-scheme-settings...$(NC)"
	cd $(SETTINGS_DIR) && $(UV) sync --dev
	@echo -e "$(GREEN)✓ color-scheme-settings installed$(NC)"

install-templates: ## Install color-scheme-templates package
	@echo -e "$(BLUE)Installing color-scheme-templates...$(NC)"
	cd $(TEMPLATES_DIR) && $(UV) sync --dev
	@echo -e "$(GREEN)✓ color-scheme-templates installed$(NC)"

##@ Code Quality
lint: lint-core lint-settings lint-templates lint-orchestrator ## Run linting on all packages

lint-core: ## Lint core package
	@echo -e "$(BLUE)Linting core package...$(NC)"
	@$(UV) run ruff check --line-length 88 $(CORE_DIR) || (echo -e "$(RED)Ruff found issues. Run: make format-core$(NC)" && exit 1)
	@$(UV) run black --check --line-length 88 $(CORE_DIR) || (echo -e "$(RED)Black formatting needed. Run: make format-core$(NC)" && exit 1)
	@$(UV) run isort --check --profile black --line-length 88 $(CORE_DIR) || (echo -e "$(RED)Import sorting needed. Run: make format-core$(NC)" && exit 1)
	@$(UV) run mypy $(CORE_DIR)/src/ || (echo -e "$(RED)Type errors found. Run: $(UV) run mypy $(CORE_DIR)/src/ to see details$(NC)" && exit 1)
	@echo -e "$(GREEN)✓ Core package linting passed$(NC)"

lint-settings: ## Lint settings package
	@echo -e "$(BLUE)Linting settings package...$(NC)"
	@$(UV) run ruff check --line-length 88 $(SETTINGS_DIR) || (echo -e "$(RED)Ruff found issues. Run: make format-settings$(NC)" && exit 1)
	@$(UV) run black --check --line-length 88 $(SETTINGS_DIR) || (echo -e "$(RED)Black formatting needed. Run: make format-settings$(NC)" && exit 1)
	@$(UV) run isort --check --profile black --line-length 88 $(SETTINGS_DIR) || (echo -e "$(RED)Import sorting needed. Run: make format-settings$(NC)" && exit 1)
	@echo -e "$(GREEN)✓ Settings package linting passed$(NC)"

lint-templates: ## Lint templates package
	@echo -e "$(BLUE)Linting templates package...$(NC)"
	@$(UV) run ruff check --line-length 88 $(TEMPLATES_DIR) || (echo -e "$(RED)Ruff found issues. Run: make format-templates$(NC)" && exit 1)
	@$(UV) run black --check --line-length 88 $(TEMPLATES_DIR) || (echo -e "$(RED)Black formatting needed. Run: make format-templates$(NC)" && exit 1)
	@$(UV) run isort --check --profile black --line-length 88 $(TEMPLATES_DIR) || (echo -e "$(RED)Import sorting needed. Run: make format-templates$(NC)" && exit 1)
	@echo -e "$(GREEN)✓ Templates package linting passed$(NC)"

lint-orchestrator: ## Lint orchestrator package
	@echo -e "$(BLUE)Linting orchestrator package...$(NC)"
	@$(UV) run ruff check --line-length 88 $(ORCHESTRATOR_DIR) || (echo -e "$(RED)Ruff found issues. Run: make format-orchestrator$(NC)" && exit 1)
	@$(UV) run black --check --line-length 88 $(ORCHESTRATOR_DIR) || (echo -e "$(RED)Black formatting needed. Run: make format-orchestrator$(NC)" && exit 1)
	@$(UV) run isort --check --profile black --line-length 88 $(ORCHESTRATOR_DIR) || (echo -e "$(RED)Import sorting needed. Run: make format-orchestrator$(NC)" && exit 1)
	@$(UV) run mypy $(ORCHESTRATOR_DIR)/src/ || (echo -e "$(RED)Type errors found. Run: $(UV) run mypy $(ORCHESTRATOR_DIR)/src/ to see details$(NC)" && exit 1)
	@echo -e "$(GREEN)✓ Orchestrator package linting passed$(NC)"

format: format-core format-settings format-templates format-orchestrator ## Format all code in packages

format-core: ## Format core package
	@echo -e "$(BLUE)Formatting core package...$(NC)"
	$(UV) run isort --profile black --line-length 88 $(CORE_DIR)
	$(UV) run black --line-length 88 $(CORE_DIR)
	$(UV) run ruff check --fix --line-length 88 $(CORE_DIR)
	@echo -e "$(GREEN)✓ Core package formatted$(NC)"

format-settings: ## Format settings package
	@echo -e "$(BLUE)Formatting settings package...$(NC)"
	$(UV) run isort --profile black --line-length 88 $(SETTINGS_DIR)
	$(UV) run black --line-length 88 $(SETTINGS_DIR)
	$(UV) run ruff check --fix --line-length 88 $(SETTINGS_DIR)
	@echo -e "$(GREEN)✓ Settings package formatted$(NC)"

format-templates: ## Format templates package
	@echo -e "$(BLUE)Formatting templates package...$(NC)"
	$(UV) run isort --profile black --line-length 88 $(TEMPLATES_DIR)
	$(UV) run black --line-length 88 $(TEMPLATES_DIR)
	$(UV) run ruff check --fix --line-length 88 $(TEMPLATES_DIR)
	@echo -e "$(GREEN)✓ Templates package formatted$(NC)"

format-orchestrator: ## Format orchestrator package
	@echo -e "$(BLUE)Formatting orchestrator package...$(NC)"
	$(UV) run isort --profile black --line-length 88 $(ORCHESTRATOR_DIR)
	$(UV) run black --line-length 88 $(ORCHESTRATOR_DIR)
	$(UV) run ruff check --fix --line-length 88 $(ORCHESTRATOR_DIR)
	@echo -e "$(GREEN)✓ Orchestrator package formatted$(NC)"

##@ Security
security: security-core security-settings security-templates security-orchestrator ## Run security scans on all packages

security-core: ## Security scan for core package
	@echo -e "$(BLUE)Running security scan on core package...$(NC)"
	cd $(CORE_DIR) && $(UV) run bandit -r src/ -ll -f json -o bandit-report.json
	@echo -e "$(GREEN)✓ Core security scan complete$(NC)"

security-settings: ## Security scan for settings package
	@echo -e "$(BLUE)Running security scan on settings package...$(NC)"
	cd $(SETTINGS_DIR) && $(UV) run bandit -r src/ -ll -f json -o bandit-report.json
	@echo -e "$(GREEN)✓ Settings security scan complete$(NC)"

security-templates: ## Security scan for templates package
	@echo -e "$(BLUE)Running security scan on templates package...$(NC)"
	cd $(TEMPLATES_DIR) && $(UV) run bandit -r src/ -ll -f json -o bandit-report.json
	@echo -e "$(GREEN)✓ Templates security scan complete$(NC)"

security-orchestrator: ## Security scan for orchestrator package
	@echo -e "$(BLUE)Running security scan on orchestrator package...$(NC)"
	cd $(ORCHESTRATOR_DIR) && $(UV) run bandit -r src/ -ll -f json -o bandit-report.json
	@echo -e "$(GREEN)✓ Orchestrator security scan complete$(NC)"

##@ Testing
test-run: ## Run all tests with wallpaper - usage: make test-all WALLPAPER=path/to/wallpaper.jpg
	@if [ -z "$(WALLPAPER)" ]; then \
		echo -e "$(RED)Error: WALLPAPER argument is required$(NC)"; \
		echo -e "Usage: make test-all WALLPAPER=path/to/wallpaper.jpg"; \
		exit 1; \
	fi
	@echo -e "$(BLUE)Running comprehensive test suite with wallpaper: $(WALLPAPER)$(NC)"
	@bash $(DEV_DIR)/test-all-commands.sh "$(WALLPAPER)"

test-all: test-core test-settings test-templates test-orchestrator ## Run full Python test suite
	@echo -e "$(GREEN)✓ All package tests completed$(NC)"

test-core: ## Test core package
	@echo -e "$(BLUE)Testing core package...$(NC)"
	cd $(CORE_DIR) && $(UV) run pytest -n auto --color=yes --cov=src --cov-report=term
	cd $(CORE_DIR) && $(UV) run coverage report --fail-under=95

test-settings: ## Test settings package
	@echo -e "$(BLUE)Testing settings package...$(NC)"
	cd $(SETTINGS_DIR) && $(UV) run pytest -n auto --color=yes --cov=src --cov-report=term
	cd $(SETTINGS_DIR) && $(UV) run coverage report --fail-under=95

test-templates: ## Test templates package
	@echo -e "$(BLUE)Testing templates package...$(NC)"
	cd $(TEMPLATES_DIR) && $(UV) run pytest -n auto --color=yes --cov=src --cov-report=term
	cd $(TEMPLATES_DIR) && $(UV) run coverage report --fail-under=95

test-orchestrator: ## Test orchestrator package
	@echo -e "$(BLUE)Testing orchestrator package...$(NC)"
	cd $(ORCHESTRATOR_DIR) && $(UV) run pytest -n auto --color=yes --cov=src --cov-report=term
	cd $(ORCHESTRATOR_DIR) && $(UV) run coverage report --fail-under=95

##@ Building
build: build-core build-settings build-templates build-orchestrator ## Build all packages

build-core: ## Build core package
	@echo -e "$(BLUE)Building core package...$(NC)"
	cd $(CORE_DIR) && $(UV) build
	@echo -e "$(GREEN)✓ Core package built$(NC)"

build-settings: ## Build settings package
	@echo -e "$(BLUE)Building settings package...$(NC)"
	cd $(SETTINGS_DIR) && $(UV) build
	@echo -e "$(GREEN)✓ Settings package built$(NC)"

build-templates: ## Build templates package
	@echo -e "$(BLUE)Building templates package...$(NC)"
	cd $(TEMPLATES_DIR) && $(UV) build
	@echo -e "$(GREEN)✓ Templates package built$(NC)"

build-orchestrator: ## Build orchestrator package
	@echo -e "$(BLUE)Building orchestrator package...$(NC)"
	cd $(ORCHESTRATOR_DIR) && $(UV) build
	@echo -e "$(GREEN)✓ Orchestrator package built$(NC)"

##@ Smoke Testing
SMOKE_TEST_WALLPAPER := tests/fixtures/test-wallpaper.jpg
SMOKE_TEST_SCRIPT := tests/smoke/run-smoke-tests.sh

.PHONY: smoke-test-check-deps smoke-test-custom smoke-test-pywal smoke-test-wallust smoke-test

smoke-test-check-deps: ## Check smoke test dependencies
	@echo -e "$(BLUE)Checking smoke test dependencies...$(NC)"
	@# Check test wallpaper exists
	@if [ ! -f "$(SMOKE_TEST_WALLPAPER)" ]; then \
		echo -e "$(RED)✗ Test wallpaper not found at $(SMOKE_TEST_WALLPAPER)$(NC)"; \
		exit 1; \
	fi
	@echo -e "$(GREEN)✓ Test wallpaper available$(NC)"
	@# Check ImageMagick
	@if ! command -v magick &> /dev/null; then \
		echo -e "$(RED)✗ ImageMagick (magick) not found$(NC)"; \
		echo -e "$(RED)  Install: sudo apt-get install imagemagick$(NC)"; \
		echo -e "$(RED)  Or macOS: brew install imagemagick$(NC)"; \
		echo -e "$(RED)  Or Fedora: sudo dnf install ImageMagick$(NC)"; \
		exit 1; \
	fi
	@echo -e "$(GREEN)✓ ImageMagick available: $$(magick --version | head -1)$(NC)"
	@# Check Docker or Podman
	@if ! command -v docker &> /dev/null && ! command -v podman &> /dev/null; then \
		echo -e "$(RED)✗ Docker or Podman not found$(NC)"; \
		echo -e "$(RED)  Install Docker: https://docs.docker.com/get-docker/$(NC)"; \
		echo -e "$(RED)  Or Podman: sudo apt-get install podman$(NC)"; \
		exit 1; \
	fi
	@if command -v docker &> /dev/null; then \
		echo -e "$(GREEN)✓ Docker available: $$(docker --version)$(NC)"; \
	else \
		echo -e "$(GREEN)✓ Podman available: $$(podman --version)$(NC)"; \
	fi
	@# Check smoke test script exists
	@if [ ! -f "$(SMOKE_TEST_SCRIPT)" ]; then \
		echo -e "$(RED)✗ Smoke test script not found at $(SMOKE_TEST_SCRIPT)$(NC)"; \
		exit 1; \
	fi
	@echo -e "$(GREEN)✓ Smoke test script available$(NC)"

smoke-test-custom: smoke-test-check-deps ## Run smoke tests with custom backend only
	@echo -e "$(BLUE)Running smoke tests: Custom Backend$(NC)"
	@if [ "$(VERBOSE)" = "true" ]; then \
		bash $(SMOKE_TEST_SCRIPT) --verbose $(SMOKE_TEST_WALLPAPER); \
	else \
		bash $(SMOKE_TEST_SCRIPT) $(SMOKE_TEST_WALLPAPER); \
	fi
	@echo -e "$(GREEN)✓ Custom backend smoke tests completed$(NC)"

smoke-test-pywal: smoke-test-check-deps ## Run smoke tests with pywal backend only
	@echo -e "$(BLUE)Running smoke tests: Pywal Backend$(NC)"
	@# Check if pywal is installed
	@if ! command -v wal &> /dev/null; then \
		echo -e "$(YELLOW)⚠ Pywal not installed, install with: pip install pywal$(NC)"; \
		echo -e "$(YELLOW)⊘ Skipping pywal smoke tests$(NC)"; \
		exit 0; \
	fi
	@if [ "$(VERBOSE)" = "true" ]; then \
		bash $(SMOKE_TEST_SCRIPT) --verbose $(SMOKE_TEST_WALLPAPER); \
	else \
		bash $(SMOKE_TEST_SCRIPT) $(SMOKE_TEST_WALLPAPER); \
	fi
	@echo -e "$(GREEN)✓ Pywal backend smoke tests completed$(NC)"

smoke-test-wallust: smoke-test-check-deps ## Run smoke tests with wallust backend only
	@echo -e "$(BLUE)Running smoke tests: Wallust Backend$(NC)"
	@# Check if wallust is installed
	@if ! command -v wallust &> /dev/null; then \
		echo -e "$(YELLOW)⚠ Wallust not installed, install with: cargo install wallust$(NC)"; \
		echo -e "$(YELLOW)⊘ Skipping wallust smoke tests$(NC)"; \
		exit 0; \
	fi
	@if [ "$(VERBOSE)" = "true" ]; then \
		bash $(SMOKE_TEST_SCRIPT) --verbose $(SMOKE_TEST_WALLPAPER); \
	else \
		bash $(SMOKE_TEST_SCRIPT) $(SMOKE_TEST_WALLPAPER); \
	fi
	@echo -e "$(GREEN)✓ Wallust backend smoke tests completed$(NC)"

smoke-test: smoke-test-check-deps ## Run all smoke tests (all backends)
	@echo -e "$(BLUE)Running smoke tests: All Backends$(NC)"
	@echo -e ""
	@# Run custom (always available)
	@$(MAKE) smoke-test-custom
	@echo -e ""
	@# Run pywal if available
	@if command -v wal &> /dev/null; then \
		$(MAKE) smoke-test-pywal; \
	else \
		echo -e "$(YELLOW)⊘ Skipping pywal smoke tests (not installed)$(NC)"; \
	fi
	@echo -e ""
	@# Run wallust if available
	@if command -v wallust &> /dev/null; then \
		$(MAKE) smoke-test-wallust; \
	else \
		echo -e "$(YELLOW)⊘ Skipping wallust smoke tests (not installed)$(NC)"; \
	fi
	@echo -e ""
	@echo -e "$(GREEN)✓ All available smoke tests completed$(NC)"

##@ CI/CD Pipeline
pipeline: ## Validate pipeline - simulate GitHub Actions workflows locally
	@echo -e "$(BLUE)Running pipeline validation...$(NC)"
	@echo -e ""
	@echo -e "$(BLUE)Step 1: Linting (All packages)$(NC)"
	@$(MAKE) lint
	@echo -e "$(GREEN)✓ Linting passed$(NC)"
	@echo -e ""
	@echo -e "$(BLUE)Step 2: Security Scan (All packages)$(NC)"
	@$(MAKE) security
	@echo -e "$(GREEN)✓ Security scans passed$(NC)"
	@echo -e ""
	@echo -e "$(BLUE)Step 3: Testing (All packages)$(NC)"
	@$(MAKE) test-all
	@echo -e "$(GREEN)✓ Tests passed with 95%+ coverage$(NC)"
	@echo -e ""
	@echo -e "$(GREEN)✓✓✓ Pipeline validation successful! $(NC)"
	@echo -e "$(GREEN)Your changes are safe to push to the cloud.$(NC)"
	@echo -e ""

push: ## Run GitHub Actions workflows locally (add SMOKE=true for smoke tests)
	@echo -e "$(BLUE)Setting up GitHub Actions locally...$(NC)"
	@if [ ! -f ./bin/act ]; then \
		echo -e "$(BLUE)Downloading act (GitHub Actions CLI)...$(NC)"; \
		mkdir -p ./bin; \
		curl -sL https://github.com/nektos/act/releases/download/v0.2.65/act_Linux_x86_64.tar.gz -o /tmp/act.tar.gz; \
		tar -xzf /tmp/act.tar.gz -C ./bin; \
		rm /tmp/act.tar.gz; \
		echo -e "$(GREEN)✓ act installed to ./bin/act$(NC)"; \
	else \
		echo -e "$(GREEN)✓ act already available$(NC)"; \
	fi
	@echo -e ""
	@mkdir -p .logs
	@TIMESTAMP=$$(date +%Y%m%d-%H%M%S); \
	LOG_FILE=".logs/make-push-$$TIMESTAMP.log"; \
	if [ "$(SMOKE)" = "true" ]; then \
		echo -e "$(BLUE)═══════════════════════════════════════════════════════════$(NC)" | tee "$$LOG_FILE"; \
		echo -e "$(BLUE)Running GitHub Actions with SMOKE TESTS enabled$(NC)" | tee -a "$$LOG_FILE"; \
		echo -e "$(BLUE)═══════════════════════════════════════════════════════════$(NC)" | tee -a "$$LOG_FILE"; \
		echo -e "$(BLUE)Phase 1: Standard CI (4 package workflows)$(NC)" | tee -a "$$LOG_FILE"; \
		echo -e "$(BLUE)Phase 2: Smoke Tests (3 backend workflows)$(NC)" | tee -a "$$LOG_FILE"; \
		echo -e "$(BLUE)Logs: $$LOG_FILE$(NC)" | tee -a "$$LOG_FILE"; \
		echo -e "$(BLUE)═══════════════════════════════════════════════════════════$(NC)" | tee -a "$$LOG_FILE"; \
		echo -e "" | tee -a "$$LOG_FILE"; \
		echo -e "$(BLUE)───────────────────────────────────────────────────────────$(NC)" | tee -a "$$LOG_FILE"; \
		echo -e "$(BLUE)PHASE 1: Standard CI Workflows$(NC)" | tee -a "$$LOG_FILE"; \
		echo -e "$(BLUE)───────────────────────────────────────────────────────────$(NC)" | tee -a "$$LOG_FILE"; \
		./bin/act push 2>&1 | tee -a "$$LOG_FILE"; \
		STANDARD_EXIT=$${PIPESTATUS[0]}; \
		echo -e "" | tee -a "$$LOG_FILE"; \
		if [ $$STANDARD_EXIT -eq 0 ]; then \
			echo -e "$(GREEN)✓ Standard CI passed$(NC)" | tee -a "$$LOG_FILE"; \
			echo -e "" | tee -a "$$LOG_FILE"; \
			echo -e "$(BLUE)───────────────────────────────────────────────────────────$(NC)" | tee -a "$$LOG_FILE"; \
			echo -e "$(BLUE)PHASE 2: Smoke Test Workflows$(NC)" | tee -a "$$LOG_FILE"; \
			echo -e "$(BLUE)───────────────────────────────────────────────────────────$(NC)" | tee -a "$$LOG_FILE"; \
			SMOKE_FAILED=0; \
			echo -e "$(BLUE)Running: Custom Backend Smoke Test$(NC)" | tee -a "$$LOG_FILE"; \
			./bin/act workflow_dispatch -W .github/workflows/smoke-test-custom.yml 2>&1 | tee -a "$$LOG_FILE"; \
			ACT_EXIT=$${PIPESTATUS[0]}; \
			if [ $$ACT_EXIT -ne 0 ]; then SMOKE_FAILED=$$((SMOKE_FAILED + 1)); fi; \
			echo -e "" | tee -a "$$LOG_FILE"; \
			echo -e "$(BLUE)Running: Pywal Backend Smoke Test$(NC)" | tee -a "$$LOG_FILE"; \
			./bin/act workflow_dispatch -W .github/workflows/smoke-test-pywal.yml 2>&1 | tee -a "$$LOG_FILE"; \
			ACT_EXIT=$${PIPESTATUS[0]}; \
			if [ $$ACT_EXIT -ne 0 ]; then SMOKE_FAILED=$$((SMOKE_FAILED + 1)); fi; \
			echo -e "" | tee -a "$$LOG_FILE"; \
			echo -e "$(BLUE)Running: Wallust Backend Smoke Test$(NC)" | tee -a "$$LOG_FILE"; \
			./bin/act workflow_dispatch -W .github/workflows/smoke-test-wallust.yml 2>&1 | tee -a "$$LOG_FILE"; \
			ACT_EXIT=$${PIPESTATUS[0]}; \
			if [ $$ACT_EXIT -ne 0 ]; then SMOKE_FAILED=$$((SMOKE_FAILED + 1)); fi; \
			echo -e "" | tee -a "$$LOG_FILE"; \
			if [ $$SMOKE_FAILED -eq 0 ]; then \
				echo -e "$(GREEN)✓ All smoke tests passed (3/3)$(NC)" | tee -a "$$LOG_FILE"; \
				EXIT_CODE=0; \
			else \
				echo -e "$(RED)✗ Some smoke tests failed ($$SMOKE_FAILED/3)$(NC)" | tee -a "$$LOG_FILE"; \
				EXIT_CODE=1; \
			fi; \
		else \
			echo -e "$(RED)✗ Standard CI failed, skipping smoke tests$(NC)" | tee -a "$$LOG_FILE"; \
			EXIT_CODE=$$STANDARD_EXIT; \
		fi; \
	else \
		echo -e "$(BLUE)═══════════════════════════════════════════════════════════$(NC)" | tee "$$LOG_FILE"; \
		echo -e "$(BLUE)Running Standard GitHub Actions Workflows$(NC)" | tee -a "$$LOG_FILE"; \
		echo -e "$(BLUE)═══════════════════════════════════════════════════════════$(NC)" | tee -a "$$LOG_FILE"; \
		echo -e "$(BLUE)Logs: $$LOG_FILE$(NC)" | tee -a "$$LOG_FILE"; \
		echo -e "$(YELLOW)Tip: Add SMOKE=true to include smoke tests$(NC)" | tee -a "$$LOG_FILE"; \
		echo -e "$(BLUE)═══════════════════════════════════════════════════════════$(NC)" | tee -a "$$LOG_FILE"; \
		echo -e "" | tee -a "$$LOG_FILE"; \
		./bin/act push 2>&1 | tee -a "$$LOG_FILE"; \
		EXIT_CODE=$${PIPESTATUS[0]}; \
	fi; \
	echo -e "" | tee -a "$$LOG_FILE"; \
	echo -e "$(BLUE)═══════════════════════════════════════════════════════════$(NC)" | tee -a "$$LOG_FILE"; \
	if [ $$EXIT_CODE -eq 0 ]; then \
		echo -e "$(GREEN)✓ GitHub Actions simulation complete$(NC)" | tee -a "$$LOG_FILE"; \
	else \
		echo -e "$(RED)✗ GitHub Actions simulation failed (exit: $$EXIT_CODE)$(NC)" | tee -a "$$LOG_FILE"; \
	fi; \
	echo -e "$(BLUE)═══════════════════════════════════════════════════════════$(NC)" | tee -a "$$LOG_FILE"; \
	echo -e "" | tee -a "$$LOG_FILE"; \
	echo -e "$(GREEN)📋 Full logs: $$LOG_FILE$(NC)"; \
	echo -e "$(GREEN)View logs: cat $$LOG_FILE$(NC)"; \
	echo -e "$(GREEN)Search: grep 'PASSED\|FAILED' $$LOG_FILE$(NC)"; \
	echo -e ""; \
	exit $$EXIT_CODE

##@ Cleanup
clean: ## Remove build artifacts and caches
	@echo -e "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type f -name "bandit-report.json" -delete
	rm -rf /tmp/color-scheme-test
	@echo -e "$(GREEN)✓ Cleanup complete$(NC)"
