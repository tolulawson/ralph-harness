#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "verify-interruption-contract: $*" >&2
  exit 1
}

[[ -f "skills/ralph-interrupt/SKILL.md" ]] || fail "missing skills/ralph-interrupt/SKILL.md"
[[ -f "skills/ralph-interrupt/agents/openai.yaml" ]] || fail "missing skills/ralph-interrupt/agents/openai.yaml"
[[ -f "src/.ralph/templates/amendments-template.md" ]] || fail "missing src/.ralph/templates/amendments-template.md"

for path in \
  AGENTS.md \
  CLAUDE.md
do
  grep -Fq -- 'implementation changes in `src/`' "$path" \
    || grep -Fq -- 'must be changed in `src/`' "$path" \
    || fail "$path must document the source-only implementation rule"
done

for path in \
  README.md \
  src/.ralph/runtime-contract.md \
  src/.ralph/policy/project-policy.md
do
  grep -Fq -- 'resume_spec_stack' "$path" || fail "$path must mention resume_spec_stack"
done

for path in \
  skills/ralph-execute/SKILL.md \
  skills/ralph-interrupt/SKILL.md
do
  grep -Fq -- 'preflight consistency check' "$path" || fail "$path must require preflight consistency checks"
  grep -Fq -- 'mixed-version state' "$path" || fail "$path must block mixed-version state"
done

for path in \
  README.md \
  INSTALLATION.md \
  UPGRADING.md \
  skills/ralph-install/references/source-vs-runtime.md
do
  grep -Fq -- 'ralph-interrupt' "$path" || fail "$path must mention ralph-interrupt"
done

grep -Fq -- 'Interruption Assessment' src/.ralph/templates/role-report-template.md \
  || fail "src/.ralph/templates/role-report-template.md missing Interruption Assessment"

grep -Fq -- 'projection only' src/.agents/skills/state-sync/SKILL.md \
  || fail "src/.agents/skills/state-sync/SKILL.md must describe workflow-state.md as a projection"

python3 - <<'PY'
import json
from pathlib import Path

workflow = json.loads(Path("src/.ralph/state/workflow-state.json").read_text())
queue = json.loads(Path("src/.ralph/state/spec-queue.json").read_text())
template = json.loads(Path("src/.ralph/templates/spec-queue-template.json").read_text())

if "resume_spec_stack" not in workflow:
    raise SystemExit("verify-interruption-contract: workflow-state missing resume_spec_stack")

if queue["queue_policy"].get("preemption") != "failing_out_of_scope_bug":
    raise SystemExit("verify-interruption-contract: seed queue preemption mismatch")

sample = template["specs"][0]
for key in ["origin_spec_key", "origin_task_id", "triggered_by_role", "trigger_report_path", "trigger_summary"]:
    if key not in sample:
        raise SystemExit(f"verify-interruption-contract: spec queue template missing {key}")

active_interrupt = {"spec_id": "007", "kind": "interrupt", "status": "in_progress", "created_at": "2026-03-08T10:00:00Z"}
ready_interrupt = {"spec_id": "008", "kind": "interrupt", "status": "ready", "created_at": "2026-03-08T11:00:00Z"}
active_normal = {"spec_id": "005", "kind": "normal", "status": "in_progress", "created_at": "2026-03-08T09:00:00Z"}
ready_normal = {"spec_id": "006", "kind": "normal", "status": "ready", "created_at": "2026-03-08T12:00:00Z"}

specs = [ready_normal, active_normal, ready_interrupt, active_interrupt]

def rank(spec):
    status = spec["status"]
    kind = spec["kind"]
    created = spec["created_at"]
    spec_id = int(spec["spec_id"])
    if kind == "interrupt" and status == "in_progress":
        return (0, created, spec_id)
    if kind == "interrupt" and status == "ready":
        return (1, created, spec_id)
    if kind == "normal" and status == "in_progress":
        return (2, created, spec_id)
    return (3, created, spec_id)

ordered = [spec["spec_id"] for spec in sorted(specs, key=rank)]
if ordered != ["007", "008", "005", "006"]:
    raise SystemExit(f"verify-interruption-contract: interrupt ordering mismatch {ordered}")
PY

echo "verify-interruption-contract: ok"
