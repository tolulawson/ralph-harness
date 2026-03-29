#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "verify-canonical-control-plane-contract: $*" >&2
  exit 1
}

for path in \
  README.md \
  src/.ralph/runtime-contract.md \
  src/.ralph/policy/project-policy.md \
  src/.agents/skills/orchestrator/SKILL.md \
  src/.agents/skills/bootstrap/SKILL.md \
  src/.agents/skills/implement/SKILL.md \
  src/.agents/skills/review/SKILL.md \
  src/.agents/skills/verify/SKILL.md \
  skills/ralph-execute/SKILL.md \
  skills/ralph-install/SKILL.md \
  skills/ralph-upgrade/SKILL.md \
  INSTALLATION.md \
  UPGRADING.md \
  scripts/runtime_state_helpers.py \
  scripts/orchestrator-coordination.py
do
  [[ -f "$path" ]] || fail "missing required file $path"
done

grep -Fq -- 'canonical shared control plane' README.md \
  || fail "README.md must describe canonical shared-state ownership"

grep -Fq -- '.ralph/shared/' README.md \
  || fail "README.md must describe the generated shared overlay"

grep -Fq -- 'canonical shared control plane' src/.ralph/runtime-contract.md \
  || fail "runtime contract must define the canonical shared control plane"

grep -Fq -- '.ralph/shared/' src/.ralph/runtime-contract.md \
  || fail "runtime contract must define the generated shared overlay"

grep -Fq -- 'worktree-local tracked copies' src/.ralph/runtime-contract.md \
  || fail "runtime contract must forbid relying on tracked shared-state copies inside worktrees"

grep -Fq -- '.ralph/shared/' src/.ralph/policy/project-policy.md \
  || fail "project policy must mention the generated shared overlay"

for path in \
  src/.agents/skills/orchestrator/SKILL.md \
  src/.agents/skills/bootstrap/SKILL.md \
  src/.agents/skills/implement/SKILL.md \
  src/.agents/skills/review/SKILL.md \
  src/.agents/skills/verify/SKILL.md \
  skills/ralph-execute/SKILL.md \
  skills/ralph-install/SKILL.md \
  skills/ralph-upgrade/SKILL.md
do
  grep -Fq -- '.ralph/shared/' "$path" \
    || fail "$path must mention the generated shared overlay"
done

grep -Fq -- 'canonical shared control plane' INSTALLATION.md \
  || fail "INSTALLATION.md must describe canonical shared-state ownership"

grep -Fq -- '.ralph/shared/' INSTALLATION.md \
  || fail "INSTALLATION.md must describe the generated shared overlay"

grep -Fq -- '.ralph/shared/' UPGRADING.md \
  || fail "UPGRADING.md must describe the generated shared overlay"

grep -Fq -- 'resolve_canonical_checkout_root' scripts/runtime_state_helpers.py \
  || fail "runtime helpers must define canonical checkout resolution"

grep -Fq -- 'ensure_worktree_shared_overlay' scripts/runtime_state_helpers.py \
  || fail "runtime helpers must generate the worktree shared overlay"

grep -Fq -- 'shared_control_plane_status_entries' scripts/runtime_state_helpers.py \
  || fail "runtime helpers must validate shared-control-plane edits in worktrees"

grep -Fq -- 'resolve_canonical_checkout_root' scripts/orchestrator-coordination.py \
  || fail "orchestrator coordination must resolve the canonical checkout before touching shared state"

echo "verify-canonical-control-plane-contract: ok"
