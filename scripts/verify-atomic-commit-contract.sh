#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "verify-atomic-commit-contract: $*" >&2
  exit 1
}

for path in \
  src/.ralph/constitution.md \
  src/.ralph/runtime-contract.md \
  src/.ralph/policy/project-policy.md \
  src/.ralph/templates/role-report-template.md \
  src/.agents/skills/reporting/SKILL.md \
  src/.agents/skills/react-effects-without-effects/SKILL.md \
  src/.agents/skills/react-effects-without-effects/references/patterns.md \
  src/.agents/skills/deslopify-lite/SKILL.md \
  src/.agents/skills/implement/SKILL.md \
  src/.agents/skills/review/SKILL.md \
  src/.agents/skills/verify/SKILL.md \
  src/.agents/skills/release/SKILL.md \
  src/.agents/skills/orchestrator/SKILL.md \
  src/.codex/agents/implement.toml \
  src/.codex/agents/orchestrator.toml \
  src/.codex/agents/review.toml \
  src/.codex/agents/release.toml \
  src/.codex/agents/verify.toml \
  skills/ralph-execute/SKILL.md \
  skills/ralph-execute/references/resume-checklist.md
do
  [[ -f "$path" ]] || fail "missing $path"
done

grep -Fq -- 'atomic commit' src/.ralph/constitution.md \
  || fail "src/.ralph/constitution.md must define the atomic commit rule"

grep -Fq -- 'Commit Evidence' src/.ralph/constitution.md \
  || fail "src/.ralph/constitution.md must require the Commit Evidence section"

grep -Fq -- 'clean worktree' src/.ralph/runtime-contract.md \
  || fail "src/.ralph/runtime-contract.md must mention clean worktree handoff guards"

grep -Fq -- 'Atomic commits required before task handoff: yes' src/.ralph/policy/project-policy.md \
  || fail "src/.ralph/policy/project-policy.md must require atomic commits before handoff"

grep -Fq -- '## Commit Evidence' src/.ralph/templates/role-report-template.md \
  || fail "src/.ralph/templates/role-report-template.md must include a Commit Evidence section"

grep -Fq -- '## Quality Gate' src/.ralph/templates/role-report-template.md \
  || fail "src/.ralph/templates/role-report-template.md must include a Quality Gate section"

for required in \
  'React Effects Audit:' \
  'React files checked:' \
  'Deslopify Lite:'
do
  grep -Fq -- "$required" src/.ralph/templates/role-report-template.md \
    || fail "role-report template missing $required"
done

for required in \
  'Head commit:' \
  'Commit subject:' \
  'Task ids covered:' \
  'Validation run:' \
  'Additional commits or range:'
do
  grep -Fq -- "$required" src/.ralph/templates/role-report-template.md \
    || fail "role-report template missing $required"
done

grep -Fq -- 'Commit Evidence' src/.agents/skills/reporting/SKILL.md \
  || fail "reporting skill must require Commit Evidence"

grep -Fq -- 'Quality Gate' src/.agents/skills/reporting/SKILL.md \
  || fail "reporting skill must require Quality Gate"

grep -Fq -- 'atomic commit' src/.agents/skills/implement/SKILL.md \
  || fail "implement skill must require atomic commits"

grep -Fq -- 'clean worktree' src/.agents/skills/implement/SKILL.md \
  || fail "implement skill must require a clean worktree before handoff"

for path in \
  src/.agents/skills/implement/SKILL.md \
  src/.codex/agents/implement.toml
do
  grep -Fq -- 'react-effects-without-effects' "$path" \
    || fail "$path must require the react-effects-without-effects helper at applicable handoffs"
  grep -Fq -- 'deslopify-lite' "$path" \
    || fail "$path must require the deslopify-lite helper at handoff"
done

for path in \
  src/.agents/skills/review/SKILL.md \
  src/.codex/agents/review.toml
do
  grep -Eiq 'missing .*commit evidence|Commit Evidence' "$path" \
    || fail "$path must treat missing commit evidence as a review finding"
  grep -Fq -- 'Quality Gate' "$path" \
    || fail "$path must treat missing or failed Quality Gate as a review finding"
done

for path in \
  src/.agents/skills/release/SKILL.md \
  src/.codex/agents/release.toml
do
  grep -Fq -- 'clean worktree' "$path" \
    || fail "$path must require a clean worktree for release"
done

for path in \
  src/.agents/skills/orchestrator/SKILL.md \
  src/.codex/agents/orchestrator.toml
do
  grep -Fq -- 'Commit Evidence' "$path" \
    || fail "$path must validate Commit Evidence at handoff boundaries"
  grep -Fq -- 'Quality Gate' "$path" \
    || fail "$path must validate Quality Gate at handoff boundaries"
done

for path in \
  skills/ralph-execute/SKILL.md \
  skills/ralph-execute/references/resume-checklist.md
do
  grep -Fq -- 'Quality Gate' "$path" \
    || fail "$path must enforce Quality Gate at resume boundaries"
done

echo "verify-atomic-commit-contract: ok"
