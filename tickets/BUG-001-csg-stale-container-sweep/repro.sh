#!/usr/bin/env bash
# Prototype repro for BUG-001 — NOT product code.
#
# Creates a container that carries the labels the fix will use, runs a normal
# container-mode csg generate, and shows that the pre-existing labelled
# container is still there afterwards. Current csg has no startup sweep, so the
# stale container survives. After the fix, the same run must remove it.
#
# Requirements: a built csg engine image (default csg-wallust-podman:v0.2.0),
# a synced .venv (make sync), and podman or docker.
set -euo pipefail

ENGINE="${ENGINE:-podman}"
TAG="${CSG_TAG:-v0.2.0}"
PREFIX="${CSG_PREFIX:-csg}"
BACKEND="${CSG_BACKEND:-wallust}"
NAME="${STALE_NAME:-csg-bug001-stale}"
ROOT="${CSG_REPRO_ROOT:-/tmp/opencode/csg-bug001-repro}"
CSG="${CSG:-.venv/bin/csg}"
PYTHON="${PYTHON:-.venv/bin/python}"

command -v "$ENGINE" >/dev/null 2>&1 || {
  echo "missing container engine: $ENGINE" >&2
  exit 2
}
test -x "$CSG" || {
  echo "missing csg at $CSG; run 'make sync' first or set CSG=" >&2
  exit 2
}
test -x "$PYTHON" || {
  echo "missing python at $PYTHON; run 'make sync' first or set PYTHON=" >&2
  exit 2
}

mkdir -p "$ROOT/out"

# The same deterministic 16x16 RGB PNG the contract test uses (test_contract),
# so wallust gets a real gradient rather than a 1x1 image.
"$PYTHON" - "$ROOT/wallpaper.png" <<'PY'
import sys

from PIL import Image

image = Image.new("RGB", (16, 16))
pixels = image.load()
assert pixels is not None
for x in range(16):
    for y in range(16):
        pixels[x, y] = (x * 16, y * 16, (x * y) % 256)
image.save(sys.argv[1], format="PNG")
PY

image_exists() {
  "$ENGINE" image inspect "$1" >/dev/null 2>&1
}

SHORT_REF="${PREFIX}-${BACKEND}-${ENGINE}:${TAG}"
if ! image_exists "$SHORT_REF"; then
  LOCAL_REF="localhost/${SHORT_REF}"
  if image_exists "$LOCAL_REF"; then
    "$ENGINE" tag "$LOCAL_REF" "$SHORT_REF" >/dev/null
  else
    echo "missing image: $SHORT_REF (or $LOCAL_REF)" >&2
    exit 2
  fi
fi

"$ENGINE" rm -f "$NAME" >/dev/null 2>&1 || true
"$ENGINE" create --name "$NAME" \
  --label csg.managed=true \
  --label csg.session=00000000-0000-4000-8000-000000000000 \
  --label csg.created_at=2026-01-01T00:00:00Z \
  --label csg.timeout_seconds=300 \
  "$SHORT_REF" true >/dev/null

echo "--- before the csg run ---"
"$ENGINE" ps -a --filter label=csg.managed=true \
  --format '{{.Names}}|{{.State}}|{{.Labels}}'

set +e
env \
  COLORSCHEME__RUNTIME__MODE=container \
  COLORSCHEME__GENERATION__BACKEND="$BACKEND" \
  COLORSCHEME__CONTAINER__ENGINE="$ENGINE" \
  COLORSCHEME__CONTAINER__IMAGE_TAG="$TAG" \
  COLORSCHEME__OUTPUT__DIRECTORY="$ROOT/out" \
  COLORSCHEME__OUTPUT__OVERWRITE=true \
  COLORSCHEME__OUTPUT__APPLY_TO_TERMINAL=false \
  "$CSG" --output-format plain generate "$ROOT/wallpaper.png" \
    --format yaml --backend "$BACKEND" --container-engine "$ENGINE" \
    >"$ROOT/csg.out" 2>"$ROOT/csg.err"
RC=$?
set -e
echo "csg exit: $RC (0 = normal run; non-zero is also acceptable for this repro)"
sed -n '1,3p' "$ROOT/csg.err" 2>/dev/null || true

echo "--- after the csg run ---"
"$ENGINE" ps -a --filter label=csg.managed=true \
  --format '{{.Names}}|{{.State}}|{{.Labels}}'

echo
echo "EXPECTED AFTER FIX: ${NAME} is gone; the run's own wrapper is gone too."
echo "CURRENT (BUG-001): ${NAME} is still listed."
echo "Cleanup: $ENGINE rm -f ${NAME}"
