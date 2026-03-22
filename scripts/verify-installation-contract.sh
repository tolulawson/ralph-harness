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
INSTALL_SKILL="skills/ralph-install/SKILL.md"
VERSION_FILE="VERSION"

[[ -f "$INSTALLATION_MD" ]] || fail "missing $INSTALLATION_MD"
[[ -f "$INSTALL_MANIFEST" ]] || fail "missing $INSTALL_MANIFEST"
[[ -f "$GENERATED_MANIFEST" ]] || fail "missing $GENERATED_MANIFEST"
[[ -f "$SRC_AGENTS" ]] || fail "missing $SRC_AGENTS"
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
  '.ralph/state/orchestrator-lease.json' \
  '.ralph/state/orchestrator-intents.jsonl' \
  'latest report referenced by `last_report_path`' \
  '.ralph/context/learning-log.jsonl'
do
  grep -Fq -- "$required" "$INSTALLATION_MD" || fail "INSTALLATION.md missing AGENTS loader requirement: $required"
done

for required in \
  '`fork_context = true`' \
  'all role configs use `sandbox_mode = "danger-full-access"`'
do
  grep -Fq -- "$required" "$INSTALLATION_MD" || fail "INSTALLATION.md missing subagent isolation requirement: $required"
done

grep -Fq -- 'the report at `last_report_path`' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing last_report_path read-order entry"

grep -Fq -- '.ralph/policy/runtime-overrides.md' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing runtime-overrides read-order entry"

grep -Fq -- '<!-- RALPH-HARNESS:START -->' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing managed block start marker"

grep -Fq -- '<!-- RALPH-HARNESS:END -->' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing managed block end marker"

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
