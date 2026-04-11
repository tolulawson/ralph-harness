#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = ROOT / "src/.ralph/hooks/stop-boundary.py"


def build_repo_fixture(tmp_root: Path, project_facts: dict | None = None) -> Path:
    repo_root = tmp_root / "repo"
    (repo_root / ".ralph/context").mkdir(parents=True)
    (repo_root / ".ralph/state").mkdir(parents=True, exist_ok=True)
    (repo_root / ".ralph").mkdir(exist_ok=True)
    (repo_root / ".ralph/context/project-facts.json").write_text(
        json.dumps(
            project_facts
            or {
                "schema_version": "1.1.0",
                "orchestrator_stop_hook": {
                    "enabled": True,
                    "mode": "conservative",
                    "max_auto_continue_count": 1,
                },
            },
            indent=2,
        )
        + "\n"
    )
    (repo_root / ".ralph/runtime-contract.md").write_text(
        "# Runtime Contract\n\n"
        "Review, verification, and release failures are remediation signals, not stop conditions.\n"
    )
    return repo_root


def write_runtime_state(
    repo_root: Path,
    *,
    workflow: dict | None = None,
    queue: dict | None = None,
    scheduler_lock: dict | None = None,
    execution_claims: dict | None = None,
    intents: list[dict] | None = None,
) -> None:
    defaults = {
        "workflow": {
            "schema_version": "7.0.0",
            "scheduler_lock_path": ".ralph/state/scheduler-lock.json",
            "execution_claims_path": ".ralph/state/execution-claims.json",
            "scheduler_intents_path": ".ralph/state/scheduler-intents.jsonl",
            "active_spec_ids": [],
        },
        "queue": {
            "schema_version": "7.0.0",
            "queue_revision": 0,
            "active_spec_ids": [],
            "specs": [],
        },
        "scheduler_lock": {
            "schema_version": "2.0.0",
            "owner_token": None,
            "heartbeat_at": None,
            "expires_at": None,
            "status": "idle",
        },
        "execution_claims": {
            "schema_version": "2.0.0",
            "claims": [],
        },
    }

    payloads = {
        "workflow": {**defaults["workflow"], **(workflow or {})},
        "queue": {**defaults["queue"], **(queue or {})},
        "scheduler_lock": {**defaults["scheduler_lock"], **(scheduler_lock or {})},
        "execution_claims": {**defaults["execution_claims"], **(execution_claims or {})},
    }

    (repo_root / ".ralph/state/workflow-state.json").write_text(json.dumps(payloads["workflow"]) + "\n")
    (repo_root / ".ralph/state/spec-queue.json").write_text(json.dumps(payloads["queue"]) + "\n")
    (repo_root / ".ralph/state/scheduler-lock.json").write_text(json.dumps(payloads["scheduler_lock"]) + "\n")
    (repo_root / ".ralph/state/execution-claims.json").write_text(json.dumps(payloads["execution_claims"]) + "\n")
    intents_path = repo_root / ".ralph/state/scheduler-intents.jsonl"
    lines = [json.dumps(intent) for intent in (intents or [])]
    intents_path.write_text(("\n".join(lines) + "\n") if lines else "")


def run_hook(repo_root: Path, runtime: str, payload: dict) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(HOOK_PATH), "--runtime", runtime],
        cwd=repo_root,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )


def parse_json_stdout(completed: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(completed.stdout) if completed.stdout.strip() else {}


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = build_repo_fixture(Path(tmpdir))
        write_runtime_state(repo_root)

        codex_continue = parse_json_stdout(
            run_hook(
                repo_root,
                "codex",
                {
                    "turn_id": "turn-1",
                    "stop_hook_active": False,
                    "last_assistant_message": "Verification failed, but I can resolve it by rerunning bootstrap and fixing the issue.",
                },
            )
        )
        assert codex_continue["decision"] == "block"
        assert "continue autonomously" in codex_continue["reason"]

        codex_human_gate = parse_json_stdout(
            run_hook(
                repo_root,
                "codex",
                {
                    "turn_id": "turn-2",
                    "stop_hook_active": False,
                    "last_assistant_message": "I need the user to approve the release and provide an API key before I can continue.",
                },
            )
        )
        assert codex_human_gate["continue"] is False
        assert "human-gated boundary" in codex_human_gate["stopReason"]

        claude_already_continued = parse_json_stdout(
            run_hook(
                repo_root,
                "claude",
                {
                    "session_id": "session-1",
                    "stop_hook_active": True,
                    "last_assistant_message": "I can probably fix this with one more pass.",
                },
            )
        )
        assert claude_already_continued["continue"] is False
        assert "already consumed" in claude_already_continued["stopReason"]

        cursor_error_continue = parse_json_stdout(
            run_hook(
                repo_root,
                "cursor",
                {
                    "conversation_id": "conv-1",
                    "generation_id": "gen-1",
                    "status": "error",
                    "loop_count": 0,
                },
            )
        )
        assert "followup_message" in cursor_error_continue
        assert "Hook rationale" in cursor_error_continue["followup_message"]

        cursor_completed_stop = run_hook(
            repo_root,
            "cursor",
            {
                "conversation_id": "conv-2",
                "generation_id": "gen-2",
                "status": "completed",
                "loop_count": 1,
            },
        )
        assert cursor_completed_stop.stdout.strip() == ""

        pending_repo = build_repo_fixture(Path(tmpdir) / "pending")
        write_runtime_state(
            pending_repo,
            intents=[{"intent_id": "intent-1", "status": "pending", "kind": "schedule_spec"}],
        )
        pending_continue = parse_json_stdout(
            run_hook(
                pending_repo,
                "codex",
                {
                    "turn_id": "turn-3",
                    "stop_hook_active": False,
                    "last_assistant_message": "I think I'm done.",
                },
            )
        )
        assert pending_continue["decision"] == "block"
        assert "pending scheduler intents remain" in pending_continue["reason"]

        admitted_repo = build_repo_fixture(Path(tmpdir) / "admitted")
        write_runtime_state(
            admitted_repo,
            workflow={"active_spec_ids": ["056"]},
            queue={
                "active_spec_ids": ["056"],
                "specs": [
                    {
                        "spec_id": "056",
                        "spec_key": "056-peer-fixture",
                        "admission_status": "admitted",
                    }
                ],
            },
        )
        admitted_continue = parse_json_stdout(
            run_hook(
                admitted_repo,
                "codex",
                {
                    "turn_id": "turn-4",
                    "stop_hook_active": False,
                    "last_assistant_message": "Finished the last pass.",
                },
            )
        )
        assert admitted_continue["decision"] == "block"
        assert "has no healthy execution claim" in admitted_continue["reason"]

    print("test-stop-boundary-hook: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
