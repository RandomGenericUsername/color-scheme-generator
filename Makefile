.PHONY: help install install-dev clean test lint format type-check build check dev docker-build docker-clean

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Color Scheme Generator - Root$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets (runs on both core and orchestrator):$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Component-specific targets:$(NC)"
	@echo "  $(YELLOW)make core-<target>$(NC)         Run target in core/"
	@echo "  $(YELLOW)make orchestrator-<target>$(NC) Run target in orchestrator/"
	@echo ""
	@echo "$(GREEN)Examples:$(NC)"
	@echo "  make install              # Install both components"
	@echo "  make core-test            # Run tests in core only"
	@echo "  make orchestrator-build   # Build orchestrator only"

install: core-install orchestrator-install ## Install both core and orchestrator

install-dev: core-install-dev orchestrator-install-dev ## Install both with dev dependencies

clean: core-clean orchestrator-clean ## Clean both components

test: core-test orchestrator-test ## Run tests for both components

lint: core-lint orchestrator-lint ## Lint both components

format: core-format orchestrator-format ## Format both components

type-check: core-type-check orchestrator-type-check ## Type check both components

build: core-build orchestrator-build ## Build both components

check: core-check orchestrator-check ## Run all checks on both components

dev: install-dev ## Setup development environment for both components
	@echo "$(GREEN)Development environment ready for both components!$(NC)"

# Docker targets (orchestrator only)
docker-build: orchestrator-docker-build ## Build all Docker images

docker-clean: orchestrator-docker-clean ## Remove all Docker images

# Core targets
core-%:
	@echo "$(BLUE)Running target '$*' in core/$(NC)"
	@$(MAKE) -C core $*

# Orchestrator targets
orchestrator-%:
	@echo "$(BLUE)Running target '$*' in orchestrator/$(NC)"
	@$(MAKE) -C orchestrator $*

# Quick start targets
quick-start: ## Quick start guide
	@echo "$(GREEN)Color Scheme Generator - Quick Start$(NC)"
	@echo ""
	@echo "$(YELLOW)1. Install dependencies:$(NC)"
	@echo "   make install-dev"
	@echo ""
	@echo "$(YELLOW)2. Run tests:$(NC)"
	@echo "   make test"
	@echo ""
	@echo "$(YELLOW)3. Build Docker images (orchestrator):$(NC)"
	@echo "   make docker-build"
	@echo ""
	@echo "$(YELLOW)4. Use the CLI:$(NC)"
	@echo "   # Direct usage (core):"
	@echo "   cd core && source .venv/bin/activate"
	@echo "   colorscheme-gen generate wallpaper.png"
	@echo ""
	@echo "   # Container orchestration:"
	@echo "   cd orchestrator && source .venv/bin/activate"
	@echo "   color-scheme generate wallpaper.png --backend pywal"
	@echo ""
	@echo "For more information, see README.md"

status: ## Show installation status
	@echo "$(BLUE)Installation Status$(NC)"
	@echo ""
	@echo "$(YELLOW)Core:$(NC)"
	@if [ -d "core/.venv" ]; then \
		echo "  ✓ Virtual environment exists"; \
	else \
		echo "  ✗ Virtual environment not found (run: make core-install)"; \
	fi
	@if [ -f "core/uv.lock" ]; then \
		echo "  ✓ Lock file exists"; \
	else \
		echo "  ✗ Lock file not found"; \
	fi
	@echo ""
	@echo "$(YELLOW)Orchestrator:$(NC)"
	@if [ -d "orchestrator/.venv" ]; then \
		echo "  ✓ Virtual environment exists"; \
	else \
		echo "  ✗ Virtual environment not found (run: make orchestrator-install)"; \
	fi
	@if [ -f "orchestrator/uv.lock" ]; then \
		echo "  ✓ Lock file exists"; \
	else \
		echo "  ✗ Lock file not found"; \
	fi

