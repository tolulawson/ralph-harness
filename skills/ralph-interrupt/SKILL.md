---
name: ralph-interrupt
description: Inject a bugfix interrupt into an already-installed Ralph harness by creating a new interrupt spec that preempts the normal queue and resumes paused work after release.
---

# Ralph Interrupt

Create a new interrupt spec in the current repository for a failing out-of-scope bug that should run ahead of the remaining normal queue.

Use this as the public manual entry point when a human identifies a bug that belongs to an earlier spec or no spec at all and wants it fixed before the queue continues.

In this source repository, the root runtime artifacts are dogfood examples. Installed target repos should use their own copied scaffold from `src/` and generate their own runtime records after installation.

## Use When

- The current repository already has the Ralph harness installed.
- A bug has been identified that is outside the currently executing or admitted normal spec's intended scope.
- The bug should preempt the remaining normal queue and be tracked as its own numbered interrupt spec.

## Workflow

1. Verify the Ralph harness exists in the current repository.
2. Read the constitution, runtime contract, runtime overrides, project policy, workflow state, and spec queue.
3. Treat `workflow-state.json`, `spec-queue.json`, and `task-state.json` as canonical. Treat `workflow-state.md` and `specs/INDEX.md` as projections that must be regenerated from machine state.
4. Run a preflight consistency check before seeding any interrupt:
   - current runtime shape must already be interrupt-capable
   - `.ralph/state/workflow-state.md` must match the canonical JSON projection
   - `specs/INDEX.md` must match the canonical queue projection
   - the origin spec `tasks.md` and `task-state.json` must agree semantically
   - `.ralph/state/orchestrator-lease.json` and `.ralph/state/orchestrator-intents.jsonl` must exist and parse
5. If preflight fails or the repo is in mixed-version state, stop and route to `$ralph-upgrade` instead of creating an interrupt.
6. Acquire the single-writer lease before mutating canonical shared state. If another healthy lease-holder is active, append a durable interrupt request to `.ralph/state/orchestrator-intents.jsonl` and stop instead of mutating the queue concurrently.
7. Confirm the bug is out of scope for the currently executing or otherwise affected normal spec.
8. Create a new numbered spec with `kind = interrupt`.
9. Link the interrupt to `origin_spec_key` and `origin_task_id` when they exist, else leave them `null`.
10. Update the full synchronized state set together:
   - pause the origin task in `task-state.json`
   - pause the origin spec in `.ralph/state/spec-queue.json`
   - add the new interrupt queue entry and interrupt metadata
   - freeze new normal admissions and mark any admitted normal slots paused at role boundaries
   - update `active_interrupt_spec_id`, `resume_spec_stack`, `resume_spec_id`, and `interruption_state`
   - refresh deprecated compatibility mirrors in `.ralph/state/workflow-state.json` when applicable
   - preserve worktree metadata so the interrupted specs can resume safely
11. Seed the new interrupt spec artifacts and `task-state.json`.
12. Regenerate `.ralph/state/workflow-state.md` and `specs/INDEX.md` from canonical JSON after the machine state changes.
13. If the bug belongs to an earlier spec, append an entry to `specs/<origin-spec-key>/amendments.md`.
14. Recommend the next public entry point:
   - `$ralph-execute` when the installed harness should immediately run the interrupt spec
   - `$ralph-plan` only when the interrupt spec still needs broader planning before execution

## Outputs

- updated `.ralph/state/spec-queue.json`
- updated `.ralph/state/workflow-state.json`
- updated `.ralph/state/orchestrator-intents.jsonl` when another healthy lease-holder is already active
- updated `.ralph/state/workflow-state.md`
- updated `specs/INDEX.md`
- new `specs/<spec-key>/spec.md`
- new `specs/<spec-key>/plan.md`
- new `specs/<spec-key>/tasks.md`
- new `specs/<spec-key>/task-state.json`
- updated `specs/<origin-spec-key>/amendments.md` when applicable

## Guardrails

- Do not use this for defects that still belong to the current spec's own scope.
- Do not create an interrupt from mixed-version or drifted runtime state.
- Do not mutate canonical shared state while another healthy lease-holder is active.
- Do not rewrite the original spec, plan, or tasks in place as part of the canonical interrupt flow.
- Keep earlier specs historically immutable and record corrected guidance through linked amendments.

## Completion

Stop once the interrupt spec is seeded cleanly and the next recommended entry point is clear.
