#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

sys.path.insert(0, str(ROOT / "scripts"))

from runtime_state_helpers import (  # noqa: E402
    CURRENT_TASK_STATE_SCHEMA_VERSION,
    normalize_queue,
    normalize_workflow,
    render_spec_index_markdown,
    render_workflow_state_markdown,
)


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def copy_scaffold(target: Path) -> None:
    manifest = (SRC / "install-manifest.txt").read_text().splitlines()
    for raw_path in manifest:
        path = raw_path.strip()
        if not path or path.startswith("#"):
            continue
        source = SRC / path
        destination = target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(source, destination)

    generated = (SRC / "generated-runtime-manifest.txt").read_text().splitlines()
    for raw_path in generated:
        path = raw_path.strip()
        if not path or path.startswith("#"):
            continue
        destination = target / path
        if path.endswith("/"):
            destination.mkdir(parents=True, exist_ok=True)
        elif "." in destination.name:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text("")
        else:
            destination.mkdir(parents=True, exist_ok=True)


def init_git_repo(target: Path) -> None:
    run(["git", "init", "-q", "-b", "main"], target)
    run(["git", "config", "user.name", "Ralph Harness Tests"], target)
    run(["git", "config", "user.email", "ralph-harness-tests@example.test"], target)
    run(["git", "add", "."], target)
    run(["git", "commit", "-q", "-m", "chore: seed runtime fixture"], target)


def make_spec(
    *,
    spec_id: str,
    slug: str,
    title: str,
    status: str,
    admission_status: str,
    slot_status: str,
    active_task_id: str | None = None,
    task_status: str | None = None,
    assigned_role: str | None = None,
) -> dict[str, object]:
    spec_key = f"{spec_id}-{slug}"
    return {
        "spec_id": spec_id,
        "spec_slug": slug,
        "spec_key": spec_key,
        "title": title,
        "epoch_id": "E001",
        "created_at": "2026-04-02T09:00:00-07:00",
        "last_worked_at": "2026-04-02T09:00:00-07:00",
        "status": status,
        "kind": "normal",
        "origin_spec_key": None,
        "origin_task_id": None,
        "triggered_by_role": None,
        "trigger_report_path": None,
        "trigger_summary": None,
        "priority_override": None,
        "blocked_reason": None,
        "depends_on_spec_ids": [],
        "admission_status": admission_status,
        "admitted_at": "2026-04-02T09:05:00-07:00" if admission_status != "pending" else None,
        "research_status": "not_started",
        "research_artifact_path": f"specs/{spec_key}/research.md",
        "research_report_path": None,
        "research_updated_at": None,
        "planning_batch_id": "batch-001",
        "prd_path": "tasks/prd-fixture.md",
        "spec_path": f"specs/{spec_key}/spec.md",
        "plan_path": f"specs/{spec_key}/plan.md",
        "tasks_path": f"specs/{spec_key}/tasks.md",
        "task_state_path": f"specs/{spec_key}/task-state.json",
        "latest_report_path": None,
        "worktree_name": f"ralph-{spec_key}",
        "worktree_path": f".ralph/worktrees/{spec_key}",
        "branch_name": f"ralph/{spec_key}",
        "base_branch": "main",
        "bootstrap_status": "required",
        "bootstrap_last_claim_id": None,
        "bootstrap_last_report_path": None,
        "bootstrap_last_completed_at": None,
        "slot_status": slot_status,
        "active_task_id": active_task_id,
        "task_status": task_status,
        "assigned_role": assigned_role,
        "active_pr_number": None,
        "active_pr_url": None,
        "last_dispatch_at": None,
        "pr_number": None,
        "pr_url": None,
        "pr_state": None,
        "merge_commit": None,
        "task_summary": {"total": 0, "done": 0, "in_progress": 0, "blocked": 0},
        "next_task_id": active_task_id,
    }


def write_task_artifacts(
    repo: Path,
    spec: dict[str, object],
    *,
    tasks_body: str,
    write_task_state: bool,
) -> None:
    spec_dir = repo / "specs" / str(spec["spec_key"])
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(f"# {spec['title']}\n\nFixture spec.\n")
    (spec_dir / "plan.md").write_text(f"# Plan For {spec['spec_key']}\n\nFixture plan.\n")
    (spec_dir / "tasks.md").write_text(tasks_body)
    if write_task_state:
        task_id = str(spec["active_task_id"] or "001-T001")
        task_state = {
            "schema_version": CURRENT_TASK_STATE_SCHEMA_VERSION,
            "spec_id": spec["spec_id"],
            "spec_key": spec["spec_key"],
            "tasks": [
                {
                    "task_id": task_id,
                    "status": str(spec["task_status"] or "ready"),
                    "previous_status": None,
                    "last_role": str(spec["assigned_role"] or "plan"),
                    "last_report_path": None,
                    "updated_at": "2026-04-02T09:10:00-07:00",
                    "blocked_reason": None,
                    "review_result": None,
                    "verification_result": None,
                    "requirement_ids": [],
                    "verification_commands": [],
                    "planned_artifacts": [],
                }
            ],
        }
        (spec_dir / "task-state.json").write_text(json.dumps(task_state, indent=2) + "\n")


def write_runtime(repo: Path, specs: list[dict[str, object]], *, current_phase: str, task_status: str = "queued") -> None:
    workflow = json.loads((SRC / ".ralph/state/workflow-state.json").read_text())
    queue = json.loads((SRC / ".ralph/state/spec-queue.json").read_text())
    project_facts = json.loads((SRC / ".ralph/context/project-facts.json").read_text())

    active_spec_ids = [
        str(spec["spec_id"])
        for spec in specs
        if spec["admission_status"] in {"admitted", "running", "paused"} or spec["slot_status"] in {"admitted", "running", "paused"}
    ]

    queue["specs"] = deepcopy(specs)
    queue["active_spec_ids"] = active_spec_ids
    queue["active_spec_id"] = active_spec_ids[0] if active_spec_ids else None
    project_facts["base_branch"] = "main"

    workflow["project_name"] = repo.name
    workflow["current_phase"] = current_phase
    workflow["task_status"] = task_status
    workflow["assigned_role"] = "orchestrator"
    workflow["active_spec_ids"] = active_spec_ids
    workflow["active_spec_id"] = active_spec_ids[0] if active_spec_ids else None
    workflow["active_task_id"] = str(specs[0]["active_task_id"]) if active_spec_ids and specs[0]["active_task_id"] else None

    queue = normalize_queue(queue, workflow, project_facts, repo)
    workflow = normalize_workflow(workflow, queue)

    (repo / ".ralph/context/project-facts.json").write_text(json.dumps(project_facts, indent=2) + "\n")
    (repo / ".ralph/state/spec-queue.json").write_text(json.dumps(queue, indent=2) + "\n")
    (repo / ".ralph/state/workflow-state.json").write_text(json.dumps(workflow, indent=2) + "\n")
    (repo / ".ralph/state/workflow-state.md").write_text(render_workflow_state_markdown(workflow, queue))
    (repo / "specs/INDEX.md").write_text(render_spec_index_markdown(queue))


def create_fixture(name: str) -> Path:
    target = Path(tempfile.mkdtemp(prefix=f"ralph-{name}-"))
    copy_scaffold(target)
    init_git_repo(target)
    return target


def run_check_at_path(repo_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/check-installed-runtime-state.py"), "--repo", str(repo_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def run_check(repo: Path) -> subprocess.CompletedProcess[str]:
    return run_check_at_path(repo)


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected to find {needle!r} in:\n{text}")


def assert_not_contains(text: str, needle: str) -> None:
    if needle in text:
        raise AssertionError(f"did not expect to find {needle!r} in:\n{text}")


def test_planned_spec_routes_to_task_gen() -> None:
    repo = create_fixture("planned-task-gen")
    spec = make_spec(
        spec_id="001",
        slug="planned-task-gap",
        title="Planned Task Gap",
        status="planned",
        admission_status="pending",
        slot_status="inactive",
    )
    write_task_artifacts(
        repo,
        spec,
        tasks_body="# Tasks\n\n## Phase 1\n\n- [ ] 001-T001 Prepare runtime fixture\n",
        write_task_state=False,
    )
    write_runtime(repo, [spec], current_phase="planning")

    result = run_check(repo)
    if result.returncode != 1:
        raise AssertionError(result.stdout + result.stderr)
    assert_contains(result.stdout, "Route To Planning/Task-Gen:")
    assert_contains(result.stdout, "run task-gen or refresh planning artifacts before execution")
    assert_not_contains(result.stdout, "Upgrade Required:")


def test_planned_spec_without_numbered_tasks_stays_valid() -> None:
    repo = create_fixture("planned-optional-task-state")
    spec = make_spec(
        spec_id="001",
        slug="planned-optional-task-state",
        title="Optional Task State",
        status="planned",
        admission_status="pending",
        slot_status="inactive",
    )
    write_task_artifacts(
        repo,
        spec,
        tasks_body="# Tasks\n\nPlanning is still in progress.\n",
        write_task_state=False,
    )
    write_runtime(repo, [spec], current_phase="planning")

    result = run_check(repo)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    assert_contains(result.stdout, "check-installed-runtime-state: ok")
    assert_not_contains(result.stdout, "Route To Planning/Task-Gen:")


def test_missing_admitted_worktree_self_heals() -> None:
    repo = create_fixture("missing-worktree")
    spec = make_spec(
        spec_id="001",
        slug="missing-worktree",
        title="Missing Worktree",
        status="ready",
        admission_status="admitted",
        slot_status="admitted",
        active_task_id="001-T001",
        task_status="ready",
        assigned_role="bootstrap",
    )
    write_task_artifacts(
        repo,
        spec,
        tasks_body="# Tasks\n\n## Phase 1\n\n- [ ] 001-T001 Prepare worktree\n",
        write_task_state=True,
    )
    write_runtime(repo, [spec], current_phase="implementation", task_status="ready")

    result = run_check(repo)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    assert_contains(result.stdout, "Self-healed:")
    assert_contains(result.stdout, "materialized admitted worktree")
    worktree = repo / ".ralph/worktrees/001-missing-worktree"
    if not worktree.exists():
        raise AssertionError("expected admitted worktree to be created")
    if not (worktree / ".ralph/shared/state").is_symlink():
        raise AssertionError("expected shared overlay symlink inside repaired worktree")


def test_stale_projections_self_heal() -> None:
    repo = create_fixture("stale-projections")
    write_runtime(repo, [], current_phase="bootstrap")
    (repo / ".ralph/state/workflow-state.md").write_text("stale workflow projection\n")
    (repo / "specs/INDEX.md").write_text("stale index projection\n")

    result = run_check(repo)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    assert_contains(result.stdout, "regenerated .ralph/state/workflow-state.md from canonical JSON")
    assert_contains(result.stdout, "regenerated specs/INDEX.md from canonical queue state")


def test_runtime_contract_baseline_drift_requires_upgrade() -> None:
    repo = create_fixture("baseline-drift")
    (repo / ".ralph/runtime-contract.md").write_text(
        (repo / ".ralph/runtime-contract.md").read_text() + "\nScaffold drift for fixture.\n"
    )

    result = run_check(repo)
    if result.returncode != 1:
        raise AssertionError(result.stdout + result.stderr)
    assert_contains(result.stdout, "Upgrade Required:")
    assert_contains(result.stdout, ".ralph/runtime-contract.md differs from its recorded canonical baseline")


def test_custom_canonical_worktree_repo_arg_is_respected() -> None:
    repo = create_fixture("custom-canonical-worktree")
    project_facts_path = repo / ".ralph/context/project-facts.json"
    project_facts = json.loads(project_facts_path.read_text())
    project_facts["base_branch"] = "staging"
    project_facts_path.write_text(json.dumps(project_facts, indent=2) + "\n")
    run(["git", "add", ".ralph/context/project-facts.json"], repo)
    run(["git", "commit", "-q", "-m", "test: set staging as canonical base branch"], repo)

    staging_checkout = repo.parent / f"{repo.name}-staging"
    run(["git", "worktree", "add", "-q", "-b", "staging", str(staging_checkout), "HEAD"], repo)

    result = run_check_at_path(staging_checkout)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    assert_contains(result.stdout, "check-installed-runtime-state: ok")


def test_configured_custom_canonical_checkout_path_is_honored() -> None:
    repo = create_fixture("configured-canonical-path")
    staging_checkout = repo.parent / f"{repo.name}-staging"
    run(["git", "worktree", "add", "-q", "-b", "staging", str(staging_checkout), "HEAD"], repo)

    main_facts_path = repo / ".ralph/context/project-facts.json"
    main_facts = json.loads(main_facts_path.read_text())
    main_facts["base_branch"] = "staging"
    main_facts["canonical_control_plane"] = {
        "mode": "custom",
        "checkout_path": str(staging_checkout),
        "base_branch": "staging",
    }
    main_facts_path.write_text(json.dumps(main_facts, indent=2) + "\n")

    staging_facts_path = staging_checkout / ".ralph/context/project-facts.json"
    staging_facts = json.loads(staging_facts_path.read_text())
    staging_facts["base_branch"] = "staging"
    staging_facts["canonical_control_plane"] = {
        "mode": "current_checkout",
        "checkout_path": None,
        "base_branch": "staging",
    }
    staging_facts_path.write_text(json.dumps(staging_facts, indent=2) + "\n")

    result = run_check(repo)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    assert_contains(result.stdout, "check-installed-runtime-state: ok")


def test_spec_worktree_repo_arg_resolves_to_canonical_root() -> None:
    repo = create_fixture("worktree-repo-arg")
    spec = make_spec(
        spec_id="001",
        slug="worktree-repo-arg",
        title="Worktree Repo Arg",
        status="ready",
        admission_status="admitted",
        slot_status="admitted",
        active_task_id="001-T001",
        task_status="ready",
        assigned_role="bootstrap",
    )
    write_task_artifacts(
        repo,
        spec,
        tasks_body="# Tasks\n\n## Phase 1\n\n- [ ] 001-T001 Prepare worktree\n",
        write_task_state=True,
    )
    write_runtime(repo, [spec], current_phase="implementation", task_status="ready")

    initial = run_check(repo)
    if initial.returncode != 0:
        raise AssertionError(initial.stdout + initial.stderr)

    spec_worktree = repo / ".ralph/worktrees/001-worktree-repo-arg"
    result = run_check_at_path(spec_worktree)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    assert_not_contains(result.stdout, "canonical control-plane checkout must stay on base branch")
    assert_contains(result.stdout, "check-installed-runtime-state: ok")


def main() -> int:
    tests = [
        test_planned_spec_routes_to_task_gen,
        test_planned_spec_without_numbered_tasks_stays_valid,
        test_missing_admitted_worktree_self_heals,
        test_stale_projections_self_heal,
        test_runtime_contract_baseline_drift_requires_upgrade,
        test_custom_canonical_worktree_repo_arg_is_respected,
        test_configured_custom_canonical_checkout_path_is_honored,
        test_spec_worktree_repo_arg_resolves_to_canonical_root,
    ]
    for test in tests:
        test()
    print("test-runtime-preflight-repairs: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
