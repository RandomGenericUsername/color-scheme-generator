# color-scheme-generator — fresh-clone rebuild with make.
#
# Fresh machine path:
#   1. `make sync`     (uv-managed env from the committed lock)
#   2. `make test`     (pytest; skip reasons are printed)
#   3. `make gates`    (test + lint + hermetic + lock-check + docs-check)
#   4. `make build`    (sdist + wheel in dist/)
#   5. `make image`    (build the four Dockerfiles from this repo root at v<version>)
#   6. `make install`  (install the built package into the local .venv)
#
# Every target is anchored on $(CURDIR); none assumes a parent checkout.

UV     ?= uv
PYTHON := $(CURDIR)/.venv/bin/python
VERSION := $(shell sed -n 's/^version = "\(.*\)"/\1/p' $(CURDIR)/pyproject.toml | head -1)

# AD-7: the image tag is the pin, not `latest`. Names match the CLI's own
# `engine_qualified_image` scheme (`<prefix>-<suffix>-<engine>:<tag>`), so
# `csg install` produces the same references this target builds.
IMAGE_ENGINE ?= podman
IMAGE_TAG    ?= v$(VERSION)
IMAGE_PREFIX ?= csg
BASE_IMAGE    = $(IMAGE_PREFIX)-base-$(IMAGE_ENGINE):$(IMAGE_TAG)
BACKENDS      = custom pywal wallust
DOCKER_DIR   := $(CURDIR)/src/color_scheme_generator/adapters/docker

# The authoritative gate set. `make gates` runs it for a developer; CI runs one
# job per member (`.github/workflows/gates.yml`) and `make ci-gates-parity`
# fails when the two sets differ. Add a gate here AND a job there in one commit.
# `image` is a verb and a declared CI-only job, not a gate: it needs a live
# engine and network access to the pinned git dependencies.
GATES := test lint hermetic lock-check docs-check

.PHONY: help sync install test lint format check gates gates-ci hermetic lock-check docs-check image build ci-gates-parity clean

help:
	@echo "sync            Install the env from uv.lock (uv sync --frozen)"
	@echo "test            Run the test suite (skip reasons shown)"
	@echo "lint            Ruff check src/"
	@echo "format          Ruff format src/"
	@echo "check           Alias of lint (in-tree name)"
	@echo "hermetic        Run the suite with empty HOME/XDG and a foreign cwd"
	@echo "lock-check      uv lock --check (the committed lock is current)"
	@echo "docs-check      README/CHANGELOG/LICENSE/AGENTS + CLAUDE symlink exist"
	@echo "gates           $(GATES)"
	@echo "ci-gates-parity Workflow jobs equal GATES + declared CI-only jobs"
	@echo "image           Build $(BASE_IMAGE) + the three backends, run csg --version"
	@echo "build           Build sdist + wheel into dist/"
	@echo "install         Install the built package into .venv"
	@echo "clean           Remove dist/ and local caches"

sync:
	$(UV) sync --frozen

install: sync
	$(UV) pip install --reinstall .

# -rs prints every skip with its reason: engine-dependent tests skip honestly
# when no engine is reachable, they are never silently absent.
test:
	$(UV) run pytest -q -rs

lint:
	$(UV) run ruff check src

format:
	$(UV) run ruff format src

check: lint

# AD-8: pass with HOME and all four XDG roots pointing at empty temp dirs and an
# unrelated working directory. The chdir itself is the autouse fixture's job
# (tests/conftest.py); the canary proves it runs.
hermetic:
	@test -x "$(PYTHON)" || { echo "run 'make sync' first"; exit 1; }
	@tmp=$$(mktemp -d); trap 'rm -rf "$$tmp" 2>/dev/null || true' EXIT; \
	env HOME="$$tmp" \
	    XDG_CONFIG_HOME="$$tmp/config" XDG_CACHE_HOME="$$tmp/cache" \
	    XDG_DATA_HOME="$$tmp/data" XDG_STATE_HOME="$$tmp/state" \
	    TMPDIR="$$tmp" \
	    "$(PYTHON)" -m pytest -q -rs

lock-check:
	$(UV) lock --check

docs-check:
	@test -f README.md      || { echo "missing README.md"; exit 1; }
	@test -f CHANGELOG.md   || { echo "missing CHANGELOG.md"; exit 1; }
	@test -f LICENSE        || { echo "missing LICENSE"; exit 1; }
	@test -f AGENTS.md      || { echo "missing AGENTS.md"; exit 1; }
	@test -L CLAUDE.md      || { echo "CLAUDE.md must be a symlink to AGENTS.md"; exit 1; }
	@grep -q "MIT License" LICENSE || { echo "LICENSE is not the MIT text"; exit 1; }
	@for d in base custom pywal wallust; do \
	  test -f "$(DOCKER_DIR)/Dockerfile.$$d" || { echo "missing Dockerfile.$$d"; exit 1; }; \
	done
	@! grep -REn "src/shared|src/cli-tools|\.\./" "$(DOCKER_DIR)/" \
	    || { echo "Dockerfile references a path outside this repo"; exit 1; }

# AD-5/AD-7: the build context is this repo root; the tag is the pin. The base
# image is built first; the three backends derive from it via BASE_IMAGE.
image:
	@for d in base $(BACKENDS); do \
	  test -f "$(DOCKER_DIR)/Dockerfile.$$d" || { echo "missing Dockerfile.$$d"; exit 1; }; \
	done
	$(IMAGE_ENGINE) build -t "$(BASE_IMAGE)" -f "$(DOCKER_DIR)/Dockerfile.base" "$(CURDIR)"
	@for backend in $(BACKENDS); do \
	  echo "building $(IMAGE_PREFIX)-$$backend-$(IMAGE_ENGINE):$(IMAGE_TAG)"; \
	  $(IMAGE_ENGINE) build -t "$(IMAGE_PREFIX)-$$backend-$(IMAGE_ENGINE):$(IMAGE_TAG)" \
	    --build-arg BASE_IMAGE="$(BASE_IMAGE)" \
	    -f "$(DOCKER_DIR)/Dockerfile.$$backend" "$(CURDIR)" || exit 1; \
	done
	$(IMAGE_ENGINE) run --rm "$(BASE_IMAGE)" csg --version

gates: $(GATES)

# Alias kept so a CI parity check and a local run name the same set.
gates-ci: $(GATES)

ci-gates-parity:
	python3 scripts/ci-gates-parity.py

build:
	$(UV) build

clean:
	rm -rf dist .pytest_cache .ruff_cache .coverage htmlcov build
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
