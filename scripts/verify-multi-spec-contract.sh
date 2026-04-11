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
  src/.agents/skills/release/SKILL.md \
  skills/ralph-execute/SKILL.md \
  skills/ralph-plan/SKILL.md \
  scripts/check-installed-runtime-state.py \
  scripts/runtime_state_helpers.py
do
  [[ -f "$path" ]] || fail "missing required file $path"
done

grep -Fq -- 'active_spec_ids' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention active_spec_ids"

grep -Fq -- 'depends_on_spec_ids' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention depends_on_spec_ids"

grep -Fq -- 'scheduler-lock.json' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention the scheduler lock file"

grep -Fq -- 'execution-claims.json' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention the execution claims file"

grep -Fq -- '.ralph/shared/' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention the generated shared overlay"

grep -Fq -- 'scheduler-intents.jsonl' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention the durable intents file"

grep -Fq -- 'git worktree' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention per-spec git worktrees"

grep -Fq -- 'bootstrap' src/.ralph/runtime-contract.md \
  || fail "runtime contract must mention bootstrap"

grep -Fq -- 'dedicated orchestrator peer subagent per invocation' src/.ralph/runtime-contract.md \
  || fail "runtime contract must require execute invocations to launch orchestrator peers"

grep -Fq -- 'queue write lock' src/.ralph/runtime-contract.md \
  || fail "runtime contract must describe the short-lived queue write lock"

grep -Fq -- 'queue_revision' src/.ralph/runtime-contract.md \
  || fail "runtime contract must document queue_revision"

for status in awaiting_review awaiting_verification awaiting_release release_failed
do
  grep -Fq -- "$status" src/.ralph/runtime-contract.md \
    || fail "runtime contract must mention $status in the lifecycle"
done

grep -Fq -- 'workers release their claims and exit' src/.ralph/runtime-contract.md \
  || fail "runtime contract must make workers release claims before orchestrator reconciliation"

grep -Fq -- 'orchestrator peer may later acquire the scheduler lock' src/.ralph/runtime-contract.md \
  || fail "runtime contract must keep reconciliation on an orchestrator peer under the scheduler lock"

grep -Fq -- 'short-lived global queue write lock' src/.ralph/policy/project-policy.md \
  || fail "project policy must describe the shared queue write lock"

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

grep -Fq -- 'refill freed execution slots' src/.agents/skills/orchestrator/SKILL.md \
  || fail "orchestrator skill must refill freed worker slots while runnable work remains"

grep -Fq -- 'execution_mode = native_subagent' src/.agents/skills/orchestrator/SKILL.md \
  || fail "orchestrator skill must require native subagent execution claims"

grep -Fq -- 'depends_on_spec_ids' src/.agents/skills/plan/SKILL.md \
  || fail "plan skill must seed depends_on_spec_ids"

grep -Fq -- 'queue write lock' skills/ralph-execute/SKILL.md \
  || fail "ralph-execute must mention queue-lock coordination"

grep -Fq -- '.ralph/shared/' skills/ralph-execute/SKILL.md \
  || fail "ralph-execute must mention the generated shared overlay"

grep -Fq -- 'orchestrator peer subagent' skills/ralph-execute/SKILL.md \
  || fail "ralph-execute must describe the orchestrator-peer topology"

grep -Fq -- 'record every delegated worker' skills/ralph-execute/SKILL.md \
  || fail "ralph-execute must require native subagent execution claims"

if grep -Fq -- 'lease ownership must transfer' skills/ralph-execute/SKILL.md; then
  fail "ralph-execute must not use legacy lease-transfer stop language"
fi

if grep -Fq -- 'lease ownership must transfer' src/.agents/skills/orchestrator/SKILL.md; then
  fail "orchestrator skill must not use legacy lease-transfer stop language"
fi

grep -Fq -- 'route to `$ralph-plan`' skills/ralph-execute/SKILL.md \
  || fail "ralph-execute must route planning gaps back to ralph-plan"

grep -Fq -- 'execution-ready specs, but planned specs that still need `task-gen` may legitimately lack it' skills/ralph-execute/SKILL.md \
  || fail "ralph-execute must distinguish execution-ready task registries from planned specs"

grep -Fq -- 'task-state.json' skills/ralph-plan/SKILL.md \
  || fail "ralph-plan must mention task-state.json outputs"

grep -Fq -- 'plan-check' skills/ralph-plan/SKILL.md \
  || fail "ralph-plan must mention the plan-check handoff"

grep -Fq -- 'Delegate `task-gen`' skills/ralph-plan/SKILL.md \
  || fail "ralph-plan must delegate task generation instead of implying inline ownership"

for outcome in pr_created awaiting_review awaiting_merge merge_completed release_failed human_gate_waiting
do
  grep -Fq -- "$outcome" src/.agents/skills/release/SKILL.md \
    || fail "release skill must mention explicit outcome $outcome"
done

grep -Fq -- 'check_runtime_preflight' scripts/check-installed-runtime-state.py \
  || fail "check-installed-runtime-state.py must use the shared runtime preflight classifier"

grep -Fq -- 'route_to_planning_task_gen' scripts/runtime_state_helpers.py \
  || fail "runtime helpers must classify planning/task-gen preflight gaps explicitly"

grep -Fq -- 'spec_requires_task_state' scripts/runtime_state_helpers.py \
  || fail "runtime helpers must gate task-state requirements by execution readiness"

python3 - <<'PY'
import json
from pathlib import Path

constitution = Path("src/.ralph/constitution.md").read_text()
workflow = json.loads(Path("src/.ralph/state/workflow-state.json").read_text())
queue = json.loads(Path("src/.ralph/state/spec-queue.json").read_text())
lease = json.loads(Path("src/.ralph/state/scheduler-lock.json").read_text())
queue_template = json.loads(Path("src/.ralph/templates/spec-queue-template.json").read_text())

for needle in ("release_failed", "awaiting_release", "awaiting_merge"):
    if needle not in constitution:
        raise SystemExit(f"verify-multi-spec-contract: constitution must include {needle}")

for key in ("active_spec_ids", "active_interrupt_spec_id", "scheduler_lock_path", "execution_claims_path", "scheduler_intents_path", "scheduler_summary"):
    if key not in workflow:
        raise SystemExit(f"verify-multi-spec-contract: workflow-state missing {key}")

for key in ("active_spec_ids", "active_interrupt_spec_id", "execution_claims_path", "queue_revision"):
    if key not in queue:
        raise SystemExit(f"verify-multi-spec-contract: spec-queue missing {key}")

if queue["queue_policy"].get("selection") != "explicit_first_ready_set":
    raise SystemExit("verify-multi-spec-contract: queue state selection policy must be explicit_first_ready_set")

if queue_template["queue_policy"].get("normal_execution_limit") != 3:
    raise SystemExit("verify-multi-spec-contract: queue template default normal_execution_limit must be 3")

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
        raise SystemExit(f"verify-multi-spec-contract: scheduler lock state missing {key}")
PY

echo "verify-multi-spec-contract: ok"
