#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

sys.path.insert(0, str(ROOT / "scripts"))

from runtime_state_helpers import (  # noqa: E402
    CHECKED_TASK_STATUSES,
    HANDOFF_TASK_STATUSES,
    RELEASE_OUTCOMES,
    SUPPORTED_EXECUTION_MODES,
    infer_task_entries,
    task_status_expected_role,
)


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected to find {needle!r}")


def assert_equal(actual: object, expected: object) -> None:
    if actual != expected:
        raise AssertionError(f"expected {expected!r}, got {actual!r}")


def lifecycle_spec(status: str) -> dict[str, object]:
    return {
        "spec_id": "001",
        "spec_key": "001-lifecycle-fixture",
        "status": status,
        "latest_report_path": ".ralph/reports/fixture/001-lifecycle-fixture/release.md",
        "created_at": "2026-04-02T12:00:00Z",
        "last_worked_at": "2026-04-02T12:30:00Z",
        "blocked_reason": None,
    }


def test_task_status_role_routing() -> None:
    expected = {
        "ready": "implement",
        "in_progress": "implement",
        "awaiting_review": "review",
        "review_failed": "review",
        "awaiting_verification": "verify",
        "verification_failed": "verify",
        "awaiting_release": "release",
        "release_failed": "release",
    }
    for status, role in expected.items():
        assert_equal(task_status_expected_role(status), role)
    assert_equal(task_status_expected_role("done"), None)
    assert_equal(task_status_expected_role("blocked"), None)


def test_release_failed_is_a_checked_handoff_status() -> None:
    assert_contains(" ".join(sorted(CHECKED_TASK_STATUSES)), "release_failed")
    assert_contains(" ".join(sorted(HANDOFF_TASK_STATUSES)), "release_failed")


def test_release_outcomes_are_explicit() -> None:
    expected_outcomes = {
        "pr_created",
        "awaiting_review",
        "awaiting_merge",
        "merge_completed",
        "release_failed",
        "human_gate_waiting",
    }
    assert_equal(RELEASE_OUTCOMES, expected_outcomes)


def test_supported_execution_mode_is_native_subagent_only() -> None:
    assert_equal(SUPPORTED_EXECUTION_MODES, {"native_subagent"})
    coordination = (ROOT / "scripts/orchestrator-coordination.py").read_text()
    assert_contains(coordination, 'default="native_subagent"')


def test_final_release_handoff_and_next_task_readiness() -> None:
    final_tasks = [
        {"task_id": "001-T001", "checked": True},
        {"task_id": "001-T002", "checked": True},
    ]
    release_entries = infer_task_entries(lifecycle_spec("awaiting_release"), final_tasks, {})
    assert_equal(release_entries[-1]["status"], "awaiting_release")
    assert_equal(release_entries[-1]["review_result"], "passed")
    assert_equal(release_entries[-1]["verification_result"], "passed")

    release_failed_entries = infer_task_entries(lifecycle_spec("release_failed"), final_tasks, {})
    assert_equal(release_failed_entries[-1]["status"], "release_failed")
    assert_equal(release_failed_entries[-1]["review_result"], "passed")
    assert_equal(release_failed_entries[-1]["verification_result"], "passed")

    assert_equal(task_status_expected_role("in_progress"), "implement")
    assert_equal(task_status_expected_role("awaiting_review"), "review")
    assert_equal(task_status_expected_role("awaiting_verification"), "verify")
    assert_equal(task_status_expected_role("awaiting_release"), "release")
    assert_equal(task_status_expected_role("done"), None)
    assert_equal(task_status_expected_role("ready"), "implement")


def test_contract_language_covers_queue_drain_and_reconciliation() -> None:
    runtime_contract = (SRC / ".ralph/runtime-contract.md").read_text()
    orchestrator_skill = (SRC / ".agents/skills/orchestrator/SKILL.md").read_text()
    execute_skill = (ROOT / "skills/ralph-execute/SKILL.md").read_text()
    release_skill = (SRC / ".agents/skills/release/SKILL.md").read_text()
    plan_skill = (ROOT / "skills/ralph-plan/SKILL.md").read_text()

    for text in (runtime_contract, orchestrator_skill, execute_skill):
        assert_contains(text, "awaiting_review")
        assert_contains(text, "awaiting_verification")
        assert_contains(text, "awaiting_release")
        assert_contains(text, "release_failed")

    assert_contains(runtime_contract.lower(), "workers release their claims and exit")
    assert_contains(runtime_contract.lower(), "orchestrator alone")
    assert_contains(runtime_contract.lower(), "refill freed execution slots")
    assert_contains(orchestrator_skill.lower(), "workers release their claims and exit")
    assert_contains(orchestrator_skill.lower(), "refill freed slots")
    assert_contains(execute_skill, "record every delegated worker")
    assert_contains(execute_skill, "Do not accept inline current-session worker execution")
    assert_contains(runtime_contract, "main thread must never continue as the PRD or planning coordinator")
    assert_contains(orchestrator_skill, "launcher thread is already done being a launcher")

    for outcome in RELEASE_OUTCOMES:
        assert_contains(release_skill, outcome)

    assert_contains(plan_skill, "must not become Ralph's planning coordinator")
    assert_contains(plan_skill, "delegate `specify`")
    assert_contains(plan_skill, "Delegate `task-gen`")
    assert_contains(plan_skill, "Delegate `plan-check`")


def main() -> int:
    tests = [
        test_task_status_role_routing,
        test_release_failed_is_a_checked_handoff_status,
        test_release_outcomes_are_explicit,
        test_supported_execution_mode_is_native_subagent_only,
        test_final_release_handoff_and_next_task_readiness,
        test_contract_language_covers_queue_drain_and_reconciliation,
    ]
    for test in tests:
        test()
    print("test-control-plane-lifecycle: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
