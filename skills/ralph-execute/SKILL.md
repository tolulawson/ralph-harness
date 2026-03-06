---
name: ralph-execute
description: Resume an already-installed Ralph harness in the current repository by reading the constitution, policy, workflow state, spec queue, latest report, and recent events, then guiding Codex through the next orchestrator step or handoff cycle.
---

# Ralph Execute

Resume and advance an already-installed Ralph harness in the current repository.

This skill does not install the harness. It assumes the current repository already contains the Ralph harness scaffold.

In this source repository, the root `.ralph/`, `tasks/`, and `specs/` paths are dogfood runtime artifacts. Target repos should reach the same shape after installing from `src/`.

## Use When

- The current repository already has the Ralph harness installed.
- You want an explicit named way to resume the harness.
- You want Codex to read the current queue state and advance the next orchestrator step or role handoff.

## Required Inputs

- `AGENTS.md`
- `.ralph/constitution.md`
- `.ralph/policy/project-policy.md`
- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`

## Runtime Read Order

1. `AGENTS.md`
2. `.ralph/constitution.md`
3. `.ralph/policy/project-policy.md`
4. `.ralph/state/workflow-state.json`
5. `.ralph/state/spec-queue.json`
6. the file at `last_report_path`
7. active spec artifacts under `specs/<spec-id>-<slug>/`
8. a recent tail of `.ralph/logs/events.jsonl`

## Workflow

1. Verify the Ralph harness exists in the current repository.
2. Read the constitution, project policy, workflow state, and spec queue.
3. Read the latest report and active spec artifacts.
4. Read a recent tail of the event log rather than the full history.
5. Determine the next role from current phase, spec status, task status, and PR state.
6. Guide Codex to perform either:
   - one orchestrator step, or
   - one full role handoff cycle
   depending on what the current state requires.
7. Stop with a concise summary of:
   - what moved
   - what artifacts changed
   - what the next role and next spec are

## Guardrails

- Do not install or reinstall the scaffold here.
- If the harness files are missing, stop and tell the user to use `$ralph-install`.
- Treat the constitution, policy, workflow state, and spec queue as source of truth.
- Use recent events for normal resume; read older logs only if diagnosing a blocker.

## Completion

Stop after one explicit orchestration step or one full handoff cycle. Do not keep looping indefinitely in a single invocation.
