#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "verify-parallel-research-contract: $*" >&2
  exit 1
}

for path in \
  src/.codex/agents/research.toml \
  src/.codex/agents/plan-check.toml \
  src/.agents/skills/research/SKILL.md \
  src/.agents/skills/plan-check/SKILL.md \
  src/.ralph/templates/research-template.md
do
  [[ -f "$path" ]] || fail "missing required file $path"
done

grep -Fq -- 'bounded parallel `research`' src/.ralph/runtime-contract.md \
  || fail "runtime contract must document bounded parallel research"

grep -Fq -- 'At most one non-research worker role may be active per admitted spec' src/.ralph/runtime-contract.md \
  || fail "runtime contract must enforce one non-research worker per admitted spec"

grep -Fq -- 'planning batch' src/.agents/skills/orchestrator/SKILL.md \
  || fail "orchestrator skill must scope research parallelism to the same planning batch"

grep -Fq -- 'Do not spawn nested workers.' src/.agents/skills/research/SKILL.md \
  || fail "research skill must forbid nested fan-out"

grep -Fq -- 'one-task-at-a-time execution' src/.agents/skills/plan-check/SKILL.md \
  || fail "plan-check skill must stay sequential"

if grep -Eq -- '\[P\]' src/.agents/skills/task-gen/SKILL.md; then
  fail "task-gen skill must not reintroduce stale [P] parallel guidance"
fi

python3 - <<'PY'
import json
from pathlib import Path

queue = json.loads(Path("src/.ralph/templates/spec-queue-template.json").read_text())
task_state = json.loads(Path("src/.ralph/templates/task-state-template.json").read_text())

spec = queue["specs"][0]
required_queue_fields = {
    "research_status",
    "research_artifact_path",
    "research_report_path",
    "research_updated_at",
    "planning_batch_id",
}
missing = sorted(required_queue_fields - set(spec))
if missing:
    raise SystemExit(f"verify-parallel-research-contract: queue template missing fields: {', '.join(missing)}")

task = task_state["tasks"][0]
for field in ("requirement_ids", "verification_commands", "planned_artifacts"):
    if field not in task:
        raise SystemExit(f"verify-parallel-research-contract: task-state template missing `{field}`")
PY

echo "verify-parallel-research-contract: ok"
