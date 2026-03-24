#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "verify-human-stop-boundaries: $*" >&2
  exit 1
}

for path in \
  src/.ralph/runtime-contract.md \
  src/.agents/skills/orchestrator/SKILL.md \
  src/.codex/agents/orchestrator.toml \
  skills/ralph-execute/SKILL.md
do
  [[ -f "$path" ]] || fail "missing required file $path"
done

grep -Fq -- 'Review, verification, and release failures are remediation signals, not stop conditions.' src/.ralph/runtime-contract.md \
  || fail "runtime contract must classify failed review, verification, and release as remediation signals"

for forbidden in \
  '- review failed' \
  '- verification failed' \
  '- release failed'
do
  if grep -Fq -- "$forbidden" src/.ralph/runtime-contract.md; then
    fail "runtime contract stop conditions must not list $forbidden"
  fi
done

grep -Fq -- 'Do not stop merely because review, verification, or release failed.' src/.agents/skills/orchestrator/SKILL.md \
  || fail "orchestrator skill must forbid stopping on failed review, verification, or release"

grep -Fq -- 'Do not stop merely because review, verification, or release failed.' src/.codex/agents/orchestrator.toml \
  || fail "orchestrator agent instructions must forbid stopping on failed review, verification, or release"

grep -Fq -- 'Do not stop merely because review, verification, or release failed;' skills/ralph-execute/SKILL.md \
  || fail "ralph-execute must keep failed review, verification, and release inside remediation flow"

echo "verify-human-stop-boundaries: ok"
