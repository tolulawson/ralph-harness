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

echo "smoke-test-install-upgrade: ok"
