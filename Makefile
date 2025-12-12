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
	@printf "$(BLUE)Color Scheme Generator - Root$(NC)\n"
	@printf "\n"
	@printf "$(GREEN)Available targets (runs on both core and orchestrator):$(NC)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@printf "\n"
	@printf "$(GREEN)Component-specific targets:$(NC)\n"
	@printf "  $(YELLOW)make core-<target>$(NC)         Run target in core/\n"
	@printf "  $(YELLOW)make orchestrator-<target>$(NC) Run target in orchestrator/\n"
	@printf "\n"
	@printf "$(GREEN)Examples:$(NC)\n"
	@printf "  make install              # Install both components\n"
	@printf "  make core-test            # Run tests in core only\n"
	@printf "  make orchestrator-build   # Build orchestrator only\n"

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
	@printf "$(GREEN)Development environment ready for both components!$(NC)\n"

# Docker targets (orchestrator only)
docker-build: orchestrator-docker-build ## Build all Docker images

docker-clean: orchestrator-docker-clean ## Remove all Docker images

# Core targets
core-%:
	@printf "$(BLUE)Running target '$*' in core/$(NC)\n"
	@$(MAKE) -C core $*

# Orchestrator targets
orchestrator-%:
	@printf "$(BLUE)Running target '$*' in orchestrator/$(NC)\n"
	@$(MAKE) -C orchestrator $*

# Quick start targets
quick-start: ## Quick start guide
	@printf "$(GREEN)Color Scheme Generator - Quick Start$(NC)\n"
	@printf "\n"
	@printf "$(YELLOW)1. Install dependencies:$(NC)\n"
	@printf "   make install-dev\n"
	@printf "\n"
	@printf "$(YELLOW)2. Run tests:$(NC)\n"
	@printf "   make test\n"
	@printf "\n"
	@printf "$(YELLOW)3. Build Docker images (orchestrator):$(NC)\n"
	@printf "   make docker-build\n"
	@printf "\n"
	@printf "$(YELLOW)4. Use the CLI:$(NC)\n"
	@printf "   # Direct usage (core):\n"
	@printf "   cd core && uv run colorscheme-gen generate wallpaper.png\n"
	@printf "\n"
	@printf "   # Container orchestration:\n"
	@printf "   cd orchestrator && uv run color-scheme generate wallpaper.png\n"
	@printf "\n"
	@printf "For more information, see docs/README.md\n"

status: ## Show installation status
	@printf "$(BLUE)Installation Status$(NC)\n"
	@printf "\n"
	@printf "$(YELLOW)Core:$(NC)\n"
	@if [ -d "core/.venv" ]; then \
		printf "  ✓ Virtual environment exists\n"; \
	else \
		printf "  ✗ Virtual environment not found (run: make core-install)\n"; \
	fi
	@if [ -f "core/uv.lock" ]; then \
		printf "  ✓ Lock file exists\n"; \
	else \
		printf "  ✗ Lock file not found\n"; \
	fi
	@printf "\n"
	@printf "$(YELLOW)Orchestrator:$(NC)\n"
	@if [ -d "orchestrator/.venv" ]; then \
		printf "  ✓ Virtual environment exists\n"; \
	else \
		printf "  ✗ Virtual environment not found (run: make orchestrator-install)\n"; \
	fi
	@if [ -f "orchestrator/uv.lock" ]; then \
		printf "  ✓ Lock file exists\n"; \
	else \
		printf "  ✗ Lock file not found\n"; \
	fi

