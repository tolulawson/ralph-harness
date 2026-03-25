---
name: ralph-execute
description: Resume an already-installed Ralph harness in the current repository by reading the constitution, runtime contract, policy, workflow state, spec queue, worker claims, latest report, and recent events, then draining the queue until it is complete or a human-gated stop condition occurs.
---

# Ralph Execute

Resume and advance an already-installed Ralph harness in the current repository until the queue is empty, lease ownership must transfer, or a documented human-gated stop condition occurs.

This skill does not install the harness. It assumes the current repository already contains the Ralph harness scaffold.

In this source repository, the root `.ralph/`, `tasks/`, and `specs/` paths are dogfood runtime artifacts. The shipped scaffold under `src/` stays cleaner than the root runtime, and target runtime records are generated after installation or first run.

## Use When

- The current repository already has the Ralph harness installed.
- You want an explicit named way to resume the harness.
- You want the active coding agent to read the current queue state and advance the next orchestrator step or role handoff.

## Required Inputs

- `AGENTS.md` or `CLAUDE.md`
- `.ralph/constitution.md`
- `.ralph/runtime-contract.md`
- `.ralph/policy/runtime-overrides.md`
- `.ralph/policy/project-policy.md`
- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/state/worker-claims.json`

## Runtime Read Order

1. `AGENTS.md` or `CLAUDE.md`
2. `.ralph/constitution.md`
3. `.ralph/runtime-contract.md`
4. `.ralph/policy/runtime-overrides.md`
5. `.ralph/policy/project-policy.md`
6. `.ralph/state/workflow-state.json`
7. `.ralph/state/spec-queue.json`
8. `.ralph/state/worker-claims.json`
9. the file at `last_report_path`
10. admitted or active spec artifacts under `specs/<spec-id>-<slug>/`
11. a recent tail of `.ralph/logs/events.jsonl`

## Workflow

1. Verify the Ralph harness exists in the current repository.
2. Read the constitution, runtime contract, runtime overrides, project policy, workflow state, spec queue, and worker claims.
3. Treat `workflow-state.json`, `spec-queue.json`, and `task-state.json` as the canonical machine state. Treat `workflow-state.md` and `specs/INDEX.md` as projections only.
4. Run a preflight consistency check before selecting the next role:
   - the runtime must already be on the current multi-spec, lease-capable state shape
   - `.ralph/state/workflow-state.md` must match the canonical JSON projection
   - `specs/INDEX.md` must match the canonical queue projection
   - `tasks.md` and `task-state.json` must agree semantically
   - the lease file, worker claims file, and durable intents file must exist and parse
   - admitted specs must have valid worktrees whose branches match the active queue entries
   - review, verification, release, and completed-task handoffs must not sit on a dirty spec worktree
   - the latest relevant worker report must include `Quality Gate` evidence (`React Effects Audit` and `Deslopify Lite`) before work advances past implementation
   - the latest relevant worker report must include `Commit Evidence` for the checkpoint under handoff before work advances past implementation
5. If preflight fails or the repo is in mixed-version state, stop and route to `$ralph-upgrade` before continuing.
6. Read the latest report and admitted spec artifacts.
7. Read a recent tail of the event log rather than the full history.
8. Determine the next role from current phase, spec status, task lifecycle state, and PR state.
9. Guide the active runtime to use Ralph's lease-plus-claims execution model to:
   - acquire a single-writer lease before mutating canonical shared state
   - append durable intents when another healthy lease-holder is already active
   - honor `depends_on_spec_ids` as hard admission blockers
   - admit bounded normal specs in FIFO order up to `queue_policy.normal_execution_limit`
   - ensure admitted specs have dedicated git worktrees
   - allow bounded same-batch `research` workers only before queue-head planning resumes
   - either dispatch native subagents when the current runtime supports them or expose admitted slots for claim in `.ralph/state/worker-claims.json`
   - preserve the canonical analysis-heavy and delivery-heavy role classification
   - spawn at most one non-research worker per admitted spec at a time
   - wait for completed workers or released claims
   - close completed worker threads before mutating shared state when native subagents were used
   - synchronize validated control-plane artifacts back into the canonical checkout
   - create an interrupt spec automatically for any failing out-of-scope bug
   - pause admitted normal specs at role boundaries and later resume them after the interrupt is released
   - validate outputs
   - update shared state
   - treat `review_failed`, `verification_failed`, and `release_failed` as remediation states rather than terminal stops
   - continue dispatching until the queue is empty, lease ownership must transfer, or a human-gated runtime-contract stop condition occurs
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
- Keep all parallelism bounded to same-batch `research` plus the scheduler's admitted-spec execution window.
- Keep all role configs at full permissions (`danger-full-access`).
- Do not advance review, verification, or release from a report that lacks `Quality Gate` evidence.
- Do not advance review, verification, or release from a dirty spec worktree or a report that lacks checkpoint traceability.
- Use recent events for normal resume; read older logs only if diagnosing a blocker.
- Do not stop after a single handoff unless the runtime contract reaches queue completion, lease transfer, or a human-gated boundary.
- Do not stop merely because review, verification, or release failed; keep routing those failures back through orchestrator-managed remediation unless the report names a human blocker.

## Completion

Stop only when the queue is empty, lease ownership must transfer, or a documented human-gated runtime-contract stop condition occurs. Do not loop indefinitely past the orchestration safety cap; treat that cap as a human review boundary rather than an automatic workflow failure.
