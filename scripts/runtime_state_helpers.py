from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib  # type: ignore


CURRENT_QUEUE_SCHEMA_VERSION = "3.0.0"
CURRENT_WORKFLOW_SCHEMA_VERSION = "3.0.0"
CURRENT_TASK_STATE_SCHEMA_VERSION = "1.1.0"
CURRENT_PREEMPTION_POLICY = "failing_out_of_scope_bug"
CURRENT_QUEUE_SELECTION = "fifo_admission_window"
CURRENT_NORMAL_EXECUTION_LIMIT = 2
CURRENT_UPGRADE_CONTRACT_VERSION = 6
CURRENT_LEASE_SCHEMA_VERSION = "1.0.0"
DEFAULT_LEASE_PATH = ".ralph/state/orchestrator-lease.json"
DEFAULT_INTENTS_PATH = ".ralph/state/orchestrator-intents.jsonl"
DEFAULT_WORKTREE_ROOT = ".ralph/worktrees"
LEASE_LOCK_SUFFIX = ".lock"
LEASE_TTL_SECONDS = 90
SCAFFOLD_ROOT = Path(__file__).resolve().parents[1]
MANAGED_AGENT_NAMES = (
    "orchestrator",
    "prd",
    "specify",
    "research",
    "plan",
    "task_gen",
    "plan_check",
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
    "implement": "danger-full-access",
    "review": "danger-full-access",
    "verify": "danger-full-access",
    "release": "danger-full-access",
}
MAX_AGENT_DEPTH = 2
RUNTIME_CONTRACT_REQUIRED_SNIPPETS = (
    "forked context semantics (`fork_context = true`)",
    'agent_type = "explorer"',
    'agent_type = "worker"',
    "Child roles must not spawn nested workers.",
    "single-writer lease",
    "orchestrator-intents.jsonl",
    "git worktree",
)
ORCHESTRATOR_SKILL_REQUIRED_SNIPPETS = (
    "`fork_context = true`",
    "`agent_type` mapping",
    "close that worker thread",
    "durable intent",
    "worktree",
)

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
    "queue_head_spec_id",
    "orchestrator_lease_path",
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

TASK_LINE_RE = re.compile(r"^\s*-\s\[(?P<checked>[ xX])\]\s(?P<task_id>\d{3,}-T\d{3,})\b")

UNCHECKED_TASK_STATUSES = {"queued", "ready", "in_progress", "paused", "blocked"}
CHECKED_TASK_STATUSES = {
    "awaiting_review",
    "review_failed",
    "plan_check_failed",
    "awaiting_verification",
    "verification_failed",
    "awaiting_release",
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
    "blocked",
    "paused",
}
ADMISSION_ACTIVE_STATUSES = {"admitted", "running", "paused"}
WORKTREE_REQUIRED_SLOT_STATUSES = {"admitted", "running", "paused"}
HANDOFF_PHASES = {"review", "verification", "release"}
HANDOFF_TASK_STATUSES = {
    "awaiting_review",
    "review_failed",
    "awaiting_verification",
    "verification_failed",
    "awaiting_release",
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
    "implement",
    "review",
    "verify",
    "release",
}
COMMIT_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
INTENT_TYPES = {"create_spec", "schedule_spec", "pause_spec", "resume_spec", "status_request"}
INTENT_STATUSES = {"pending", "acknowledged", "processed", "rejected"}
LEASE_STATUSES = {"idle", "held"}


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


def default_worktree_name(spec_key: str) -> str:
    return f"ralph-{spec_key}"


def default_worktree_path(spec_key: str) -> str:
    return f"{DEFAULT_WORKTREE_ROOT}/{spec_key}"


def default_worktree_path_for_suffix(spec_key: str, suffix: str) -> str:
    return default_worktree_path(f"{spec_key}{suffix}")


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


def merge_codex_config(installed: dict[str, Any], scaffold: dict[str, Any]) -> dict[str, Any]:
    merged = dict(installed)

    for key, value in scaffold.items():
        if key in {"features", "agents"}:
            continue
        merged.setdefault(key, value)

    merged_features = dict(installed.get("features") or {})
    scaffold_features = dict(scaffold.get("features") or {})
    for key, value in scaffold_features.items():
        if key == "multi_agent":
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
                existing_depth = merged_agents.get(key)
                if isinstance(existing_depth, int):
                    merged_agents[key] = min(existing_depth, value)
                else:
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


def derive_queue_head_spec_id(queue: dict[str, Any]) -> Any:
    for spec in queue.get("specs", []):
        if spec.get("status") not in {"done", "superseded"}:
            return spec.get("spec_id")
    return None


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
        f"- Active spec: `{format_code(workflow.get('active_spec_key'))}`",
        f"- Active task: `{format_code(workflow.get('active_task_id'))}`",
        f"- Phase: `{format_code(workflow.get('current_phase'))}`",
        f"- Task status: `{format_code(workflow.get('task_status'))}`",
        f"- Assigned role: `{format_code(workflow.get('assigned_role'))}`",
        f"- Branch: `{format_code(workflow.get('current_branch'))}`",
        f"- Run id: `{format_code(workflow.get('current_run_id'))}`",
        f"- Active PR number: `{format_code(workflow.get('active_pr_number'))}`",
        f"- Active PR URL: `{format_code(workflow.get('active_pr_url'))}`",
        f"- Queue head spec: `{format_code(workflow.get('queue_head_spec_id'))}`",
        f"- Active interrupt spec: `{format_code(workflow.get('active_interrupt_spec_id'))}`",
        f"- Lease path: `{format_code(workflow.get('orchestrator_lease_path'))}`",
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
        "| Spec | Kind | Depends On | Epoch | Title | Status | Admission | Slot | Worktree | Branch | PR | Latest Report |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for spec in queue.get("specs", []):
        branch_name = spec.get("branch_name") or f"codex/{spec.get('spec_key')}"
        depends_on = ",".join(spec.get("depends_on_spec_ids") or []) or "null"
        lines.append(
            "| {spec_key} | {kind} | {depends_on} | {epoch} | {title} | {status} | {admission} | {slot} | `{worktree}` | `{branch}` | `{pr}` | `{report}` |".format(
                spec_key=spec.get("spec_key"),
                kind=spec.get("kind"),
                depends_on=depends_on,
                epoch=spec.get("epoch_id"),
                title=spec.get("title"),
                status=spec.get("status"),
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
    worktree_root = repo_root / DEFAULT_WORKTREE_ROOT
    worktree_root.mkdir(parents=True, exist_ok=True)
    return worktree_root


def ensure_spec_worktree(repo_root: Path, spec: dict[str, Any]) -> Path:
    worktree_root = ensure_worktree_root(repo_root)
    worktree_path = repo_root / spec["worktree_path"]
    if worktree_path.exists() and is_git_worktree(worktree_path):
        return worktree_path
    if worktree_path.exists() and worktree_path_is_obstructed(repo_root, spec["worktree_path"]):
        raise RuntimeStateError(
            f"{spec.get('spec_key')}: cannot create worktree because {spec['worktree_path']} is already occupied by non-worktree content"
        )

    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    branch_name = spec.get("branch_name") or f"codex/{spec['spec_key']}"
    base_branch = spec.get("base_branch") or "main"
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
    return worktree_path


def find_active_specs(queue: dict[str, Any]) -> list[dict[str, Any]]:
    active_ids = set(derive_active_spec_ids(queue))
    return [spec for spec in queue.get("specs", []) if spec.get("spec_id") in active_ids]


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
    if status in {"awaiting_release", "awaiting_pr", "awaiting_merge", "done"}:
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
    elif status in {"awaiting_release", "awaiting_pr", "awaiting_merge"}:
        target_status = "awaiting_release"
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
                "review_result": "passed" if entry_status in {"awaiting_verification", "awaiting_release", "released", "done"} else None,
                "verification_result": "passed" if entry_status in {"awaiting_release", "released", "done"} else None,
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


def normalize_spec_entry(spec: dict[str, Any]) -> dict[str, Any]:
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
    normalized["branch_name"] = normalized.get("branch_name") or f"codex/{normalized['spec_key']}"
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


def normalize_queue(queue: dict[str, Any], workflow: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(queue)
    normalized["schema_version"] = CURRENT_QUEUE_SCHEMA_VERSION
    queue_policy = dict(normalized.get("queue_policy") or {})
    queue_policy["selection"] = CURRENT_QUEUE_SELECTION
    queue_policy["preemption"] = CURRENT_PREEMPTION_POLICY
    queue_policy["normal_execution_limit"] = int(queue_policy.get("normal_execution_limit") or CURRENT_NORMAL_EXECUTION_LIMIT)
    normalized["queue_policy"] = queue_policy
    normalized_specs = [normalize_spec_entry(spec) for spec in normalized.get("specs", [])]
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
    normalized["queue_head_spec_id"] = derive_queue_head_spec_id(queue)
    normalized["queue_snapshot"] = derive_queue_snapshot(queue)
    normalized["orchestrator_lease_path"] = normalized.get("orchestrator_lease_path") or DEFAULT_LEASE_PATH
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
    normalized["scheduler_summary"] = dict(
        normalized.get("scheduler_summary")
        or {
            "normal_execution_limit": queue.get("queue_policy", {}).get("normal_execution_limit", CURRENT_NORMAL_EXECUTION_LIMIT),
            "active_spec_count": len(active_spec_ids),
            "pending_intent_count": 0,
            "dependency_blocked_count": count_dependency_blocked_specs(queue),
        }
    )
    if active_spec is None:
        normalized["active_task_id"] = None
        if normalized.get("current_phase") == "complete":
            normalized["task_status"] = None
            normalized["assigned_role"] = None
    return normalized


def migrate_repo_state(repo_root: Path) -> None:
    merge_installed_codex_config(repo_root)
    migrate_legacy_agent_configs(repo_root)

    workflow_path = repo_root / ".ralph/state/workflow-state.json"
    queue_path = repo_root / ".ralph/state/spec-queue.json"
    workflow = load_json(workflow_path)
    queue = load_json(queue_path)
    queue = normalize_queue(queue, workflow)
    workflow = normalize_workflow(workflow, queue)
    lease = ensure_lease_file(repo_root, workflow)
    if lease_is_healthy(lease):
        raise RuntimeStateError(
            "upgrade blocked because .ralph/state/orchestrator-lease.json still shows a healthy active lease; stop the live orchestrator or wait for lease expiry before upgrading"
        )
    intents_path = ensure_intent_log(repo_root, workflow)
    ensure_worktree_root(repo_root)
    normalize_queue_worktree_metadata(repo_root, queue)
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
            ensure_spec_worktree(repo_root, spec)

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
    workflow["queue_head_spec_id"] = derive_queue_head_spec_id(queue)
    workflow["active_spec_ids"] = derive_active_spec_ids(queue, workflow)
    workflow["active_spec_id"] = workflow["active_spec_ids"][0] if workflow["active_spec_ids"] else None
    workflow["active_interrupt_spec_id"] = derive_interrupt_spec_id(workflow, queue)
    workflow["lease_owner_token"] = lease.get("owner_token")
    workflow["lease_heartbeat_at"] = lease.get("heartbeat_at")
    workflow["lease_expires_at"] = lease.get("expires_at")
    workflow["scheduler_summary"] = {
        "normal_execution_limit": queue.get("queue_policy", {}).get("normal_execution_limit", CURRENT_NORMAL_EXECUTION_LIMIT),
        "active_spec_count": len(workflow["active_spec_ids"]),
        "pending_intent_count": len(load_jsonl_records(intents_path)),
        "dependency_blocked_count": count_dependency_blocked_specs(queue),
    }

    harness_version_path = repo_root / ".ralph/harness-version.json"
    if harness_version_path.exists():
        harness_version = load_json(harness_version_path)
        harness_version["upgrade_contract_version"] = CURRENT_UPGRADE_CONTRACT_VERSION
        write_json(harness_version_path, harness_version)

    write_json(queue_path, queue)
    write_json(workflow_path, workflow)
    (repo_root / ".ralph/state/workflow-state.md").write_text(render_workflow_state_markdown(workflow, queue))
    (repo_root / "specs/INDEX.md").write_text(render_spec_index_markdown(queue))


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
    issues: list[str] = []
    parsed_agent_targets: dict[str, dict[str, Any]] = {}

    config_path, configured_targets, config_issues = configured_agent_targets(repo_root)
    issues.extend(config_issues)
    if config_path.exists():
        config = load_toml(config_path)
        max_depth = config.get("agents", {}).get("max_depth")
        if not isinstance(max_depth, int):
            issues.append(".codex/config.toml agents.max_depth must be an integer")
        elif max_depth > MAX_AGENT_DEPTH:
            issues.append(
                f".codex/config.toml agents.max_depth must be <= {MAX_AGENT_DEPTH} to enforce no nested worker fan-out"
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
    intents_path = repo_root / DEFAULT_INTENTS_PATH
    runtime_contract_path = repo_root / ".ralph/runtime-contract.md"
    orchestrator_skill_path = repo_root / ".agents/skills/orchestrator/SKILL.md"
    for path in (workflow_json_path, queue_json_path, workflow_md_path, spec_index_path, lease_path, intents_path):
        if not path.exists():
            issues.append(f"missing required runtime file: {path.relative_to(repo_root)}")

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

    workflow = load_json(workflow_json_path)
    queue = load_json(queue_json_path)

    harness_version_path = repo_root / ".ralph/harness-version.json"
    if harness_version_path.exists():
        harness_version = load_json(harness_version_path)
        if harness_version.get("upgrade_contract_version") != CURRENT_UPGRADE_CONTRACT_VERSION:
            issues.append(
                ".ralph/harness-version.json upgrade_contract_version does not match the current migration-aware contract"
            )

    for key in WORKFLOW_REQUIRED_KEYS:
        if key not in workflow:
            issues.append(f".ralph/state/workflow-state.json is missing `{key}`")

    if queue.get("schema_version") != CURRENT_QUEUE_SCHEMA_VERSION:
        issues.append(".ralph/state/spec-queue.json schema_version is not current")
    if queue.get("queue_policy", {}).get("selection") != CURRENT_QUEUE_SELECTION:
        issues.append(".ralph/state/spec-queue.json selection policy is not the current FIFO admission window mode")
    if queue.get("queue_policy", {}).get("preemption") != CURRENT_PREEMPTION_POLICY:
        issues.append(".ralph/state/spec-queue.json still uses a pre-interrupt preemption policy")
    if queue.get("queue_policy", {}).get("normal_execution_limit") != CURRENT_NORMAL_EXECUTION_LIMIT:
        issues.append(".ralph/state/spec-queue.json normal_execution_limit does not match the current default")

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

    expected_workflow_md = render_workflow_state_markdown(workflow, queue)
    actual_workflow_md = workflow_md_path.read_text()
    if actual_workflow_md != expected_workflow_md:
        issues.append(".ralph/state/workflow-state.md does not match the canonical JSON projection")

    expected_spec_index = render_spec_index_markdown(queue)
    actual_spec_index = spec_index_path.read_text()
    if actual_spec_index != expected_spec_index:
        issues.append("specs/INDEX.md does not match the canonical spec queue projection")

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
    if scheduler_summary.get("normal_execution_limit") != CURRENT_NORMAL_EXECUTION_LIMIT:
        issues.append(".ralph/state/workflow-state.json scheduler_summary normal_execution_limit is not current")
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

    for spec in queue.get("specs", []):
        task_state_relpath = spec.get("task_state_path")
        if not task_state_relpath:
            issues.append(f"{spec.get('spec_key', 'unknown-spec')}: queue entry is missing task_state_path")
            continue
        task_state_path = repo_root / task_state_relpath
        if not task_state_path.exists():
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
