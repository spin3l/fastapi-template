#!/usr/bin/env bash
# Render the template with a few answer sets and run each generated project's full checks.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
out="$root/.generated"
rm -rf "$out"
mkdir -p "$out"

check() {
  local slug="$1"
  shift
  echo "==> Generating $slug ($*)"
  uv run --project "$root" cookiecutter "$root" --no-input --output-dir "$out" "$@" >/dev/null

  (
    cd "$out/$slug"
    if grep -rIl --exclude-dir=.venv -e '{{' -e '{%' -e 'cookiecutter\.' . ; then
      echo "Unrendered Jinja left in the files above" >&2
      exit 1
    fi
    uv lock --check
    uv sync --quiet --locked
    uv run ruff format --check .
    make check
  )
}

# Defaults.
check my-service
# The project this template was extracted from.
check feature-flags "project_name=Feature Flags" module_name=grades entity_name=grade
# Multi-word names exercise the case conversions.
check acme-order-hub "project_name=Acme Order Hub" module_name=order_items entity_name=order_item

echo "==> Template OK"
