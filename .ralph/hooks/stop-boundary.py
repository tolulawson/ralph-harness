#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_CONTINUATION_PROMPT = (
    "Re-check whether you are actually done or blocked on explicit human verification, "
    "approval, or review. If not, continue autonomously, resolve any self-service blocker, "
    "and keep draining the queue. Stop only if the work is complete, the queue is empty, "
    "or a true human-gated boundary remains."
)

HUMAN_GATED_PATTERNS = (
    r"\bapprove\b",
    r"\bapproval\b",
    r"\bcredential",
    r"\blog ?in\b",
    r"\bsign ?in\b",
    r"\bauth(?:entication)?\b",
    r"\bapi key\b",
    r"\bsecret\b",
    r"\btoken\b",
    r"\bmanual review\b",
    r"\brelease approval\b",
    r"\bneeds? (?:the )?user\b",
    r"\bneed(?:s)? human\b",
    r"\bwait(?:ing)? for (?:the )?user\b",
    r"\bconfirm(?:ation)?\b",
    r"\bexplicit human\b",
    r"\bexternal decision\b",
    r"\bpr review\b",
    r"\bcode review\b",
)

DONE_PATTERNS = (
    r"\bqueue is empty\b",
    r"\ball tasks? (?:are )?(?:complete|done)\b",
    r"\bwork (?:is )?complete\b",
    r"\bcompleted successfully\b",
    r"\bnothing left to do\b",
    r"\bdone\b",
    r"\bfinished\b",
)

SELF_RESOLVABLE_PATTERNS = (
    r"\bcan continue\b",
    r"\bcan resolve\b",
    r"\bneeds? another pass\b",
    r"\bretry\b",
    r"\bfix\b",
    r"\bresolve\b",
    r"\bunblock\b",
    r"\bbootstrap\b",
    r"\binstall\b",
    r"\btest\b",
    r"\bverification failed\b",
    r"\breview failed\b",
    r"\brelease failed\b",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".ralph").exists():
            return candidate
    return start


def load_project_facts(repo_root: Path) -> dict[str, Any]:
    path = repo_root / ".ralph/context/project-facts.json"
    if not path.exists():
        return {}
    try:
        return load_json(path)
    except Exception:
        return {}


def load_runtime_contract(repo_root: Path) -> str:
    path = repo_root / ".ralph/runtime-contract.md"
    if not path.exists():
        return ""
    return path.read_text()


def text_matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in patterns)


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return False


def coerce_int(value: Any, default: int = 0) -> int:
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def should_continue(runtime: str, payload: dict[str, Any], project_facts: dict[str, Any], runtime_contract: str) -> tuple[bool, str]:
    stop_hook_config = project_facts.get("orchestrator_stop_hook") or {}
    if not isinstance(stop_hook_config, dict):
        stop_hook_config = {}
    if not stop_hook_config.get("enabled", True):
        return False, "orchestrator stop hook disabled in project facts"

    max_auto_continue_count = coerce_int(stop_hook_config.get("max_auto_continue_count"), 1)
    last_assistant_message = payload.get("last_assistant_message")
    if not isinstance(last_assistant_message, str):
        last_assistant_message = ""
    message = last_assistant_message.strip()
    combined_context = "\n".join(part for part in (message, runtime_contract) if part)

    if runtime in {"codex", "claude"} and coerce_bool(payload.get("stop_hook_active")):
        return False, "auto-continue already consumed for this stop chain"
    if runtime == "cursor" and coerce_int(payload.get("loop_count"), 0) >= max_auto_continue_count:
        return False, "auto-continue already consumed for this stop chain"

    if payload.get("agent_type") not in {None, "", "orchestrator"}:
        return False, "v1 stop hook only applies to the top-level orchestrator"

    if runtime == "cursor":
        status = payload.get("status")
        if status in {"error", "aborted"} and max_auto_continue_count > 0:
            return True, "cursor stop status indicates an interrupted run that merits one autonomous continuation pass"
        if not message:
            return False, "cursor stop payload does not include assistant text, so the conservative policy will not auto-continue a completed stop"

    if text_matches_any(combined_context, HUMAN_GATED_PATTERNS):
        return False, "stop message indicates a true human-gated boundary"
    if message and text_matches_any(message, DONE_PATTERNS) and not text_matches_any(message, SELF_RESOLVABLE_PATTERNS):
        return False, "stop message indicates the orchestrator is already done"
    if message and text_matches_any(message, SELF_RESOLVABLE_PATTERNS):
        return True, "stop message describes a self-resolvable blocker"
    if message and not text_matches_any(message, DONE_PATTERNS):
        return True, "stop message does not look terminal and no explicit human gate was detected"
    return False, "conservative policy found no safe continuation signal"


def render_output(runtime: str, continue_run: bool, detail: str) -> dict[str, Any]:
    if continue_run:
        prompt = f"{DEFAULT_CONTINUATION_PROMPT}\n\nHook rationale: {detail}"
        if runtime == "cursor":
            return {"followup_message": prompt}
        return {"decision": "block", "reason": prompt}

    if runtime == "cursor":
        return {}
    return {
        "continue": False,
        "stopReason": f"Ralph stop-boundary hook respected the stop: {detail}.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Conservative Ralph stop-boundary continuation hook.")
    parser.add_argument("--runtime", required=True, choices=("codex", "claude", "cursor"))
    args = parser.parse_args()

    repo_root = find_repo_root(Path.cwd())
    payload = json.loads(sys.stdin.read() or "{}")
    project_facts = load_project_facts(repo_root)
    runtime_contract = load_runtime_contract(repo_root)
    continue_run, detail = should_continue(args.runtime, payload, project_facts, runtime_contract)
    output = render_output(args.runtime, continue_run, detail)
    if output:
        json.dump(output, sys.stdout)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
