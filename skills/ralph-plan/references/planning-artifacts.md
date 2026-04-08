# Ralph Planning Artifacts

The standard planning set is:

1. `tasks/prd-<project>.md`
2. `.ralph/state/spec-queue.json`
3. `specs/INDEX.md`
4. `specs/<spec-id>-<slug>/spec.md`
5. `specs/<spec-id>-<slug>/research.md` when research completed for that spec
6. `specs/<spec-id>-<slug>/plan.md`
7. `specs/<spec-id>-<slug>/tasks.md`
8. `specs/<spec-id>-<slug>/task-state.json` when the spec is meant to leave planning execution-ready

Expectations:

- the PRD frames ordered epochs
- the queue records numbered specs plus `depends_on_spec_ids`, without inventing queue-head priority when dependencies are absent
- `spec.md` explains behavior and constraints for one numbered spec
- `plan.md` records the intended implementation approach for that spec
- `tasks.md` is dependency-ordered and execution-ready
- `task-state.json` is the canonical machine-readable task registry for the generated tasks
- public `ralph-plan` should first launch a dedicated planning coordinator subagent, then let that coordinator drive `specify` -> same-batch `research` -> `plan` -> `task-gen` -> `plan-check` when the goal is a direct handoff to execution
- the invoking thread must stay launcher-only; planning must not continue inline on the main thread
- planning should stop before code changes begin
