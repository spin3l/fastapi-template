#!/usr/bin/env bash
# PostToolUse hook: after Claude edits Python under app/ or tests/, enforce the
# project's architecture rules. Exit code 2 feeds stderr back to Claude.
set -uo pipefail

file=$(jq -r '.tool_input.file_path // .tool_response.filePath // empty')
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
rel="${file#"$root"/}"

case "$rel" in
  app/*.py | tests/*.py) ;;
  *) exit 0 ;;
esac

cd "$root" || exit 0

if [[ "$(basename "$rel")" == "__init__.py" ]]; then
  echo "Don't add __init__.py: app/ and tests/ use PEP 420 namespace packages (see CLAUDE.md). Delete $rel." >&2
  exit 2
fi

failed=0
if [[ -f "$rel" ]] && ! out=$(uv run --quiet ruff check "$rel" 2>&1); then
  echo "ruff check failed for $rel:" >&2
  echo "$out" >&2
  failed=1
fi

if ! out=$(uv run --quiet lint-imports 2>&1); then
  echo "import-linter: hexagonal layer contracts broken (see CLAUDE.md):" >&2
  echo "$out" | grep -vE '^\s*$' | tail -n 25 >&2
  failed=1
fi

[[ $failed -eq 0 ]] || exit 2
