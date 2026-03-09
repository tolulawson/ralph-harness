from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib  # type: ignore


CURRENT_QUEUE_SCHEMA_VERSION = "2.1.0"
CURRENT_WORKFLOW_SCHEMA_VERSION = "2.0.0"
CURRENT_TASK_STATE_SCHEMA_VERSION = "1.1.0"
CURRENT_PREEMPTION_POLICY = "failing_out_of_scope_bug"
CURRENT_UPGRADE_CONTRACT_VERSION = 4
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

WORKFLOW_REQUIRED_KEYS = (
    "schema_version",
    "project_name",
    "active_epoch_id",
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
    "branch_name",
    "base_branch",
    "pr_number",
    "pr_url",
    "pr_state",
    "merge_commit",
    "task_summary",
    "next_task_id",
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
COMMIT_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")


class RuntimeStateError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


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
                "branch_name": spec.get("branch_name"),
                "pr_number": spec.get("pr_number"),
            }
        )
    return snapshot


def derive_queue_head_spec_id(queue: dict[str, Any]) -> Any:
    for spec in queue.get("specs", []):
        if spec.get("status") not in {"done", "superseded"}:
            return spec.get("spec_id")
    return None


def render_workflow_state_markdown(workflow: dict[str, Any], queue: dict[str, Any]) -> str:
    resume_stack = workflow.get("resume_spec_stack") or []
    interrupt_spec_id = derive_interrupt_spec_id(workflow, queue)
    resume_pending = "yes" if resume_stack else "no"
    lines = [
        "# Workflow State",
        "",
        f"- Project: `{format_code(workflow.get('project_name'))}`",
        f"- Active epoch: `{format_code(workflow.get('active_epoch_id'))}`",
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
        "| Spec | Kind | Origin | Epoch | Title | Status | Branch | PR | Latest Report |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for spec in queue.get("specs", []):
        branch_name = spec.get("branch_name") or f"codex/{spec.get('spec_key')}"
        lines.append(
            "| {spec_key} | {kind} | {origin} | {epoch} | {title} | {status} | `{branch}` | `{pr}` | `{report}` |".format(
                spec_key=spec.get("spec_key"),
                kind=spec.get("kind"),
                origin=format_code(spec.get("origin_spec_key")),
                epoch=spec.get("epoch_id"),
                title=spec.get("title"),
                status=spec.get("status"),
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
    normalized["research_status"] = normalized.get("research_status") or "not_started"
    normalized["research_artifact_path"] = normalized.get("research_artifact_path") or f"specs/{normalized['spec_key']}/research.md"
    normalized["research_report_path"] = normalized.get("research_report_path")
    normalized["research_updated_at"] = normalized.get("research_updated_at")
    normalized["planning_batch_id"] = normalized.get("planning_batch_id")
    normalized["task_state_path"] = normalized.get("task_state_path") or f"specs/{normalized['spec_key']}/task-state.json"
    normalized["branch_name"] = normalized.get("branch_name") or f"codex/{normalized['spec_key']}"
    normalized["task_summary"] = normalized.get("task_summary") or {"total": 0, "done": 0, "in_progress": 0, "blocked": 0}
    normalized["next_task_id"] = normalized.get("next_task_id")
    normalized["blocked_reason"] = normalized.get("blocked_reason")
    return normalized


def normalize_queue(queue: dict[str, Any], workflow: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(queue)
    normalized["schema_version"] = CURRENT_QUEUE_SCHEMA_VERSION
    queue_policy = dict(normalized.get("queue_policy") or {})
    queue_policy["selection"] = "fifo"
    queue_policy["preemption"] = CURRENT_PREEMPTION_POLICY
    normalized["queue_policy"] = queue_policy
    normalized_specs = [normalize_spec_entry(spec) for spec in normalized.get("specs", [])]
    normalized["specs"] = normalized_specs

    active_spec_id = normalized.get("active_spec_id")
    if active_spec_id is None:
        for spec in normalized_specs:
            if spec.get("status") in ACTIVE_SPEC_STATUSES and spec.get("kind") != "interrupt":
                active_spec_id = spec.get("spec_id")
                break
    normalized["active_spec_id"] = active_spec_id
    normalized["resume_spec_id"] = workflow.get("resume_spec_id")
    return normalized


def normalize_workflow(workflow: dict[str, Any], queue: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(workflow)
    normalized["schema_version"] = CURRENT_WORKFLOW_SCHEMA_VERSION
    normalized["resume_spec_stack"] = list(normalized.get("resume_spec_stack") or [])
    normalized["interruption_state"] = normalized.get("interruption_state")
    normalized["queue_head_spec_id"] = derive_queue_head_spec_id(queue)
    normalized["queue_snapshot"] = derive_queue_snapshot(queue)
    active_spec_id = normalized.get("active_spec_id") or queue.get("active_spec_id")
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

    for spec in queue.get("specs", []):
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
        write_json(task_state_path, task_state)
        spec["task_summary"] = summarize_task_entries(task_state.get("tasks", []))
        if spec.get("status") == "done":
            spec["next_task_id"] = None

    workflow["queue_snapshot"] = derive_queue_snapshot(queue)
    workflow["queue_head_spec_id"] = derive_queue_head_spec_id(queue)

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

    config_path, configured_targets, config_issues = configured_agent_targets(repo_root)
    issues.extend(config_issues)
    if config_path.exists():
        for role, target in configured_targets.items():
            rel_target = target.relative_to(repo_root) if target.is_relative_to(repo_root) else target
            if not target.exists():
                issues.append(f".codex/config.toml points `{role}` at missing file `{rel_target}`")
                continue
            try:
                load_toml(target)
            except Exception as exc:
                issues.append(f"{rel_target} does not parse as TOML: {exc}")

    legacy_dir = repo_root / "agents"
    if legacy_dir.exists():
        legacy_files = sorted(path.name for path in legacy_dir.glob("*.toml"))
        if legacy_files:
            issues.append("legacy repo-root agents/ still exists; migrate the role configs into .codex/agents/")

    workflow_json_path = repo_root / ".ralph/state/workflow-state.json"
    queue_json_path = repo_root / ".ralph/state/spec-queue.json"
    workflow_md_path = repo_root / ".ralph/state/workflow-state.md"
    spec_index_path = repo_root / "specs/INDEX.md"
    for path in (workflow_json_path, queue_json_path, workflow_md_path, spec_index_path):
        if not path.exists():
            issues.append(f"missing required runtime file: {path.relative_to(repo_root)}")

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
    if queue.get("queue_policy", {}).get("preemption") != CURRENT_PREEMPTION_POLICY:
        issues.append(".ralph/state/spec-queue.json still uses a pre-interrupt preemption policy")

    for spec in queue.get("specs", []):
        for key in QUEUE_SPEC_REQUIRED_KEYS:
            if key not in spec:
                issues.append(f"{spec.get('spec_key', 'unknown-spec')}: queue entry is missing `{key}`")
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

    active_spec: dict[str, Any] | None = None
    active_task_state: dict[str, Any] | None = None

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
        else:
            git_branch = current_git_branch(repo_root)
            if active_spec and active_spec.get("branch_name") and git_branch != active_spec.get("branch_name"):
                issues.append(
                    "git branch does not match the active spec branch: "
                    f"expected {active_spec.get('branch_name')}, got {git_branch}"
                )

            if handoff_requires_clean_worktree(workflow) and git_worktree_dirty(repo_root):
                issues.append("dirty worktree blocks review, verification, release, or completed-task handoff")

            if handoff_requires_commit_evidence(workflow):
                report_path = resolve_relevant_report_path(repo_root, workflow, active_spec, active_task_state)
                if report_path is None:
                    issues.append("missing relevant implement/review/verify/release report for commit-evidence preflight")
                else:
                    evidence, evidence_issues = parse_commit_evidence(report_path)
                    issues.extend(evidence_issues)
                    if not evidence_issues:
                        checkpoint_commit = evidence.get("head commit", "")
                        if not COMMIT_SHA_RE.match(checkpoint_commit):
                            issues.append(f"{report_path}: `Head commit` must be a 7-40 character git SHA")
                        else:
                            try:
                                resolved_commit = run_git(repo_root, "rev-parse", checkpoint_commit)
                            except subprocess.CalledProcessError:
                                resolved_commit = ""
                            if not resolved_commit:
                                issues.append(
                                    f"{report_path}: `Head commit` {checkpoint_commit} does not resolve to a git commit in this repo"
                                )
                            else:
                                merge_base = subprocess.run(
                                    ["git", "merge-base", "--is-ancestor", resolved_commit, "HEAD"],
                                    cwd=repo_root,
                                    capture_output=True,
                                    text=True,
                                )
                                if merge_base.returncode != 0:
                                    issues.append(
                                        f"{report_path}: `Head commit` {checkpoint_commit} is not contained in the current branch tip"
                                    )

                                expected_subject = run_git(repo_root, "log", "-1", "--format=%s", resolved_commit)
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
