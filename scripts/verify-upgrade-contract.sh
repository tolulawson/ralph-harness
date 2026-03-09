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
UPGRADE_SKILL="skills/ralph-upgrade/SKILL.md"
SRC_AGENTS="src/AGENTS.md"
MIGRATION_SCRIPT="scripts/migrate-installed-runtime.py"
CHECK_SCRIPT="scripts/check-installed-runtime-state.py"

[[ -f "$UPGRADING_MD" ]] || fail "missing $UPGRADING_MD"
[[ -f "$UPGRADE_MANIFEST" ]] || fail "missing $UPGRADE_MANIFEST"
[[ -f "$VERSION_FILE" ]] || fail "missing $VERSION_FILE"
[[ -f "$HARNESS_VERSION_JSON" ]] || fail "missing $HARNESS_VERSION_JSON"
[[ -f "$UPGRADE_SKILL" ]] || fail "missing $UPGRADE_SKILL"
[[ -f "$SRC_AGENTS" ]] || fail "missing $SRC_AGENTS"
[[ -f "$MIGRATION_SCRIPT" ]] || fail "missing $MIGRATION_SCRIPT"
[[ -f "$CHECK_SCRIPT" ]] || fail "missing $CHECK_SCRIPT"

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

grep -Fq -- 'merge the installed `.codex/config.toml` with the scaffold config' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document the config merge behavior"

grep -Fq -- 'upgrade_contract_version' "$UPGRADING_MD" \
  || fail "UPGRADING.md must document upgrade_contract_version"

grep -Fq -- '<!-- RALPH-HARNESS:START -->' "$UPGRADING_MD" \
  || fail "UPGRADING.md missing managed AGENTS block start marker"

grep -Fq -- '<!-- RALPH-HARNESS:END -->' "$UPGRADING_MD" \
  || fail "UPGRADING.md missing managed AGENTS block end marker"

grep -Fq -- '.ralph/runtime-contract.md' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing runtime-contract read-order entry"

grep -Fq -- '<!-- RALPH-HARNESS:START -->' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing managed block start marker"

grep -Fq -- '<!-- RALPH-HARNESS:END -->' "$SRC_AGENTS" \
  || fail "src/AGENTS.md missing managed block end marker"

grep -Fq -- '`UPGRADING.md` is the canonical upgrade source of truth' "$UPGRADE_SKILL" \
  || fail "ralph-upgrade skill must defer to UPGRADING.md"

grep -Fq -- 'migrate-installed-runtime.py' "$UPGRADE_SKILL" \
  || fail "ralph-upgrade skill must mention the migration phase"

python3 - <<'PY'
import json
from pathlib import Path

version = Path("VERSION").read_text().strip()
current_tag = f"v{version}"
payload = json.loads(Path("src/.ralph/harness-version.json").read_text())

if payload.get("version") != version:
    raise SystemExit("verify-upgrade-contract: harness-version.json version mismatch")
if payload.get("tag") != current_tag:
    raise SystemExit("verify-upgrade-contract: harness-version.json tag mismatch")
if payload.get("upgrade_contract_version") != 4:
    raise SystemExit("verify-upgrade-contract: upgrade_contract_version must equal 4")
PY

echo "verify-upgrade-contract: ok"
