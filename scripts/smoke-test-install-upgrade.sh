#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

MANAGED_START='<!-- RALPH-HARNESS:START -->'
MANAGED_END='<!-- RALPH-HARNESS:END -->'

render_loader_block() {
  local source_path="$1"
  cat "$source_path"
}

update_loader_file() {
  local target="$1"
  local block_file="$2"
  python3 - "$target" "$block_file" <<'PY'
from pathlib import Path
import sys

target = Path(sys.argv[1])
block = Path(sys.argv[2]).read_text().rstrip() + "\n"
start = "<!-- RALPH-HARNESS:START -->"
end = "<!-- RALPH-HARNESS:END -->"

if target.exists():
    text = target.read_text()
else:
    text = ""

if start in text and end in text:
    prefix, rest = text.split(start, 1)
    _, suffix = rest.split(end, 1)
    new_text = prefix.rstrip() + "\n\n" + block + suffix
else:
    base = text.rstrip()
    if base:
        new_text = base + "\n\n" + block
    else:
        new_text = block

target.write_text(new_text.rstrip() + "\n")
PY
}

sync_loader_files() {
  local target="$1"
  update_loader_file "$target/AGENTS.md" "$TMP_DIR/managed-agents-block.md"
  update_loader_file "$target/CLAUDE.md" "$TMP_DIR/managed-claude-block.md"
}

copy_manifest_paths() {
  local manifest="$1"
  local target="$2"
  while IFS= read -r path; do
    [[ -z "$path" || "$path" == \#* ]] && continue
    if [[ "$path" == "AGENTS.md" && -f "$target/AGENTS.md" ]]; then
      continue
    fi
    if [[ "$path" == "CLAUDE.md" && -f "$target/CLAUDE.md" ]]; then
      continue
    fi
    if [[ -f "$target/$path" ]]; then
      case "$path" in
        .codex/config.toml|.codex/hooks.json|.claude/settings.json|.cursor/hooks.json)
          continue
          ;;
      esac
    fi
    mkdir -p "$target/$(dirname "$path")"
    rsync -a "src/$path" "$target/$path"
  done < "$manifest"
}

create_generated_runtime() {
  local target="$1"
  while IFS= read -r path; do
    [[ -z "$path" || "$path" == \#* ]] && continue
    if [[ "$path" == */ ]]; then
      mkdir -p "$target/$path"
    elif [[ "$path" == *"."* ]]; then
      mkdir -p "$target/$(dirname "$path")"
      : > "$target/$path"
    else
      mkdir -p "$target/$path"
    fi
  done < src/generated-runtime-manifest.txt
}

render_state_projections() {
  local target="$1"
  python3 - "$target" <<'PY'
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path.cwd() / "scripts"))

from runtime_state_helpers import render_spec_index_markdown, render_workflow_state_markdown

repo = Path(sys.argv[1])
workflow = json.loads((repo / ".ralph/state/workflow-state.json").read_text())
queue = json.loads((repo / ".ralph/state/spec-queue.json").read_text())
(repo / ".ralph/state/workflow-state.md").write_text(render_workflow_state_markdown(workflow, queue))
(repo / "specs/INDEX.md").write_text(render_spec_index_markdown(queue))
PY
}

normalize_current_runtime_fixture() {
  local target="$1"
  python3 - "$target" <<'PY'
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd() / "scripts"))

from runtime_state_helpers import (
    ensure_project_facts_file,
    ensure_spec_worktree,
    ensure_worker_claims_file,
    load_json,
    merge_bootstrap_summary_from_claims,
    normalize_queue,
    normalize_workflow,
    render_spec_index_markdown,
    render_workflow_state_markdown,
    write_json,
)

repo = Path(sys.argv[1])
workflow_path = repo / ".ralph/state/workflow-state.json"
queue_path = repo / ".ralph/state/spec-queue.json"

workflow = load_json(workflow_path)
queue = load_json(queue_path)
project_facts_path, project_facts = ensure_project_facts_file(repo, queue, workflow)
queue = normalize_queue(queue, workflow, project_facts)
workflow = normalize_workflow(workflow, queue)
claims_path = ensure_worker_claims_file(repo, workflow)
claims = load_json(claims_path)
merge_bootstrap_summary_from_claims(queue, claims)
for spec in queue.get("specs", []):
    if spec.get("spec_id") in queue.get("active_spec_ids", []) or spec.get("slot_status") in {"admitted", "running", "paused"}:
        ensure_spec_worktree(repo, spec, project_facts)
write_json(queue_path, queue)
write_json(workflow_path, workflow)
(repo / ".ralph/state/workflow-state.md").write_text(render_workflow_state_markdown(workflow, queue))
(repo / "specs/INDEX.md").write_text(render_spec_index_markdown(queue))
PY
}

init_git_repo() {
  local target="$1"
  git -C "$target" init -q -b main
  git -C "$target" config user.name "Ralph Harness Smoke"
  git -C "$target" config user.email "ralph-harness-smoke@example.test"
  git -C "$target" add .
  git -C "$target" commit -q -m "chore: seed harness fixture"
}

write_atomic_runtime() {
  local target="$1"
  mkdir -p \
    "$target/.ralph/reports/atomic-20260308" \
    "$target/specs/001-atomic-commit-demo"
  cat > "$target/.ralph/state/workflow-state.json" <<'EOF'
{
  "schema_version": "3.0.0",
  "project_name": "atomic-target",
  "active_epoch_id": "E001",
  "active_spec_ids": [
    "001"
  ],
  "active_interrupt_spec_id": null,
  "active_spec_id": "001",
  "active_spec_key": "001-atomic-commit-demo",
  "active_task_id": "001-T001",
  "current_phase": "review",
  "task_status": "awaiting_review",
  "assigned_role": "review",
  "current_branch": "main",
  "current_run_id": "atomic-20260308",
  "active_pr_number": null,
  "active_pr_url": null,
  "queue_head_spec_id": "001",
  "orchestrator_lease_path": ".ralph/state/orchestrator-lease.json",
  "orchestrator_intents_path": ".ralph/state/orchestrator-intents.jsonl",
  "lease_owner_token": null,
  "lease_heartbeat_at": null,
  "lease_expires_at": null,
  "scheduler_summary": {
    "normal_execution_limit": 2,
    "active_spec_count": 1,
    "pending_intent_count": 0,
    "dependency_blocked_count": 0
  },
  "resume_spec_id": null,
  "resume_spec_stack": [],
  "interruption_state": null,
  "last_event_id": "evt-0001",
  "last_report_path": ".ralph/reports/atomic-20260308/implement.md",
  "last_verified_at": null,
  "blocked_reason": null,
  "failure_count": 0,
  "next_action": "Review the completed task checkpoint for 001-T001.",
  "queue_snapshot": [
    {
      "spec_id": "001",
      "spec_key": "001-atomic-commit-demo",
      "epoch_id": "E001",
      "status": "awaiting_review",
      "admission_status": "admitted",
      "slot_status": "running",
      "branch_name": "ralph/001-atomic-commit-demo",
      "pr_number": null
    }
  ]
}
EOF
  cat > "$target/.ralph/state/spec-queue.json" <<'EOF'
{
  "schema_version": "3.0.0",
  "queue_policy": {
    "selection": "fifo_admission_window",
    "preemption": "failing_out_of_scope_bug",
    "normal_execution_limit": 2
  },
  "active_spec_id": "001",
  "active_spec_ids": [
    "001"
  ],
  "active_interrupt_spec_id": null,
  "resume_spec_id": null,
  "specs": [
    {
      "spec_id": "001",
      "spec_slug": "atomic-commit-demo",
      "spec_key": "001-atomic-commit-demo",
      "title": "Atomic commit demo",
      "epoch_id": "E001",
      "created_at": "2026-03-08T13:00:00-08:00",
      "last_worked_at": "2026-03-08T13:15:00-08:00",
      "status": "awaiting_review",
      "kind": "normal",
      "origin_spec_key": null,
      "origin_task_id": null,
      "triggered_by_role": null,
      "trigger_report_path": null,
      "trigger_summary": null,
      "priority_override": null,
      "blocked_reason": null,
      "depends_on_spec_ids": [],
      "admission_status": "admitted",
      "admitted_at": "2026-03-08T13:10:00-08:00",
      "research_status": "done",
      "research_artifact_path": "specs/001-atomic-commit-demo/research.md",
      "research_report_path": null,
      "research_updated_at": "2026-03-08T13:05:00-08:00",
      "planning_batch_id": "batch-20260308-atomic",
      "prd_path": "tasks/prd-atomic-target.md",
      "spec_path": "specs/001-atomic-commit-demo/spec.md",
      "plan_path": "specs/001-atomic-commit-demo/plan.md",
      "tasks_path": "specs/001-atomic-commit-demo/tasks.md",
      "task_state_path": "specs/001-atomic-commit-demo/task-state.json",
      "latest_report_path": ".ralph/reports/atomic-20260308/implement.md",
      "worktree_name": "ralph-001-atomic-commit-demo",
      "worktree_path": ".ralph/worktrees/001-atomic-commit-demo",
      "branch_name": "ralph/001-atomic-commit-demo",
      "base_branch": "main",
      "slot_status": "running",
      "active_task_id": "001-T001",
      "task_status": "awaiting_review",
      "assigned_role": "review",
      "active_pr_number": null,
      "active_pr_url": null,
      "last_dispatch_at": "2026-03-08T13:15:00-08:00",
      "pr_number": null,
      "pr_url": null,
      "pr_state": null,
      "merge_commit": null,
      "task_summary": {
        "total": 1,
        "done": 1,
        "in_progress": 0,
        "blocked": 0
      },
      "next_task_id": "001-T001"
    }
  ]
}
EOF
  cat > "$target/specs/001-atomic-commit-demo/spec.md" <<'EOF'
# Atomic Commit Demo Spec

This fixture proves atomic checkpoint handoff validation.
EOF
  cat > "$target/specs/001-atomic-commit-demo/plan.md" <<'EOF'
# Atomic Commit Demo Plan
EOF
  cat > "$target/specs/001-atomic-commit-demo/research.md" <<'EOF'
# Atomic Commit Demo Research
EOF
  cat > "$target/specs/001-atomic-commit-demo/tasks.md" <<'EOF'
# Tasks: 001-atomic-commit-demo

- [x] 001-T001 Complete an atomic checkpoint before review
EOF
  cat > "$target/specs/001-atomic-commit-demo/task-state.json" <<'EOF'
{
  "schema_version": "1.1.0",
  "spec_id": "001",
  "spec_key": "001-atomic-commit-demo",
  "tasks": [
    {
      "task_id": "001-T001",
      "status": "awaiting_review",
      "previous_status": "in_progress",
      "last_role": "implement",
      "last_report_path": ".ralph/reports/atomic-20260308/implement.md",
      "updated_at": "2026-03-08T13:15:00-08:00",
      "blocked_reason": null,
      "review_result": null,
      "verification_result": null,
      "requirement_ids": [
        "R1"
      ],
      "verification_commands": [
        "python3 scripts/check-installed-runtime-state.py --repo ."
      ],
      "planned_artifacts": [
        "specs/001-atomic-commit-demo/spec.md"
      ]
    }
  ]
}
EOF
  render_state_projections "$target"
}

write_parallel_research_runtime() {
  local target="$1"
  mkdir -p \
    "$target/.ralph/reports/research-batch-20260308" \
    "$target/specs/001-batch-head" \
    "$target/specs/002-batch-follow-on"
  cat > "$target/.ralph/state/workflow-state.json" <<'EOF'
{
  "schema_version": "3.0.0",
  "project_name": "parallel-research-target",
  "active_epoch_id": null,
  "active_spec_ids": [],
  "active_interrupt_spec_id": null,
  "active_spec_id": null,
  "active_spec_key": null,
  "active_task_id": null,
  "current_phase": "planning",
  "task_status": null,
  "assigned_role": "orchestrator",
  "current_branch": "main",
  "current_run_id": "research-batch-20260308",
  "active_pr_number": null,
  "active_pr_url": null,
  "queue_head_spec_id": "001",
  "orchestrator_lease_path": ".ralph/state/orchestrator-lease.json",
  "orchestrator_intents_path": ".ralph/state/orchestrator-intents.jsonl",
  "lease_owner_token": null,
  "lease_heartbeat_at": null,
  "lease_expires_at": null,
  "scheduler_summary": {
    "normal_execution_limit": 2,
    "active_spec_count": 0,
    "pending_intent_count": 0,
    "dependency_blocked_count": 1
  },
  "resume_spec_id": null,
  "resume_spec_stack": [],
  "interruption_state": null,
  "last_event_id": "evt-0009",
  "last_report_path": ".ralph/reports/research-batch-20260308/orchestrator.md",
  "last_verified_at": null,
  "blocked_reason": null,
  "failure_count": 0,
  "next_action": "Plan the queue head after joined research completes.",
  "queue_snapshot": [
    {
      "spec_id": "001",
      "spec_key": "001-batch-head",
      "epoch_id": "E001",
      "status": "planned",
      "admission_status": "pending",
      "slot_status": "inactive",
      "branch_name": "codex/001-batch-head",
      "pr_number": null
    },
    {
      "spec_id": "002",
      "spec_key": "002-batch-follow-on",
      "epoch_id": "E001",
      "status": "planned",
      "admission_status": "pending",
      "slot_status": "inactive",
      "branch_name": "codex/002-batch-follow-on",
      "pr_number": null
    }
  ]
}
EOF
  cat > "$target/.ralph/state/spec-queue.json" <<'EOF'
{
  "schema_version": "3.0.0",
  "queue_policy": {
    "selection": "fifo_admission_window",
    "preemption": "failing_out_of_scope_bug",
    "normal_execution_limit": 2
  },
  "active_spec_id": null,
  "active_spec_ids": [],
  "active_interrupt_spec_id": null,
  "resume_spec_id": null,
  "specs": [
    {
      "spec_id": "001",
      "spec_slug": "batch-head",
      "spec_key": "001-batch-head",
      "title": "Batch head",
      "epoch_id": "E001",
      "created_at": "2026-03-08T14:00:00-08:00",
      "last_worked_at": "2026-03-08T14:20:00-08:00",
      "status": "planned",
      "kind": "normal",
      "origin_spec_key": null,
      "origin_task_id": null,
      "triggered_by_role": "specify",
      "trigger_report_path": ".ralph/reports/research-batch-20260308/specify.md",
      "trigger_summary": "Queued from the same planning batch.",
      "priority_override": null,
      "blocked_reason": null,
      "depends_on_spec_ids": [],
      "admission_status": "pending",
      "admitted_at": null,
      "research_status": "done",
      "research_artifact_path": "specs/001-batch-head/research.md",
      "research_report_path": ".ralph/reports/research-batch-20260308/research-001.md",
      "research_updated_at": "2026-03-08T14:15:00-08:00",
      "planning_batch_id": "batch-20260308-demo",
      "prd_path": "tasks/prd-demo.md",
      "spec_path": "specs/001-batch-head/spec.md",
      "plan_path": "specs/001-batch-head/plan.md",
      "tasks_path": "specs/001-batch-head/tasks.md",
      "task_state_path": "specs/001-batch-head/task-state.json",
      "latest_report_path": ".ralph/reports/research-batch-20260308/orchestrator.md",
      "worktree_name": "ralph-001-batch-head",
      "worktree_path": ".ralph/worktrees/001-batch-head",
      "branch_name": "codex/001-batch-head",
      "base_branch": "main",
      "slot_status": "inactive",
      "active_task_id": null,
      "task_status": null,
      "assigned_role": null,
      "active_pr_number": null,
      "active_pr_url": null,
      "last_dispatch_at": null,
      "pr_number": null,
      "pr_url": null,
      "pr_state": null,
      "merge_commit": null,
      "task_summary": {
        "total": 0,
        "done": 0,
        "in_progress": 0,
        "blocked": 0
      },
      "next_task_id": null
    },
    {
      "spec_id": "002",
      "spec_slug": "batch-follow-on",
      "spec_key": "002-batch-follow-on",
      "title": "Batch follow-on",
      "epoch_id": "E001",
      "created_at": "2026-03-08T14:00:00-08:00",
      "last_worked_at": "2026-03-08T14:20:00-08:00",
      "status": "planned",
      "kind": "normal",
      "origin_spec_key": null,
      "origin_task_id": null,
      "triggered_by_role": "specify",
      "trigger_report_path": ".ralph/reports/research-batch-20260308/specify.md",
      "trigger_summary": "Queued from the same planning batch.",
      "priority_override": null,
      "blocked_reason": null,
      "depends_on_spec_ids": [
        "001"
      ],
      "admission_status": "pending",
      "admitted_at": null,
      "research_status": "in_progress",
      "research_artifact_path": "specs/002-batch-follow-on/research.md",
      "research_report_path": ".ralph/reports/research-batch-20260308/research-002.md",
      "research_updated_at": "2026-03-08T14:16:00-08:00",
      "planning_batch_id": "batch-20260308-demo",
      "prd_path": "tasks/prd-demo.md",
      "spec_path": "specs/002-batch-follow-on/spec.md",
      "plan_path": "specs/002-batch-follow-on/plan.md",
      "tasks_path": "specs/002-batch-follow-on/tasks.md",
      "task_state_path": "specs/002-batch-follow-on/task-state.json",
      "latest_report_path": ".ralph/reports/research-batch-20260308/orchestrator.md",
      "worktree_name": "ralph-002-batch-follow-on",
      "worktree_path": ".ralph/worktrees/002-batch-follow-on",
      "branch_name": "codex/002-batch-follow-on",
      "base_branch": "main",
      "slot_status": "inactive",
      "active_task_id": null,
      "task_status": null,
      "assigned_role": null,
      "active_pr_number": null,
      "active_pr_url": null,
      "last_dispatch_at": null,
      "pr_number": null,
      "pr_url": null,
      "pr_state": null,
      "merge_commit": null,
      "task_summary": {
        "total": 0,
        "done": 0,
        "in_progress": 0,
        "blocked": 0
      },
      "next_task_id": null
    }
  ]
}
EOF
  cat > "$target/specs/001-batch-head/spec.md" <<'EOF'
# Batch Head Spec
EOF
  cat > "$target/specs/002-batch-follow-on/spec.md" <<'EOF'
# Batch Follow-On Spec
EOF
  cat > "$target/specs/001-batch-head/plan.md" <<'EOF'
# Batch Head Plan
EOF
  cat > "$target/specs/002-batch-follow-on/plan.md" <<'EOF'
# Batch Follow-On Plan
EOF
  cat > "$target/specs/001-batch-head/research.md" <<'EOF'
# Batch Head Research
EOF
  cat > "$target/specs/002-batch-follow-on/research.md" <<'EOF'
# Batch Follow-On Research
EOF
  cat > "$target/specs/001-batch-head/tasks.md" <<'EOF'
# Tasks: 001-batch-head
EOF
  cat > "$target/specs/002-batch-follow-on/tasks.md" <<'EOF'
# Tasks: 002-batch-follow-on
EOF
  cat > "$target/specs/001-batch-head/task-state.json" <<'EOF'
{
  "schema_version": "1.1.0",
  "spec_id": "001",
  "spec_key": "001-batch-head",
  "tasks": []
}
EOF
  cat > "$target/specs/002-batch-follow-on/task-state.json" <<'EOF'
{
  "schema_version": "1.1.0",
  "spec_id": "002",
  "spec_key": "002-batch-follow-on",
  "tasks": []
}
EOF
  cat > "$target/specs/INDEX.md" <<'EOF'
# stale projection
EOF
  render_state_projections "$target"
}

write_atomic_report() {
  local target="$1"
  local additional="$2"
  local checkpoint_sha="$3"
  local checkpoint_subject
  checkpoint_subject="$(git -C "$target" log -1 --format=%s "$checkpoint_sha")"
  cat > "$target/.ralph/reports/atomic-20260308/implement.md" <<EOF
# Implementation Report

## Objective

Complete task \`001-T001\` with an atomic checkpoint.

## Inputs Read

- \`specs/001-atomic-commit-demo/tasks.md\`

## Artifacts Written

- \`specs/001-atomic-commit-demo/spec.md\`
- \`.ralph/reports/atomic-20260308/implement.md\`

## Verification

- \`python3 scripts/check-installed-runtime-state.py --repo .\` (recorded for the fixture only)

## Commit Evidence

- Head commit: \`$checkpoint_sha\`
- Commit subject: $checkpoint_subject
- Task ids covered: \`001-T001\`
- Validation run: \`python3 scripts/check-installed-runtime-state.py --repo .\`
- Additional commits or range: $additional

## Interruption Assessment

- Scope: \`current\`
- Blocking: \`false\`
- Origin spec key: \`null\`
- Origin task id: \`null\`
- Summary: None.
- Recommended fix direction: None.

## Candidate Learnings

- None.

## Open Issues

- None.

## Recommended Next Role

\`review\`
EOF
}

seed_legacy_agent_configs() {
  local target="$1"
  mkdir -p "$target/agents"
  cp .codex/agents/*.toml "$target/agents/"
}

write_positive_legacy_runtime() {
  local target="$1"
  mkdir -p \
    "$target/.ralph/policy" \
    "$target/.ralph/context" \
    "$target/.ralph/state" \
    "$target/.ralph/reports" \
    "$target/.ralph/reports/release-legacy" \
    "$target/.ralph/logs" \
    "$target/tasks" \
    "$target/specs/001-legacy-spec"
  seed_legacy_agent_configs "$target"
  printf 'Legacy loader.\n' > "$target/AGENTS.md"
  printf 'keep-policy\n' > "$target/.ralph/policy/project-policy.md"
  printf 'keep-context\n' > "$target/.ralph/context/project-truths.md"
  printf 'keep-reports\n' > "$target/.ralph/reports/existing.md"
  cat > "$target/.ralph/reports/release-legacy/release.md" <<'EOF'
# Release Report

## Objective

Capture the completed handoff for the legacy spec.
EOF
  printf 'keep-logs\n' > "$target/.ralph/logs/events.jsonl"
  printf 'keep-tasks\n' > "$target/tasks/todo.md"
  cat > "$target/.ralph/state/workflow-state.json" <<'EOF'
{
  "schema_version": "2.0.0",
  "project_name": "legacy-target",
  "active_epoch_id": null,
  "active_spec_id": null,
  "active_spec_key": null,
  "active_task_id": null,
  "current_phase": "complete",
  "task_status": null,
  "assigned_role": null,
  "current_branch": "main",
  "current_run_id": "release-legacy",
  "active_pr_number": null,
  "active_pr_url": null,
  "queue_head_spec_id": null,
  "resume_spec_id": null,
  "interruption_state": null,
  "last_event_id": "evt-0001",
  "last_report_path": ".ralph/reports/release-legacy/release.md",
  "last_verified_at": null,
  "blocked_reason": null,
  "failure_count": 0,
  "next_action": "Queue complete. No remaining specs.",
  "queue_snapshot": []
}
EOF
  cat > "$target/.ralph/state/workflow-state.md" <<'EOF'
# old workflow projection
EOF
  cat > "$target/.ralph/state/spec-queue.json" <<'EOF'
{
  "schema_version": "1.0.0",
  "queue_policy": {
    "selection": "fifo",
    "preemption": "emergency_only"
  },
  "active_spec_id": null,
  "resume_spec_id": null,
  "specs": [
    {
      "spec_id": "001",
      "spec_slug": "legacy-spec",
      "spec_key": "001-legacy-spec",
      "title": "Legacy completed spec",
      "epoch_id": "E001",
      "created_at": "2026-03-01T10:00:00-08:00",
      "last_worked_at": "2026-03-01T11:00:00-08:00",
      "status": "done",
      "kind": "normal",
      "priority_override": null,
      "blocked_reason": null,
      "prd_path": "tasks/prd-legacy.md",
      "spec_path": "specs/001-legacy-spec/spec.md",
      "plan_path": "specs/001-legacy-spec/plan.md",
      "tasks_path": "specs/001-legacy-spec/tasks.md",
      "latest_report_path": ".ralph/reports/release-legacy/release.md",
      "branch_name": "codex/001-legacy-spec",
      "base_branch": "main",
      "pr_number": 12,
      "pr_url": "https://example.test/pull/12",
      "pr_state": "merged",
      "merge_commit": "abc123",
      "task_summary": {
        "total": 2,
        "done": 2,
        "in_progress": 0,
        "blocked": 0
      },
      "next_task_id": null
    }
  ]
}
EOF
  cat > "$target/specs/INDEX.md" <<'EOF'
# old spec index
EOF
  cat > "$target/specs/001-legacy-spec/spec.md" <<'EOF'
# Legacy Spec
EOF
  cat > "$target/specs/001-legacy-spec/plan.md" <<'EOF'
# Legacy Plan
EOF
  cat > "$target/specs/001-legacy-spec/tasks.md" <<'EOF'
# Tasks: 001-legacy-spec

- [x] 001-T001 Restore the existing flow
- [x] 001-T002 Verify the existing flow
EOF
}

write_ambiguous_legacy_runtime() {
  local target="$1"
  mkdir -p \
    "$target/.ralph/policy" \
    "$target/.ralph/context" \
    "$target/.ralph/state" \
    "$target/.ralph/reports" \
    "$target/.ralph/logs" \
    "$target/specs/005-ios-settings-and-failure-recovery"
  seed_legacy_agent_configs "$target"
  printf 'Legacy loader.\n' > "$target/AGENTS.md"
  printf 'keep-policy\n' > "$target/.ralph/policy/project-policy.md"
  printf 'keep-context\n' > "$target/.ralph/context/project-truths.md"
  printf 'keep-reports\n' > "$target/.ralph/reports/existing.md"
  printf 'keep-logs\n' > "$target/.ralph/logs/events.jsonl"
  cat > "$target/.ralph/state/workflow-state.json" <<'EOF'
{
  "schema_version": "2.0.0",
  "project_name": "ambiguous-target",
  "active_epoch_id": "E003",
  "active_spec_id": "005",
  "active_spec_key": "005-ios-settings-and-failure-recovery",
  "active_task_id": "005-T001",
  "current_phase": "implementation",
  "task_status": "in_progress",
  "assigned_role": "implement",
  "current_branch": "codex/005-ios-settings-and-failure-recovery",
  "current_run_id": "implement-legacy",
  "active_pr_number": null,
  "active_pr_url": null,
  "queue_head_spec_id": "005",
  "resume_spec_id": null,
  "interruption_state": null,
  "last_event_id": "evt-0040",
  "last_report_path": ".ralph/reports/implement-legacy/implement.md",
  "last_verified_at": null,
  "blocked_reason": null,
  "failure_count": 0,
  "next_action": "Continue task 005-T001.",
  "queue_snapshot": []
}
EOF
  cat > "$target/.ralph/state/workflow-state.md" <<'EOF'
# stale workflow projection
EOF
  cat > "$target/.ralph/state/spec-queue.json" <<'EOF'
{
  "schema_version": "1.0.0",
  "queue_policy": {
    "selection": "fifo",
    "preemption": "emergency_only"
  },
  "active_spec_id": "005",
  "resume_spec_id": null,
  "specs": [
    {
      "spec_id": "005",
      "spec_slug": "ios-settings-and-failure-recovery",
      "spec_key": "005-ios-settings-and-failure-recovery",
      "title": "Ambiguous legacy spec",
      "epoch_id": "E003",
      "created_at": "2026-03-08T10:00:00-08:00",
      "last_worked_at": "2026-03-08T10:30:00-08:00",
      "status": "in_progress",
      "kind": "normal",
      "priority_override": null,
      "blocked_reason": null,
      "prd_path": "tasks/prd-legacy.md",
      "spec_path": "specs/005-ios-settings-and-failure-recovery/spec.md",
      "plan_path": "specs/005-ios-settings-and-failure-recovery/plan.md",
      "tasks_path": "specs/005-ios-settings-and-failure-recovery/tasks.md",
      "latest_report_path": ".ralph/reports/implement-legacy/implement.md",
      "branch_name": "codex/005-ios-settings-and-failure-recovery",
      "base_branch": "main",
      "pr_number": null,
      "pr_url": null,
      "pr_state": null,
      "merge_commit": null,
      "task_summary": {
        "total": 2,
        "done": 1,
        "in_progress": 1,
        "blocked": 0
      },
      "next_task_id": "005-T001"
    }
  ]
}
EOF
  cat > "$target/specs/INDEX.md" <<'EOF'
# stale spec index
EOF
  cat > "$target/specs/005-ios-settings-and-failure-recovery/spec.md" <<'EOF'
# Ambiguous Legacy Spec
EOF
  cat > "$target/specs/005-ios-settings-and-failure-recovery/plan.md" <<'EOF'
# Ambiguous Legacy Plan
EOF
  cat > "$target/specs/005-ios-settings-and-failure-recovery/tasks.md" <<'EOF'
# Tasks: 005-ios-settings-and-failure-recovery

- [x] 005-T001 Add the settings route
- [ ] 005-T002 Persist the settings
EOF
}

write_conflicting_legacy_runtime() {
  local target="$1"
  write_positive_legacy_runtime "$target"
  printf 'title = "custom-user-agent"\n' > "$target/agents/custom.toml"
}

write_lease_file() {
  local target="$1"
  local owner_token="$2"
  local holder_thread="$3"
  local run_id="$4"
  local acquired_at="$5"
  local heartbeat_at="$6"
  local expires_at="$7"
  mkdir -p "$target/.ralph/state"
  python3 - "$target/.ralph/state/orchestrator-lease.json" "$owner_token" "$holder_thread" "$run_id" "$acquired_at" "$heartbeat_at" "$expires_at" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
payload = {
    "schema_version": "1.0.0",
    "owner_token": sys.argv[2] or None,
    "holder_thread": sys.argv[3] or None,
    "run_id": sys.argv[4] or None,
    "acquired_at": sys.argv[5] or None,
    "heartbeat_at": sys.argv[6] or None,
    "expires_at": sys.argv[7] or None,
    "status": "held",
}
path.write_text(json.dumps(payload, indent=2) + "\n")
PY
}

write_worktree_collision_runtime() {
  local target="$1"
  write_positive_legacy_runtime "$target"
  mkdir -p "$target/.ralph/reports/follow-on-legacy"
  mkdir -p "$target/specs/002-follow-on-spec"
  cat > "$target/.ralph/reports/follow-on-legacy/release.md" <<'EOF'
# Follow-on Release Report

## Objective

Capture the follow-on handoff for the second spec.
EOF
  cat > "$target/.ralph/state/workflow-state.json" <<'EOF'
{
  "schema_version": "3.0.0",
  "project_name": "collision-target",
  "active_epoch_id": null,
  "active_spec_ids": [],
  "active_interrupt_spec_id": null,
  "active_spec_id": null,
  "active_spec_key": null,
  "active_task_id": null,
  "current_phase": "complete",
  "task_status": null,
  "assigned_role": null,
  "current_branch": "main",
  "current_run_id": "collision-upgrade",
  "active_pr_number": null,
  "active_pr_url": null,
  "queue_head_spec_id": null,
  "orchestrator_lease_path": ".ralph/state/orchestrator-lease.json",
  "orchestrator_intents_path": ".ralph/state/orchestrator-intents.jsonl",
  "lease_owner_token": null,
  "lease_heartbeat_at": null,
  "lease_expires_at": null,
  "scheduler_summary": {
    "normal_execution_limit": 2,
    "active_spec_count": 0,
    "pending_intent_count": 0,
    "dependency_blocked_count": 0
  },
  "resume_spec_id": null,
  "resume_spec_stack": [],
  "interruption_state": null,
  "last_event_id": "evt-0001",
  "last_report_path": ".ralph/reports/release-legacy/release.md",
  "last_verified_at": null,
  "blocked_reason": null,
  "failure_count": 0,
  "next_action": "Queue complete. No remaining specs.",
  "queue_snapshot": []
}
EOF
  cat > "$target/.ralph/state/spec-queue.json" <<'EOF'
{
  "schema_version": "3.0.0",
  "queue_policy": {
    "selection": "fifo_admission_window",
    "preemption": "failing_out_of_scope_bug",
    "normal_execution_limit": 2
  },
  "active_spec_id": null,
  "active_spec_ids": [],
  "active_interrupt_spec_id": null,
  "resume_spec_id": null,
  "specs": [
    {
      "spec_id": "001",
      "spec_slug": "legacy-spec",
      "spec_key": "001-legacy-spec",
      "title": "Legacy completed spec",
      "epoch_id": "E001",
      "created_at": "2026-03-01T10:00:00-08:00",
      "last_worked_at": "2026-03-01T11:00:00-08:00",
      "status": "done",
      "kind": "normal",
      "origin_spec_key": null,
      "origin_task_id": null,
      "triggered_by_role": null,
      "trigger_report_path": null,
      "trigger_summary": null,
      "priority_override": null,
      "blocked_reason": null,
      "depends_on_spec_ids": [],
      "admission_status": "done",
      "admitted_at": null,
      "research_status": "not_started",
      "research_artifact_path": "specs/001-legacy-spec/research.md",
      "research_report_path": null,
      "research_updated_at": null,
      "planning_batch_id": null,
      "prd_path": "tasks/prd-legacy.md",
      "spec_path": "specs/001-legacy-spec/spec.md",
      "plan_path": "specs/001-legacy-spec/plan.md",
      "tasks_path": "specs/001-legacy-spec/tasks.md",
      "task_state_path": "specs/001-legacy-spec/task-state.json",
      "latest_report_path": ".ralph/reports/release-legacy/release.md",
      "worktree_name": "canonical-root",
      "worktree_path": ".",
      "branch_name": "codex/001-legacy-spec",
      "base_branch": "main",
      "slot_status": "inactive",
      "active_task_id": null,
      "task_status": null,
      "assigned_role": null,
      "active_pr_number": 12,
      "active_pr_url": "https://example.test/pull/12",
      "last_dispatch_at": null,
      "pr_number": 12,
      "pr_url": "https://example.test/pull/12",
      "pr_state": "merged",
      "merge_commit": "abc123",
      "task_summary": {
        "total": 2,
        "done": 2,
        "in_progress": 0,
        "blocked": 0
      },
      "next_task_id": null
    },
    {
      "spec_id": "002",
      "spec_slug": "follow-on-spec",
      "spec_key": "002-follow-on-spec",
      "title": "Follow-on completed spec",
      "epoch_id": "E002",
      "created_at": "2026-03-02T10:00:00-08:00",
      "last_worked_at": "2026-03-02T11:00:00-08:00",
      "status": "done",
      "kind": "normal",
      "origin_spec_key": null,
      "origin_task_id": null,
      "triggered_by_role": null,
      "trigger_report_path": null,
      "trigger_summary": null,
      "priority_override": null,
      "blocked_reason": null,
      "depends_on_spec_ids": [],
      "admission_status": "done",
      "admitted_at": null,
      "research_status": "not_started",
      "research_artifact_path": "specs/002-follow-on-spec/research.md",
      "research_report_path": null,
      "research_updated_at": null,
      "planning_batch_id": null,
      "prd_path": "tasks/prd-legacy.md",
      "spec_path": "specs/002-follow-on-spec/spec.md",
      "plan_path": "specs/002-follow-on-spec/plan.md",
      "tasks_path": "specs/002-follow-on-spec/tasks.md",
      "task_state_path": "specs/002-follow-on-spec/task-state.json",
      "latest_report_path": ".ralph/reports/follow-on-legacy/release.md",
      "worktree_name": "canonical-root",
      "worktree_path": ".",
      "branch_name": "codex/002-follow-on-spec",
      "base_branch": "main",
      "slot_status": "inactive",
      "active_task_id": null,
      "task_status": null,
      "assigned_role": null,
      "active_pr_number": null,
      "active_pr_url": null,
      "last_dispatch_at": null,
      "pr_number": null,
      "pr_url": null,
      "pr_state": null,
      "merge_commit": null,
      "task_summary": {
        "total": 1,
        "done": 1,
        "in_progress": 0,
        "blocked": 0
      },
      "next_task_id": null
    }
  ]
}
EOF
  cat > "$target/specs/002-follow-on-spec/spec.md" <<'EOF'
# Follow-on Spec
EOF
  cat > "$target/specs/002-follow-on-spec/plan.md" <<'EOF'
# Follow-on Plan
EOF
  cat > "$target/specs/002-follow-on-spec/tasks.md" <<'EOF'
# Tasks: 002-follow-on-spec

- [x] 002-T001 Release the follow-on flow
EOF
}

write_branch_collision_runtime() {
  local target="$1"
  write_worktree_collision_runtime "$target"
  python3 - "$target" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1]) / ".ralph/state/spec-queue.json"
queue = json.loads(path.read_text())
queue["specs"][1]["branch_name"] = "codex/001-legacy-spec"
path.write_text(json.dumps(queue, indent=2) + "\n")
PY
}

write_shared_report_collision_runtime() {
  local target="$1"
  write_worktree_collision_runtime "$target"
  python3 - "$target" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1]) / ".ralph/state/spec-queue.json"
queue = json.loads(path.read_text())
queue["specs"][1]["latest_report_path"] = ".ralph/reports/release-legacy/release.md"
path.write_text(json.dumps(queue, indent=2) + "\n")
PY
}

INSTALL_TARGET="$TMP_DIR/install-target"
mkdir -p "$INSTALL_TARGET"
printf 'Project loader before install.\n' > "$INSTALL_TARGET/AGENTS.md"
printf 'Claude loader before install.\n' > "$INSTALL_TARGET/CLAUDE.md"
copy_manifest_paths src/install-manifest.txt "$INSTALL_TARGET"
create_generated_runtime "$INSTALL_TARGET"
render_loader_block src/AGENTS.md > "$TMP_DIR/managed-agents-block.md"
render_loader_block src/CLAUDE.md > "$TMP_DIR/managed-claude-block.md"
sync_loader_files "$INSTALL_TARGET"
python3 scripts/check-installed-runtime-state.py --repo "$INSTALL_TARGET"

[[ -d "$INSTALL_TARGET/.codex/agents" ]] || {
  echo "smoke-test-install-upgrade: missing .codex/agents after install" >&2
  exit 1
}

[[ -d "$INSTALL_TARGET/.claude/agents" ]] || {
  echo "smoke-test-install-upgrade: missing .claude/agents after install" >&2
  exit 1
}

[[ -d "$INSTALL_TARGET/.cursor/rules" ]] || {
  echo "smoke-test-install-upgrade: missing .cursor/rules after install" >&2
  exit 1
}

[[ -f "$INSTALL_TARGET/.codex/hooks.json" ]] || {
  echo "smoke-test-install-upgrade: missing .codex/hooks.json after install" >&2
  exit 1
}

[[ -f "$INSTALL_TARGET/.claude/settings.json" ]] || {
  echo "smoke-test-install-upgrade: missing .claude/settings.json after install" >&2
  exit 1
}

[[ -f "$INSTALL_TARGET/.cursor/hooks.json" ]] || {
  echo "smoke-test-install-upgrade: missing .cursor/hooks.json after install" >&2
  exit 1
}

[[ -f "$INSTALL_TARGET/.ralph/hooks/stop-boundary.py" ]] || {
  echo "smoke-test-install-upgrade: missing .ralph/hooks/stop-boundary.py after install" >&2
  exit 1
}

[[ ! -d "$INSTALL_TARGET/agents" ]] || {
  echo "smoke-test-install-upgrade: legacy root agents directory should not exist after install" >&2
  exit 1
}

[[ -f "$INSTALL_TARGET/.ralph/runtime-contract.md" ]] || {
  echo "smoke-test-install-upgrade: missing runtime-contract after install" >&2
  exit 1
}

[[ -f "$INSTALL_TARGET/.ralph/policy/runtime-overrides.md" ]] || {
  echo "smoke-test-install-upgrade: missing runtime-overrides after install" >&2
  exit 1
}

[[ -f "$INSTALL_TARGET/.ralph/harness-version.json" ]] || {
  echo "smoke-test-install-upgrade: missing harness-version after install" >&2
  exit 1
}

grep -Fq "$MANAGED_START" "$INSTALL_TARGET/AGENTS.md" || {
  echo "smoke-test-install-upgrade: AGENTS.md missing managed block start" >&2
  exit 1
}

grep -Fq "$MANAGED_END" "$INSTALL_TARGET/AGENTS.md" || {
  echo "smoke-test-install-upgrade: AGENTS.md missing managed block end" >&2
  exit 1
}

grep -Fq "$MANAGED_START" "$INSTALL_TARGET/CLAUDE.md" || {
  echo "smoke-test-install-upgrade: CLAUDE.md missing managed block start" >&2
  exit 1
}

grep -Fq "$MANAGED_END" "$INSTALL_TARGET/CLAUDE.md" || {
  echo "smoke-test-install-upgrade: CLAUDE.md missing managed block end" >&2
  exit 1
}

grep -Fq 'Project loader before install.' "$INSTALL_TARGET/AGENTS.md" || {
  echo "smoke-test-install-upgrade: AGENTS.md non-Ralph content was not preserved during install" >&2
  exit 1
}

grep -Fq 'Claude loader before install.' "$INSTALL_TARGET/CLAUDE.md" || {
  echo "smoke-test-install-upgrade: CLAUDE.md non-Ralph content was not preserved during install" >&2
  exit 1
}

python3 scripts/check-upgrade-surface.py --repo "$INSTALL_TARGET"
python3 - <<'PY' "$INSTALL_TARGET"
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
project_facts = json.loads((root / ".ralph/context/project-facts.json").read_text())
assert project_facts["orchestrator_stop_hook"] == {
    "enabled": True,
    "mode": "conservative",
    "max_auto_continue_count": 1,
}
assert project_facts["worktree_bootstrap_commands"] == []
assert project_facts["bootstrap_env_files"] == []
assert "node_modules" in project_facts["bootstrap_copy_exclude_globs"]
assert ".venv/**" in project_facts["bootstrap_copy_exclude_globs"]

codex_hooks = json.loads((root / ".codex/hooks.json").read_text())
assert codex_hooks["hooks"]["Stop"][0]["hooks"][0]["command"] == "python3 ./.ralph/hooks/stop-boundary.py --runtime codex"

claude_settings = json.loads((root / ".claude/settings.json").read_text())
assert claude_settings["hooks"]["Stop"][0]["hooks"][0]["command"] == 'python3 "$CLAUDE_PROJECT_DIR"/.ralph/hooks/stop-boundary.py --runtime claude'

cursor_hooks = json.loads((root / ".cursor/hooks.json").read_text())
assert cursor_hooks["hooks"]["stop"][0]["command"] == "python3 ./.ralph/hooks/stop-boundary.py --runtime cursor"
PY

OVERLAY_TARGET="$TMP_DIR/overlay-target"
mkdir -p "$OVERLAY_TARGET"
copy_manifest_paths src/install-manifest.txt "$OVERLAY_TARGET"
create_generated_runtime "$OVERLAY_TARGET"
sync_loader_files "$OVERLAY_TARGET"
printf 'keep-runtime-overrides\n' > "$OVERLAY_TARGET/.ralph/policy/runtime-overrides.md"
python3 scripts/check-upgrade-surface.py --repo "$OVERLAY_TARGET"
copy_manifest_paths src/upgrade-manifest.txt "$OVERLAY_TARGET"
sync_loader_files "$OVERLAY_TARGET"
python3 scripts/migrate-installed-runtime.py --repo "$OVERLAY_TARGET"
python3 scripts/check-installed-runtime-state.py --repo "$OVERLAY_TARGET"
grep -Fq 'keep-runtime-overrides' "$OVERLAY_TARGET/.ralph/policy/runtime-overrides.md" || {
  echo "smoke-test-install-upgrade: runtime overrides changed during upgrade" >&2
  exit 1
}

DRIFTED_RUNTIME_TARGET="$TMP_DIR/drifted-runtime-target"
mkdir -p "$DRIFTED_RUNTIME_TARGET"
copy_manifest_paths src/install-manifest.txt "$DRIFTED_RUNTIME_TARGET"
create_generated_runtime "$DRIFTED_RUNTIME_TARGET"
sync_loader_files "$DRIFTED_RUNTIME_TARGET"
printf '\n## Local Drift\n\n- keep custom runtime edits here.\n' >> "$DRIFTED_RUNTIME_TARGET/.ralph/runtime-contract.md"
if python3 scripts/check-upgrade-surface.py --repo "$DRIFTED_RUNTIME_TARGET"; then
  echo "smoke-test-install-upgrade: direct runtime-contract edits should have blocked upgrade preflight" >&2
  exit 1
fi

DRIFTED_MANAGED_SKILL_TARGET="$TMP_DIR/drifted-managed-skill-target"
mkdir -p "$DRIFTED_MANAGED_SKILL_TARGET"
copy_manifest_paths src/install-manifest.txt "$DRIFTED_MANAGED_SKILL_TARGET"
create_generated_runtime "$DRIFTED_MANAGED_SKILL_TARGET"
sync_loader_files "$DRIFTED_MANAGED_SKILL_TARGET"
printf '\nLocal managed-skill drift.\n' >> "$DRIFTED_MANAGED_SKILL_TARGET/.agents/skills/bootstrap/SKILL.md"
if python3 scripts/check-upgrade-surface.py --repo "$DRIFTED_MANAGED_SKILL_TARGET"; then
  echo "smoke-test-install-upgrade: managed runtime skill drift should have blocked upgrade preflight" >&2
  exit 1
fi

LEGACY_TARGET="$TMP_DIR/legacy-target"
write_positive_legacy_runtime "$LEGACY_TARGET"
python3 scripts/check-upgrade-surface.py --repo "$LEGACY_TARGET"
copy_manifest_paths src/upgrade-manifest.txt "$LEGACY_TARGET"
sync_loader_files "$LEGACY_TARGET"
python3 scripts/migrate-installed-runtime.py --repo "$LEGACY_TARGET"
python3 scripts/check-installed-runtime-state.py --repo "$LEGACY_TARGET"

[[ -d "$LEGACY_TARGET/.codex/agents" ]] || {
  echo "smoke-test-install-upgrade: missing .codex/agents after legacy upgrade" >&2
  exit 1
}

[[ ! -d "$LEGACY_TARGET/agents" ]] || {
  echo "smoke-test-install-upgrade: legacy root agents directory should be removed after migration" >&2
  exit 1
}

grep -Fq 'keep-policy' "$LEGACY_TARGET/.ralph/policy/project-policy.md" || {
  echo "smoke-test-install-upgrade: policy changed during upgrade" >&2
  exit 1
}

grep -Fq 'keep-context' "$LEGACY_TARGET/.ralph/context/project-truths.md" || {
  echo "smoke-test-install-upgrade: context changed during upgrade" >&2
  exit 1
}

[[ -f "$LEGACY_TARGET/.ralph/policy/runtime-overrides.md" ]] || {
  echo "smoke-test-install-upgrade: runtime-overrides missing after legacy upgrade" >&2
  exit 1
}

grep -Fq 'keep-tasks' "$LEGACY_TARGET/tasks/todo.md" || {
  echo "smoke-test-install-upgrade: tasks changed during upgrade" >&2
  exit 1
}

grep -Fq '# Legacy Spec' "$LEGACY_TARGET/specs/001-legacy-spec/spec.md" || {
  echo "smoke-test-install-upgrade: spec prose changed during upgrade" >&2
  exit 1
}

python3 - <<'PY' "$LEGACY_TARGET"
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
workflow = json.loads((root / ".ralph/state/workflow-state.json").read_text())
queue = json.loads((Path(sys.argv[1]) / ".ralph/state/spec-queue.json").read_text())
spec = queue["specs"][0]
assert spec["research_status"] == "not_started"
assert spec["research_artifact_path"] == "specs/001-legacy-spec/research.md"
assert spec["planning_batch_id"] is None
assert workflow["last_report_path"] == ".ralph/reports/release-legacy/001-legacy-spec/release.md"
assert spec["latest_report_path"] == ".ralph/reports/release-legacy/001-legacy-spec/release.md"
assert (root / workflow["last_report_path"]).exists()
task_state = json.loads((root / "specs/001-legacy-spec/task-state.json").read_text())
assert task_state["tasks"][0]["last_report_path"] == ".ralph/reports/release-legacy/001-legacy-spec/release.md"
PY

HEALTHY_LEASE_TARGET="$TMP_DIR/healthy-lease-target"
write_positive_legacy_runtime "$HEALTHY_LEASE_TARGET"
copy_manifest_paths src/upgrade-manifest.txt "$HEALTHY_LEASE_TARGET"
sync_loader_files "$HEALTHY_LEASE_TARGET"
write_lease_file \
  "$HEALTHY_LEASE_TARGET" \
  "lease-owner-1" \
  "thread-1" \
  "run-healthy" \
  "2026-03-08T12:00:00-08:00" \
  "2026-03-08T12:01:00-08:00" \
  "2099-03-08T12:03:00-08:00"
if python3 scripts/migrate-installed-runtime.py --repo "$HEALTHY_LEASE_TARGET"; then
  echo "smoke-test-install-upgrade: healthy held lease should have blocked upgrade" >&2
  exit 1
fi

STALE_LEASE_TARGET="$TMP_DIR/stale-lease-target"
write_positive_legacy_runtime "$STALE_LEASE_TARGET"
copy_manifest_paths src/upgrade-manifest.txt "$STALE_LEASE_TARGET"
sync_loader_files "$STALE_LEASE_TARGET"
write_lease_file \
  "$STALE_LEASE_TARGET" \
  "lease-owner-stale" \
  "thread-stale" \
  "run-stale" \
  "2026-03-08T12:00:00-08:00" \
  "2026-03-08T12:01:00-08:00" \
  "2026-03-08T12:02:00-08:00"
python3 scripts/migrate-installed-runtime.py --repo "$STALE_LEASE_TARGET"
python3 scripts/check-installed-runtime-state.py --repo "$STALE_LEASE_TARGET"
python3 - <<'PY' "$STALE_LEASE_TARGET"
import json
import sys
from pathlib import Path

lease = json.loads((Path(sys.argv[1]) / ".ralph/state/orchestrator-lease.json").read_text())
assert lease["status"] == "idle"
assert lease["owner_token"] is None
assert lease["heartbeat_at"] is None
assert lease["expires_at"] is None
PY

WORKTREE_COLLISION_TARGET="$TMP_DIR/worktree-collision-target"
write_worktree_collision_runtime "$WORKTREE_COLLISION_TARGET"
copy_manifest_paths src/upgrade-manifest.txt "$WORKTREE_COLLISION_TARGET"
sync_loader_files "$WORKTREE_COLLISION_TARGET"
python3 scripts/migrate-installed-runtime.py --repo "$WORKTREE_COLLISION_TARGET"
python3 scripts/check-installed-runtime-state.py --repo "$WORKTREE_COLLISION_TARGET"
python3 - <<'PY' "$WORKTREE_COLLISION_TARGET"
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
queue = json.loads((root / ".ralph/state/spec-queue.json").read_text())
names = [spec["worktree_name"] for spec in queue["specs"]]
paths = [spec["worktree_path"] for spec in queue["specs"]]
assert len(names) == len(set(names))
assert len(paths) == len(set(paths))
assert all(path.startswith(".ralph/worktrees/") for path in paths)
reports = [spec["latest_report_path"] for spec in queue["specs"]]
assert reports == [
    ".ralph/reports/release-legacy/001-legacy-spec/release.md",
    ".ralph/reports/follow-on-legacy/002-follow-on-spec/release.md",
]
assert all((root / report).exists() for report in reports)
PY

SHARED_REPORT_COLLISION_TARGET="$TMP_DIR/shared-report-collision-target"
write_shared_report_collision_runtime "$SHARED_REPORT_COLLISION_TARGET"
copy_manifest_paths src/upgrade-manifest.txt "$SHARED_REPORT_COLLISION_TARGET"
sync_loader_files "$SHARED_REPORT_COLLISION_TARGET"
if python3 scripts/migrate-installed-runtime.py --repo "$SHARED_REPORT_COLLISION_TARGET"; then
  echo "smoke-test-install-upgrade: ambiguous shared legacy report ownership should have failed" >&2
  exit 1
fi

BRANCH_COLLISION_TARGET="$TMP_DIR/branch-collision-target"
write_branch_collision_runtime "$BRANCH_COLLISION_TARGET"
copy_manifest_paths src/upgrade-manifest.txt "$BRANCH_COLLISION_TARGET"
sync_loader_files "$BRANCH_COLLISION_TARGET"
if python3 scripts/migrate-installed-runtime.py --repo "$BRANCH_COLLISION_TARGET"; then
  echo "smoke-test-install-upgrade: duplicate branch assignment should have failed" >&2
  exit 1
fi

CUSTOM_CONFIG_TARGET="$TMP_DIR/custom-config-target"
mkdir -p "$CUSTOM_CONFIG_TARGET"
copy_manifest_paths src/install-manifest.txt "$CUSTOM_CONFIG_TARGET"
create_generated_runtime "$CUSTOM_CONFIG_TARGET"
sync_loader_files "$CUSTOM_CONFIG_TARGET"
cat > "$CUSTOM_CONFIG_TARGET/.codex/config.toml" <<'EOF'
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "danger-full-access"

[features]
multi_agent = false

[agents]
max_threads = 9
max_depth = 3

[agents.orchestrator]
config_file = "../agents/orchestrator.toml"

[agents.prd]
config_file = "../agents/prd.toml"

[agents.specify]
config_file = "../agents/specify.toml"

[agents.plan]
config_file = "../agents/plan.toml"

[agents.task_gen]
config_file = "../agents/task-gen.toml"

[agents.implement]
config_file = "../agents/implement.toml"

[agents.review]
config_file = "../agents/review.toml"

[agents.verify]
config_file = "../agents/verify.toml"

[agents.release]
config_file = "../agents/release.toml"

[agents.custom]
config_file = "agents/custom.toml"
EOF
cat > "$CUSTOM_CONFIG_TARGET/.codex/agents/custom.toml" <<'EOF'
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "workspace-write"
developer_instructions = """
Custom user agent.
"""
EOF
cat > "$CUSTOM_CONFIG_TARGET/.codex/hooks.json" <<'EOF'
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ./.codex/hooks/custom-stop.py"
          }
        ]
      }
    ]
  }
}
EOF
mkdir -p "$CUSTOM_CONFIG_TARGET/.claude" "$CUSTOM_CONFIG_TARGET/.cursor" "$CUSTOM_CONFIG_TARGET/.agents/skills/custom-user-skill"
cat > "$CUSTOM_CONFIG_TARGET/.claude/settings.json" <<'EOF'
{
  "env": {
    "KEEP_ME": "true"
  },
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/custom-stop.py"
          }
        ]
      }
    ]
  }
}
EOF
cat > "$CUSTOM_CONFIG_TARGET/.cursor/hooks.json" <<'EOF'
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [
      {
        "command": "./hooks/check-shell.sh",
        "matcher": "curl|wget"
      }
    ],
    "stop": [
      {
        "command": "./hooks/custom-stop.sh",
        "failClosed": true
      }
    ]
  }
}
EOF
cat > "$CUSTOM_CONFIG_TARGET/.agents/skills/custom-user-skill/SKILL.md" <<'EOF'
# Custom User Skill

Preserve this during Ralph upgrades.
EOF
copy_manifest_paths src/upgrade-manifest.txt "$CUSTOM_CONFIG_TARGET"
python3 scripts/migrate-installed-runtime.py --repo "$CUSTOM_CONFIG_TARGET"
python3 scripts/check-installed-runtime-state.py --repo "$CUSTOM_CONFIG_TARGET"
python3 - <<'PY' "$CUSTOM_CONFIG_TARGET"
import json
from pathlib import Path
import sys

try:
    import tomllib
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib

config = tomllib.loads((Path(sys.argv[1]) / ".codex/config.toml").read_text())
assert config["sandbox_mode"] == "danger-full-access"
assert config["features"]["multi_agent"] is True
assert config["features"]["codex_hooks"] is True
assert config["agents"]["max_threads"] == 9
assert config["agents"]["max_depth"] == 2
assert config["agents"]["orchestrator"]["config_file"] == "agents/orchestrator.toml"
assert config["agents"]["research"]["config_file"] == "agents/research.toml"
assert config["agents"]["plan_check"]["config_file"] == "agents/plan-check.toml"
assert config["agents"]["custom"]["config_file"] == "agents/custom.toml"

codex_hooks = json.loads((Path(sys.argv[1]) / ".codex/hooks.json").read_text())
codex_stop_commands = [
    hook["command"]
    for group in codex_hooks["hooks"]["Stop"]
    for hook in group.get("hooks", [])
]
assert "python3 ./.codex/hooks/custom-stop.py" in codex_stop_commands
assert "python3 ./.ralph/hooks/stop-boundary.py --runtime codex" in codex_stop_commands

claude_settings = json.loads((Path(sys.argv[1]) / ".claude/settings.json").read_text())
claude_stop_commands = [
    hook["command"]
    for group in claude_settings["hooks"]["Stop"]
    for hook in group.get("hooks", [])
]
assert claude_settings["env"]["KEEP_ME"] == "true"
assert 'python3 "$CLAUDE_PROJECT_DIR"/.claude/custom-stop.py' in claude_stop_commands
assert 'python3 "$CLAUDE_PROJECT_DIR"/.ralph/hooks/stop-boundary.py --runtime claude' in claude_stop_commands

cursor_hooks = json.loads((Path(sys.argv[1]) / ".cursor/hooks.json").read_text())
assert cursor_hooks["hooks"]["beforeShellExecution"][0]["command"] == "./hooks/check-shell.sh"
cursor_stop_commands = [entry["command"] for entry in cursor_hooks["hooks"]["stop"]]
assert "./hooks/custom-stop.sh" in cursor_stop_commands
assert "python3 ./.ralph/hooks/stop-boundary.py --runtime cursor" in cursor_stop_commands
assert (Path(sys.argv[1]) / ".agents/skills/custom-user-skill/SKILL.md").exists()

orchestrator = tomllib.loads((Path(sys.argv[1]) / ".codex/agents/orchestrator.toml").read_text())
implement = tomllib.loads((Path(sys.argv[1]) / ".codex/agents/implement.toml").read_text())
review = tomllib.loads((Path(sys.argv[1]) / ".codex/agents/review.toml").read_text())
plan_check = tomllib.loads((Path(sys.argv[1]) / ".codex/agents/plan-check.toml").read_text())

assert orchestrator["sandbox_mode"] == "danger-full-access"
assert implement["sandbox_mode"] == "danger-full-access"
assert review["sandbox_mode"] == "danger-full-access"
assert plan_check["sandbox_mode"] == "danger-full-access"
PY

[[ -f "$LEGACY_TARGET/.ralph/runtime-contract.md" ]] || {
  echo "smoke-test-install-upgrade: runtime-contract missing after upgrade" >&2
  exit 1
}

[[ -f "$LEGACY_TARGET/.ralph/harness-version.json" ]] || {
  echo "smoke-test-install-upgrade: harness-version missing after upgrade" >&2
  exit 1
}

AMBIGUOUS_TARGET="$TMP_DIR/ambiguous-target"
write_ambiguous_legacy_runtime "$AMBIGUOUS_TARGET"
copy_manifest_paths src/upgrade-manifest.txt "$AMBIGUOUS_TARGET"
sync_loader_files "$AMBIGUOUS_TARGET"

if python3 scripts/migrate-installed-runtime.py --repo "$AMBIGUOUS_TARGET"; then
  echo "smoke-test-install-upgrade: ambiguous migration should have failed" >&2
  exit 1
fi

if python3 scripts/check-installed-runtime-state.py --repo "$AMBIGUOUS_TARGET"; then
  echo "smoke-test-install-upgrade: ambiguous runtime preflight should have failed" >&2
  exit 1
fi

CONFLICT_TARGET="$TMP_DIR/conflict-target"
write_conflicting_legacy_runtime "$CONFLICT_TARGET"
copy_manifest_paths src/upgrade-manifest.txt "$CONFLICT_TARGET"
sync_loader_files "$CONFLICT_TARGET"

if python3 scripts/migrate-installed-runtime.py --repo "$CONFLICT_TARGET"; then
  echo "smoke-test-install-upgrade: conflicting legacy agent layout should have failed" >&2
  exit 1
fi

ATOMIC_PASS_TARGET="$TMP_DIR/atomic-pass-target"
mkdir -p "$ATOMIC_PASS_TARGET"
copy_manifest_paths src/install-manifest.txt "$ATOMIC_PASS_TARGET"
create_generated_runtime "$ATOMIC_PASS_TARGET"
sync_loader_files "$ATOMIC_PASS_TARGET"
init_git_repo "$ATOMIC_PASS_TARGET"
write_atomic_runtime "$ATOMIC_PASS_TARGET"
git -C "$ATOMIC_PASS_TARGET" add .ralph/reports .ralph/state specs tasks
git -C "$ATOMIC_PASS_TARGET" commit -q -m "chore: seed atomic runtime fixture"
normalize_current_runtime_fixture "$ATOMIC_PASS_TARGET"
ATOMIC_PASS_WORKTREE="$ATOMIC_PASS_TARGET/.ralph/worktrees/001-atomic-commit-demo"
git -C "$ATOMIC_PASS_TARGET" add AGENTS.md CLAUDE.md .codex .claude .cursor .agents .ralph/context .ralph/harness-version.json .ralph/logs .ralph/policy .ralph/reports .ralph/state specs tasks
git -C "$ATOMIC_PASS_TARGET" commit -q -m "chore: normalize canonical control plane"
printf '\nImplemented from the spec worktree.\n' >> "$ATOMIC_PASS_WORKTREE/specs/001-atomic-commit-demo/spec.md"
git -C "$ATOMIC_PASS_WORKTREE" add .
git -C "$ATOMIC_PASS_WORKTREE" commit -q -m "feat: implement 001-T001"
ATOMIC_PASS_SHA="$(git -C "$ATOMIC_PASS_WORKTREE" rev-parse --short HEAD)"
write_atomic_report "$ATOMIC_PASS_TARGET" "None." "$ATOMIC_PASS_SHA"
git -C "$ATOMIC_PASS_TARGET" add .ralph/reports/atomic-20260308/implement.md
git -C "$ATOMIC_PASS_TARGET" commit -q -m "docs: record 001-T001 commit evidence"
python3 scripts/check-installed-runtime-state.py --repo "$ATOMIC_PASS_TARGET"
python3 scripts/check-installed-runtime-state.py --repo "$ATOMIC_PASS_WORKTREE"
ATOMIC_AUX_WORKTREE="$ATOMIC_PASS_TARGET/.ralph/worktrees/aux-canonical-overlay-check"
git -C "$ATOMIC_PASS_TARGET" worktree add -q -b ralph/aux-canonical-overlay-check "$ATOMIC_AUX_WORKTREE" main
python3 - <<'PY' "$ATOMIC_PASS_TARGET" "$ATOMIC_AUX_WORKTREE"
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "scripts"))

from runtime_state_helpers import ensure_worktree_shared_overlay

root = Path(sys.argv[1])
aux = Path(sys.argv[2])
ensure_worktree_shared_overlay(root, aux)
PY
python3 - <<'PY' "$ATOMIC_PASS_TARGET" "$ATOMIC_PASS_WORKTREE" "$ATOMIC_AUX_WORKTREE"
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "scripts"))

from runtime_state_helpers import resolve_canonical_checkout_root

root = Path(sys.argv[1]).resolve()
worktrees = [Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()]
expected_queue = json.loads((root / ".ralph/state/spec-queue.json").read_text())
expected_lease = json.loads((root / ".ralph/state/orchestrator-lease.json").read_text())
expected_claims = json.loads((root / ".ralph/state/worker-claims.json").read_text())
expected_report = (root / ".ralph/reports/atomic-20260308/implement.md").read_text()
for worktree in worktrees:
    assert resolve_canonical_checkout_root(worktree) == root
    assert (worktree / ".ralph/shared/state").is_symlink()
    assert (worktree / ".ralph/shared/reports").is_symlink()
    assert json.loads((worktree / ".ralph/shared/state/spec-queue.json").read_text()) == expected_queue
    assert json.loads((worktree / ".ralph/shared/state/orchestrator-lease.json").read_text()) == expected_lease
    assert json.loads((worktree / ".ralph/shared/state/worker-claims.json").read_text()) == expected_claims
    assert (worktree / ".ralph/shared/reports/atomic-20260308/implement.md").read_text() == expected_report
PY

CANONICAL_RECONCILE_TARGET="$TMP_DIR/canonical-reconcile-target"
mkdir -p "$CANONICAL_RECONCILE_TARGET"
copy_manifest_paths src/install-manifest.txt "$CANONICAL_RECONCILE_TARGET"
create_generated_runtime "$CANONICAL_RECONCILE_TARGET"
sync_loader_files "$CANONICAL_RECONCILE_TARGET"
init_git_repo "$CANONICAL_RECONCILE_TARGET"
write_atomic_runtime "$CANONICAL_RECONCILE_TARGET"
git -C "$CANONICAL_RECONCILE_TARGET" add .ralph/reports .ralph/state specs tasks
git -C "$CANONICAL_RECONCILE_TARGET" commit -q -m "chore: seed canonical reconcile fixture"
normalize_current_runtime_fixture "$CANONICAL_RECONCILE_TARGET"
CANONICAL_RECONCILE_WORKTREE="$CANONICAL_RECONCILE_TARGET/.ralph/worktrees/001-atomic-commit-demo"
python3 - <<'PY' "$CANONICAL_RECONCILE_WORKTREE/.ralph/state/spec-queue.json"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
payload = json.loads(path.read_text())
payload["specs"][0]["title"] = "WRONG WORKTREE TITLE"
path.write_text(json.dumps(payload, indent=2) + "\n")
PY
python3 scripts/orchestrator-coordination.py reconcile \
  --repo "$CANONICAL_RECONCILE_WORKTREE" \
  --owner-token canonical-reconcile-owner \
  --holder-thread canonical-reconcile-thread \
  --run-id canonical-reconcile-run
python3 - <<'PY' "$CANONICAL_RECONCILE_TARGET"
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
queue = json.loads((root / ".ralph/state/spec-queue.json").read_text())
assert queue["specs"][0]["title"] != "WRONG WORKTREE TITLE"
PY

PARALLEL_RESEARCH_TARGET="$TMP_DIR/parallel-research-target"
mkdir -p "$PARALLEL_RESEARCH_TARGET"
copy_manifest_paths src/install-manifest.txt "$PARALLEL_RESEARCH_TARGET"
create_generated_runtime "$PARALLEL_RESEARCH_TARGET"
sync_loader_files "$PARALLEL_RESEARCH_TARGET"
write_parallel_research_runtime "$PARALLEL_RESEARCH_TARGET"
normalize_current_runtime_fixture "$PARALLEL_RESEARCH_TARGET"
python3 scripts/check-installed-runtime-state.py --repo "$PARALLEL_RESEARCH_TARGET"
python3 - <<'PY' "$PARALLEL_RESEARCH_TARGET"
import json
import sys
from pathlib import Path

queue = json.loads((Path(sys.argv[1]) / ".ralph/state/spec-queue.json").read_text())
batch_ids = {spec["planning_batch_id"] for spec in queue["specs"]}
research_statuses = {spec["research_status"] for spec in queue["specs"]}
assert batch_ids == {"batch-20260308-demo"}
assert research_statuses == {"done", "in_progress"}
assert queue["active_spec_id"] is None
PY

ATOMIC_MULTI_TARGET="$TMP_DIR/atomic-multi-target"
mkdir -p "$ATOMIC_MULTI_TARGET"
copy_manifest_paths src/install-manifest.txt "$ATOMIC_MULTI_TARGET"
create_generated_runtime "$ATOMIC_MULTI_TARGET"
sync_loader_files "$ATOMIC_MULTI_TARGET"
init_git_repo "$ATOMIC_MULTI_TARGET"
write_atomic_runtime "$ATOMIC_MULTI_TARGET"
git -C "$ATOMIC_MULTI_TARGET" add .ralph/reports .ralph/state specs tasks
git -C "$ATOMIC_MULTI_TARGET" commit -q -m "chore: seed atomic runtime fixture"
normalize_current_runtime_fixture "$ATOMIC_MULTI_TARGET"
ATOMIC_MULTI_WORKTREE="$ATOMIC_MULTI_TARGET/.ralph/worktrees/001-atomic-commit-demo"
git -C "$ATOMIC_MULTI_TARGET" add AGENTS.md CLAUDE.md .codex .claude .cursor .agents .ralph/context .ralph/harness-version.json .ralph/logs .ralph/policy .ralph/reports .ralph/state specs tasks
git -C "$ATOMIC_MULTI_TARGET" commit -q -m "chore: normalize canonical control plane"
printf '\nFirst checkpoint for the same task.\n' >> "$ATOMIC_MULTI_WORKTREE/specs/001-atomic-commit-demo/spec.md"
git -C "$ATOMIC_MULTI_WORKTREE" add .
git -C "$ATOMIC_MULTI_WORKTREE" commit -q -m "feat: implement core of 001-T001"
printf '\nSecond checkpoint for the same task.\n' >> "$ATOMIC_MULTI_WORKTREE/specs/001-atomic-commit-demo/spec.md"
git -C "$ATOMIC_MULTI_WORKTREE" add specs/001-atomic-commit-demo/spec.md
git -C "$ATOMIC_MULTI_WORKTREE" commit -q -m "test: finish 001-T001 checkpoint"
ATOMIC_MULTI_SHA="$(git -C "$ATOMIC_MULTI_WORKTREE" rev-parse --short HEAD)"
ATOMIC_MULTI_PREV_SHA="$(git -C "$ATOMIC_MULTI_WORKTREE" rev-parse --short HEAD~1)"
write_atomic_report "$ATOMIC_MULTI_TARGET" "\`$ATOMIC_MULTI_PREV_SHA..$ATOMIC_MULTI_SHA\`" "$ATOMIC_MULTI_SHA"
git -C "$ATOMIC_MULTI_TARGET" add .ralph/reports/atomic-20260308/implement.md
git -C "$ATOMIC_MULTI_TARGET" commit -q -m "docs: record 001-T001 multi-commit evidence"
python3 scripts/check-installed-runtime-state.py --repo "$ATOMIC_MULTI_TARGET"

ATOMIC_DIRTY_TARGET="$TMP_DIR/atomic-dirty-target"
cp -R "$ATOMIC_PASS_TARGET" "$ATOMIC_DIRTY_TARGET"
printf '\nUncommitted change.\n' >> "$ATOMIC_DIRTY_TARGET/.ralph/worktrees/001-atomic-commit-demo/specs/001-atomic-commit-demo/spec.md"
if python3 scripts/check-installed-runtime-state.py --repo "$ATOMIC_DIRTY_TARGET"; then
  echo "smoke-test-install-upgrade: dirty worktree should have failed" >&2
  exit 1
fi

CONTROL_PLANE_DIRTY_TARGET="$TMP_DIR/control-plane-dirty-target"
mkdir -p "$CONTROL_PLANE_DIRTY_TARGET"
copy_manifest_paths src/install-manifest.txt "$CONTROL_PLANE_DIRTY_TARGET"
create_generated_runtime "$CONTROL_PLANE_DIRTY_TARGET"
sync_loader_files "$CONTROL_PLANE_DIRTY_TARGET"
init_git_repo "$CONTROL_PLANE_DIRTY_TARGET"
write_atomic_runtime "$CONTROL_PLANE_DIRTY_TARGET"
git -C "$CONTROL_PLANE_DIRTY_TARGET" add .ralph/reports .ralph/state specs tasks
git -C "$CONTROL_PLANE_DIRTY_TARGET" commit -q -m "chore: seed control-plane dirty fixture"
normalize_current_runtime_fixture "$CONTROL_PLANE_DIRTY_TARGET"
python3 - <<'PY' "$CONTROL_PLANE_DIRTY_TARGET/.ralph/worktrees/001-atomic-commit-demo/.ralph/state/spec-queue.json"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
payload = json.loads(path.read_text())
payload["specs"][0]["title"] = "DIRTY SHARED STATE"
path.write_text(json.dumps(payload, indent=2) + "\n")
PY
if python3 scripts/check-installed-runtime-state.py --repo "$CONTROL_PLANE_DIRTY_TARGET"; then
  echo "smoke-test-install-upgrade: worktree-local shared-control-plane edits should have failed" >&2
  exit 1
fi

ATOMIC_MISSING_REPORT_TARGET="$TMP_DIR/atomic-missing-report-target"
mkdir -p "$ATOMIC_MISSING_REPORT_TARGET"
copy_manifest_paths src/install-manifest.txt "$ATOMIC_MISSING_REPORT_TARGET"
create_generated_runtime "$ATOMIC_MISSING_REPORT_TARGET"
sync_loader_files "$ATOMIC_MISSING_REPORT_TARGET"
init_git_repo "$ATOMIC_MISSING_REPORT_TARGET"
write_atomic_runtime "$ATOMIC_MISSING_REPORT_TARGET"
git -C "$ATOMIC_MISSING_REPORT_TARGET" add .ralph/reports .ralph/state specs tasks
git -C "$ATOMIC_MISSING_REPORT_TARGET" commit -q -m "chore: seed atomic runtime fixture"
normalize_current_runtime_fixture "$ATOMIC_MISSING_REPORT_TARGET"
ATOMIC_MISSING_WORKTREE="$ATOMIC_MISSING_REPORT_TARGET/.ralph/worktrees/001-atomic-commit-demo"
git -C "$ATOMIC_MISSING_REPORT_TARGET" add AGENTS.md CLAUDE.md .codex .claude .cursor .agents .ralph/context .ralph/harness-version.json .ralph/logs .ralph/policy .ralph/reports .ralph/state specs tasks
git -C "$ATOMIC_MISSING_REPORT_TARGET" commit -q -m "chore: normalize canonical control plane"
printf '\nImplemented without a complete report.\n' >> "$ATOMIC_MISSING_WORKTREE/specs/001-atomic-commit-demo/spec.md"
git -C "$ATOMIC_MISSING_WORKTREE" add .
git -C "$ATOMIC_MISSING_WORKTREE" commit -q -m "feat: implement 001-T001"
cat > "$ATOMIC_MISSING_REPORT_TARGET/.ralph/reports/atomic-20260308/implement.md" <<'EOF'
# Implementation Report

## Objective

Complete task `001-T001` with an atomic checkpoint.
EOF
git -C "$ATOMIC_MISSING_REPORT_TARGET" add .ralph/reports/atomic-20260308/implement.md
git -C "$ATOMIC_MISSING_REPORT_TARGET" commit -q -m "docs: write incomplete 001-T001 report"
if python3 scripts/check-installed-runtime-state.py --repo "$ATOMIC_MISSING_REPORT_TARGET"; then
  echo "smoke-test-install-upgrade: missing commit evidence should have failed" >&2
  exit 1
fi

ATOMIC_BRANCH_MISMATCH_TARGET="$TMP_DIR/atomic-branch-mismatch-target"
mkdir -p "$ATOMIC_BRANCH_MISMATCH_TARGET"
copy_manifest_paths src/install-manifest.txt "$ATOMIC_BRANCH_MISMATCH_TARGET"
create_generated_runtime "$ATOMIC_BRANCH_MISMATCH_TARGET"
sync_loader_files "$ATOMIC_BRANCH_MISMATCH_TARGET"
init_git_repo "$ATOMIC_BRANCH_MISMATCH_TARGET"
write_atomic_runtime "$ATOMIC_BRANCH_MISMATCH_TARGET"
git -C "$ATOMIC_BRANCH_MISMATCH_TARGET" add .ralph/reports .ralph/state specs tasks
git -C "$ATOMIC_BRANCH_MISMATCH_TARGET" commit -q -m "chore: seed atomic runtime fixture"
normalize_current_runtime_fixture "$ATOMIC_BRANCH_MISMATCH_TARGET"
ATOMIC_BRANCH_WORKTREE="$ATOMIC_BRANCH_MISMATCH_TARGET/.ralph/worktrees/001-atomic-commit-demo"
git -C "$ATOMIC_BRANCH_MISMATCH_TARGET" add AGENTS.md CLAUDE.md .codex .claude .cursor .agents .ralph/context .ralph/harness-version.json .ralph/logs .ralph/policy .ralph/reports .ralph/state specs tasks
git -C "$ATOMIC_BRANCH_MISMATCH_TARGET" commit -q -m "chore: normalize canonical control plane"
git -C "$ATOMIC_BRANCH_WORKTREE" checkout -q -b wrong-branch
printf '\nImplemented on the wrong branch.\n' >> "$ATOMIC_BRANCH_WORKTREE/specs/001-atomic-commit-demo/spec.md"
git -C "$ATOMIC_BRANCH_WORKTREE" add .
git -C "$ATOMIC_BRANCH_WORKTREE" commit -q -m "feat: implement 001-T001 on the wrong branch"
ATOMIC_BRANCH_SHA="$(git -C "$ATOMIC_BRANCH_WORKTREE" rev-parse --short HEAD)"
write_atomic_report "$ATOMIC_BRANCH_MISMATCH_TARGET" "None." "$ATOMIC_BRANCH_SHA"
git -C "$ATOMIC_BRANCH_MISMATCH_TARGET" add .ralph/reports/atomic-20260308/implement.md
git -C "$ATOMIC_BRANCH_MISMATCH_TARGET" commit -q -m "docs: record 001-T001 commit evidence on the wrong branch"
if python3 scripts/check-installed-runtime-state.py --repo "$ATOMIC_BRANCH_MISMATCH_TARGET"; then
  echo "smoke-test-install-upgrade: branch mismatch should have failed" >&2
  exit 1
fi

echo "smoke-test-install-upgrade: ok"
