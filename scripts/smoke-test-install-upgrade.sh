#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

MANAGED_START='<!-- RALPH-HARNESS:START -->'
MANAGED_END='<!-- RALPH-HARNESS:END -->'

render_managed_block() {
  cat src/AGENTS.md
}

update_agents_file() {
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

copy_manifest_paths() {
  local manifest="$1"
  local target="$2"
  while IFS= read -r path; do
    [[ -z "$path" || "$path" == \#* ]] && continue
    if [[ "$path" == "AGENTS.md" && -f "$target/AGENTS.md" ]]; then
      continue
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
  "schema_version": "2.0.0",
  "project_name": "atomic-target",
  "active_epoch_id": "E001",
  "active_spec_id": "001",
  "active_spec_key": "001-atomic-commit-demo",
  "active_task_id": "001-T001",
  "current_phase": "review",
  "task_status": "awaiting_review",
  "assigned_role": "review",
  "current_branch": "codex/001-atomic-commit-demo",
  "current_run_id": "atomic-20260308",
  "active_pr_number": null,
  "active_pr_url": null,
  "queue_head_spec_id": "001",
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
      "branch_name": "codex/001-atomic-commit-demo",
      "pr_number": null
    }
  ]
}
EOF
  cat > "$target/.ralph/state/spec-queue.json" <<'EOF'
{
  "schema_version": "2.1.0",
  "queue_policy": {
    "selection": "fifo",
    "preemption": "failing_out_of_scope_bug"
  },
  "active_spec_id": "001",
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
      "branch_name": "codex/001-atomic-commit-demo",
      "base_branch": "main",
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
  "schema_version": "2.0.0",
  "project_name": "parallel-research-target",
  "active_epoch_id": null,
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
      "branch_name": "codex/001-batch-head",
      "pr_number": null
    },
    {
      "spec_id": "002",
      "spec_key": "002-batch-follow-on",
      "epoch_id": "E001",
      "status": "planned",
      "branch_name": "codex/002-batch-follow-on",
      "pr_number": null
    }
  ]
}
EOF
  cat > "$target/.ralph/state/spec-queue.json" <<'EOF'
{
  "schema_version": "2.1.0",
  "queue_policy": {
    "selection": "fifo",
    "preemption": "failing_out_of_scope_bug"
  },
  "active_spec_id": null,
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
      "branch_name": "codex/001-batch-head",
      "base_branch": "main",
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
      "branch_name": "codex/002-batch-follow-on",
      "base_branch": "main",
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
    "$target/.ralph/logs" \
    "$target/tasks" \
    "$target/specs/001-legacy-spec"
  seed_legacy_agent_configs "$target"
  printf 'Legacy loader.\n' > "$target/AGENTS.md"
  printf 'keep-policy\n' > "$target/.ralph/policy/project-policy.md"
  printf 'keep-context\n' > "$target/.ralph/context/project-truths.md"
  printf 'keep-reports\n' > "$target/.ralph/reports/existing.md"
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

INSTALL_TARGET="$TMP_DIR/install-target"
mkdir -p "$INSTALL_TARGET"
printf 'Project loader before install.\n' > "$INSTALL_TARGET/AGENTS.md"
copy_manifest_paths src/install-manifest.txt "$INSTALL_TARGET"
create_generated_runtime "$INSTALL_TARGET"
render_managed_block > "$TMP_DIR/managed-block.md"
update_agents_file "$INSTALL_TARGET/AGENTS.md" "$TMP_DIR/managed-block.md"
python3 scripts/check-installed-runtime-state.py --repo "$INSTALL_TARGET"

[[ -d "$INSTALL_TARGET/.codex/agents" ]] || {
  echo "smoke-test-install-upgrade: missing .codex/agents after install" >&2
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

LEGACY_TARGET="$TMP_DIR/legacy-target"
write_positive_legacy_runtime "$LEGACY_TARGET"
copy_manifest_paths src/upgrade-manifest.txt "$LEGACY_TARGET"
update_agents_file "$LEGACY_TARGET/AGENTS.md" "$TMP_DIR/managed-block.md"
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

queue = json.loads((Path(sys.argv[1]) / ".ralph/state/spec-queue.json").read_text())
spec = queue["specs"][0]
assert spec["research_status"] == "not_started"
assert spec["research_artifact_path"] == "specs/001-legacy-spec/research.md"
assert spec["planning_batch_id"] is None
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
update_agents_file "$AMBIGUOUS_TARGET/AGENTS.md" "$TMP_DIR/managed-block.md"

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
update_agents_file "$CONFLICT_TARGET/AGENTS.md" "$TMP_DIR/managed-block.md"

if python3 scripts/migrate-installed-runtime.py --repo "$CONFLICT_TARGET"; then
  echo "smoke-test-install-upgrade: conflicting legacy agent layout should have failed" >&2
  exit 1
fi

ATOMIC_PASS_TARGET="$TMP_DIR/atomic-pass-target"
mkdir -p "$ATOMIC_PASS_TARGET"
copy_manifest_paths src/install-manifest.txt "$ATOMIC_PASS_TARGET"
create_generated_runtime "$ATOMIC_PASS_TARGET"
update_agents_file "$ATOMIC_PASS_TARGET/AGENTS.md" "$TMP_DIR/managed-block.md"
init_git_repo "$ATOMIC_PASS_TARGET"
git -C "$ATOMIC_PASS_TARGET" checkout -q -b codex/001-atomic-commit-demo
write_atomic_runtime "$ATOMIC_PASS_TARGET"
git -C "$ATOMIC_PASS_TARGET" add .
git -C "$ATOMIC_PASS_TARGET" commit -q -m "feat: implement 001-T001"
ATOMIC_PASS_SHA="$(git -C "$ATOMIC_PASS_TARGET" rev-parse --short HEAD)"
write_atomic_report "$ATOMIC_PASS_TARGET" "None." "$ATOMIC_PASS_SHA"
git -C "$ATOMIC_PASS_TARGET" add .ralph/reports/atomic-20260308/implement.md
git -C "$ATOMIC_PASS_TARGET" commit -q -m "docs: record 001-T001 commit evidence"
python3 scripts/check-installed-runtime-state.py --repo "$ATOMIC_PASS_TARGET"

PARALLEL_RESEARCH_TARGET="$TMP_DIR/parallel-research-target"
mkdir -p "$PARALLEL_RESEARCH_TARGET"
copy_manifest_paths src/install-manifest.txt "$PARALLEL_RESEARCH_TARGET"
create_generated_runtime "$PARALLEL_RESEARCH_TARGET"
update_agents_file "$PARALLEL_RESEARCH_TARGET/AGENTS.md" "$TMP_DIR/managed-block.md"
write_parallel_research_runtime "$PARALLEL_RESEARCH_TARGET"
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
update_agents_file "$ATOMIC_MULTI_TARGET/AGENTS.md" "$TMP_DIR/managed-block.md"
init_git_repo "$ATOMIC_MULTI_TARGET"
git -C "$ATOMIC_MULTI_TARGET" checkout -q -b codex/001-atomic-commit-demo
write_atomic_runtime "$ATOMIC_MULTI_TARGET"
git -C "$ATOMIC_MULTI_TARGET" add .
git -C "$ATOMIC_MULTI_TARGET" commit -q -m "feat: implement core of 001-T001"
printf '\nSecond checkpoint for the same task.\n' >> "$ATOMIC_MULTI_TARGET/specs/001-atomic-commit-demo/spec.md"
git -C "$ATOMIC_MULTI_TARGET" add specs/001-atomic-commit-demo/spec.md
git -C "$ATOMIC_MULTI_TARGET" commit -q -m "test: finish 001-T001 checkpoint"
ATOMIC_MULTI_SHA="$(git -C "$ATOMIC_MULTI_TARGET" rev-parse --short HEAD)"
ATOMIC_MULTI_PREV_SHA="$(git -C "$ATOMIC_MULTI_TARGET" rev-parse --short HEAD~1)"
write_atomic_report "$ATOMIC_MULTI_TARGET" "\`$ATOMIC_MULTI_PREV_SHA..$ATOMIC_MULTI_SHA\`" "$ATOMIC_MULTI_SHA"
git -C "$ATOMIC_MULTI_TARGET" add .ralph/reports/atomic-20260308/implement.md
git -C "$ATOMIC_MULTI_TARGET" commit -q -m "docs: record 001-T001 multi-commit evidence"
python3 scripts/check-installed-runtime-state.py --repo "$ATOMIC_MULTI_TARGET"

ATOMIC_DIRTY_TARGET="$TMP_DIR/atomic-dirty-target"
cp -R "$ATOMIC_PASS_TARGET" "$ATOMIC_DIRTY_TARGET"
printf '\nUncommitted change.\n' >> "$ATOMIC_DIRTY_TARGET/specs/001-atomic-commit-demo/spec.md"
if python3 scripts/check-installed-runtime-state.py --repo "$ATOMIC_DIRTY_TARGET"; then
  echo "smoke-test-install-upgrade: dirty worktree should have failed" >&2
  exit 1
fi

ATOMIC_MISSING_REPORT_TARGET="$TMP_DIR/atomic-missing-report-target"
mkdir -p "$ATOMIC_MISSING_REPORT_TARGET"
copy_manifest_paths src/install-manifest.txt "$ATOMIC_MISSING_REPORT_TARGET"
create_generated_runtime "$ATOMIC_MISSING_REPORT_TARGET"
update_agents_file "$ATOMIC_MISSING_REPORT_TARGET/AGENTS.md" "$TMP_DIR/managed-block.md"
init_git_repo "$ATOMIC_MISSING_REPORT_TARGET"
git -C "$ATOMIC_MISSING_REPORT_TARGET" checkout -q -b codex/001-atomic-commit-demo
write_atomic_runtime "$ATOMIC_MISSING_REPORT_TARGET"
git -C "$ATOMIC_MISSING_REPORT_TARGET" add .
git -C "$ATOMIC_MISSING_REPORT_TARGET" commit -q -m "feat: implement 001-T001"
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
update_agents_file "$ATOMIC_BRANCH_MISMATCH_TARGET/AGENTS.md" "$TMP_DIR/managed-block.md"
init_git_repo "$ATOMIC_BRANCH_MISMATCH_TARGET"
write_atomic_runtime "$ATOMIC_BRANCH_MISMATCH_TARGET"
git -C "$ATOMIC_BRANCH_MISMATCH_TARGET" add .
git -C "$ATOMIC_BRANCH_MISMATCH_TARGET" commit -q -m "feat: implement 001-T001 on the wrong branch"
ATOMIC_BRANCH_SHA="$(git -C "$ATOMIC_BRANCH_MISMATCH_TARGET" rev-parse --short HEAD)"
write_atomic_report "$ATOMIC_BRANCH_MISMATCH_TARGET" "None." "$ATOMIC_BRANCH_SHA"
git -C "$ATOMIC_BRANCH_MISMATCH_TARGET" add .ralph/reports/atomic-20260308/implement.md
git -C "$ATOMIC_BRANCH_MISMATCH_TARGET" commit -q -m "docs: record 001-T001 commit evidence on the wrong branch"
if python3 scripts/check-installed-runtime-state.py --repo "$ATOMIC_BRANCH_MISMATCH_TARGET"; then
  echo "smoke-test-install-upgrade: branch mismatch should have failed" >&2
  exit 1
fi

echo "smoke-test-install-upgrade: ok"
