#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

MANAGED_START='<!-- RALPH-HARNESS:START -->'
MANAGED_END='<!-- RALPH-HARNESS:END -->'

render_managed_block() {
  cat src/AGENTS.md
}

update_agents_file() {
  local target="$1"
  local block_file="$2"
  python3 - "$target" "$block_file" <<'PY'
from pathlib import Path
import sys

target = Path(sys.argv[1])
block = Path(sys.argv[2]).read_text().rstrip() + "\n"
start = "<!-- RALPH-HARNESS:START -->"
end = "<!-- RALPH-HARNESS:END -->"

if target.exists():
    text = target.read_text()
else:
    text = ""

if start in text and end in text:
    prefix, rest = text.split(start, 1)
    _, suffix = rest.split(end, 1)
    new_text = prefix.rstrip() + "\n\n" + block + suffix
else:
    base = text.rstrip()
    if base:
        new_text = base + "\n\n" + block
    else:
        new_text = block

target.write_text(new_text.rstrip() + "\n")
PY
}

copy_manifest_paths() {
  local manifest="$1"
  local target="$2"
  while IFS= read -r path; do
    [[ -z "$path" || "$path" == \#* ]] && continue
    if [[ "$path" == "AGENTS.md" && -f "$target/AGENTS.md" ]]; then
      continue
    fi
    mkdir -p "$target/$(dirname "$path")"
    rsync -a "src/$path" "$target/$path"
  done < "$manifest"
}

create_generated_runtime() {
  local target="$1"
  while IFS= read -r path; do
    [[ -z "$path" || "$path" == \#* ]] && continue
    if [[ "$path" == */ ]]; then
      mkdir -p "$target/$path"
    elif [[ "$path" == *"."* ]]; then
      mkdir -p "$target/$(dirname "$path")"
      : > "$target/$path"
    else
      mkdir -p "$target/$path"
    fi
  done < src/generated-runtime-manifest.txt
}

INSTALL_TARGET="$TMP_DIR/install-target"
mkdir -p "$INSTALL_TARGET"
printf 'Project loader before install.\n' > "$INSTALL_TARGET/AGENTS.md"
copy_manifest_paths src/install-manifest.txt "$INSTALL_TARGET"
create_generated_runtime "$INSTALL_TARGET"
render_managed_block > "$TMP_DIR/managed-block.md"
update_agents_file "$INSTALL_TARGET/AGENTS.md" "$TMP_DIR/managed-block.md"

[[ -f "$INSTALL_TARGET/.ralph/runtime-contract.md" ]] || {
  echo "smoke-test-install-upgrade: missing runtime-contract after install" >&2
  exit 1
}

[[ -f "$INSTALL_TARGET/.ralph/harness-version.json" ]] || {
  echo "smoke-test-install-upgrade: missing harness-version after install" >&2
  exit 1
}

grep -Fq "$MANAGED_START" "$INSTALL_TARGET/AGENTS.md" || {
  echo "smoke-test-install-upgrade: AGENTS.md missing managed block start" >&2
  exit 1
}

grep -Fq "$MANAGED_END" "$INSTALL_TARGET/AGENTS.md" || {
  echo "smoke-test-install-upgrade: AGENTS.md missing managed block end" >&2
  exit 1
}

LEGACY_TARGET="$TMP_DIR/legacy-target"
mkdir -p "$LEGACY_TARGET/.ralph/policy" "$LEGACY_TARGET/.ralph/context" "$LEGACY_TARGET/.ralph/state" \
  "$LEGACY_TARGET/tasks" "$LEGACY_TARGET/specs" "$LEGACY_TARGET/.ralph/reports" "$LEGACY_TARGET/.ralph/logs"
printf 'Legacy loader.\n' > "$LEGACY_TARGET/AGENTS.md"
printf 'keep-policy\n' > "$LEGACY_TARGET/.ralph/policy/project-policy.md"
printf 'keep-context\n' > "$LEGACY_TARGET/.ralph/context/project-truths.md"
printf 'keep-state\n' > "$LEGACY_TARGET/.ralph/state/workflow-state.json"
printf 'keep-tasks\n' > "$LEGACY_TARGET/tasks/todo.md"
printf 'keep-specs\n' > "$LEGACY_TARGET/specs/INDEX.md"
printf 'keep-reports\n' > "$LEGACY_TARGET/.ralph/reports/existing.md"
printf 'keep-logs\n' > "$LEGACY_TARGET/.ralph/logs/events.jsonl"

copy_manifest_paths src/upgrade-manifest.txt "$LEGACY_TARGET"
update_agents_file "$LEGACY_TARGET/AGENTS.md" "$TMP_DIR/managed-block.md"

grep -Fq 'keep-policy' "$LEGACY_TARGET/.ralph/policy/project-policy.md" || {
  echo "smoke-test-install-upgrade: policy changed during upgrade" >&2
  exit 1
}

grep -Fq 'keep-context' "$LEGACY_TARGET/.ralph/context/project-truths.md" || {
  echo "smoke-test-install-upgrade: context changed during upgrade" >&2
  exit 1
}

grep -Fq 'keep-state' "$LEGACY_TARGET/.ralph/state/workflow-state.json" || {
  echo "smoke-test-install-upgrade: state changed during upgrade" >&2
  exit 1
}

grep -Fq 'keep-tasks' "$LEGACY_TARGET/tasks/todo.md" || {
  echo "smoke-test-install-upgrade: tasks changed during upgrade" >&2
  exit 1
}

grep -Fq 'keep-specs' "$LEGACY_TARGET/specs/INDEX.md" || {
  echo "smoke-test-install-upgrade: specs changed during upgrade" >&2
  exit 1
}

[[ -f "$LEGACY_TARGET/.ralph/runtime-contract.md" ]] || {
  echo "smoke-test-install-upgrade: runtime-contract missing after upgrade" >&2
  exit 1
}

[[ -f "$LEGACY_TARGET/.ralph/harness-version.json" ]] || {
  echo "smoke-test-install-upgrade: harness-version missing after upgrade" >&2
  exit 1
}

echo "smoke-test-install-upgrade: ok"
