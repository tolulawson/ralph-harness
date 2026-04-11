#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "verify-subagent-isolation-contract: $*" >&2
  exit 1
}

for path in \
  src/.ralph/runtime-contract.md \
  src/.agents/skills/orchestrator/SKILL.md \
  src/.ralph/state/execution-claims.json \
  src/CLAUDE.md \
  src/.claude/agents/orchestrator.md \
  src/.claude/agents/bootstrap.md \
  src/.claude/agents/implement.md \
  src/.claude/agents/review.md \
  src/.claude/agents/verify.md \
  src/.claude/agents/release.md \
  src/.claude/commands/ralph-execute.md \
  src/.claude/commands/ralph-plan.md \
  src/.claude/commands/ralph-prd.md \
  src/.cursor/rules/ralph-core.mdc \
  src/.cursor/rules/ralph-execute.mdc \
  src/.codex/config.toml \
  src/.codex/agents/orchestrator.toml \
  skills/ralph-execute/SKILL.md \
  skills/ralph-plan/SKILL.md \
  skills/ralph-prd/SKILL.md
do
  [[ -f "$path" ]] || fail "missing required file $path"
done

grep -Fq -- '.ralph/state/execution-claims.json' src/.ralph/runtime-contract.md \
  || fail "runtime contract must require the execution claims registry"

grep -Fq -- 'native runtime subagents' src/.ralph/runtime-contract.md \
  || fail "runtime contract must describe native runtime subagents"

grep -Fq -- 'unsupported by the shipped harness' src/.ralph/runtime-contract.md \
  || fail "runtime contract must reject adapters that cannot delegate the full Ralph topology"

grep -Fq -- 'thin and immediately hand off substantive Ralph work to a dedicated subagent' src/.ralph/runtime-contract.md \
  || fail "runtime contract must require thin entry-thread delegation"

grep -Fq -- 'main thread must never continue as the PRD or planning coordinator' src/.ralph/runtime-contract.md \
  || fail "runtime contract must forbid main-thread PRD or planning coordination"

grep -Fq -- 'Child roles must not spawn nested workers' src/.ralph/runtime-contract.md \
  || fail "runtime contract must forbid nested worker fan-out"

grep -Fq -- '.ralph/state/execution-claims.json' src/.agents/skills/orchestrator/SKILL.md \
  || fail "orchestrator skill must mention the execution claims registry"

grep -Fq -- 'native subagents' src/.agents/skills/orchestrator/SKILL.md \
  || fail "orchestrator skill must mention native subagents"

grep -Fq -- 'launcher thread is already done being a launcher' src/.agents/skills/orchestrator/SKILL.md \
  || fail "orchestrator skill must assume launcher-only entry threads"

grep -Fq -- '.ralph/state/execution-claims.json' src/CLAUDE.md \
  || fail "CLAUDE.md must include execution-claims in the read order"

grep -Fq -- 'close that worker thread' src/.agents/skills/orchestrator/SKILL.md \
  || fail "orchestrator skill must close worker threads after wait"

grep -Fq -- 'dedicated orchestrator peer subagent' skills/ralph-execute/SKILL.md \
  || fail "public execute skill must launch a dedicated orchestrator peer subagent"

grep -Fq -- 'dedicated Ralph planning coordinator subagent' skills/ralph-plan/SKILL.md \
  || fail "public plan skill must launch a dedicated planning coordinator subagent"

grep -Fq -- 'must not become Ralph'\''s planning coordinator' skills/ralph-plan/SKILL.md \
  || fail "public plan skill must forbid inline planning on the main thread"

grep -Fq -- 'dedicated `prd` subagent' skills/ralph-prd/SKILL.md \
  || fail "public PRD skill must launch a dedicated PRD subagent"

grep -Fq -- 'dedicated Ralph orchestrator peer subagent' src/.claude/commands/ralph-execute.md \
  || fail "Claude execute command must keep the command thread thin"

grep -Fq -- 'shared scheduler lock' src/.claude/commands/ralph-execute.md \
  || fail "Claude execute command must describe shared scheduler-lock coordination"

grep -Fq -- 'dedicated Ralph planning coordinator subagent' src/.claude/commands/ralph-plan.md \
  || fail "Claude plan command must keep the command thread thin"

grep -Fq -- 'main thread become the planning coordinator' src/.claude/commands/ralph-plan.md \
  || fail "Claude plan command must forbid inline planning on the main thread"

grep -Fq -- 'delegate `specify`' src/.claude/commands/ralph-plan.md \
  || fail "Claude plan command must describe delegated planning roles"

grep -Fq -- 'dedicated Ralph `prd` subagent' src/.claude/commands/ralph-prd.md \
  || fail "Claude PRD command must keep the command thread thin"

grep -Fq -- '.ralph/state/execution-claims.json' src/.claude/agents/orchestrator.md \
  || fail "Claude orchestrator agent must include execution claims in canonical inputs"

grep -Fq -- 'execution-claims registry' src/.cursor/rules/ralph-core.mdc \
  || fail "Cursor core rule must mention the shared Ralph claim contract"

grep -Fq -- 'execution_mode = native_subagent' src/.cursor/rules/ralph-execute.mdc \
  || fail "Cursor execute rule must require native subagent execution claims"

if grep -Fq -- 'finishing session may reconcile its own validated work' src/.cursor/rules/ralph-execute.mdc; then
  fail "Cursor execute rule must keep reconciliation on the orchestrator"
fi

python3 - <<'PY'
import json
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib

config = tomllib.loads(Path("src/.codex/config.toml").read_text())
if not config.get("features", {}).get("multi_agent"):
    raise SystemExit("verify-subagent-isolation-contract: multi_agent must be enabled")

max_depth = config.get("agents", {}).get("max_depth")
if not isinstance(max_depth, int) or max_depth != 3:
    raise SystemExit("verify-subagent-isolation-contract: agents.max_depth must be the integer 3")

targets = {}
for role, entry in (config.get("agents") or {}).items():
    if isinstance(entry, dict) and isinstance(entry.get("config_file"), str):
        targets[role] = Path("src/.codex") / entry["config_file"]

required_roles = {
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
}
missing = sorted(required_roles - set(targets))
if missing:
    raise SystemExit(
        "verify-subagent-isolation-contract: missing managed agent targets: " + ", ".join(missing)
    )

expected_sandbox = {
    "orchestrator": "danger-full-access",
    "plan_check": "danger-full-access",
    "review": "danger-full-access",
    "prd": "danger-full-access",
    "specify": "danger-full-access",
    "research": "danger-full-access",
    "plan": "danger-full-access",
    "task_gen": "danger-full-access",
    "implement": "danger-full-access",
    "bootstrap": "danger-full-access",
    "verify": "danger-full-access",
    "release": "danger-full-access",
}

for role, expected in expected_sandbox.items():
    payload = tomllib.loads(targets[role].read_text())
    actual = payload.get("sandbox_mode")
    if actual != expected:
        raise SystemExit(
            f"verify-subagent-isolation-contract: role {role} must use sandbox_mode={expected!r}, got {actual!r}"
        )

registry = json.loads(Path("src/.ralph/agent-registry.json").read_text())
delegation_by_role = {
    entry["id"]: entry["native_subagent_delegation"]
    for entry in registry["roles"]
}
required_native_roles = set(delegation_by_role)
for role in required_native_roles:
    if delegation_by_role.get(role) is not True:
        raise SystemExit(
            f"verify-subagent-isolation-contract: role {role} must allow native subagent delegation"
        )

for role in sorted(required_native_roles):
    agent_doc = Path("src/.claude/agents") / f"{role}.md"
    if "Native subagent delegation: `allowed`" not in agent_doc.read_text():
        raise SystemExit(
            f"verify-subagent-isolation-contract: generated Claude agent for {role} must advertise native delegation"
        )

PY

echo "verify-subagent-isolation-contract: ok"
