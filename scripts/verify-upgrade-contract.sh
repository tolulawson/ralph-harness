#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "verify-upgrade-contract: $*" >&2
  exit 1
}

UPGRADING_MD="UPGRADING.md"
UPGRADE_MANIFEST="src/upgrade-manifest.txt"
VERSION_FILE="VERSION"
HARNESS_VERSION_JSON="src/.ralph/harness-version.json"
RUNTIME_OVERRIDES_MD="src/.ralph/policy/runtime-overrides.md"
UPGRADE_SKILL="skills/ralph-upgrade/SKILL.md"
SRC_AGENTS="src/AGENTS.md"
SRC_CLAUDE="src/CLAUDE.md"
MIGRATION_SCRIPT="scripts/migrate-installed-runtime.py"
CHECK_SCRIPT="scripts/check-installed-runtime-state.py"
PREFLIGHT_SCRIPT="scripts/check-upgrade-surface.py"

[[ -f "$UPGRADING_MD" ]] || fail "missing $UPGRADING_MD"
[[ -f "$UPGRADE_MANIFEST" ]] || fail "missing $UPGRADE_MANIFEST"
[[ -f "$VERSION_FILE" ]] || fail "missing $VERSION_FILE"
[[ -f "$HARNESS_VERSION_JSON" ]] || fail "missing $HARNESS_VERSION_JSON"
[[ -f "$RUNTIME_OVERRIDES_MD" ]] || fail "missing $RUNTIME_OVERRIDES_MD"
[[ -f "$UPGRADE_SKILL" ]] || fail "missing $UPGRADE_SKILL"
[[ -f "$SRC_AGENTS" ]] || fail "missing $SRC_AGENTS"
[[ -f "$SRC_CLAUDE" ]] || fail "missing $SRC_CLAUDE"
[[ -f "$MIGRATION_SCRIPT" ]] || fail "missing $MIGRATION_SCRIPT"
[[ -f "$CHECK_SCRIPT" ]] || fail "missing $CHECK_SCRIPT"
[[ -f "$PREFLIGHT_SCRIPT" ]] || fail "missing $PREFLIGHT_SCRIPT"

CURRENT_VERSION="$(tr -d '[:space:]' < "$VERSION_FILE")"
CURRENT_TAG="v$CURRENT_VERSION"

grep -q '`UPGRADING.md` is the canonical upgrade source of truth' "$UPGRADING_MD" \
  || fail "UPGRADING.md must declare itself canonical"

grep -Fq -- "$CURRENT_TAG" "$UPGRADING_MD" \
  || fail "UPGRADING.md must reference current tag $CURRENT_TAG"

while IFS= read -r path; do
  [[ -z "$path" || "$path" == \#* ]] && continue
  grep -Fq -- "\`$path\`" "$UPGRADING_MD" || fail "UPGRADING.md missing upgrade-path reference for $path"
done < "$UPGRADE_MANIFEST"

grep -Fq -- 'scripts/migrate-installed-runtime.py' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document the migration script"

grep -Fq -- 'scripts/check-upgrade-surface.py' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document the upgrade preflight script"

grep -Fq -- '.ralph/state/worker-claims.json' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document the worker claims file"

grep -Fq -- 'base_branch' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document canonical base-branch preservation"

grep -Fq -- '.claude/agents/' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document the Claude adapter pack"

grep -Fq -- '.cursor/rules/' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document the Cursor adapter pack"

for required in \
  '.codex/hooks.json' \
  '.claude/settings.json' \
  '.cursor/hooks.json' \
  '.ralph/hooks/' \
  '.ralph/shared/' \
  'canonical shared control plane' \
  'orchestrator_stop_hook' \
  'bootstrap_env_files' \
  'bootstrap_copy_exclude_globs' \
  'preserve unknown runtime skills' \
  'managed runtime skill' \
  'check-upgrade-surface.py'
do
  grep -Fq -- "$required" "$UPGRADING_MD" || fail "UPGRADING.md missing hook/bootstrap/skill-preservation requirement: $required"
done

grep -Fq -- 'upgrade_contract_version' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document upgrade_contract_version"

grep -Fq -- 'orchestrator-lease.json' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document the lease file"

grep -Fq -- 'healthy held lease' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document the live-lease upgrade block"

grep -Fq -- 'orchestrator-intents.jsonl' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document the durable intents file"

grep -Fq -- '.ralph/worktrees/' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document the worktree directory"

grep -Fq -- 'spec-scoped' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document spec-scoped worker report normalization"

grep -Fq -- '.ralph/policy/runtime-overrides.md' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document the preserved runtime overrides surface"

grep -Fq -- 'duplicate branch ownership' "$UPGRADE_SKILL" \
  || fail "ralph-upgrade skill must warn about duplicate branch ownership"

grep -Fq -- 'all role configs use `sandbox_mode = "danger-full-access"`' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document all-role full-permission mode"

grep -Fq -- '<!-- RALPH-HARNESS:START -->' "$UPGRADING_MD" \
  || fail "UPGRADING.md missing managed AGENTS block start marker"

grep -Fq -- '<!-- RALPH-HARNESS:END -->' "$UPGRADING_MD" \
  || fail "UPGRADING.md missing managed AGENTS block end marker"

grep -Fq -- '.ralph/runtime-contract.md' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing runtime-contract read-order entry"

grep -Fq -- '.ralph/policy/runtime-overrides.md' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing runtime-overrides read-order entry"

grep -Fq -- '.ralph/state/worker-claims.json' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing worker-claims read-order entry"

grep -Fq -- '<!-- RALPH-HARNESS:START -->' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing managed block start marker"

grep -Fq -- '<!-- RALPH-HARNESS:END -->' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing managed block end marker"

grep -Fq -- '.ralph/state/worker-claims.json' "$SRC_CLAUDE" \
  || fail "src/CLAUDE.md missing worker-claims read-order entry"

grep -Fq -- '`UPGRADING.md` is the canonical upgrade source of truth' "$UPGRADE_SKILL" \
  || fail "ralph-upgrade skill must defer to UPGRADING.md"

grep -Fq -- 'migrate-installed-runtime.py' "$UPGRADE_SKILL" \
  || fail "ralph-upgrade skill must mention the migration phase"

grep -Fq -- 'check-upgrade-surface.py' "$UPGRADE_SKILL" \
  || fail "ralph-upgrade skill must mention the upgrade preflight phase"

python3 - <<'PY'
import hashlib
import json
from pathlib import Path

version = Path("VERSION").read_text().strip()
current_tag = f"v{version}"
payload = json.loads(Path("src/.ralph/harness-version.json").read_text())
runtime_contract_hash = hashlib.sha256(Path("src/.ralph/runtime-contract.md").read_bytes()).hexdigest()

if payload.get("version") != version:
    raise SystemExit("verify-upgrade-contract: harness-version.json version mismatch")
if payload.get("tag") != current_tag:
    raise SystemExit("verify-upgrade-contract: harness-version.json tag mismatch")
if payload.get("upgrade_contract_version") != 11:
    raise SystemExit("verify-upgrade-contract: upgrade_contract_version must equal 11")
if payload.get("runtime_contract_baseline_sha256") != runtime_contract_hash:
    raise SystemExit("verify-upgrade-contract: runtime_contract_baseline_sha256 must match src/.ralph/runtime-contract.md")
if payload.get("runtime_overrides_path") != ".ralph/policy/runtime-overrides.md":
    raise SystemExit("verify-upgrade-contract: runtime_overrides_path must match the canonical overlay path")
if payload.get("runtime_adapters") != ["codex", "claude", "cursor"]:
    raise SystemExit("verify-upgrade-contract: runtime_adapters must equal ['codex', 'claude', 'cursor']")
if payload.get("branch_prefix") != "ralph":
    raise SystemExit("verify-upgrade-contract: branch_prefix must equal 'ralph'")
PY

echo "verify-upgrade-contract: ok"
