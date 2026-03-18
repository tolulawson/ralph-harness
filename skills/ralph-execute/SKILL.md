---
name: ralph-execute
description: Resume an already-installed Ralph harness in the current repository by reading the constitution, runtime contract, policy, workflow state, spec queue, latest report, and recent events, then draining the queue until a documented stop condition occurs.
---

# Ralph Execute

Resume and advance an already-installed Ralph harness in the current repository until the queue is empty or a documented stop condition occurs.

This skill does not install the harness. It assumes the current repository already contains the Ralph harness scaffold.

In this source repository, the root `.ralph/`, `tasks/`, and `specs/` paths are dogfood runtime artifacts. The shipped scaffold under `src/` stays cleaner than the root runtime, and target runtime records are generated after installation or first run.

## Use When

- The current repository already has the Ralph harness installed.
- You want an explicit named way to resume the harness.
- You want Codex to read the current queue state and advance the next orchestrator step or role handoff.

## Required Inputs

- `AGENTS.md`
- `.ralph/constitution.md`
- `.ralph/runtime-contract.md`
- `.ralph/policy/project-policy.md`
- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`

## Runtime Read Order

1. `AGENTS.md`
2. `.ralph/constitution.md`
3. `.ralph/runtime-contract.md`
4. `.ralph/policy/project-policy.md`
5. `.ralph/state/workflow-state.json`
6. `.ralph/state/spec-queue.json`
7. the file at `last_report_path`
8. active spec artifacts under `specs/<spec-id>-<slug>/`
9. a recent tail of `.ralph/logs/events.jsonl`

## Workflow

1. Verify the Ralph harness exists in the current repository.
2. Read the constitution, runtime contract, project policy, workflow state, and spec queue.
3. Treat `workflow-state.json`, `spec-queue.json`, and `task-state.json` as the canonical machine state. Treat `workflow-state.md` and `specs/INDEX.md` as projections only.
4. Run a preflight consistency check before selecting the next role:
   - the runtime must already be on the current interrupt-capable state shape
   - `.ralph/state/workflow-state.md` must match the canonical JSON projection
   - `specs/INDEX.md` must match the canonical queue projection
   - `tasks.md` and `task-state.json` must agree semantically
   - the active git branch must match the active spec branch when a spec is active
   - review, verification, release, and completed-task handoffs must not sit on a dirty worktree
   - the latest relevant worker report must include `Commit Evidence` for the checkpoint under handoff before work advances past implementation
5. If preflight fails or the repo is in mixed-version state, stop and route to `$ralph-upgrade` before continuing.
6. Read the latest report and active spec artifacts.
7. Read a recent tail of the event log rather than the full history.
8. Determine the next role from current phase, spec status, task lifecycle state, and PR state.
9. Guide Codex to use built-in multi-agent orchestration to:
   - allow bounded same-batch `research` workers only before queue-head planning resumes
   - spawn workers with `fork_context = true` to isolate worker context from orchestrator context
   - map analysis-heavy roles to `agent_type = "explorer"` and delivery-heavy roles to `agent_type = "worker"`
   - spawn exactly one non-research worker role at a time
   - wait for the worker to finish
   - close completed worker threads before mutating shared state
   - create an interrupt spec automatically for any failing out-of-scope bug
   - pause the current spec and later resume it after the interrupt is released
   - validate outputs
   - update shared state
   - continue dispatching until a runtime-contract stop condition occurs
10. Stop with a concise summary of:
   - what moved
   - what artifacts changed
   - why execution stopped
   - what the next role and next spec are

## Guardrails

- Do not install or reinstall the scaffold here.
- If the harness files are missing, stop and tell the user to use `$ralph-install`.
- Treat the constitution, runtime contract, policy, workflow state, and spec queue as source of truth.
- Do not continue execution from stale projections or mixed-version runtime state.
- Keep all parallelism bounded to same-batch `research`; `plan`, `task-gen`, `plan-check`, `implement`, `review`, `verify`, and `release` remain sequential.
- Keep all role configs at full permissions (`danger-full-access`).
- Do not advance review, verification, or release from a dirty worktree or a report that lacks checkpoint traceability.
- Use recent events for normal resume; read older logs only if diagnosing a blocker.
- Do not stop after a single handoff unless the runtime contract says to stop.

## Completion

Stop only when the queue is empty or a documented runtime-contract stop condition occurs. Do not loop indefinitely past the orchestration safety cap.
