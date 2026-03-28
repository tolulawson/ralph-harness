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

    print("test-stop-boundary-hook: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
