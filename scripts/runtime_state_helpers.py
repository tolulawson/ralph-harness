from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib  # type: ignore


CURRENT_QUEUE_SCHEMA_VERSION = "6.0.0"
CURRENT_WORKFLOW_SCHEMA_VERSION = "6.0.0"
CURRENT_TASK_STATE_SCHEMA_VERSION = "1.1.0"
CURRENT_PROJECT_FACTS_SCHEMA_VERSION = "1.1.0"
CURRENT_PREEMPTION_POLICY = "failing_out_of_scope_bug"
CURRENT_QUEUE_SELECTION = "explicit_first_ready_set"
DEFAULT_MAX_THREADS = 4
ORCHESTRATOR_THREAD_RESERVE = 1
CURRENT_UPGRADE_CONTRACT_VERSION = 11
CURRENT_LEASE_SCHEMA_VERSION = "1.0.0"
CURRENT_WORKER_CLAIMS_SCHEMA_VERSION = "1.1.0"
CURRENT_SCAFFOLD_REF = "__current_scaffold__"
DEFAULT_LEASE_PATH = ".ralph/state/orchestrator-lease.json"
DEFAULT_WORKER_CLAIMS_PATH = ".ralph/state/worker-claims.json"
DEFAULT_INTENTS_PATH = ".ralph/state/orchestrator-intents.jsonl"
DEFAULT_WORKTREE_ROOT = ".ralph/worktrees"
DEFAULT_SHARED_OVERLAY_ROOT = ".ralph/shared"
DEFAULT_RUNTIME_OVERRIDES_PATH = ".ralph/policy/runtime-overrides.md"
DEFAULT_STOP_HOOK_PATH = ".ralph/hooks/stop-boundary.py"
DEFAULT_CODEX_HOOKS_PATH = ".codex/hooks.json"
DEFAULT_CLAUDE_SETTINGS_PATH = ".claude/settings.json"
DEFAULT_CURSOR_HOOKS_PATH = ".cursor/hooks.json"
LEASE_LOCK_SUFFIX = ".lock"
LEASE_TTL_SECONDS = 90
SCAFFOLD_ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_RUNTIME_CONTRACT_PATH = SCAFFOLD_ROOT / "src/.ralph/runtime-contract.md"
SCAFFOLD_RUNTIME_OVERRIDES_PATH = SCAFFOLD_ROOT / "src/.ralph/policy/runtime-overrides.md"
MANAGED_AGENT_NAMES = (
    "orchestrator",
    "prd",
    "specify",
    "research",
    "plan",
    "task_gen",
    "plan_check",
    "bootstrap",
    "implement",
    "review",
    "verify",
    "release",
)
MANAGED_AGENT_FILES = (
    "implement.toml",
    "orchestrator.toml",
    "plan.toml",
    "plan-check.toml",
    "prd.toml",
    "research.toml",
    "bootstrap.toml",
    "release.toml",
    "review.toml",
    "specify.toml",
    "task-gen.toml",
    "verify.toml",
)
MANAGED_AGENT_SANDBOX_MODES = {
    "orchestrator": "danger-full-access",
    "prd": "danger-full-access",
    "specify": "danger-full-access",
    "research": "danger-full-access",
    "plan": "danger-full-access",
    "task_gen": "danger-full-access",
    "plan_check": "danger-full-access",
    "bootstrap": "danger-full-access",
    "implement": "danger-full-access",
    "review": "danger-full-access",
    "verify": "danger-full-access",
    "release": "danger-full-access",
}
MAX_AGENT_DEPTH = 3
RUNTIME_CONTRACT_REQUIRED_SNIPPETS = (
    "supported runtime adapter packs together",
    "native runtime subagents",
    "unsupported by the shipped harness",
    ".ralph/state/worker-claims.json",
    ".ralph/shared/",
    "canonical shared control plane",
    "worktree-local tracked copies",
    "Child roles must not spawn nested workers",
    "Review, verification, and release failures are remediation signals, not stop conditions.",
    "Release reports must record one explicit outcome",
    "single-writer lease",
    "orchestrator-intents.jsonl",
    "git worktree",
    "bootstrap",
)
ORCHESTRATOR_SKILL_REQUIRED_SNIPPETS = (
    "worker-claims",
    "native subagents",
    "execution_mode = native_subagent",
    "release their claims and exit",
    "orchestrator alone",
    ".ralph/shared/",
    "canonical checkout",
    "shared-control-plane",
    "close that worker thread",
    "Do not stop merely because review, verification, or release failed.",
    "durable intent",
    "worktree",
    "bootstrap",
)
DEFAULT_ORCHESTRATOR_STOP_HOOK = {
    "enabled": True,
    "mode": "conservative",
    "max_auto_continue_count": 1,
}
DEFAULT_BOOTSTRAP_COPY_EXCLUDE_GLOBS = [
    "node_modules",
    "node_modules/**",
    ".venv",
    ".venv/**",
    "venv",
    "venv/**",
    ".next",
    ".next/**",
    "dist",
    "dist/**",
    "build",
    "build/**",
    ".turbo",
    ".turbo/**",
    ".cache",
    ".cache/**",
]
CANONICAL_SHARED_CONTROL_PLANE_PATHS = (
    ".ralph/constitution.md",
    ".ralph/runtime-contract.md",
    ".ralph/context",
    ".ralph/policy",
    ".ralph/state",
    ".ralph/logs",
    ".ralph/reports",
    "specs/INDEX.md",
)
SHARED_OVERLAY_LINK_TARGETS = {
    "constitution.md": ".ralph/constitution.md",
    "runtime-contract.md": ".ralph/runtime-contract.md",
    "context": ".ralph/context",
    "policy": ".ralph/policy",
    "state": ".ralph/state",
    "logs": ".ralph/logs",
    "reports": ".ralph/reports",
    "specs/INDEX.md": "specs/INDEX.md",
}
CODEX_STOP_HOOK_COMMAND = f"python3 ./{DEFAULT_STOP_HOOK_PATH} --runtime codex"
CLAUDE_STOP_HOOK_COMMAND = f'python3 "$CLAUDE_PROJECT_DIR"/{DEFAULT_STOP_HOOK_PATH} --runtime claude'
CURSOR_STOP_HOOK_COMMAND = f"python3 ./{DEFAULT_STOP_HOOK_PATH} --runtime cursor"
RUNTIME_HOOK_MANAGED_COMMANDS = {
    CODEX_STOP_HOOK_COMMAND,
    CLAUDE_STOP_HOOK_COMMAND,
    CURSOR_STOP_HOOK_COMMAND,
}

WORKFLOW_REQUIRED_KEYS = (
    "schema_version",
    "project_name",
    "active_epoch_id",
    "active_spec_ids",
    "active_interrupt_spec_id",
    "active_spec_id",
    "active_spec_key",
    "active_task_id",
    "current_phase",
    "task_status",
    "assigned_role",
    "current_branch",
    "current_run_id",
    "active_pr_number",
    "active_pr_url",
    "orchestrator_lease_path",
    "worker_claims_path",
    "orchestrator_intents_path",
    "lease_owner_token",
    "lease_heartbeat_at",
    "lease_expires_at",
    "scheduler_summary",
    "resume_spec_id",
    "resume_spec_stack",
    "interruption_state",
    "last_event_id",
    "last_report_path",
    "last_verified_at",
    "blocked_reason",
    "failure_count",
    "next_action",
    "queue_snapshot",
)

QUEUE_SPEC_REQUIRED_KEYS = (
    "spec_id",
    "spec_slug",
    "spec_key",
    "title",
    "epoch_id",
    "created_at",
    "last_worked_at",
    "status",
    "kind",
    "origin_spec_key",
    "origin_task_id",
    "triggered_by_role",
    "trigger_report_path",
    "trigger_summary",
    "priority_override",
    "blocked_reason",
    "depends_on_spec_ids",
    "admission_status",
    "admitted_at",
    "research_status",
    "research_artifact_path",
    "research_report_path",
    "research_updated_at",
    "planning_batch_id",
    "prd_path",
    "spec_path",
    "plan_path",
    "tasks_path",
    "task_state_path",
    "latest_report_path",
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
    "pr_number",
    "pr_url",
    "pr_state",
    "merge_commit",
    "task_summary",
    "next_task_id",
)

LEASE_REQUIRED_KEYS = (
    "schema_version",
    "owner_token",
    "holder_thread",
    "run_id",
    "acquired_at",
    "heartbeat_at",
    "expires_at",
    "status",
)

WORKER_CLAIMS_REQUIRED_KEYS = (
    "schema_version",
    "claims",
)

TASK_LINE_RE = re.compile(r"^\s*-\s\[(?P<checked>[ xX])\]\s(?P<task_id>\d{3,}-T\d{3,})\b")

UNCHECKED_TASK_STATUSES = {"queued", "ready", "in_progress", "paused", "blocked"}
CHECKED_TASK_STATUSES = {
    "awaiting_review",
    "review_failed",
    "awaiting_verification",
    "verification_failed",
    "awaiting_release",
    "release_failed",
    "released",
    "done",
}
ACTIVE_SPEC_STATUSES = {
    "draft",
    "planned",
    "ready",
    "plan_check_failed",
    "in_progress",
    "awaiting_pr",
    "awaiting_review",
    "review_failed",
    "awaiting_verification",
    "verification_failed",
    "awaiting_merge",
    "release_failed",
    "blocked",
    "paused",
}
TASK_STATE_OPTIONAL_SPEC_STATUSES = {"draft", "planned"}
ADMISSION_ACTIVE_STATUSES = {"admitted", "running", "paused"}
WORKTREE_REQUIRED_SLOT_STATUSES = {"admitted", "running", "paused"}
HANDOFF_PHASES = {"review", "verification", "release"}
HANDOFF_TASK_STATUSES = {
    "awaiting_review",
    "review_failed",
    "awaiting_verification",
    "verification_failed",
    "awaiting_release",
    "release_failed",
    "released",
}
REPORT_COMMIT_ROLES = {"implement", "review", "verify", "release"}
SPEC_SCOPED_REPORT_ROLES = {
    "prd",
    "specify",
    "research",
    "plan",
    "task-gen",
    "plan-check",
    "bootstrap",
    "implement",
    "review",
    "verify",
    "release",
}
COMMIT_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
INTENT_TYPES = {"create_spec", "schedule_spec", "pause_spec", "resume_spec", "status_request"}
INTENT_STATUSES = {"pending", "acknowledged", "processed", "rejected"}
LEASE_STATUSES = {"idle", "held"}
CLAIM_STATUSES = {"claimed", "released", "expired"}
BOOTSTRAP_STATUSES = {"required", "in_progress", "passed", "failed"}
SUPPORTED_RUNTIME_NAMES = {"codex", "claude", "cursor"}
SUPPORTED_EXECUTION_MODES = {"native_subagent"}
TASK_STATUS_ROLE_ROUTING = {
    "ready": "implement",
    "in_progress": "implement",
    "awaiting_review": "review",
    "review_failed": "review",
    "awaiting_verification": "verify",
    "verification_failed": "verify",
    "awaiting_release": "release",
    "release_failed": "release",
}
RELEASE_OUTCOMES = {
    "pr_created",
    "awaiting_review",
    "awaiting_merge",
    "merge_completed",
    "release_failed",
    "human_gate_waiting",
}


class RuntimeStateError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_jsonl_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        records.append(json.loads(stripped))
    return records


def load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def write_jsonl_records(path: Path, records: list[dict[str, Any]]) -> None:
    rendered = "".join(json.dumps(record, sort_keys=True) + "\n" for record in records)
    path.write_text(rendered)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def default_worktree_name(spec_key: str) -> str:
    return f"ralph-{spec_key}"


def default_worktree_path(spec_key: str) -> str:
    return f"{DEFAULT_WORKTREE_ROOT}/{spec_key}"


def default_worktree_path_for_suffix(spec_key: str, suffix: str) -> str:
    return default_worktree_path(f"{spec_key}{suffix}")


def default_branch_name(spec_key: str) -> str:
    return f"ralph/{spec_key}"


def derive_default_normal_execution_limit(repo_root: Path | None = None) -> int:
    config_path = (repo_root / ".codex/config.toml") if repo_root is not None else (SCAFFOLD_ROOT / "src/.codex/config.toml")
    max_threads = DEFAULT_MAX_THREADS
    if config_path.exists():
        config = load_toml(config_path)
        max_threads = int((config.get("agents") or {}).get("max_threads") or DEFAULT_MAX_THREADS)
    return max(1, max_threads - ORCHESTRATOR_THREAD_RESERVE)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def toml_literal(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, list):
        return "[" + ", ".join(toml_literal(item) for item in value) + "]"
    raise RuntimeStateError(f"unsupported TOML value type: {type(value).__name__}")


def render_toml_table(table: dict[str, Any], prefix: tuple[str, ...] = ()) -> list[str]:
    scalar_lines: list[str] = []
    nested_tables: list[tuple[str, dict[str, Any]]] = []

    for key, value in table.items():
        if isinstance(value, dict):
            nested_tables.append((key, value))
        else:
            scalar_lines.append(f"{key} = {toml_literal(value)}")

    lines: list[str] = []
    if prefix:
        lines.append(f"[{'.'.join(prefix)}]")
    lines.extend(scalar_lines)

    for key, value in nested_tables:
        if lines:
            lines.append("")
        lines.extend(render_toml_table(value, prefix + (key,)))

    return lines


def write_toml(path: Path, payload: dict[str, Any]) -> None:
    path.write_text("\n".join(render_toml_table(payload)).rstrip() + "\n")


def default_project_facts() -> dict[str, Any]:
    return {
        "schema_version": CURRENT_PROJECT_FACTS_SCHEMA_VERSION,
        "repo_kind": None,
        "runtime_kind": None,
        "base_branch": None,
        "orchestrator_stop_hook": dict(DEFAULT_ORCHESTRATOR_STOP_HOOK),
        "worktree_bootstrap_commands": [],
        "bootstrap_env_files": [],
        "bootstrap_copy_exclude_globs": list(DEFAULT_BOOTSTRAP_COPY_EXCLUDE_GLOBS),
        "validation_bootstrap_commands": [],
        "verification_commands": [],
        "deployment_model": None,
        "tooling_facts": {},
        "unknowns": [],
        "fact_sources": [],
    }


def normalize_project_facts(project_facts: dict[str, Any]) -> dict[str, Any]:
    normalized = default_project_facts()
    normalized.update(project_facts)
    stop_hook = normalized.get("orchestrator_stop_hook")
    merged_stop_hook = dict(DEFAULT_ORCHESTRATOR_STOP_HOOK)
    if isinstance(stop_hook, dict):
        merged_stop_hook.update(stop_hook)
    merged_stop_hook["enabled"] = bool(merged_stop_hook.get("enabled", True))
    mode = merged_stop_hook.get("mode")
    merged_stop_hook["mode"] = mode if isinstance(mode, str) and mode else DEFAULT_ORCHESTRATOR_STOP_HOOK["mode"]
    max_auto_continue_count = merged_stop_hook.get("max_auto_continue_count")
    if not isinstance(max_auto_continue_count, int) or max_auto_continue_count < 0:
        max_auto_continue_count = DEFAULT_ORCHESTRATOR_STOP_HOOK["max_auto_continue_count"]
    merged_stop_hook["max_auto_continue_count"] = max_auto_continue_count
    normalized["orchestrator_stop_hook"] = merged_stop_hook
    normalized["worktree_bootstrap_commands"] = list(normalized.get("worktree_bootstrap_commands") or [])
    normalized["bootstrap_env_files"] = list(normalized.get("bootstrap_env_files") or [])
    exclude_globs = list(normalized.get("bootstrap_copy_exclude_globs") or [])
    normalized["bootstrap_copy_exclude_globs"] = exclude_globs or list(DEFAULT_BOOTSTRAP_COPY_EXCLUDE_GLOBS)
    normalized["validation_bootstrap_commands"] = list(normalized.get("validation_bootstrap_commands") or [])
    normalized["verification_commands"] = list(normalized.get("verification_commands") or [])
    normalized["tooling_facts"] = dict(normalized.get("tooling_facts") or {})
    normalized["unknowns"] = list(normalized.get("unknowns") or [])
    normalized["fact_sources"] = list(normalized.get("fact_sources") or [])
    normalized["schema_version"] = CURRENT_PROJECT_FACTS_SCHEMA_VERSION
    base_branch = normalized.get("base_branch")
    normalized["base_branch"] = base_branch if isinstance(base_branch, str) and base_branch else None
    return normalized


def merge_codex_config(installed: dict[str, Any], scaffold: dict[str, Any]) -> dict[str, Any]:
    merged = dict(installed)

    for key, value in scaffold.items():
        if key in {"features", "agents"}:
            continue
        merged.setdefault(key, value)

    merged_features = dict(installed.get("features") or {})
    scaffold_features = dict(scaffold.get("features") or {})
    for key, value in scaffold_features.items():
        if key in {"multi_agent", "codex_hooks"}:
            merged_features[key] = True
        else:
            merged_features.setdefault(key, value)
    merged["features"] = merged_features

    merged_agents = dict(installed.get("agents") or {})
    scaffold_agents = dict(scaffold.get("agents") or {})
    for key, value in scaffold_agents.items():
        if isinstance(value, dict):
            existing = dict(merged_agents.get(key) or {})
            if key in MANAGED_AGENT_NAMES and "config_file" in value:
                existing["config_file"] = value["config_file"]
            for nested_key, nested_value in value.items():
                existing.setdefault(nested_key, nested_value)
            merged_agents[key] = existing
        else:
            if key == "max_depth" and isinstance(value, int):
                merged_agents[key] = value
            else:
                merged_agents.setdefault(key, value)
    merged["agents"] = merged_agents

    return merged


def merge_installed_codex_config(repo_root: Path) -> None:
    scaffold_config_path = SCAFFOLD_ROOT / "src/.codex/config.toml"
    target_config_path = repo_root / ".codex/config.toml"
    scaffold_config = load_toml(scaffold_config_path)
    installed_config = load_toml(target_config_path) if target_config_path.exists() else {}
    merged_config = merge_codex_config(installed_config, scaffold_config)
    target_config_path.parent.mkdir(parents=True, exist_ok=True)
    write_toml(target_config_path, merged_config)


def merge_nested_command_hooks(
    installed_groups: list[Any],
    scaffold_groups: list[Any],
    managed_commands: set[str],
) -> list[Any]:
    merged_groups: list[Any] = []
    for group in installed_groups:
        if not isinstance(group, dict):
            merged_groups.append(group)
            continue
        hooks = group.get("hooks")
        if not isinstance(hooks, list):
            merged_groups.append(group)
            continue
        filtered_hooks = [
            hook
            for hook in hooks
            if not (isinstance(hook, dict) and isinstance(hook.get("command"), str) and hook.get("command") in managed_commands)
        ]
        if filtered_hooks:
            updated_group = dict(group)
            updated_group["hooks"] = filtered_hooks
            merged_groups.append(updated_group)
    merged_groups.extend(scaffold_groups)
    return merged_groups


def merge_top_level_command_hooks(
    installed_entries: list[Any],
    scaffold_entries: list[Any],
    managed_commands: set[str],
) -> list[Any]:
    filtered_entries = [
        entry
        for entry in installed_entries
        if not (isinstance(entry, dict) and isinstance(entry.get("command"), str) and entry.get("command") in managed_commands)
    ]
    filtered_entries.extend(scaffold_entries)
    return filtered_entries


def merge_installed_codex_hooks(repo_root: Path) -> None:
    scaffold_hooks_path = SCAFFOLD_ROOT / f"src/{DEFAULT_CODEX_HOOKS_PATH}"
    target_hooks_path = repo_root / DEFAULT_CODEX_HOOKS_PATH
    scaffold_hooks = load_json(scaffold_hooks_path)
    installed_hooks = load_json(target_hooks_path) if target_hooks_path.exists() else {}
    merged = dict(installed_hooks)
    merged_hooks = dict(merged.get("hooks") or {})
    for event_name, scaffold_groups in (scaffold_hooks.get("hooks") or {}).items():
        merged_hooks[event_name] = merge_nested_command_hooks(
            list(merged_hooks.get(event_name) or []),
            list(scaffold_groups or []),
            {CODEX_STOP_HOOK_COMMAND},
        )
    merged["hooks"] = merged_hooks
    target_hooks_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(target_hooks_path, merged)


def merge_installed_claude_settings(repo_root: Path) -> None:
    scaffold_settings_path = SCAFFOLD_ROOT / f"src/{DEFAULT_CLAUDE_SETTINGS_PATH}"
    target_settings_path = repo_root / DEFAULT_CLAUDE_SETTINGS_PATH
    scaffold_settings = load_json(scaffold_settings_path)
    installed_settings = load_json(target_settings_path) if target_settings_path.exists() else {}
    merged = dict(installed_settings)
    merged_hooks = dict(merged.get("hooks") or {})
    for event_name, scaffold_groups in (scaffold_settings.get("hooks") or {}).items():
        merged_hooks[event_name] = merge_nested_command_hooks(
            list(merged_hooks.get(event_name) or []),
            list(scaffold_groups or []),
            {CLAUDE_STOP_HOOK_COMMAND},
        )
    merged["hooks"] = merged_hooks
    target_settings_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(target_settings_path, merged)


def merge_installed_cursor_hooks(repo_root: Path) -> None:
    scaffold_hooks_path = SCAFFOLD_ROOT / f"src/{DEFAULT_CURSOR_HOOKS_PATH}"
    target_hooks_path = repo_root / DEFAULT_CURSOR_HOOKS_PATH
    scaffold_hooks = load_json(scaffold_hooks_path)
    installed_hooks = load_json(target_hooks_path) if target_hooks_path.exists() else {}
    merged = dict(installed_hooks)
    merged["version"] = scaffold_hooks.get("version", 1)
    merged_hooks = dict(merged.get("hooks") or {})
    for event_name, scaffold_entries in (scaffold_hooks.get("hooks") or {}).items():
        merged_hooks[event_name] = merge_top_level_command_hooks(
            list(merged_hooks.get(event_name) or []),
            list(scaffold_entries or []),
            {CURSOR_STOP_HOOK_COMMAND},
        )
    merged["hooks"] = merged_hooks
    target_hooks_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(target_hooks_path, merged)


def format_code(value: Any) -> str:
    if value is None:
        return "null"
    return str(value)


def derive_interrupt_spec_id(workflow: dict[str, Any], queue: dict[str, Any]) -> Any:
    if queue.get("active_interrupt_spec_id") is not None:
        return queue.get("active_interrupt_spec_id")
    if workflow.get("active_interrupt_spec_id") is not None:
        return workflow.get("active_interrupt_spec_id")
    interruption_state = workflow.get("interruption_state")
    if isinstance(interruption_state, dict):
        for key in ("interrupt_spec_id", "active_interrupt_spec_id", "spec_id"):
            if interruption_state.get(key) is not None:
                return interruption_state.get(key)
    for spec in queue.get("specs", []):
        if spec.get("kind") == "interrupt" and spec.get("status") in ACTIVE_SPEC_STATUSES:
            return spec.get("spec_id")
    return None


def derive_queue_snapshot(queue: dict[str, Any]) -> list[dict[str, Any]]:
    snapshot: list[dict[str, Any]] = []
    for spec in queue.get("specs", []):
        snapshot.append(
            {
                "spec_id": spec.get("spec_id"),
                "spec_key": spec.get("spec_key"),
                "epoch_id": spec.get("epoch_id"),
                "status": spec.get("status"),
                "admission_status": spec.get("admission_status"),
                "slot_status": spec.get("slot_status"),
                "bootstrap_status": spec.get("bootstrap_status"),
                "branch_name": spec.get("branch_name"),
                "pr_number": spec.get("pr_number"),
            }
        )
    return snapshot


def derive_active_spec_ids(queue: dict[str, Any], workflow: dict[str, Any] | None = None) -> list[Any]:
    active_spec_ids = list(queue.get("active_spec_ids") or [])
    if active_spec_ids:
        return active_spec_ids

    fallback_active = queue.get("active_spec_id")
    if fallback_active is None and workflow is not None:
        fallback_active = workflow.get("active_spec_id")
    if fallback_active is not None:
        return [fallback_active]

    derived: list[Any] = []
    for spec in queue.get("specs", []):
        if spec.get("kind") == "interrupt":
            continue
        if spec.get("slot_status") in WORKTREE_REQUIRED_SLOT_STATUSES or spec.get("admission_status") in ADMISSION_ACTIVE_STATUSES:
            derived.append(spec.get("spec_id"))
    return derived


def count_dependency_blocked_specs(queue: dict[str, Any]) -> int:
    count = 0
    statuses = {spec.get("spec_id"): spec.get("status") for spec in queue.get("specs", [])}
    for spec in queue.get("specs", []):
        deps = list(spec.get("depends_on_spec_ids") or [])
        if any(statuses.get(dep) not in {"released", "done"} for dep in deps):
            count += 1
    return count


def render_workflow_state_markdown(workflow: dict[str, Any], queue: dict[str, Any]) -> str:
    resume_stack = workflow.get("resume_spec_stack") or []
    interrupt_spec_id = derive_interrupt_spec_id(workflow, queue)
    resume_pending = "yes" if resume_stack else "no"
    active_spec_ids = workflow.get("active_spec_ids") or derive_active_spec_ids(queue, workflow)
    scheduler_summary = workflow.get("scheduler_summary") or {}
    lines = [
        "# Workflow State",
        "",
        f"- Project: `{format_code(workflow.get('project_name'))}`",
        f"- Active epoch: `{format_code(workflow.get('active_epoch_id'))}`",
        f"- Active specs: `{format_code(active_spec_ids)}`",
        f"- Primary active spec (compatibility mirror): `{format_code(workflow.get('active_spec_key'))}`",
        f"- Active task: `{format_code(workflow.get('active_task_id'))}`",
        f"- Phase: `{format_code(workflow.get('current_phase'))}`",
        f"- Task status: `{format_code(workflow.get('task_status'))}`",
        f"- Assigned role: `{format_code(workflow.get('assigned_role'))}`",
        f"- Primary active branch (compatibility mirror): `{format_code(workflow.get('current_branch'))}`",
        f"- Run id: `{format_code(workflow.get('current_run_id'))}`",
        f"- Active PR number: `{format_code(workflow.get('active_pr_number'))}`",
        f"- Active PR URL: `{format_code(workflow.get('active_pr_url'))}`",
        f"- Admission policy: `{format_code(queue.get('queue_policy', {}).get('selection'))}`",
        f"- Normal spec capacity: `{format_code(queue.get('queue_policy', {}).get('normal_execution_limit'))}`",
        f"- Active interrupt spec: `{format_code(workflow.get('active_interrupt_spec_id'))}`",
        f"- Lease path: `{format_code(workflow.get('orchestrator_lease_path'))}`",
        f"- Worker claims path: `{format_code(workflow.get('worker_claims_path'))}`",
        f"- Intents path: `{format_code(workflow.get('orchestrator_intents_path'))}`",
        f"- Lease owner token: `{format_code(workflow.get('lease_owner_token'))}`",
        f"- Lease heartbeat: `{format_code(workflow.get('lease_heartbeat_at'))}`",
        f"- Lease expires: `{format_code(workflow.get('lease_expires_at'))}`",
        f"- Scheduler summary: `{format_code(scheduler_summary)}`",
        f"- Resume spec id: `{format_code(workflow.get('resume_spec_id'))}`",
        f"- Resume stack depth: `{len(resume_stack)}`",
        f"- Current interrupt spec: `{format_code(interrupt_spec_id)}`",
        f"- Resume pending: `{resume_pending}`",
        f"- Last event id: `{format_code(workflow.get('last_event_id'))}`",
        f"- Last report: `{format_code(workflow.get('last_report_path'))}`",
        f"- Next action: {workflow.get('next_action')}",
    ]
    return "\n".join(lines) + "\n"


def render_spec_index_markdown(queue: dict[str, Any]) -> str:
    lines = [
        "# Spec Register",
        "",
        "| Spec | Kind | Depends On | Epoch | Title | Status | Bootstrap | Admission | Slot | Worktree | Branch | PR | Latest Report |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for spec in queue.get("specs", []):
        branch_name = spec.get("branch_name") or default_branch_name(spec.get("spec_key"))
        depends_on = ",".join(spec.get("depends_on_spec_ids") or []) or "null"
        lines.append(
            "| {spec_key} | {kind} | {depends_on} | {epoch} | {title} | {status} | {bootstrap} | {admission} | {slot} | `{worktree}` | `{branch}` | `{pr}` | `{report}` |".format(
                spec_key=spec.get("spec_key"),
                kind=spec.get("kind"),
                depends_on=depends_on,
                epoch=spec.get("epoch_id"),
                title=spec.get("title"),
                status=spec.get("status"),
                bootstrap=format_code(spec.get("bootstrap_status")),
                admission=format_code(spec.get("admission_status")),
                slot=format_code(spec.get("slot_status")),
                worktree=format_code(spec.get("worktree_path")),
                branch=branch_name,
                pr=format_code(spec.get("pr_number")),
                report=format_code(spec.get("latest_report_path")),
            )
        )
    return "\n".join(lines) + "\n"


def parse_tasks_markdown(tasks_path: Path) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for raw_line in tasks_path.read_text().splitlines():
        match = TASK_LINE_RE.match(raw_line)
        if match:
            tasks.append(
                {
                    "task_id": match.group("task_id"),
                    "checked": match.group("checked").lower() == "x",
                }
            )
    return tasks


def task_checkbox_matches_status(status: str) -> bool | None:
    if status in CHECKED_TASK_STATUSES:
        return True
    if status in UNCHECKED_TASK_STATUSES:
        return False
    return None


def task_status_expected_role(status: Any, previous_status: Any = None) -> str | None:
    if not isinstance(status, str):
        return None
    if status == "paused" and isinstance(previous_status, str):
        status = previous_status
    return TASK_STATUS_ROLE_ROUTING.get(status)


def report_role_from_path(report_path: Any) -> Any:
    if not report_path:
        return None
    return Path(str(report_path)).stem


def run_git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def resolve_canonical_checkout_root(repo_root: Path) -> Path:
    candidate = repo_root.resolve()
    if not is_git_worktree(candidate):
        return candidate
    try:
        common_dir = run_git(candidate, "rev-parse", "--git-common-dir")
    except subprocess.CalledProcessError:
        return candidate
    common_dir_path = Path(common_dir)
    if not common_dir_path.is_absolute():
        common_dir_path = (candidate / common_dir_path).resolve()
    else:
        common_dir_path = common_dir_path.resolve()
    return common_dir_path.parent if common_dir_path.name == ".git" else common_dir_path.parent


def resolve_canonical_shared_path(repo_root: Path, relative_path: str) -> Path:
    return resolve_canonical_checkout_root(repo_root) / relative_path


def shared_overlay_root(worktree_path: Path) -> Path:
    return worktree_path / DEFAULT_SHARED_OVERLAY_ROOT


def recreate_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.exists():
        shutil.rmtree(path)


def ensure_relative_symlink(link_path: Path, target_path: Path) -> None:
    link_path.parent.mkdir(parents=True, exist_ok=True)
    link_parent = link_path.parent.resolve()
    target_path = target_path.resolve()
    desired_target = os.path.relpath(target_path, start=link_parent)
    if link_path.is_symlink():
        if os.readlink(link_path) == desired_target:
            return
        link_path.unlink()
    elif link_path.exists():
        recreate_path(link_path)
    os.symlink(desired_target, link_path)


def ensure_worktree_shared_overlay(canonical_root: Path, worktree_path: Path) -> Path:
    canonical_root = canonical_root.resolve()
    worktree_path = worktree_path.resolve()
    overlay_root = shared_overlay_root(worktree_path)
    overlay_root.mkdir(parents=True, exist_ok=True)
    for relative_link, relative_target in SHARED_OVERLAY_LINK_TARGETS.items():
        ensure_relative_symlink(overlay_root / relative_link, canonical_root / relative_target)
    return overlay_root


def validate_worktree_shared_overlay(
    canonical_root: Path,
    worktree_path: Path,
    spec_key: str | None = None,
) -> list[str]:
    issues: list[str] = []
    label = spec_key or "unknown-spec"
    resolved_root = resolve_canonical_checkout_root(worktree_path)
    if resolved_root != canonical_root:
        issues.append(
            f"{label}: worktree resolves canonical checkout {resolved_root} but expected {canonical_root}"
        )
    overlay_root = shared_overlay_root(worktree_path)
    if not overlay_root.exists():
        issues.append(f"{label}: missing generated shared overlay at {overlay_root.relative_to(worktree_path)}")
        return issues
    for relative_link, relative_target in SHARED_OVERLAY_LINK_TARGETS.items():
        overlay_path = overlay_root / relative_link
        target_path = canonical_root / relative_target
        if not overlay_path.is_symlink():
            issues.append(
                f"{label}: shared overlay entry `{overlay_path.relative_to(worktree_path)}` must be a symlink to `{relative_target}`"
            )
            continue
        try:
            resolved_target = overlay_path.resolve(strict=True)
        except FileNotFoundError:
            issues.append(
                f"{label}: shared overlay entry `{overlay_path.relative_to(worktree_path)}` points at a missing target"
            )
            continue
        if resolved_target != target_path.resolve():
            issues.append(
                f"{label}: shared overlay entry `{overlay_path.relative_to(worktree_path)}` must resolve to `{relative_target}` in the canonical checkout"
            )
    return issues


def shared_control_plane_status_entries(worktree_path: Path) -> list[str]:
    try:
        output = run_git(
            worktree_path,
            "status",
            "--porcelain",
            "--untracked-files=all",
            "--",
            *CANONICAL_SHARED_CONTROL_PLANE_PATHS,
        )
    except subprocess.CalledProcessError:
        return []
    return [line for line in output.splitlines() if line.strip()]


def discover_remote_head_branch(repo_root: Path) -> tuple[str | None, str | None]:
    try:
        remote_head = run_git(repo_root, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    except subprocess.CalledProcessError:
        remote_head = None
    if isinstance(remote_head, str) and remote_head.startswith("origin/"):
        return remote_head.split("/", 1)[1], "git:refs/remotes/origin/HEAD"

    try:
        remote_show = run_git(repo_root, "remote", "show", "origin")
    except subprocess.CalledProcessError:
        remote_show = ""
    for line in remote_show.splitlines():
        stripped = line.strip()
        if stripped.startswith("HEAD branch: "):
            branch = stripped.split(": ", 1)[1].strip()
            if branch and branch != "(unknown)":
                return branch, "git:remote-show-origin"
    return None, None


def discover_local_base_branch(repo_root: Path, queue: dict[str, Any], workflow: dict[str, Any]) -> tuple[str | None, str | None]:
    current_branch = current_git_branch(repo_root)
    if not isinstance(current_branch, str) or not current_branch or current_branch == "HEAD":
        return None, None

    known_spec_branches = {spec.get("branch_name") for spec in queue.get("specs", []) if isinstance(spec.get("branch_name"), str)}
    if current_branch in known_spec_branches:
        return None, None

    branch_prefix = infer_branch_prefix(queue, workflow)
    if current_branch.startswith(f"{branch_prefix}/"):
        return None, None

    if current_branch in {"main", "master", "trunk", "develop", "dev"}:
        return current_branch, "git:local-head"

    try:
        local_branches = [line.strip() for line in run_git(repo_root, "branch", "--format=%(refname:short)").splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        local_branches = []
    if len(local_branches) == 1 and local_branches[0] == current_branch:
        return current_branch, "git:single-local-branch"
    return None, None


def discover_canonical_base_branch(repo_root: Path, queue: dict[str, Any], workflow: dict[str, Any]) -> tuple[str | None, str | None]:
    branch, source = discover_remote_head_branch(repo_root)
    if branch:
        return branch, source
    return discover_local_base_branch(repo_root, queue, workflow)


def ensure_project_facts_file(repo_root: Path, queue: dict[str, Any], workflow: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    repo_root = resolve_canonical_checkout_root(repo_root)
    path = repo_root / ".ralph/context/project-facts.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        project_facts = normalize_project_facts(load_json(path))
    else:
        project_facts = default_project_facts()

    if project_facts.get("base_branch") is None and is_git_worktree(repo_root):
        branch, source = discover_canonical_base_branch(repo_root, queue, workflow)
        if branch:
            project_facts["base_branch"] = branch
            if source and source not in project_facts["fact_sources"]:
                project_facts["fact_sources"].append(source)

    write_json(path, project_facts)
    return path, project_facts


def ensure_runtime_overrides_file(repo_root: Path) -> Path:
    repo_root = resolve_canonical_checkout_root(repo_root)
    target_path = repo_root / DEFAULT_RUNTIME_OVERRIDES_PATH
    if target_path.exists():
        return target_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(SCAFFOLD_RUNTIME_OVERRIDES_PATH.read_text())
    return target_path


def ensure_worker_claims_file(repo_root: Path, workflow: dict[str, Any]) -> Path:
    repo_root = resolve_canonical_checkout_root(repo_root)
    relative_path = workflow.get("worker_claims_path") or DEFAULT_WORKER_CLAIMS_PATH
    target_path = repo_root / relative_path
    if target_path.exists():
        payload = load_json(target_path)
        payload["schema_version"] = CURRENT_WORKER_CLAIMS_SCHEMA_VERSION
        claims = list(payload.get("claims") or [])
        for claim in claims:
            claim.setdefault("bootstrap_status", "required")
            claim.setdefault("bootstrap_started_at", None)
            claim.setdefault("bootstrap_completed_at", None)
            claim.setdefault("bootstrap_report_path", None)
            claim.setdefault("validation_ready", False)
        payload["claims"] = claims
        write_json(target_path, payload)
        return target_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(target_path, {"schema_version": CURRENT_WORKER_CLAIMS_SCHEMA_VERSION, "claims": []})
    return target_path


def worker_claim_is_healthy(claim: dict[str, Any], now: datetime | None = None) -> bool:
    now = now or utc_now()
    if claim.get("status") != "claimed":
        return False
    heartbeat_at = parse_timestamp(claim.get("heartbeat_at"))
    expires_at = parse_timestamp(claim.get("expires_at"))
    if heartbeat_at is None or expires_at is None:
        return False
    if expires_at <= heartbeat_at:
        return False
    return expires_at > now


def count_active_claims(worker_claims: dict[str, Any], now: datetime | None = None) -> int:
    now = now or utc_now()
    return sum(1 for claim in worker_claims.get("claims", []) if worker_claim_is_healthy(claim, now))


def canonical_runtime_contract_hash_for_ref(ref: str) -> str | None:
    if not ref:
        return None
    try:
        content = run_git(SCAFFOLD_ROOT, "show", f"{ref}:src/.ralph/runtime-contract.md")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return sha256_text(content)


def expected_runtime_contract_baseline_hash(repo_root: Path) -> str | None:
    harness_version_path = repo_root / ".ralph/harness-version.json"
    if not harness_version_path.exists():
        return None
    harness_version = load_json(harness_version_path)
    baseline_hash = harness_version.get("runtime_contract_baseline_sha256")
    if isinstance(baseline_hash, str) and baseline_hash:
        return baseline_hash
    for candidate_ref in (harness_version.get("resolved_commit"), harness_version.get("tag")):
        if isinstance(candidate_ref, str):
            resolved = canonical_runtime_contract_hash_for_ref(candidate_ref)
            if resolved:
                return resolved
    return None


def current_scaffold_tag() -> str | None:
    harness_version_path = SCAFFOLD_ROOT / "src/.ralph/harness-version.json"
    if not harness_version_path.exists():
        return None
    payload = load_json(harness_version_path)
    tag = payload.get("tag")
    return tag if isinstance(tag, str) and tag else None


def current_scaffold_runtime_contract_hash() -> str | None:
    runtime_contract_path = SCAFFOLD_ROOT / "src/.ralph/runtime-contract.md"
    if not runtime_contract_path.exists():
        return None
    return sha256_file(runtime_contract_path)


def load_managed_runtime_skill_names() -> list[str]:
    registry_path = SCAFFOLD_ROOT / "src/.ralph/agent-registry.json"
    if not registry_path.exists():
        return []
    payload = load_json(registry_path)
    skills = payload.get("managed_runtime_skills") or []
    return [skill for skill in skills if isinstance(skill, str) and skill]


def canonical_src_paths_for_ref(ref: str, prefix: str) -> list[str] | None:
    if not ref:
        return None
    if ref == CURRENT_SCAFFOLD_REF:
        current_prefix = SCAFFOLD_ROOT / prefix
        if not current_prefix.exists():
            return []
        return [
            path.relative_to(SCAFFOLD_ROOT).as_posix()
            for path in sorted(current_prefix.rglob("*"))
            if path.is_file()
        ]
    try:
        output = run_git(SCAFFOLD_ROOT, "ls-tree", "-r", "--name-only", ref, "--", prefix)
    except (subprocess.CalledProcessError, FileNotFoundError):
        output = ""
    if output:
        return [line.strip() for line in output.splitlines() if line.strip()]
    current_tag = current_scaffold_tag()
    if ref == current_tag:
        current_prefix = SCAFFOLD_ROOT / prefix
        if not current_prefix.exists():
            return []
        return [
            path.relative_to(SCAFFOLD_ROOT).as_posix()
            for path in sorted(current_prefix.rglob("*"))
            if path.is_file()
        ]
    return None


def canonical_src_text_for_ref(ref: str, relative_path: str) -> str | None:
    if not ref:
        return None
    if ref == CURRENT_SCAFFOLD_REF:
        current_path = SCAFFOLD_ROOT / relative_path
        if current_path.exists():
            return current_path.read_text()
        return None
    try:
        return run_git(SCAFFOLD_ROOT, "show", f"{ref}:{relative_path}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        current_tag = current_scaffold_tag()
        if ref == current_tag:
            current_path = SCAFFOLD_ROOT / relative_path
            if current_path.exists():
                return current_path.read_text()
    return None


def validate_managed_runtime_skill_drift(repo_root: Path) -> list[str]:
    issues: list[str] = []
    harness_version_path = repo_root / ".ralph/harness-version.json"
    if not harness_version_path.exists():
        return issues

    harness_version = load_json(harness_version_path)
    if int(harness_version.get("upgrade_contract_version") or 0) < CURRENT_UPGRADE_CONTRACT_VERSION:
        return issues
    candidate_refs = [ref for ref in (harness_version.get("resolved_commit"), harness_version.get("tag")) if isinstance(ref, str) and ref]
    managed_skills = load_managed_runtime_skill_names()
    if not managed_skills:
        return issues

    ref_for_skills: str | None = None
    canonical_files_by_skill: dict[str, list[str]] = {}
    current_contract_hash = current_scaffold_runtime_contract_hash()
    installed_contract_hash = expected_runtime_contract_baseline_hash(repo_root)
    use_current_scaffold_baseline = bool(
        current_contract_hash
        and installed_contract_hash
        and current_contract_hash == installed_contract_hash
    )

    if use_current_scaffold_baseline:
        ref_for_skills = CURRENT_SCAFFOLD_REF
        for skill_name in managed_skills:
            current_prefix = SCAFFOLD_ROOT / f"src/.agents/skills/{skill_name}"
            canonical_files_by_skill[skill_name] = [
                path.relative_to(SCAFFOLD_ROOT).as_posix()
                for path in sorted(current_prefix.rglob("*"))
                if path.is_file()
            ]

    for candidate_ref in candidate_refs:
        if ref_for_skills is not None:
            break
        missing = False
        current_files: dict[str, list[str]] = {}
        for skill_name in managed_skills:
            prefix = f"src/.agents/skills/{skill_name}"
            paths = canonical_src_paths_for_ref(candidate_ref, prefix)
            if paths is None:
                missing = True
                break
            current_files[skill_name] = paths
        if not missing:
            ref_for_skills = candidate_ref
            canonical_files_by_skill = current_files
            break

    if ref_for_skills is None:
        issues.append(
            "cannot determine the previously installed canonical managed runtime skills; restore the canonical base before upgrading or reinstall the managed runtime skills"
        )
        return issues

    for skill_name in managed_skills:
        installed_dir = repo_root / f".agents/skills/{skill_name}"
        canonical_files = canonical_files_by_skill.get(skill_name, [])
        installed_files = []
        if installed_dir.exists():
            installed_files = [
                path.relative_to(repo_root).as_posix()
                for path in sorted(installed_dir.rglob("*"))
                if path.is_file()
            ]
        expected_installed_files = [path.removeprefix("src/") for path in canonical_files]

        missing_files = sorted(set(expected_installed_files) - set(installed_files))
        extra_files = sorted(set(installed_files) - set(expected_installed_files))
        if missing_files or extra_files:
            issues.append(
                f".agents/skills/{skill_name} differs from the managed Ralph runtime skill baseline; repair the managed skill before upgrading"
            )
            continue

        for installed_relative_path in expected_installed_files:
            installed_path = repo_root / installed_relative_path
            canonical_text = canonical_src_text_for_ref(ref_for_skills, f"src/{installed_relative_path}")
            if canonical_text is None:
                issues.append(
                    f"cannot determine the canonical baseline for managed runtime skill `{skill_name}`; repair the install source before upgrading"
                )
                break
            if sha256_text(canonical_text) != sha256_file(installed_path):
                issues.append(
                    f"{installed_relative_path} differs from the managed Ralph runtime skill baseline; repair or remove the local change before upgrading"
                )
                break

    return issues


def validate_upgrade_preflight(repo_root: Path) -> list[str]:
    repo_root = resolve_canonical_checkout_root(repo_root)
    issues: list[str] = []
    runtime_contract_path = repo_root / ".ralph/runtime-contract.md"
    if not runtime_contract_path.exists():
        return issues
    expected_hash = expected_runtime_contract_baseline_hash(repo_root)
    if expected_hash is None:
        issues.append(
            "cannot determine the previously installed canonical .ralph/runtime-contract.md; restore the canonical base or move project-specific runtime rules into `.ralph/policy/runtime-overrides.md` before upgrading"
        )
        return issues
    actual_hash = sha256_file(runtime_contract_path)
    if actual_hash != expected_hash:
        issues.append(
            ".ralph/runtime-contract.md differs from its recorded canonical baseline; move project-specific runtime changes into `.ralph/policy/runtime-overrides.md` before upgrading"
        )
    issues.extend(validate_managed_runtime_skill_drift(repo_root))
    return issues


def is_git_worktree(repo_root: Path) -> bool:
    try:
        return run_git(repo_root, "rev-parse", "--is-inside-work-tree") == "true"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def current_git_branch(repo_root: Path) -> str | None:
    try:
        return run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD")
    except subprocess.CalledProcessError:
        return None


def git_worktree_dirty(repo_root: Path) -> bool:
    try:
        return bool(run_git(repo_root, "status", "--porcelain"))
    except subprocess.CalledProcessError:
        return False


def lease_is_healthy(lease: dict[str, Any], now: datetime | None = None) -> bool:
    now = now or utc_now()
    if lease.get("status") != "held":
        return False
    if not lease.get("owner_token"):
        return False
    heartbeat_at = parse_timestamp(lease.get("heartbeat_at"))
    expires_at = parse_timestamp(lease.get("expires_at"))
    if heartbeat_at is None or expires_at is None:
        return False
    if expires_at <= heartbeat_at:
        return False
    return expires_at > now


def lease_has_holder_metadata(lease: dict[str, Any]) -> bool:
    return any(
        lease.get(key) is not None
        for key in ("owner_token", "holder_thread", "run_id", "acquired_at", "heartbeat_at", "expires_at")
    )


def clear_lease_holder_state(lease: dict[str, Any]) -> dict[str, Any]:
    lease.update(
        {
            "owner_token": None,
            "holder_thread": None,
            "run_id": None,
            "acquired_at": None,
            "heartbeat_at": None,
            "expires_at": None,
            "status": "idle",
        }
    )
    return lease


def normalize_lease_state(lease: dict[str, Any], now: datetime | None = None) -> tuple[dict[str, Any], bool]:
    now = now or utc_now()
    normalized = dict(lease)
    recovered = False

    normalized["schema_version"] = CURRENT_LEASE_SCHEMA_VERSION
    if normalized.get("status") not in LEASE_STATUSES:
        recovered = True
        normalized["status"] = "idle"

    if lease_is_healthy(normalized, now):
        return normalized, recovered

    if normalized.get("status") == "held" or lease_has_holder_metadata(normalized):
        clear_lease_holder_state(normalized)
        recovered = True

    return normalized, recovered


def worktree_path_is_obstructed(repo_root: Path, relative_path: str) -> bool:
    candidate = repo_root / relative_path
    if not candidate.exists():
        return False
    if candidate.is_file():
        return True
    if is_git_worktree(candidate):
        return False
    try:
        next(candidate.iterdir())
    except StopIteration:
        return False
    return True


def worktree_assignment_is_derivable(spec: dict[str, Any], name: Any, path: Any) -> bool:
    spec_key = spec.get("spec_key") or "unknown-spec"
    return (
        name in {None, "", "canonical-root", default_worktree_name(spec_key)}
        and path in {None, "", ".", default_worktree_path(spec_key)}
    )


def choose_unique_worktree_assignment(
    repo_root: Path,
    spec: dict[str, Any],
    used_names: set[str],
    used_paths: set[str],
) -> tuple[str, str]:
    spec_key = spec["spec_key"]
    index = 0
    while True:
        suffix = "" if index == 0 else f"-wt{index + 1}"
        worktree_name = f"{default_worktree_name(spec_key)}{suffix}"
        worktree_path = default_worktree_path_for_suffix(spec_key, suffix)
        if worktree_name in used_names or worktree_path in used_paths:
            index += 1
            continue
        if worktree_path_is_obstructed(repo_root, worktree_path):
            index += 1
            continue
        return worktree_name, worktree_path


def normalize_queue_worktree_metadata(repo_root: Path, queue: dict[str, Any]) -> None:
    used_names: set[str] = set()
    used_paths: set[str] = set()
    seen_branches: dict[str, str] = {}

    for spec in queue.get("specs", []):
        branch_name = spec.get("branch_name")
        if not branch_name:
            continue
        prior_spec_key = seen_branches.get(branch_name)
        if prior_spec_key is not None and prior_spec_key != spec.get("spec_key"):
            raise RuntimeStateError(
                f"{spec.get('spec_key')}: branch_name `{branch_name}` collides with {prior_spec_key}; repair the queue before upgrading"
            )
        seen_branches[branch_name] = spec.get("spec_key")

    for spec in queue.get("specs", []):
        worktree_name = spec.get("worktree_name")
        worktree_path = spec.get("worktree_path")
        duplicate_assignment = (
            isinstance(worktree_name, str)
            and worktree_name in used_names
            or isinstance(worktree_path, str)
            and worktree_path in used_paths
        )
        obstructed_assignment = isinstance(worktree_path, str) and bool(worktree_path) and worktree_path_is_obstructed(repo_root, worktree_path)
        missing_assignment = not isinstance(worktree_name, str) or not worktree_name or not isinstance(worktree_path, str) or not worktree_path

        if worktree_path == ".":
            duplicate_assignment = True

        if missing_assignment or duplicate_assignment or obstructed_assignment:
            if not worktree_assignment_is_derivable(spec, worktree_name, worktree_path):
                problem = "duplicate" if duplicate_assignment else "obstructed" if obstructed_assignment else "missing"
                raise RuntimeStateError(
                    f"{spec.get('spec_key')}: {problem} worktree assignment is not safely derivable; repair worktree_name/worktree_path before upgrading"
                )
            worktree_name, worktree_path = choose_unique_worktree_assignment(repo_root, spec, used_names, used_paths)
            spec["worktree_name"] = worktree_name
            spec["worktree_path"] = worktree_path

        used_names.add(spec["worktree_name"])
        used_paths.add(spec["worktree_path"])


def spec_has_numbered_tasks(repo_root: Path, spec: dict[str, Any]) -> bool:
    tasks_relpath = spec.get("tasks_path")
    if not isinstance(tasks_relpath, str) or not tasks_relpath:
        return False
    tasks_path = repo_root / tasks_relpath
    if not tasks_path.exists():
        return False
    return bool(parse_tasks_markdown(tasks_path))


def spec_requires_task_state(
    repo_root: Path,
    spec: dict[str, Any],
    active_spec_ids: list[Any] | None = None,
) -> bool:
    active_ids = set(active_spec_ids or [])
    if spec.get("spec_id") in active_ids:
        return True
    if spec.get("admission_status") in ADMISSION_ACTIVE_STATUSES:
        return True
    status = spec.get("status")
    if isinstance(status, str) and status not in TASK_STATE_OPTIONAL_SPEC_STATUSES:
        return True
    return spec_has_numbered_tasks(repo_root, spec)


def refresh_runtime_derived_state(
    repo_root: Path,
    workflow: dict[str, Any],
    queue: dict[str, Any],
    worker_claims: dict[str, Any],
    lease: dict[str, Any],
    pending_intent_count: int,
) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    refreshed_queue = json.loads(json.dumps(queue))
    refreshed_workflow = json.loads(json.dumps(workflow))
    self_healed: list[str] = []
    queue_path = repo_root / ".ralph/state/spec-queue.json"
    workflow_path = repo_root / ".ralph/state/workflow-state.json"

    merge_bootstrap_summary_from_claims(refreshed_queue, worker_claims)
    rendered_queue = json.dumps(refreshed_queue, indent=2) + "\n"
    actual_queue = queue_path.read_text() if queue_path.exists() else None
    if actual_queue != rendered_queue:
        write_json(queue_path, refreshed_queue)
        self_healed.append("refreshed queue bootstrap summary fields from worker claims")

    refreshed_workflow = normalize_workflow(refreshed_workflow, refreshed_queue)
    refreshed_workflow["queue_snapshot"] = derive_queue_snapshot(refreshed_queue)
    refreshed_workflow["active_spec_ids"] = derive_active_spec_ids(refreshed_queue, refreshed_workflow)
    refreshed_workflow["active_spec_id"] = (
        refreshed_workflow["active_spec_ids"][0] if refreshed_workflow["active_spec_ids"] else None
    )
    refreshed_workflow["active_interrupt_spec_id"] = derive_interrupt_spec_id(refreshed_workflow, refreshed_queue)
    refreshed_workflow["worker_claims_path"] = (
        refreshed_queue.get("worker_claims_path") or refreshed_workflow.get("worker_claims_path") or DEFAULT_WORKER_CLAIMS_PATH
    )
    refreshed_workflow["lease_owner_token"] = lease.get("owner_token")
    refreshed_workflow["lease_heartbeat_at"] = lease.get("heartbeat_at")
    refreshed_workflow["lease_expires_at"] = lease.get("expires_at")
    refreshed_workflow["scheduler_summary"] = {
        "normal_execution_limit": refreshed_queue.get("queue_policy", {}).get(
            "normal_execution_limit",
            derive_default_normal_execution_limit(repo_root),
        ),
        "active_spec_count": len(refreshed_workflow["active_spec_ids"]),
        "active_claim_count": count_active_claims(worker_claims),
        "pending_intent_count": pending_intent_count,
        "dependency_blocked_count": count_dependency_blocked_specs(refreshed_queue),
    }
    rendered_workflow = json.dumps(refreshed_workflow, indent=2) + "\n"
    actual_workflow = workflow_path.read_text() if workflow_path.exists() else None
    if actual_workflow != rendered_workflow:
        write_json(workflow_path, refreshed_workflow)
        self_healed.append("refreshed workflow-state.json derived scheduler and lease mirror fields")

    expected_workflow_md = render_workflow_state_markdown(refreshed_workflow, refreshed_queue)
    workflow_md_path = repo_root / ".ralph/state/workflow-state.md"
    actual_workflow_md = workflow_md_path.read_text() if workflow_md_path.exists() else None
    if actual_workflow_md != expected_workflow_md:
        workflow_md_path.write_text(expected_workflow_md)
        self_healed.append("regenerated .ralph/state/workflow-state.md from canonical JSON")

    expected_spec_index = render_spec_index_markdown(refreshed_queue)
    spec_index_path = repo_root / "specs/INDEX.md"
    actual_spec_index = spec_index_path.read_text() if spec_index_path.exists() else None
    if actual_spec_index != expected_spec_index:
        spec_index_path.write_text(expected_spec_index)
        self_healed.append("regenerated specs/INDEX.md from canonical queue state")

    return refreshed_workflow, refreshed_queue, self_healed


def repair_active_spec_worktrees(
    repo_root: Path,
    queue: dict[str, Any],
    project_facts: dict[str, Any],
) -> tuple[list[str], list[str]]:
    self_healed: list[str] = []
    hard_repairs: list[str] = []
    active_spec_ids = set(queue.get("active_spec_ids") or [])

    for spec in queue.get("specs", []):
        if spec.get("admission_status") not in ADMISSION_ACTIVE_STATUSES and spec.get("spec_id") not in active_spec_ids:
            continue

        worktree_relpath = spec.get("worktree_path")
        if not isinstance(worktree_relpath, str) or not worktree_relpath:
            hard_repairs.append(f"{spec.get('spec_key', 'unknown-spec')}: active spec is missing worktree_path")
            continue

        worktree_path = repo_root / worktree_relpath
        had_worktree = worktree_path.exists() and is_git_worktree(worktree_path)
        overlay_issues = validate_worktree_shared_overlay(repo_root, worktree_path, spec.get("spec_key")) if had_worktree else []
        if had_worktree and not overlay_issues:
            continue

        try:
            ensure_spec_worktree(repo_root, spec, project_facts)
        except (RuntimeStateError, subprocess.CalledProcessError) as exc:
            hard_repairs.append(str(exc))
            continue

        if not had_worktree:
            self_healed.append(f"{spec['spec_key']}: materialized admitted worktree at {worktree_relpath}")
        elif overlay_issues:
            self_healed.append(f"{spec['spec_key']}: refreshed .ralph/shared overlay in {worktree_relpath}")

    return self_healed, hard_repairs


def ensure_lease_file(repo_root: Path, workflow: dict[str, Any]) -> dict[str, Any]:
    lease_path = repo_root / (workflow.get("orchestrator_lease_path") or DEFAULT_LEASE_PATH)
    if lease_path.exists():
        lease = load_json(lease_path)
    else:
        lease = {
            "schema_version": CURRENT_LEASE_SCHEMA_VERSION,
            "owner_token": None,
            "holder_thread": None,
            "run_id": None,
            "acquired_at": None,
            "heartbeat_at": None,
            "expires_at": None,
            "status": "idle",
        }
    lease, _ = normalize_lease_state(lease)
    lease_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(lease_path, lease)
    return lease


def ensure_intent_log(repo_root: Path, workflow: dict[str, Any]) -> Path:
    intents_path = repo_root / (workflow.get("orchestrator_intents_path") or DEFAULT_INTENTS_PATH)
    intents_path.parent.mkdir(parents=True, exist_ok=True)
    intents_path.touch(exist_ok=True)
    return intents_path


def ensure_worktree_root(repo_root: Path) -> Path:
    repo_root = resolve_canonical_checkout_root(repo_root)
    worktree_root = repo_root / DEFAULT_WORKTREE_ROOT
    worktree_root.mkdir(parents=True, exist_ok=True)
    return worktree_root


def ensure_spec_worktree(repo_root: Path, spec: dict[str, Any], project_facts: dict[str, Any] | None = None) -> Path:
    repo_root = resolve_canonical_checkout_root(repo_root)
    worktree_root = ensure_worktree_root(repo_root)
    worktree_path = repo_root / spec["worktree_path"]
    if worktree_path.exists() and is_git_worktree(worktree_path):
        ensure_worktree_shared_overlay(repo_root, worktree_path)
        return worktree_path
    if worktree_path.exists() and worktree_path_is_obstructed(repo_root, spec["worktree_path"]):
        raise RuntimeStateError(
            f"{spec.get('spec_key')}: cannot create worktree because {spec['worktree_path']} is already occupied by non-worktree content"
        )

    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    branch_name = spec.get("branch_name") or default_branch_name(spec["spec_key"])
    project_facts = normalize_project_facts(project_facts or default_project_facts())
    base_branch = spec.get("base_branch") or project_facts.get("base_branch")
    if not isinstance(base_branch, str) or not base_branch:
        raise RuntimeStateError(
            f"{spec.get('spec_key')}: cannot create worktree because the canonical base branch is unresolved; set .ralph/context/project-facts.json base_branch or an explicit spec base_branch first"
        )
    try:
        run_git(repo_root, "show-ref", "--verify", f"refs/heads/{branch_name}")
        subprocess.run(
            ["git", "worktree", "add", str(worktree_path), branch_name],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        subprocess.run(
            ["git", "worktree", "add", "-b", branch_name, str(worktree_path), base_branch],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    ensure_worktree_shared_overlay(repo_root, worktree_path)
    return worktree_path


def find_active_specs(queue: dict[str, Any]) -> list[dict[str, Any]]:
    active_ids = set(derive_active_spec_ids(queue))
    return [spec for spec in queue.get("specs", []) if spec.get("spec_id") in active_ids]


def bootstrap_claim_sort_key(claim: dict[str, Any]) -> tuple[datetime, datetime, datetime]:
    epoch = datetime.fromtimestamp(0, tz=timezone.utc)
    completed = parse_timestamp(claim.get("bootstrap_completed_at")) or epoch
    started = parse_timestamp(claim.get("bootstrap_started_at")) or epoch
    claimed = parse_timestamp(claim.get("claimed_at")) or epoch
    return completed, started, claimed


def merge_bootstrap_summary_from_claims(queue: dict[str, Any], worker_claims: dict[str, Any]) -> None:
    latest_by_spec: dict[str, dict[str, Any]] = {}
    for claim in worker_claims.get("claims", []):
        spec_id = claim.get("spec_id")
        if not isinstance(spec_id, str):
            continue
        if claim.get("bootstrap_status") not in BOOTSTRAP_STATUSES:
            continue
        prior = latest_by_spec.get(spec_id)
        if prior is None or bootstrap_claim_sort_key(claim) >= bootstrap_claim_sort_key(prior):
            latest_by_spec[spec_id] = claim

    for spec in queue.get("specs", []):
        claim = latest_by_spec.get(spec.get("spec_id"))
        if claim is None:
            continue
        spec["bootstrap_status"] = claim.get("bootstrap_status") or spec.get("bootstrap_status") or "required"
        spec["bootstrap_last_claim_id"] = claim.get("claim_id")
        spec["bootstrap_last_report_path"] = claim.get("bootstrap_report_path")
        spec["bootstrap_last_completed_at"] = (
            claim.get("bootstrap_completed_at") or claim.get("bootstrap_started_at") or claim.get("claimed_at")
        )


def detect_dependency_cycle(queue: dict[str, Any]) -> bool:
    graph = {spec.get("spec_id"): list(spec.get("depends_on_spec_ids") or []) for spec in queue.get("specs", [])}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visited:
            return False
        if node in visiting:
            return True
        visiting.add(node)
        for dep in graph.get(node, []):
            if dep in graph and visit(dep):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def collect_duplicate_queue_values(queue: dict[str, Any], field: str) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {}
    for spec in queue.get("specs", []):
        value = spec.get(field)
        if not isinstance(value, str) or not value:
            continue
        buckets.setdefault(value, []).append(spec.get("spec_key") or "unknown-spec")
    return {value: spec_keys for value, spec_keys in buckets.items() if len(spec_keys) > 1}


def parse_markdown_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def parse_commit_evidence(report_path: Path) -> tuple[dict[str, str], list[str]]:
    issues: list[str] = []
    if not report_path.exists():
        return {}, [f"missing relevant report: {report_path}"]

    sections = parse_markdown_sections(report_path.read_text())
    lines = sections.get("Commit Evidence")
    if lines is None:
        return {}, [f"{report_path}: missing `Commit Evidence` section"]

    evidence: dict[str, str] = {}
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped.startswith("- "):
            continue
        body = stripped[2:]
        if ":" not in body:
            continue
        label, value = body.split(":", 1)
        evidence[label.strip().lower()] = value.strip().strip("`")

    required = (
        "head commit",
        "commit subject",
        "task ids covered",
        "validation run",
        "additional commits or range",
    )
    for key in required:
        if not evidence.get(key):
            issues.append(f"{report_path}: `Commit Evidence` is missing `{key}`")
    return evidence, issues


def derive_spec_scoped_report_path(report_path: str, spec_key: str) -> str | None:
    path = Path(report_path)
    parts = path.parts
    if len(parts) == 5 and parts[0] == ".ralph" and parts[1] == "reports" and parts[3] == spec_key:
        return report_path
    if len(parts) != 4 or parts[0] != ".ralph" or parts[1] != "reports":
        return None
    if path.suffix != ".md" or path.stem not in SPEC_SCOPED_REPORT_ROLES:
        return None
    run_id = parts[2]
    return str(Path(".ralph") / "reports" / run_id / spec_key / path.name)


def normalize_report_pointer(
    repo_root: Path,
    report_path: Any,
    spec_key: str | None,
    legacy_report_owners: dict[str, str],
) -> Any:
    if not isinstance(report_path, str) or not report_path or not spec_key:
        return report_path
    target_report_path = derive_spec_scoped_report_path(report_path, spec_key)
    if target_report_path is None or target_report_path == report_path:
        return report_path

    owner = legacy_report_owners.get(report_path)
    if owner is not None and owner != spec_key:
        raise RuntimeStateError(
            f"legacy report path `{report_path}` is claimed by both {owner} and {spec_key}; repair the report ownership before upgrading"
        )
    legacy_report_owners[report_path] = spec_key

    source_path = repo_root / report_path
    target_path = repo_root / target_report_path
    if target_path.exists():
        if source_path.exists() and source_path.resolve() != target_path.resolve():
            if target_path.read_bytes() != source_path.read_bytes():
                raise RuntimeStateError(
                    f"legacy report path `{report_path}` conflicts with normalized target `{target_report_path}`; repair one of the reports before upgrading"
                )
        return target_report_path

    if not source_path.exists():
        return report_path

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(source_path.read_bytes())
    return target_report_path


def handoff_requires_git_checks(workflow: dict[str, Any]) -> bool:
    return (
        workflow.get("active_spec_id") is not None
        or workflow.get("current_phase") in HANDOFF_PHASES
        or workflow.get("task_status") in HANDOFF_TASK_STATUSES
    )


def handoff_requires_clean_worktree(workflow: dict[str, Any]) -> bool:
    return workflow.get("current_phase") in HANDOFF_PHASES or workflow.get("task_status") in HANDOFF_TASK_STATUSES


def handoff_requires_commit_evidence(workflow: dict[str, Any]) -> bool:
    return workflow.get("current_phase") in HANDOFF_PHASES or workflow.get("task_status") in HANDOFF_TASK_STATUSES


def find_task_entry(task_state: dict[str, Any], task_id: Any) -> dict[str, Any] | None:
    if not task_id:
        return None
    for entry in task_state.get("tasks", []):
        if entry.get("task_id") == task_id:
            return entry
    return None


def resolve_relevant_report_path(
    repo_root: Path,
    workflow: dict[str, Any],
    spec: dict[str, Any] | None,
    task_state: dict[str, Any] | None,
) -> Path | None:
    candidates: list[Any] = [workflow.get("last_report_path")]
    if task_state is not None:
        task_entry = find_task_entry(task_state, workflow.get("active_task_id"))
        if task_entry:
            candidates.append(task_entry.get("last_report_path"))
    if spec is not None:
        candidates.append(spec.get("latest_report_path"))

    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or not isinstance(candidate, str) or candidate in seen:
            continue
        seen.add(candidate)
        role = report_role_from_path(candidate)
        if role not in REPORT_COMMIT_ROLES:
            continue
        return repo_root / candidate
    return None


def configured_agent_targets(repo_root: Path) -> tuple[Path, dict[str, Path], list[str]]:
    issues: list[str] = []
    config_path = repo_root / ".codex/config.toml"
    if not config_path.exists():
        return config_path, {}, ["missing required Codex config: .codex/config.toml"]

    config = load_toml(config_path)
    if not config.get("features", {}).get("multi_agent"):
        issues.append(".codex/config.toml must enable Codex multi-agent support")

    targets: dict[str, Path] = {}
    for name, entry in (config.get("agents") or {}).items():
        if isinstance(entry, dict) and isinstance(entry.get("config_file"), str):
            targets[name] = config_path.parent / entry["config_file"]

    if not targets:
        issues.append(".codex/config.toml does not declare any agent config_file targets")

    return config_path, targets, issues


def migrate_legacy_agent_configs(repo_root: Path) -> None:
    config_path, configured_targets, config_issues = configured_agent_targets(repo_root)
    if config_issues:
        raise RuntimeStateError("; ".join(config_issues))

    legacy_dir = repo_root / "agents"
    canonical_dir = repo_root / ".codex/agents"
    if not legacy_dir.exists():
        return

    legacy_files = sorted(path.name for path in legacy_dir.glob("*.toml"))
    unknown_legacy = [name for name in legacy_files if name not in MANAGED_AGENT_FILES]
    if unknown_legacy:
        raise RuntimeStateError(
            "legacy repo-root agents/ contains unknown files: " + ", ".join(unknown_legacy)
        )

    canonical_dir.mkdir(parents=True, exist_ok=True)
    for target in configured_targets.values():
        target.parent.mkdir(parents=True, exist_ok=True)
        legacy_path = legacy_dir / target.name
        if target.exists():
            load_toml(target)
            continue
        if not legacy_path.exists():
            raise RuntimeStateError(
                f"missing canonical agent config target: {target.relative_to(repo_root)}"
            )
        target.write_text(legacy_path.read_text())
        load_toml(target)

    for path in legacy_dir.glob("*.toml"):
        path.unlink()

    leftovers = sorted(path.name for path in legacy_dir.iterdir())
    if leftovers:
        raise RuntimeStateError(
            "legacy repo-root agents/ still contains non-managed files after migration: "
            + ", ".join(leftovers)
        )
    legacy_dir.rmdir()


def infer_target_task_id(spec: dict[str, Any], tasks: list[dict[str, Any]], workflow: dict[str, Any]) -> Any:
    if workflow.get("active_spec_id") == spec.get("spec_id") and workflow.get("active_task_id"):
        return workflow.get("active_task_id")
    if spec.get("next_task_id"):
        return spec.get("next_task_id")
    checked_ids = [task["task_id"] for task in tasks if task["checked"]]
    unchecked_ids = [task["task_id"] for task in tasks if not task["checked"]]
    status = spec.get("status")
    if status in {"awaiting_review", "review_failed", "awaiting_verification", "verification_failed"}:
        return checked_ids[-1] if checked_ids else None
    if status in {"awaiting_release", "release_failed", "awaiting_pr", "awaiting_merge", "done"}:
        return tasks[-1]["task_id"] if tasks else None
    if status in {"blocked", "paused"}:
        return unchecked_ids[0] if unchecked_ids else (checked_ids[-1] if checked_ids else None)
    return unchecked_ids[0] if unchecked_ids else None


def infer_task_entries(spec: dict[str, Any], tasks: list[dict[str, Any]], workflow: dict[str, Any]) -> list[dict[str, Any]]:
    if not tasks:
        raise RuntimeStateError(f"{spec['spec_key']}: tasks.md does not contain any numbered task lines")

    target_task_id = infer_target_task_id(spec, tasks, workflow)
    task_lookup = {task["task_id"]: task for task in tasks}
    if target_task_id and target_task_id not in task_lookup:
        raise RuntimeStateError(f"{spec['spec_key']}: target task {target_task_id} is missing from tasks.md")

    status = spec.get("status")
    if status == "done":
        if any(not task["checked"] for task in tasks):
            raise RuntimeStateError(
                f"{spec['spec_key']}: spec is marked done but tasks.md still has unchecked tasks"
            )
    if (
        workflow.get("active_spec_id") == spec.get("spec_id")
        and workflow.get("task_status") in UNCHECKED_TASK_STATUSES
        and target_task_id
        and task_lookup[target_task_id]["checked"]
    ):
        raise RuntimeStateError(
            f"{spec['spec_key']}: workflow state points at {target_task_id} but tasks.md already marks it complete"
        )

    target_status = None
    if status == "done":
        target_status = "done"
    elif status in {"awaiting_review", "review_failed", "awaiting_verification", "verification_failed"}:
        target_status = status
    elif status in {"awaiting_release", "awaiting_pr", "awaiting_merge", "release_failed"}:
        target_status = "release_failed" if status == "release_failed" else "awaiting_release"
    elif status in {"blocked", "paused"}:
        target_status = status
    elif workflow.get("active_spec_id") == spec.get("spec_id") and workflow.get("task_status"):
        target_status = workflow.get("task_status")
    elif status in {"draft", "planned", "ready", "plan_check_failed"}:
        target_status = "ready"
    else:
        target_status = "in_progress"

    entries: list[dict[str, Any]] = []
    latest_role = report_role_from_path(spec.get("latest_report_path"))
    updated_at = spec.get("last_worked_at") or spec.get("created_at")
    target_seen = False
    for task in tasks:
        task_id = task["task_id"]
        checkbox_checked = task["checked"]
        if status == "done":
            entry_status = "done"
        elif task_id == target_task_id:
            entry_status = target_status
            target_seen = True
        elif target_task_id and not target_seen:
            if checkbox_checked:
                entry_status = "done"
            else:
                raise RuntimeStateError(
                    f"{spec['spec_key']}: found an unchecked task before target task {target_task_id}"
                )
        else:
            entry_status = "done" if checkbox_checked else "queued"

        expected_checked = task_checkbox_matches_status(entry_status)
        if expected_checked is not None and expected_checked != checkbox_checked:
            raise RuntimeStateError(
                f"{spec['spec_key']}: cannot infer task-state for {task_id} because tasks.md and spec status disagree"
            )

        entries.append(
            {
                "task_id": task_id,
                "status": entry_status,
                "previous_status": None,
                "last_role": latest_role,
                "last_report_path": spec.get("latest_report_path"),
                "updated_at": updated_at,
                "blocked_reason": spec.get("blocked_reason"),
                "review_result": "passed" if entry_status in {"awaiting_verification", "verification_failed", "awaiting_release", "release_failed", "released", "done"} else None,
                "verification_result": "passed" if entry_status in {"awaiting_release", "release_failed", "released", "done"} else None,
                "requirement_ids": [],
                "verification_commands": [],
                "planned_artifacts": [],
            }
        )

    return entries


def summarize_task_entries(entries: list[dict[str, Any]]) -> dict[str, int]:
    total = len(entries)
    done = sum(1 for entry in entries if entry["status"] in CHECKED_TASK_STATUSES)
    in_progress = sum(
        1
        for entry in entries
        if entry["status"] not in {"queued", "ready", "released", "done", "blocked"}
    )
    blocked = sum(1 for entry in entries if entry["status"] == "blocked")
    return {"total": total, "done": done, "in_progress": in_progress, "blocked": blocked}


def normalize_task_state(task_state: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(task_state)
    normalized["schema_version"] = CURRENT_TASK_STATE_SCHEMA_VERSION
    normalized["spec_id"] = normalized.get("spec_id") or spec.get("spec_id")
    normalized["spec_key"] = normalized.get("spec_key") or spec.get("spec_key")

    normalized_tasks: list[dict[str, Any]] = []
    for entry in normalized.get("tasks", []):
        normalized_entry = dict(entry)
        normalized_entry["requirement_ids"] = list(normalized_entry.get("requirement_ids") or [])
        normalized_entry["verification_commands"] = list(normalized_entry.get("verification_commands") or [])
        normalized_entry["planned_artifacts"] = list(normalized_entry.get("planned_artifacts") or [])
        normalized_tasks.append(normalized_entry)

    normalized["tasks"] = normalized_tasks
    return normalized


def normalize_spec_entry(spec: dict[str, Any], default_base_branch: str | None = None) -> dict[str, Any]:
    normalized = dict(spec)
    normalized["kind"] = normalized.get("kind") or "normal"
    normalized["origin_spec_key"] = normalized.get("origin_spec_key")
    normalized["origin_task_id"] = normalized.get("origin_task_id")
    normalized["triggered_by_role"] = normalized.get("triggered_by_role")
    normalized["trigger_report_path"] = normalized.get("trigger_report_path")
    normalized["trigger_summary"] = normalized.get("trigger_summary")
    normalized["depends_on_spec_ids"] = list(normalized.get("depends_on_spec_ids") or [])
    normalized["admission_status"] = normalized.get("admission_status") or "pending"
    normalized["admitted_at"] = normalized.get("admitted_at")
    normalized["research_status"] = normalized.get("research_status") or "not_started"
    normalized["research_artifact_path"] = normalized.get("research_artifact_path") or f"specs/{normalized['spec_key']}/research.md"
    normalized["research_report_path"] = normalized.get("research_report_path")
    normalized["research_updated_at"] = normalized.get("research_updated_at")
    normalized["planning_batch_id"] = normalized.get("planning_batch_id")
    normalized["task_state_path"] = normalized.get("task_state_path") or f"specs/{normalized['spec_key']}/task-state.json"
    normalized["worktree_name"] = normalized.get("worktree_name") or default_worktree_name(normalized["spec_key"])
    normalized["worktree_path"] = normalized.get("worktree_path") or default_worktree_path(normalized["spec_key"])
    normalized["branch_name"] = normalized.get("branch_name") or default_branch_name(normalized["spec_key"])
    normalized["base_branch"] = normalized.get("base_branch") or default_base_branch
    normalized["bootstrap_status"] = normalized.get("bootstrap_status") or "required"
    normalized["bootstrap_last_claim_id"] = normalized.get("bootstrap_last_claim_id")
    normalized["bootstrap_last_report_path"] = normalized.get("bootstrap_last_report_path")
    normalized["bootstrap_last_completed_at"] = normalized.get("bootstrap_last_completed_at")
    normalized["task_summary"] = normalized.get("task_summary") or {"total": 0, "done": 0, "in_progress": 0, "blocked": 0}
    normalized["slot_status"] = normalized.get("slot_status") or "inactive"
    normalized["active_task_id"] = normalized.get("active_task_id")
    normalized["task_status"] = normalized.get("task_status")
    normalized["assigned_role"] = normalized.get("assigned_role")
    normalized["active_pr_number"] = normalized.get("active_pr_number", normalized.get("pr_number"))
    normalized["active_pr_url"] = normalized.get("active_pr_url", normalized.get("pr_url"))
    normalized["last_dispatch_at"] = normalized.get("last_dispatch_at")
    normalized["next_task_id"] = normalized.get("next_task_id")
    normalized["blocked_reason"] = normalized.get("blocked_reason")
    return normalized


def normalize_queue(
    queue: dict[str, Any],
    workflow: dict[str, Any],
    project_facts: dict[str, Any] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    normalized = dict(queue)
    normalized["schema_version"] = CURRENT_QUEUE_SCHEMA_VERSION
    queue_policy = dict(normalized.get("queue_policy") or {})
    queue_policy["selection"] = CURRENT_QUEUE_SELECTION
    queue_policy["preemption"] = CURRENT_PREEMPTION_POLICY
    normal_execution_limit = queue_policy.get("normal_execution_limit")
    if isinstance(normal_execution_limit, int) and normal_execution_limit > 0:
        queue_policy["normal_execution_limit"] = normal_execution_limit
    else:
        queue_policy["normal_execution_limit"] = derive_default_normal_execution_limit(repo_root)
    normalized["queue_policy"] = queue_policy
    normalized["worker_claims_path"] = normalized.get("worker_claims_path") or workflow.get("worker_claims_path") or DEFAULT_WORKER_CLAIMS_PATH
    project_facts = normalize_project_facts(project_facts or default_project_facts())
    normalized_specs = [normalize_spec_entry(spec, project_facts.get("base_branch")) for spec in normalized.get("specs", [])]
    normalized["specs"] = normalized_specs

    active_spec_ids = derive_active_spec_ids(normalized, workflow)
    normalized["active_spec_ids"] = active_spec_ids
    normalized["active_spec_id"] = active_spec_ids[0] if active_spec_ids else normalized.get("active_spec_id")
    normalized["active_interrupt_spec_id"] = derive_interrupt_spec_id(workflow, normalized)
    normalized["resume_spec_id"] = workflow.get("resume_spec_id")
    return normalized


def normalize_workflow(workflow: dict[str, Any], queue: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(workflow)
    normalized["schema_version"] = CURRENT_WORKFLOW_SCHEMA_VERSION
    normalized["resume_spec_stack"] = list(normalized.get("resume_spec_stack") or [])
    normalized["interruption_state"] = normalized.get("interruption_state")
    normalized.pop("queue_head_spec_id", None)
    normalized["queue_snapshot"] = derive_queue_snapshot(queue)
    normalized["orchestrator_lease_path"] = normalized.get("orchestrator_lease_path") or DEFAULT_LEASE_PATH
    normalized["worker_claims_path"] = normalized.get("worker_claims_path") or queue.get("worker_claims_path") or DEFAULT_WORKER_CLAIMS_PATH
    normalized["orchestrator_intents_path"] = normalized.get("orchestrator_intents_path") or DEFAULT_INTENTS_PATH
    normalized["lease_owner_token"] = normalized.get("lease_owner_token")
    normalized["lease_heartbeat_at"] = normalized.get("lease_heartbeat_at")
    normalized["lease_expires_at"] = normalized.get("lease_expires_at")
    active_spec_ids = list(normalized.get("active_spec_ids") or queue.get("active_spec_ids") or [])
    if not active_spec_ids:
        active_spec_ids = derive_active_spec_ids(queue, normalized)
    normalized["active_spec_ids"] = active_spec_ids
    normalized["active_interrupt_spec_id"] = normalized.get("active_interrupt_spec_id")
    if normalized["active_interrupt_spec_id"] is None:
        normalized["active_interrupt_spec_id"] = derive_interrupt_spec_id(normalized, queue)
    active_spec_id = normalized.get("active_spec_id") or (active_spec_ids[0] if active_spec_ids else queue.get("active_spec_id"))
    normalized["active_spec_id"] = active_spec_id
    active_spec = None
    if active_spec_id is not None:
        for spec in queue.get("specs", []):
            if spec.get("spec_id") == active_spec_id:
                active_spec = spec
                break
    normalized["active_spec_key"] = active_spec.get("spec_key") if active_spec else None
    normalized["active_epoch_id"] = active_spec.get("epoch_id") if active_spec else normalized.get("active_epoch_id")
    if active_spec and not normalized.get("current_branch"):
        normalized["current_branch"] = active_spec.get("branch_name")
    scheduler_summary = dict(normalized.get("scheduler_summary") or {})
    scheduler_summary["normal_execution_limit"] = queue.get("queue_policy", {}).get(
        "normal_execution_limit",
        derive_default_normal_execution_limit(),
    )
    scheduler_summary["active_spec_count"] = len(active_spec_ids)
    scheduler_summary.setdefault("active_claim_count", 0)
    scheduler_summary.setdefault("pending_intent_count", 0)
    scheduler_summary["dependency_blocked_count"] = count_dependency_blocked_specs(queue)
    normalized["scheduler_summary"] = scheduler_summary
    if active_spec is None:
        normalized["active_task_id"] = None
        if normalized.get("current_phase") == "complete":
            normalized["task_status"] = None
            normalized["assigned_role"] = None
    return normalized


def migrate_repo_state(repo_root: Path) -> None:
    repo_root = resolve_canonical_checkout_root(repo_root)
    merge_installed_codex_config(repo_root)
    merge_installed_codex_hooks(repo_root)
    merge_installed_claude_settings(repo_root)
    merge_installed_cursor_hooks(repo_root)
    migrate_legacy_agent_configs(repo_root)
    ensure_runtime_overrides_file(repo_root)

    workflow_path = repo_root / ".ralph/state/workflow-state.json"
    queue_path = repo_root / ".ralph/state/spec-queue.json"
    workflow = load_json(workflow_path)
    queue = load_json(queue_path)
    project_facts_path, project_facts = ensure_project_facts_file(repo_root, queue, workflow)
    queue = normalize_queue(queue, workflow, project_facts, repo_root)
    workflow = normalize_workflow(workflow, queue)
    lease = ensure_lease_file(repo_root, workflow)
    worker_claims_path = ensure_worker_claims_file(repo_root, workflow)
    worker_claims = load_json(worker_claims_path)
    if lease_is_healthy(lease):
        raise RuntimeStateError(
            "upgrade blocked because .ralph/state/orchestrator-lease.json still shows a healthy active lease; stop the live orchestrator or wait for lease expiry before upgrading"
        )
    intents_path = ensure_intent_log(repo_root, workflow)
    ensure_worktree_root(repo_root)
    normalize_queue_worktree_metadata(repo_root, queue)
    merge_bootstrap_summary_from_claims(queue, worker_claims)
    legacy_report_owners: dict[str, str] = {}

    for spec in queue.get("specs", []):
        spec_key = spec["spec_key"]
        spec["latest_report_path"] = normalize_report_pointer(repo_root, spec.get("latest_report_path"), spec_key, legacy_report_owners)
        spec["research_report_path"] = normalize_report_pointer(repo_root, spec.get("research_report_path"), spec_key, legacy_report_owners)
        trigger_owner_spec_key = spec.get("origin_spec_key") or spec_key
        spec["trigger_report_path"] = normalize_report_pointer(
            repo_root,
            spec.get("trigger_report_path"),
            trigger_owner_spec_key,
            legacy_report_owners,
        )
        tasks_path = repo_root / spec["tasks_path"]
        task_state_path = repo_root / spec["task_state_path"]
        tasks = parse_tasks_markdown(tasks_path)
        if not task_state_path.exists():
            entries = infer_task_entries(spec, tasks, workflow)
            task_state_path.parent.mkdir(parents=True, exist_ok=True)
            task_state = {
                "schema_version": CURRENT_TASK_STATE_SCHEMA_VERSION,
                "spec_id": spec["spec_id"],
                "spec_key": spec["spec_key"],
                "tasks": entries,
            }
        else:
            task_state = load_json(task_state_path)
        task_state = normalize_task_state(task_state, spec)
        for entry in task_state.get("tasks", []):
            entry["last_report_path"] = normalize_report_pointer(
                repo_root,
                entry.get("last_report_path"),
                spec_key,
                legacy_report_owners,
            )
        write_json(task_state_path, task_state)
        spec["task_summary"] = summarize_task_entries(task_state.get("tasks", []))
        if spec.get("status") == "done":
            spec["next_task_id"] = None
            spec["slot_status"] = "inactive"
            spec["admission_status"] = "done"
        if spec.get("spec_id") in queue.get("active_spec_ids", []) or spec.get("slot_status") in WORKTREE_REQUIRED_SLOT_STATUSES:
            ensure_spec_worktree(repo_root, spec, project_facts)

    workflow_report_owner = workflow.get("active_spec_key")
    if workflow_report_owner is None and isinstance(workflow.get("last_report_path"), str):
        workflow_report_owner = legacy_report_owners.get(workflow["last_report_path"])
    workflow["last_report_path"] = normalize_report_pointer(
        repo_root,
        workflow.get("last_report_path"),
        workflow_report_owner,
        legacy_report_owners,
    )

    workflow["queue_snapshot"] = derive_queue_snapshot(queue)
    workflow["active_spec_ids"] = derive_active_spec_ids(queue, workflow)
    workflow["active_spec_id"] = workflow["active_spec_ids"][0] if workflow["active_spec_ids"] else None
    workflow["active_interrupt_spec_id"] = derive_interrupt_spec_id(workflow, queue)
    workflow["lease_owner_token"] = lease.get("owner_token")
    workflow["lease_heartbeat_at"] = lease.get("heartbeat_at")
    workflow["lease_expires_at"] = lease.get("expires_at")
    workflow["worker_claims_path"] = queue.get("worker_claims_path") or DEFAULT_WORKER_CLAIMS_PATH
    workflow["scheduler_summary"] = {
        "normal_execution_limit": queue.get("queue_policy", {}).get(
            "normal_execution_limit",
            derive_default_normal_execution_limit(repo_root),
        ),
        "active_spec_count": len(workflow["active_spec_ids"]),
        "active_claim_count": count_active_claims(worker_claims),
        "pending_intent_count": len(load_jsonl_records(intents_path)),
        "dependency_blocked_count": count_dependency_blocked_specs(queue),
    }

    harness_version_path = repo_root / ".ralph/harness-version.json"
    if harness_version_path.exists():
        harness_version = load_json(harness_version_path)
        harness_version["upgrade_contract_version"] = CURRENT_UPGRADE_CONTRACT_VERSION
        harness_version["runtime_contract_baseline_sha256"] = sha256_file(repo_root / ".ralph/runtime-contract.md")
        harness_version["runtime_overrides_path"] = DEFAULT_RUNTIME_OVERRIDES_PATH
        harness_version["branch_prefix"] = infer_branch_prefix(queue, workflow)
        harness_version["runtime_adapters"] = ["codex", "claude", "cursor"]
        write_json(harness_version_path, harness_version)

    write_json(queue_path, queue)
    write_json(workflow_path, workflow)
    write_json(project_facts_path, project_facts)
    write_json(worker_claims_path, worker_claims)
    (repo_root / ".ralph/state/workflow-state.md").write_text(render_workflow_state_markdown(workflow, queue))
    (repo_root / "specs/INDEX.md").write_text(render_spec_index_markdown(queue))


def infer_branch_prefix(queue: dict[str, Any], workflow: dict[str, Any]) -> str:
    for spec in queue.get("specs", []):
        branch_name = spec.get("branch_name")
        if isinstance(branch_name, str) and "/" in branch_name:
            return branch_name.split("/", 1)[0]
    current_branch = workflow.get("current_branch")
    if isinstance(current_branch, str) and "/" in current_branch:
        return current_branch.split("/", 1)[0]
    return "ralph"


def validate_task_state_alignment(
    spec: dict[str, Any], tasks: list[dict[str, Any]], task_state: dict[str, Any]
) -> list[str]:
    issues: list[str] = []
    task_entries = task_state.get("tasks", [])
    task_ids_from_markdown = [task["task_id"] for task in tasks]
    task_ids_from_state = [entry.get("task_id") for entry in task_entries]
    if task_ids_from_markdown != task_ids_from_state:
        issues.append(f"{spec['spec_key']}: task-state.json task ids do not match tasks.md")
        return issues

    for task, entry in zip(tasks, task_entries):
        status = entry.get("status")
        expected_checked = task_checkbox_matches_status(status)
        if expected_checked is not None and expected_checked != task["checked"]:
            issues.append(
                f"{spec['spec_key']}: {task['task_id']} is {status} in task-state.json but tasks.md checkbox disagrees"
            )
        if not isinstance(entry.get("requirement_ids"), list):
            issues.append(f"{spec['spec_key']}: {task['task_id']} requirement_ids must be a list")
        if not isinstance(entry.get("verification_commands"), list):
            issues.append(f"{spec['spec_key']}: {task['task_id']} verification_commands must be a list")
        planned_artifacts = entry.get("planned_artifacts")
        if planned_artifacts is not None and not isinstance(planned_artifacts, list):
            issues.append(f"{spec['spec_key']}: {task['task_id']} planned_artifacts must be a list when present")
    return issues


def validate_installed_runtime(repo_root: Path) -> list[str]:
    repo_root = resolve_canonical_checkout_root(repo_root)
    issues: list[str] = []
    parsed_agent_targets: dict[str, dict[str, Any]] = {}
    codex_hooks: dict[str, Any] = {}
    claude_settings: dict[str, Any] = {}
    cursor_hooks: dict[str, Any] = {}

    config_path, configured_targets, config_issues = configured_agent_targets(repo_root)
    issues.extend(config_issues)
    if config_path.exists():
        config = load_toml(config_path)
        if not config.get("features", {}).get("codex_hooks"):
            issues.append(".codex/config.toml must enable Codex hooks support")
        max_depth = config.get("agents", {}).get("max_depth")
        if not isinstance(max_depth, int):
            issues.append(".codex/config.toml agents.max_depth must be an integer")
        elif max_depth != MAX_AGENT_DEPTH:
            issues.append(
                f".codex/config.toml agents.max_depth must equal {MAX_AGENT_DEPTH} so a thin Ralph entry thread can launch one orchestrator or role subagent, which may launch worker subagents without allowing deeper fan-out"
            )
        for role, target in configured_targets.items():
            rel_target = target.relative_to(repo_root) if target.is_relative_to(repo_root) else target
            if not target.exists():
                issues.append(f".codex/config.toml points `{role}` at missing file `{rel_target}`")
                continue
            try:
                payload = load_toml(target)
            except Exception as exc:
                issues.append(f"{rel_target} does not parse as TOML: {exc}")
                continue
            parsed_agent_targets[role] = payload

        for role, expected_mode in MANAGED_AGENT_SANDBOX_MODES.items():
            payload = parsed_agent_targets.get(role)
            if payload is None:
                issues.append(f".codex/config.toml is missing managed agent mapping for `{role}`")
                continue
            actual_mode = payload.get("sandbox_mode")
            if actual_mode != expected_mode:
                issues.append(
                    f"managed agent `{role}` must use sandbox_mode `{expected_mode}`, got `{actual_mode}`"
                )

    legacy_dir = repo_root / "agents"
    if legacy_dir.exists():
        legacy_files = sorted(path.name for path in legacy_dir.glob("*.toml"))
        if legacy_files:
            issues.append("legacy repo-root agents/ still exists; migrate the role configs into .codex/agents/")

    workflow_json_path = repo_root / ".ralph/state/workflow-state.json"
    queue_json_path = repo_root / ".ralph/state/spec-queue.json"
    workflow_md_path = repo_root / ".ralph/state/workflow-state.md"
    spec_index_path = repo_root / "specs/INDEX.md"
    lease_path = repo_root / DEFAULT_LEASE_PATH
    worker_claims_path = repo_root / DEFAULT_WORKER_CLAIMS_PATH
    intents_path = repo_root / DEFAULT_INTENTS_PATH
    project_facts_path = repo_root / ".ralph/context/project-facts.json"
    runtime_contract_path = repo_root / ".ralph/runtime-contract.md"
    stop_hook_path = repo_root / DEFAULT_STOP_HOOK_PATH
    codex_hooks_path = repo_root / DEFAULT_CODEX_HOOKS_PATH
    claude_settings_path = repo_root / DEFAULT_CLAUDE_SETTINGS_PATH
    cursor_hooks_path = repo_root / DEFAULT_CURSOR_HOOKS_PATH
    orchestrator_skill_path = repo_root / ".agents/skills/orchestrator/SKILL.md"
    runtime_overrides_path = repo_root / DEFAULT_RUNTIME_OVERRIDES_PATH
    agents_loader_path = repo_root / "AGENTS.md"
    claude_loader_path = repo_root / "CLAUDE.md"
    for path in (
        workflow_json_path,
        queue_json_path,
        workflow_md_path,
        spec_index_path,
        lease_path,
        worker_claims_path,
        intents_path,
        project_facts_path,
        stop_hook_path,
        codex_hooks_path,
        claude_settings_path,
        cursor_hooks_path,
        agents_loader_path,
        claude_loader_path,
    ):
        if not path.exists():
            issues.append(f"missing required runtime file: {path.relative_to(repo_root)}")
    if not runtime_overrides_path.exists():
        issues.append(f"missing required runtime file: {runtime_overrides_path.relative_to(repo_root)}")

    if runtime_contract_path.exists():
        runtime_contract_text = runtime_contract_path.read_text()
        for snippet in RUNTIME_CONTRACT_REQUIRED_SNIPPETS:
            if snippet not in runtime_contract_text:
                issues.append(
                    f".ralph/runtime-contract.md missing required subagent isolation contract snippet: `{snippet}`"
                )
    else:
        issues.append("missing required runtime file: .ralph/runtime-contract.md")

    if orchestrator_skill_path.exists():
        orchestrator_skill_text = orchestrator_skill_path.read_text()
        for snippet in ORCHESTRATOR_SKILL_REQUIRED_SNIPPETS:
            if snippet not in orchestrator_skill_text:
                issues.append(
                    f".agents/skills/orchestrator/SKILL.md missing required delegation snippet: `{snippet}`"
                )
    else:
        issues.append("missing required runtime file: .agents/skills/orchestrator/SKILL.md")

    if issues:
        return issues

    try:
        codex_hooks = load_json(codex_hooks_path)
    except Exception as exc:
        issues.append(f"{codex_hooks_path.relative_to(repo_root)} does not parse as JSON: {exc}")
    try:
        claude_settings = load_json(claude_settings_path)
    except Exception as exc:
        issues.append(f"{claude_settings_path.relative_to(repo_root)} does not parse as JSON: {exc}")
    try:
        cursor_hooks = load_json(cursor_hooks_path)
    except Exception as exc:
        issues.append(f"{cursor_hooks_path.relative_to(repo_root)} does not parse as JSON: {exc}")

    workflow = load_json(workflow_json_path)
    queue = load_json(queue_json_path)
    worker_claims = load_json(worker_claims_path)
    project_facts = normalize_project_facts(load_json(project_facts_path))
    merge_bootstrap_summary_from_claims(queue, worker_claims)

    harness_version_path = repo_root / ".ralph/harness-version.json"
    if harness_version_path.exists():
        harness_version = load_json(harness_version_path)
        if harness_version.get("upgrade_contract_version") != CURRENT_UPGRADE_CONTRACT_VERSION:
            issues.append(
                ".ralph/harness-version.json upgrade_contract_version does not match the current migration-aware contract"
            )
        if harness_version.get("runtime_overrides_path") != DEFAULT_RUNTIME_OVERRIDES_PATH:
            issues.append(".ralph/harness-version.json runtime_overrides_path does not match the canonical overrides path")
        expected_baseline_hash = harness_version.get("runtime_contract_baseline_sha256")
        if not isinstance(expected_baseline_hash, str) or not expected_baseline_hash:
            issues.append(".ralph/harness-version.json missing runtime_contract_baseline_sha256")
        elif (repo_root / ".ralph/runtime-contract.md").exists():
            actual_runtime_contract_hash = sha256_file(repo_root / ".ralph/runtime-contract.md")
            if actual_runtime_contract_hash != expected_baseline_hash:
                issues.append(
                    ".ralph/runtime-contract.md differs from its recorded canonical baseline; move project-specific runtime changes into `.ralph/policy/runtime-overrides.md`"
                )

    for key in WORKFLOW_REQUIRED_KEYS:
        if key not in workflow:
            issues.append(f".ralph/state/workflow-state.json is missing `{key}`")

    if queue.get("schema_version") != CURRENT_QUEUE_SCHEMA_VERSION:
        issues.append(".ralph/state/spec-queue.json schema_version is not current")
    if queue.get("queue_policy", {}).get("selection") != CURRENT_QUEUE_SELECTION:
        issues.append(".ralph/state/spec-queue.json selection policy is not the current explicit-first ready-set mode")
    if queue.get("queue_policy", {}).get("preemption") != CURRENT_PREEMPTION_POLICY:
        issues.append(".ralph/state/spec-queue.json still uses a pre-interrupt preemption policy")
    normal_execution_limit = queue.get("queue_policy", {}).get("normal_execution_limit")
    if not isinstance(normal_execution_limit, int) or normal_execution_limit < 1:
        issues.append(".ralph/state/spec-queue.json normal_execution_limit must be a positive integer")
    if queue.get("worker_claims_path") != DEFAULT_WORKER_CLAIMS_PATH:
        issues.append(".ralph/state/spec-queue.json worker_claims_path must point at .ralph/state/worker-claims.json")
    if workflow.get("worker_claims_path") != DEFAULT_WORKER_CLAIMS_PATH:
        issues.append(".ralph/state/workflow-state.json worker_claims_path must point at .ralph/state/worker-claims.json")
    orchestrator_stop_hook = project_facts.get("orchestrator_stop_hook")
    if not isinstance(orchestrator_stop_hook, dict):
        issues.append(".ralph/context/project-facts.json orchestrator_stop_hook must be an object")
    else:
        if not isinstance(orchestrator_stop_hook.get("enabled"), bool):
            issues.append(".ralph/context/project-facts.json orchestrator_stop_hook.enabled must be a boolean")
        if not isinstance(orchestrator_stop_hook.get("mode"), str) or not orchestrator_stop_hook.get("mode"):
            issues.append(".ralph/context/project-facts.json orchestrator_stop_hook.mode must be a non-empty string")
        if not isinstance(orchestrator_stop_hook.get("max_auto_continue_count"), int):
            issues.append(".ralph/context/project-facts.json orchestrator_stop_hook.max_auto_continue_count must be an integer")
    if not isinstance(project_facts.get("worktree_bootstrap_commands"), list):
        issues.append(".ralph/context/project-facts.json worktree_bootstrap_commands must be a list")
    if not isinstance(project_facts.get("bootstrap_env_files"), list):
        issues.append(".ralph/context/project-facts.json bootstrap_env_files must be a list")
    if not isinstance(project_facts.get("bootstrap_copy_exclude_globs"), list):
        issues.append(".ralph/context/project-facts.json bootstrap_copy_exclude_globs must be a list")
    if not isinstance(project_facts.get("validation_bootstrap_commands"), list):
        issues.append(".ralph/context/project-facts.json validation_bootstrap_commands must be a list")
    if not isinstance(project_facts.get("verification_commands"), list):
        issues.append(".ralph/context/project-facts.json verification_commands must be a list")
    resolved_base_branch = project_facts.get("base_branch")
    if resolved_base_branch is None:
        for spec in queue.get("specs", []):
            if isinstance(spec.get("base_branch"), str) and spec.get("base_branch"):
                resolved_base_branch = spec["base_branch"]
                break
    if resolved_base_branch is None and queue.get("specs"):
        issues.append(
            ".ralph/context/project-facts.json must record the canonical base_branch, or every queued spec must carry an explicit base_branch override"
        )
    if codex_hooks.get("hooks") is None:
        issues.append(".codex/hooks.json must define a hooks object")
    else:
        stop_groups = list((codex_hooks.get("hooks") or {}).get("Stop") or [])
        if not any(
            isinstance(group, dict)
            and any(
                isinstance(hook, dict) and hook.get("command") == CODEX_STOP_HOOK_COMMAND
                for hook in list(group.get("hooks") or [])
            )
            for group in stop_groups
        ):
            issues.append(".codex/hooks.json must register the Ralph Stop hook command")
    if claude_settings.get("hooks") is None:
        issues.append(".claude/settings.json must define a hooks object")
    else:
        stop_groups = list((claude_settings.get("hooks") or {}).get("Stop") or [])
        if not any(
            isinstance(group, dict)
            and any(
                isinstance(hook, dict) and hook.get("command") == CLAUDE_STOP_HOOK_COMMAND
                for hook in list(group.get("hooks") or [])
            )
            for group in stop_groups
        ):
            issues.append(".claude/settings.json must register the Ralph Stop hook command")
    if cursor_hooks.get("version") != 1:
        issues.append(".cursor/hooks.json must declare version 1")
    if cursor_hooks.get("hooks") is None:
        issues.append(".cursor/hooks.json must define a hooks object")
    else:
        stop_entries = list((cursor_hooks.get("hooks") or {}).get("stop") or [])
        if not any(isinstance(entry, dict) and entry.get("command") == CURSOR_STOP_HOOK_COMMAND for entry in stop_entries):
            issues.append(".cursor/hooks.json must register the Ralph stop hook command")

    lease = load_json(lease_path)
    for key in LEASE_REQUIRED_KEYS:
        if key not in lease:
            issues.append(f".ralph/state/orchestrator-lease.json is missing `{key}`")
    if lease.get("status") not in LEASE_STATUSES:
        issues.append(".ralph/state/orchestrator-lease.json status must be `idle` or `held`")
    lease_heartbeat_at = parse_timestamp(lease.get("heartbeat_at"))
    lease_expires_at = parse_timestamp(lease.get("expires_at"))
    if lease.get("status") == "held":
        if lease.get("owner_token") is None:
            issues.append(".ralph/state/orchestrator-lease.json status is held but owner_token is null")
        if lease_heartbeat_at is None or lease_expires_at is None:
            issues.append(".ralph/state/orchestrator-lease.json held lease must record heartbeat_at and expires_at")
        elif lease_expires_at <= lease_heartbeat_at:
            issues.append(".ralph/state/orchestrator-lease.json expires_at must be later than heartbeat_at for a held lease")
        elif lease_expires_at <= utc_now():
            issues.append(".ralph/state/orchestrator-lease.json held lease is stale; recover it to idle before validation passes")
    elif lease_has_holder_metadata(lease):
        issues.append(".ralph/state/orchestrator-lease.json idle lease must not retain holder metadata")

    for key in WORKER_CLAIMS_REQUIRED_KEYS:
        if key not in worker_claims:
            issues.append(f".ralph/state/worker-claims.json is missing `{key}`")
    for claim in worker_claims.get("claims", []):
        for key in (
            "claim_id",
            "spec_id",
            "spec_key",
            "role",
            "runtime",
            "session_id",
            "thread_id",
            "holder",
            "execution_mode",
            "worktree_path",
            "status",
            "claimed_at",
            "heartbeat_at",
            "expires_at",
            "bootstrap_status",
            "bootstrap_started_at",
            "bootstrap_completed_at",
            "bootstrap_report_path",
            "validation_ready",
        ):
            if key not in claim:
                issues.append(f".ralph/state/worker-claims.json claim is missing `{key}`")
        if claim.get("runtime") not in SUPPORTED_RUNTIME_NAMES:
            issues.append(f".ralph/state/worker-claims.json has unsupported runtime `{claim.get('runtime')}`")
        if claim.get("execution_mode") not in SUPPORTED_EXECUTION_MODES:
            issues.append(
                f".ralph/state/worker-claims.json has unsupported execution_mode `{claim.get('execution_mode')}`"
            )
        if claim.get("status") not in CLAIM_STATUSES:
            issues.append(f".ralph/state/worker-claims.json has unsupported status `{claim.get('status')}`")
        if claim.get("bootstrap_status") not in BOOTSTRAP_STATUSES:
            issues.append(
                f".ralph/state/worker-claims.json has unsupported bootstrap_status `{claim.get('bootstrap_status')}`"
            )
        if claim.get("bootstrap_status") == "in_progress" and claim.get("bootstrap_started_at") is None:
            issues.append(".ralph/state/worker-claims.json bootstrap in_progress claims must record bootstrap_started_at")
        if claim.get("bootstrap_status") in {"passed", "failed"}:
            if claim.get("bootstrap_completed_at") is None:
                issues.append(
                    ".ralph/state/worker-claims.json bootstrap terminal claims must record bootstrap_completed_at"
                )
            if not isinstance(claim.get("bootstrap_report_path"), str) or not claim.get("bootstrap_report_path"):
                issues.append(".ralph/state/worker-claims.json bootstrap terminal claims must record bootstrap_report_path")
        if claim.get("bootstrap_status") == "passed" and claim.get("validation_ready") is not True:
            issues.append(".ralph/state/worker-claims.json bootstrap passed claims must set validation_ready=true")
        if claim.get("bootstrap_status") == "failed" and claim.get("validation_ready") is not False:
            issues.append(".ralph/state/worker-claims.json bootstrap failed claims must set validation_ready=false")
        if claim.get("role") != "bootstrap" and claim.get("status") == "claimed":
            if claim.get("bootstrap_status") != "passed" or claim.get("validation_ready") is not True:
                issues.append(
                    f".ralph/state/worker-claims.json active `{claim.get('role')}` claim for {claim.get('spec_key')} must have passed bootstrap before execution"
                )

    intents = load_jsonl_records(intents_path)
    seen_intent_ids: set[str] = set()
    last_intent_timestamp: datetime | None = None
    for record in intents:
        if record.get("type") not in INTENT_TYPES:
            issues.append(f".ralph/state/orchestrator-intents.jsonl has unsupported intent type `{record.get('type')}`")
        for key in ("intent_id", "created_at", "requested_by", "type", "status", "dependency_hints"):
            if key not in record:
                issues.append(f".ralph/state/orchestrator-intents.jsonl record missing `{key}`")
        intent_id = record.get("intent_id")
        if isinstance(intent_id, str):
            if intent_id in seen_intent_ids:
                issues.append(f".ralph/state/orchestrator-intents.jsonl contains duplicate intent_id `{intent_id}`")
            seen_intent_ids.add(intent_id)
        created_at = parse_timestamp(record.get("created_at"))
        if created_at is None:
            issues.append(".ralph/state/orchestrator-intents.jsonl record has an invalid created_at timestamp")
        elif last_intent_timestamp is not None and created_at < last_intent_timestamp:
            issues.append(".ralph/state/orchestrator-intents.jsonl records are not in append order by created_at")
        else:
            last_intent_timestamp = created_at
        if record.get("status") not in INTENT_STATUSES:
            issues.append(f".ralph/state/orchestrator-intents.jsonl has unsupported status `{record.get('status')}`")
        if not isinstance(record.get("dependency_hints"), list):
            issues.append(".ralph/state/orchestrator-intents.jsonl dependency_hints must be a list")
        if "target_spec_ids" in record and not isinstance(record.get("target_spec_ids"), list):
            issues.append(".ralph/state/orchestrator-intents.jsonl target_spec_ids must be a list when present")

    if detect_dependency_cycle(queue):
        issues.append(".ralph/state/spec-queue.json contains a dependency cycle")

    for field in ("branch_name", "worktree_name", "worktree_path"):
        duplicates = collect_duplicate_queue_values(queue, field)
        for value, spec_keys in duplicates.items():
            joined = ", ".join(spec_keys)
            issues.append(f".ralph/state/spec-queue.json duplicates {field} `{value}` across: {joined}")

    for spec in queue.get("specs", []):
        for key in QUEUE_SPEC_REQUIRED_KEYS:
            if key not in spec:
                issues.append(f"{spec.get('spec_key', 'unknown-spec')}: queue entry is missing `{key}`")
        if not isinstance(spec.get("depends_on_spec_ids"), list):
            issues.append(f"{spec.get('spec_key', 'unknown-spec')}: depends_on_spec_ids must be a list")
        for dep in spec.get("depends_on_spec_ids") or []:
            if dep not in {candidate.get("spec_id") for candidate in queue.get("specs", [])}:
                issues.append(f"{spec.get('spec_key', 'unknown-spec')}: dependency `{dep}` does not exist in the queue")
        if spec.get("research_status") not in {"not_started", "in_progress", "done", "failed"}:
            issues.append(f"{spec.get('spec_key', 'unknown-spec')}: research_status must be one of not_started, in_progress, done, failed")
        if spec.get("bootstrap_status") not in BOOTSTRAP_STATUSES:
            issues.append(
                f"{spec.get('spec_key', 'unknown-spec')}: bootstrap_status must be one of required, in_progress, passed, failed"
            )
        if spec.get("bootstrap_status") in {"passed", "failed"}:
            if not isinstance(spec.get("bootstrap_last_report_path"), str) or not spec.get("bootstrap_last_report_path"):
                issues.append(f"{spec.get('spec_key', 'unknown-spec')}: bootstrap terminal status requires bootstrap_last_report_path")
            if spec.get("bootstrap_last_completed_at") is None:
                issues.append(f"{spec.get('spec_key', 'unknown-spec')}: bootstrap terminal status requires bootstrap_last_completed_at")
        if not isinstance(spec.get("research_artifact_path"), str):
            issues.append(f"{spec.get('spec_key', 'unknown-spec')}: research_artifact_path must be a string")
        if spec.get("planning_batch_id") is not None and not isinstance(spec.get("planning_batch_id"), str):
            issues.append(f"{spec.get('spec_key', 'unknown-spec')}: planning_batch_id must be a string or null")
        research_status = spec.get("research_status")
        research_artifact_path = spec.get("research_artifact_path")
        if (
            research_status in {"in_progress", "done"}
            and isinstance(research_artifact_path, str)
            and not (repo_root / research_artifact_path).exists()
        ):
            issues.append(f"{spec.get('spec_key', 'unknown-spec')}: research_status is {research_status} but {research_artifact_path} is missing")
        if not isinstance(spec.get("base_branch"), str) or not spec.get("base_branch"):
            issues.append(f"{spec.get('spec_key', 'unknown-spec')}: queue entry must carry a resolved base_branch")
        if spec.get("admission_status") in WORKTREE_REQUIRED_SLOT_STATUSES or spec.get("spec_id") in (queue.get("active_spec_ids") or []):
            worktree_relpath = spec.get("worktree_path")
            if not isinstance(worktree_relpath, str) or not worktree_relpath:
                issues.append(f"{spec.get('spec_key', 'unknown-spec')}: active spec is missing worktree_path")
            else:
                worktree_path = repo_root / worktree_relpath
                if not worktree_path.exists():
                    issues.append(f"{spec.get('spec_key', 'unknown-spec')}: active spec worktree is missing at {worktree_relpath}")
                elif not is_git_worktree(worktree_path):
                    issues.append(f"{spec.get('spec_key', 'unknown-spec')}: worktree path is not a git worktree: {worktree_relpath}")
                else:
                    issues.extend(validate_worktree_shared_overlay(repo_root, worktree_path, spec.get("spec_key")))
                    shared_status_entries = shared_control_plane_status_entries(worktree_path)
                    if shared_status_entries:
                        preview = ", ".join(shared_status_entries[:4])
                        issues.append(
                            f"{spec.get('spec_key', 'unknown-spec')}: spec worktree must not modify canonical shared-control-plane paths; found {preview}"
                        )

    expected_workflow_md = render_workflow_state_markdown(workflow, queue)
    actual_workflow_md = workflow_md_path.read_text()
    if actual_workflow_md != expected_workflow_md:
        issues.append(".ralph/state/workflow-state.md does not match the canonical JSON projection")

    expected_spec_index = render_spec_index_markdown(queue)
    actual_spec_index = spec_index_path.read_text()
    if actual_spec_index != expected_spec_index:
        issues.append("specs/INDEX.md does not match the canonical spec queue projection")

    expected_bootstrap_projection = json.loads(json.dumps(queue))
    merge_bootstrap_summary_from_claims(expected_bootstrap_projection, worker_claims)
    for actual_spec, expected_spec in zip(queue.get("specs", []), expected_bootstrap_projection.get("specs", [])):
        for key in ("bootstrap_status", "bootstrap_last_claim_id", "bootstrap_last_report_path", "bootstrap_last_completed_at"):
            if actual_spec.get(key) != expected_spec.get(key):
                issues.append(
                    f"{actual_spec.get('spec_key', 'unknown-spec')}: queue bootstrap summary field `{key}` does not match the latest claim lifecycle"
                )

    if workflow.get("queue_snapshot") != derive_queue_snapshot(queue):
        issues.append(".ralph/state/workflow-state.json queue_snapshot does not match spec-queue.json")

    if workflow.get("active_spec_id") != queue.get("active_spec_id"):
        issues.append("workflow-state active_spec_id does not match spec-queue active_spec_id")
    if workflow.get("active_spec_ids") != queue.get("active_spec_ids"):
        issues.append("workflow-state active_spec_ids do not match spec-queue active_spec_ids")
    if workflow.get("active_interrupt_spec_id") != queue.get("active_interrupt_spec_id"):
        issues.append("workflow-state active_interrupt_spec_id does not match spec-queue active_interrupt_spec_id")
    if workflow.get("orchestrator_lease_path") != DEFAULT_LEASE_PATH:
        issues.append(".ralph/state/workflow-state.json orchestrator_lease_path does not match the canonical lease path")
    if workflow.get("orchestrator_intents_path") != DEFAULT_INTENTS_PATH:
        issues.append(".ralph/state/workflow-state.json orchestrator_intents_path does not match the canonical intents path")
    scheduler_summary = workflow.get("scheduler_summary") or {}
    if scheduler_summary.get("normal_execution_limit") != queue.get("queue_policy", {}).get("normal_execution_limit"):
        issues.append(".ralph/state/workflow-state.json scheduler_summary normal_execution_limit does not match spec-queue.json")
    if scheduler_summary.get("active_spec_count") != len(workflow.get("active_spec_ids") or []):
        issues.append(".ralph/state/workflow-state.json scheduler_summary active_spec_count does not match active_spec_ids")
    if scheduler_summary.get("pending_intent_count") != len(intents):
        issues.append(".ralph/state/workflow-state.json scheduler_summary pending_intent_count does not match the intent log")
    if scheduler_summary.get("dependency_blocked_count") != count_dependency_blocked_specs(queue):
        issues.append(".ralph/state/workflow-state.json scheduler_summary dependency_blocked_count does not match spec-queue.json")
    if workflow.get("lease_owner_token") != lease.get("owner_token"):
        issues.append(".ralph/state/workflow-state.json lease_owner_token does not match orchestrator-lease.json")
    if workflow.get("lease_heartbeat_at") != lease.get("heartbeat_at"):
        issues.append(".ralph/state/workflow-state.json lease_heartbeat_at does not match orchestrator-lease.json")
    if workflow.get("lease_expires_at") != lease.get("expires_at"):
        issues.append(".ralph/state/workflow-state.json lease_expires_at does not match orchestrator-lease.json")

    active_spec: dict[str, Any] | None = None
    active_task_state: dict[str, Any] | None = None
    spec_by_id = {spec.get("spec_id"): spec for spec in queue.get("specs", [])}

    if is_git_worktree(repo_root):
        repo_branch = current_git_branch(repo_root)
        if isinstance(resolved_base_branch, str) and resolved_base_branch and repo_branch != resolved_base_branch:
            issues.append(
                f"canonical control-plane checkout must stay on base branch `{resolved_base_branch}`, got `{repo_branch}`"
            )
        active_branches = {
            spec.get("branch_name")
            for spec in queue.get("specs", [])
            if spec.get("spec_id") in (queue.get("active_spec_ids") or []) and isinstance(spec.get("branch_name"), str)
        }
        if isinstance(repo_branch, str) and repo_branch in active_branches:
            issues.append("canonical control-plane checkout must not execute from an active spec branch")

    active_spec_ids = list(queue.get("active_spec_ids") or [])

    for spec in queue.get("specs", []):
        task_state_relpath = spec.get("task_state_path")
        if not task_state_relpath:
            issues.append(f"{spec.get('spec_key', 'unknown-spec')}: queue entry is missing task_state_path")
            continue
        task_state_path = repo_root / task_state_relpath
        if not task_state_path.exists():
            if not spec_requires_task_state(repo_root, spec, active_spec_ids):
                continue
            issues.append(f"{spec['spec_key']}: missing {task_state_relpath}")
            continue
        tasks_relpath = spec.get("tasks_path")
        if not tasks_relpath:
            issues.append(f"{spec['spec_key']}: queue entry is missing tasks_path")
            continue
        task_state = load_json(task_state_path)
        if task_state.get("schema_version") != CURRENT_TASK_STATE_SCHEMA_VERSION:
            issues.append(f"{spec['spec_key']}: task-state.json schema_version is not current")
        if task_state.get("spec_id") != spec.get("spec_id"):
            issues.append(f"{spec['spec_key']}: task-state.json spec_id does not match queue entry")
        if task_state.get("spec_key") != spec.get("spec_key"):
            issues.append(f"{spec['spec_key']}: task-state.json spec_key does not match queue entry")
        tasks = parse_tasks_markdown(repo_root / tasks_relpath)
        issues.extend(validate_task_state_alignment(spec, tasks, task_state))
        if spec.get("spec_id") == workflow.get("active_spec_id"):
            active_spec = spec
            active_task_state = task_state

    active_spec_id = workflow.get("active_spec_id")
    active_task_id = workflow.get("active_task_id")
    if active_spec_id and active_task_id:
        for spec in queue.get("specs", []):
            if spec.get("spec_id") != active_spec_id:
                continue
            tasks = parse_tasks_markdown(repo_root / spec["tasks_path"])
            lookup = {task["task_id"]: task for task in tasks}
            if active_task_id not in lookup:
                issues.append(f"workflow-state active_task_id {active_task_id} is not present in {spec['tasks_path']}")
                continue
            if workflow.get("task_status") in UNCHECKED_TASK_STATUSES and lookup[active_task_id]["checked"]:
                issues.append(
                    f"workflow-state points at {active_task_id} as the next action but tasks.md already marks it complete"
                )

    if handoff_requires_git_checks(workflow):
        if not is_git_worktree(repo_root):
            issues.append("repository must be inside a git worktree for branch-aware Ralph execution")
        for spec in find_active_specs(queue):
            worktree_relpath = spec.get("worktree_path")
            if not isinstance(worktree_relpath, str) or not worktree_relpath:
                continue
            worktree_path = repo_root / worktree_relpath
            if not worktree_path.exists() or not is_git_worktree(worktree_path):
                continue
            git_branch = current_git_branch(worktree_path)
            if spec.get("branch_name") and git_branch != spec.get("branch_name"):
                issues.append(
                    f"{spec.get('spec_key')}: git branch does not match the active spec branch: expected {spec.get('branch_name')}, got {git_branch}"
                )
            if spec.get("task_status") in HANDOFF_TASK_STATUSES and git_worktree_dirty(worktree_path):
                issues.append(f"{spec.get('spec_key')}: dirty worktree blocks review, verification, release, or completed-task handoff")

        if handoff_requires_commit_evidence(workflow):
            report_path = resolve_relevant_report_path(repo_root, workflow, active_spec, active_task_state)
            if report_path is None:
                issues.append("missing relevant implement/review/verify/release report for commit-evidence preflight")
            else:
                commit_repo = repo_root
                if active_spec and active_spec.get("worktree_path"):
                    candidate_repo = repo_root / active_spec.get("worktree_path")
                    if candidate_repo.exists() and is_git_worktree(candidate_repo):
                        commit_repo = candidate_repo
                evidence, evidence_issues = parse_commit_evidence(report_path)
                issues.extend(evidence_issues)
                if not evidence_issues:
                    checkpoint_commit = evidence.get("head commit", "")
                    if not COMMIT_SHA_RE.match(checkpoint_commit):
                        issues.append(f"{report_path}: `Head commit` must be a 7-40 character git SHA")
                    else:
                        try:
                            resolved_commit = run_git(commit_repo, "rev-parse", checkpoint_commit)
                        except subprocess.CalledProcessError:
                            resolved_commit = ""
                        if not resolved_commit:
                            issues.append(
                                f"{report_path}: `Head commit` {checkpoint_commit} does not resolve to a git commit in the active spec worktree"
                            )
                        else:
                            merge_base = subprocess.run(
                                ["git", "merge-base", "--is-ancestor", resolved_commit, "HEAD"],
                                cwd=commit_repo,
                                capture_output=True,
                                text=True,
                            )
                            if merge_base.returncode != 0:
                                issues.append(
                                    f"{report_path}: `Head commit` {checkpoint_commit} is not contained in the current branch tip"
                                )

                            expected_subject = run_git(commit_repo, "log", "-1", "--format=%s", resolved_commit)
                            if evidence.get("commit subject") != expected_subject:
                                issues.append(
                                    f"{report_path}: `Commit subject` does not match commit `{resolved_commit}` subject `{expected_subject}`"
                                )

                    if active_task_id and active_task_id not in evidence.get("task ids covered", ""):
                        issues.append(
                            f"{report_path}: `Task ids covered` must include the active task {active_task_id}"
                        )

                    if evidence.get("validation run", "").lower() in {"none", "n/a", "null"}:
                        issues.append(f"{report_path}: `Validation run` must record real checkpoint evidence")

    return issues


def dedupe_messages(messages: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for message in messages:
        if message in seen:
            continue
        seen.add(message)
        ordered.append(message)
    return ordered


def classify_preflight_issue(
    repo_root: Path,
    queue: dict[str, Any],
    issue: str,
) -> tuple[str, str] | None:
    if "differs from its recorded canonical baseline" in issue or "managed Ralph runtime skill baseline" in issue:
        return "upgrade_required", issue

    missing_task_state = re.match(r"^(?P<spec_key>[^:]+): missing (?P<path>specs/.+/task-state\.json)$", issue)
    if missing_task_state:
        spec_key = missing_task_state.group("spec_key")
        spec = next((candidate for candidate in queue.get("specs", []) if candidate.get("spec_key") == spec_key), None)
        if spec is None or spec_requires_task_state(repo_root, spec, queue.get("active_spec_ids") or []):
            return (
                "route_to_planning_task_gen",
                f"{spec_key}: missing {missing_task_state.group('path')}; run task-gen or refresh planning artifacts before execution",
            )
        return None

    if "task-state.json task ids do not match tasks.md" in issue or " in task-state.json but tasks.md checkbox disagrees" in issue:
        return "route_to_planning_task_gen", f"{issue}; refresh planning artifacts or rerun task-gen before execution"

    if "research_status is" in issue and "research.md" in issue and "is missing" in issue:
        return "route_to_planning_task_gen", f"{issue}; rerun plan or research before execution"

    if "queue entry is missing task_state_path" in issue:
        return "route_to_planning_task_gen", f"{issue}; refresh planning artifacts before execution"

    return "hard_repair_required", issue


def check_runtime_preflight(
    repo_root: Path,
    apply_repairs: bool = True,
) -> dict[str, list[str]]:
    repo_root = resolve_canonical_checkout_root(repo_root)
    results = {
        "self_healed": [],
        "route_to_planning_task_gen": [],
        "upgrade_required": [],
        "hard_repair_required": [],
    }

    upgrade_issues = validate_upgrade_preflight(repo_root)
    results["upgrade_required"].extend(upgrade_issues)
    if upgrade_issues:
        for issue in validate_installed_runtime(repo_root):
            classification = classify_preflight_issue(repo_root, {"specs": [], "active_spec_ids": []}, issue)
            if classification is None:
                continue
            category, message = classification
            if category == "upgrade_required":
                results["upgrade_required"].append(message)
        for key in results:
            results[key] = dedupe_messages(results[key])
        return results

    required_paths = (
        repo_root / ".ralph/state/workflow-state.json",
        repo_root / ".ralph/state/spec-queue.json",
        repo_root / ".ralph/state/worker-claims.json",
        repo_root / ".ralph/state/orchestrator-lease.json",
        repo_root / ".ralph/context/project-facts.json",
        repo_root / ".ralph/state/orchestrator-intents.jsonl",
    )
    if apply_repairs and all(path.exists() for path in required_paths):
        workflow = load_json(repo_root / ".ralph/state/workflow-state.json")
        queue = load_json(repo_root / ".ralph/state/spec-queue.json")
        worker_claims = load_json(repo_root / ".ralph/state/worker-claims.json")
        lease = load_json(repo_root / ".ralph/state/orchestrator-lease.json")
        project_facts = normalize_project_facts(load_json(repo_root / ".ralph/context/project-facts.json"))
        intents = load_jsonl_records(repo_root / ".ralph/state/orchestrator-intents.jsonl")

        workflow, queue, self_healed = refresh_runtime_derived_state(
            repo_root,
            workflow,
            queue,
            worker_claims,
            lease,
            pending_intent_count=len(intents),
        )
        results["self_healed"].extend(self_healed)

        worktree_repairs, hard_repairs = repair_active_spec_worktrees(repo_root, queue, project_facts)
        results["self_healed"].extend(worktree_repairs)
        results["hard_repair_required"].extend(hard_repairs)

    queue_for_classification: dict[str, Any]
    queue_path = repo_root / ".ralph/state/spec-queue.json"
    if queue_path.exists():
        queue_for_classification = load_json(queue_path)
    else:
        queue_for_classification = {"specs": [], "active_spec_ids": []}

    for issue in validate_installed_runtime(repo_root):
        classification = classify_preflight_issue(repo_root, queue_for_classification, issue)
        if classification is None:
            continue
        category, message = classification
        results[category].append(message)

    for key in results:
        results[key] = dedupe_messages(results[key])
    return results
