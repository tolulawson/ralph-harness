#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "verify-installation-contract: $*" >&2
  exit 1
}

INSTALLATION_MD="INSTALLATION.md"
INSTALL_MANIFEST="src/install-manifest.txt"
GENERATED_MANIFEST="src/generated-runtime-manifest.txt"
SRC_AGENTS="src/AGENTS.md"
SRC_CLAUDE="src/CLAUDE.md"
INSTALL_SKILL="skills/ralph-install/SKILL.md"
VERSION_FILE="VERSION"

[[ -f "$INSTALLATION_MD" ]] || fail "missing $INSTALLATION_MD"
[[ -f "$INSTALL_MANIFEST" ]] || fail "missing $INSTALL_MANIFEST"
[[ -f "$GENERATED_MANIFEST" ]] || fail "missing $GENERATED_MANIFEST"
[[ -f "$SRC_AGENTS" ]] || fail "missing $SRC_AGENTS"
[[ -f "$SRC_CLAUDE" ]] || fail "missing $SRC_CLAUDE"
[[ -f "$INSTALL_SKILL" ]] || fail "missing $INSTALL_SKILL"
[[ -f "$VERSION_FILE" ]] || fail "missing $VERSION_FILE"

CURRENT_TAG="v$(tr -d '[:space:]' < "$VERSION_FILE")"

grep -q '`INSTALLATION.md` is the canonical install source of truth' "$INSTALLATION_MD" \
  || fail "INSTALLATION.md must declare itself canonical"

grep -Fq -- "$CURRENT_TAG" "$INSTALLATION_MD" \
  || fail "INSTALLATION.md must reference current tag $CURRENT_TAG"

while IFS= read -r path; do
  [[ -z "$path" || "$path" == \#* ]] && continue
  grep -Fq -- "\`$path\`" "$INSTALLATION_MD" || fail "INSTALLATION.md missing copied-path reference for $path"
done < "$INSTALL_MANIFEST"

while IFS= read -r path; do
  [[ -z "$path" || "$path" == \#* ]] && continue
  grep -Fq -- "\`$path\`" "$INSTALLATION_MD" || fail "INSTALLATION.md missing generated-path reference for $path"
done < "$GENERATED_MANIFEST"

for required in \
  '.ralph/constitution.md' \
  '.ralph/runtime-contract.md' \
  '.ralph/policy/runtime-overrides.md' \
  '.ralph/policy/project-policy.md' \
  '.ralph/context/project-truths.md' \
  '.ralph/context/project-facts.json' \
  '.ralph/context/learning-summary.md' \
  '.ralph/state/workflow-state.json' \
  '.ralph/state/spec-queue.json' \
  '.ralph/state/scheduler-lock.json' \
  '.ralph/state/execution-claims.json' \
  '.ralph/state/scheduler-intents.jsonl' \
  'latest report referenced by `last_report_path`' \
  '.ralph/context/learning-log.jsonl'
do
  grep -Fq -- "$required" "$INSTALLATION_MD" || fail "INSTALLATION.md missing AGENTS loader requirement: $required"
done

for required in \
  '.codex/agents/' \
  '.codex/hooks.json' \
  '.claude/settings.json' \
  '.claude/agents/' \
  '.claude/commands/' \
  '.cursor/hooks.json' \
  '.cursor/rules/' \
  '.ralph/hooks/' \
  '.ralph/shared/' \
  'canonical shared control plane' \
  'execution claims' \
  'base_branch' \
  'canonical_control_plane' \
  'control_plane_versioning' \
  "question/input tool" \
  'validation_bootstrap_commands' \
  'orchestrator_stop_hook' \
  'worktree_bootstrap_commands' \
  'bootstrap_env_files' \
  'bootstrap_copy_exclude_globs'
do
  grep -Fq -- "$required" "$INSTALLATION_MD" || fail "INSTALLATION.md missing multi-runtime requirement: $required"
done

grep -Fq -- 'Do not put project-specific runtime contract or control-plane customizations into `.ralph/runtime-contract.md`' "$INSTALLATION_MD" \
  || fail "INSTALLATION.md must explicitly route custom contract/control-plane rules away from canonical runtime-contract"

for required in \
  'question/input tool' \
  'canonical_control_plane.mode' \
  'control_plane_versioning.mode' \
  'Do not write project-specific contract or control-plane instructions into `.ralph/runtime-contract.md`'
do
  grep -Fq -- "$required" "$INSTALL_SKILL" || fail "ralph-install skill missing interactive setup requirement: $required"
done

grep -Fq -- 'last_report_path' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing last_report_path read-order entry"

grep -Fq -- '.ralph/policy/runtime-overrides.md' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing runtime-overrides read-order entry"

grep -Fq -- '.ralph/state/execution-claims.json' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing execution-claims read-order entry"

grep -Fq -- '.ralph/state/execution-claims.json' "$SRC_CLAUDE" \
  || fail "src/CLAUDE.md missing execution-claims read-order entry"

grep -Fq -- '<!-- RALPH-HARNESS:START -->' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing managed block start marker"

grep -Fq -- '<!-- RALPH-HARNESS:END -->' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing managed block end marker"

grep -Fq -- '<!-- RALPH-HARNESS:START -->' "$SRC_CLAUDE" \
  || fail "src/CLAUDE.md missing managed block start marker"

grep -Fq -- '<!-- RALPH-HARNESS:END -->' "$SRC_CLAUDE" \
  || fail "src/CLAUDE.md missing managed block end marker"

grep -Fq -- '`INSTALLATION.md` is the canonical install source of truth' "$INSTALL_SKILL" \
  || fail "ralph-install skill must defer to INSTALLATION.md"

for forbidden in \
  '## What This Skill Installs' \
  'references/install-checklist.md' \
  'references/agents-loader-snippet.md'
do
  if grep -Fq -- "$forbidden" "$INSTALL_SKILL"; then
    fail "ralph-install skill still contains forbidden duplicated install truth: $forbidden"
  fi
done

echo "verify-installation-contract: ok"
