#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "verify-multi-spec-contract: $*" >&2
  exit 1
}

for path in \
  src/.ralph/runtime-contract.md \
  src/.ralph/policy/project-policy.md \
  src/.agents/skills/orchestrator/SKILL.md \
  src/.agents/skills/plan/SKILL.md \
  skills/ralph-execute/SKILL.md \
  scripts/runtime_state_helpers.py
do
  [[ -f "$path" ]] || fail "missing required file $path"
done

grep -Fq -- 'active_spec_ids' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention active_spec_ids"

grep -Fq -- 'depends_on_spec_ids' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention depends_on_spec_ids"

grep -Fq -- 'orchestrator-lease.json' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention the orchestrator lease file"

grep -Fq -- 'worker-claims.json' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention the worker claims file"

grep -Fq -- '.ralph/shared/' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention the generated shared overlay"

grep -Fq -- 'orchestrator-intents.jsonl' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention the durable intents file"

grep -Fq -- 'git worktree' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention per-spec git worktrees"

grep -Fq -- 'bootstrap' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention bootstrap"

grep -Fq -- 'single-writer lease' src/.ralph/policy/project-policy.md \
  || fail "project policy must describe the single-writer lease"

grep -Fq -- 'hard dependency' src/.ralph/policy/project-policy.md \
  || fail "project policy must describe hard dependencies"

grep -Fq -- 'durable intent' src/.agents/skills/orchestrator/SKILL.md \
  || fail "orchestrator skill must mention durable intent intake"

grep -Fq -- 'worktree' src/.agents/skills/orchestrator/SKILL.md \
  || fail "orchestrator skill must mention worktrees"

grep -Fq -- 'bootstrap' src/.agents/skills/orchestrator/SKILL.md \
  || fail "orchestrator skill must mention bootstrap"

grep -Fq -- '.ralph/shared/' src/.agents/skills/orchestrator/SKILL.md \
  || fail "orchestrator skill must mention the generated shared overlay"

grep -Fq -- 'depends_on_spec_ids' src/.agents/skills/plan/SKILL.md \
  || fail "plan skill must seed depends_on_spec_ids"

grep -Fq -- 'lease' skills/ralph-execute/SKILL.md \
  || fail "ralph-execute must mention lease coordination"

grep -Fq -- '.ralph/shared/' skills/ralph-execute/SKILL.md \
  || fail "ralph-execute must mention the generated shared overlay"

python3 - <<'PY'
import json
from pathlib import Path

workflow = json.loads(Path("src/.ralph/state/workflow-state.json").read_text())
queue = json.loads(Path("src/.ralph/state/spec-queue.json").read_text())
lease = json.loads(Path("src/.ralph/state/orchestrator-lease.json").read_text())
queue_template = json.loads(Path("src/.ralph/templates/spec-queue-template.json").read_text())

for key in ("active_spec_ids", "active_interrupt_spec_id", "orchestrator_lease_path", "worker_claims_path", "orchestrator_intents_path", "scheduler_summary"):
    if key not in workflow:
        raise SystemExit(f"verify-multi-spec-contract: workflow-state missing {key}")

for key in ("active_spec_ids", "active_interrupt_spec_id", "worker_claims_path"):
    if key not in queue:
        raise SystemExit(f"verify-multi-spec-contract: spec-queue missing {key}")

if queue["queue_policy"].get("normal_execution_limit") != 2:
    raise SystemExit("verify-multi-spec-contract: queue template default normal_execution_limit must be 2")

sample = queue_template["specs"][0]
for key in (
    "depends_on_spec_ids",
    "admission_status",
    "admitted_at",
    "worktree_name",
    "worktree_path",
    "branch_name",
    "base_branch",
    "bootstrap_status",
    "bootstrap_last_claim_id",
    "bootstrap_last_report_path",
    "bootstrap_last_completed_at",
    "slot_status",
    "active_task_id",
    "task_status",
    "assigned_role",
    "active_pr_number",
    "active_pr_url",
    "last_dispatch_at",
):
    if key not in sample:
        raise SystemExit(f"verify-multi-spec-contract: queue template missing {key}")

for key in ("schema_version", "owner_token", "heartbeat_at", "expires_at", "status"):
    if key not in lease:
        raise SystemExit(f"verify-multi-spec-contract: lease state missing {key}")
PY

echo "verify-multi-spec-contract: ok"
