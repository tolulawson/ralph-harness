# Ralph Runtime Contract

This file is the generic installed-runtime doctrine for the Ralph harness.

It defines how an installed target repository should orchestrate worker roles, own shared runtime state, and stop safely while draining the queue.

## Runtime Priority

Interpret an installed Ralph harness in this order:

1. `.ralph/constitution.md`
2. this runtime contract
3. `.ralph/policy/project-policy.md`
4. `.ralph/context/project-truths.md`
5. `.ralph/context/project-facts.json`
6. `.ralph/context/learning-summary.md`
7. `.ralph/state/workflow-state.json`
8. `.ralph/state/spec-queue.json`
9. active spec artifacts and latest role reports

`AGENTS.md` is only the Codex loader that points Codex to these files.

## Required Runtime Features

- Official Codex multi-agent support is required.
- The orchestrator must use built-in Codex agent controls such as `spawn_agent` and `wait` rather than narrating delegation without actually delegating.
- The orchestrator must spawn every worker with forked context semantics (`fork_context = true`) so child deliberation stays isolated from the main orchestration context.
- The orchestrator must map analysis-heavy roles (`research`, `plan_check`, `review`) to `agent_type = "explorer"` and delivery-heavy roles (`prd`, `specify`, `plan`, `task_gen`, `implement`, `verify`, `release`) to `agent_type = "worker"`.
- Child roles must not spawn nested workers.
- The orchestrator may persist only validated worker outputs and reports into shared runtime state; worker chain-of-thought or scratch deliberation must not be copied into shared artifacts.
- `research` may run in bounded parallel only for specs produced or refreshed in the same planning batch.
- Exactly one non-research worker role may be active at a time for normal execution.
- All role configs run with `sandbox_mode = "danger-full-access"` for maximum execution latitude.
- Interrupt specs may preempt normal specs when a failing out-of-scope bug is discovered.
- Completed tasks must be handed off through atomic git commits rather than dirty worktree state.
- No role besides the orchestrator may mutate shared queue state, workflow state, projections, promoted learnings, or event logs.

## Core Loop

1. read `.ralph/state/workflow-state.json`
2. read `.ralph/policy/project-policy.md`
3. read `.ralph/context/project-truths.md`
4. read `.ralph/context/project-facts.json`
5. read `.ralph/context/learning-summary.md`
6. read `.ralph/state/spec-queue.json`
7. determine the active spec or activate the oldest ready spec in FIFO order
8. read the latest report referenced by `last_report_path`
9. read the active spec artifacts, including `tasks.md` and `task-state.json` when present
10. tail only the recent event window
11. choose the next task in this order:
   - first `in_progress`
   - else first `paused`
   - else first `ready`
   - else first `review_failed`
   - else first `verification_failed`
   - else advance the spec toward PR, merge, or completion
12. choose the next spec in this order:
   - active interrupt spec
   - oldest ready interrupt spec by `created_at`
   - active normal spec
   - oldest ready normal spec in FIFO order
13. after a PRD-to-spec pass, identify the planning batch whose specs were created or refreshed together
14. if that batch contains specs with valid `spec.md` files and `research_status` needing work, spawn bounded parallel `research` workers only for those specs with `fork_context = true` and `agent_type = "explorer"`
15. wait for the research batch to finish, close the completed research workers, and validate every spec-local `research.md` plus report before mutating shared state
16. outside the batch-scoped research step, decide the next role from spec status, task lifecycle state, PR state, and next action
17. spawn exactly one non-research worker role with bounded inputs, a required report path, `fork_context = true`, and the role-appropriate `agent_type`
18. wait for that worker to finish and close the completed worker thread before further orchestration
19. validate the worker outputs, including required commit evidence and any clean-worktree guardrails at role boundaries
20. if the worker failed or blocked on an out-of-scope bug, create a new interrupt spec, pause the current spec, and push paused context onto `resume_spec_stack`
21. write the orchestrator report
22. append one orchestrator-owned event
23. update shared state and projections
24. after a released interrupt spec completes, pop `resume_spec_stack` and resume the paused spec
25. continue dispatching until a stop condition occurs

## Stop Conditions

The orchestrator may stop only when one of these is true:

- the queue is empty
- the active spec or task is blocked
- review failed
- verification failed
- release failed
- a credential, approval, or external human decision is required
- the orchestration safety cap is reached

The default orchestration safety cap is `200` role handoffs in one invocation.

## Shared-State Ownership

Only the orchestrator may update:

- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/state/workflow-state.md`
- `.ralph/logs/events.jsonl`
- `specs/INDEX.md`
- lifecycle transitions inside `specs/<spec-id>-<slug>/task-state.json`
- promoted learning summaries or truths
- `specs/<origin-spec-key>/amendments.md`

Worker roles must not silently mutate shared queue state or append orchestrator events.

## Worker Ownership

- `research`: `research.md` plus role-local report
- `implement`: product files, in-scope spec artifacts, `implement.md`
- `review`: `review.md` and optional spec review artifact
- `verify`: `verify.md` and optional spec verification artifact
- `release`: PR/merge artifacts plus `release.md`

## Task Lifecycle Contract

Each numbered spec should maintain:

- `tasks.md` as the human-readable task projection
- `task-state.json` as the canonical machine-readable task lifecycle registry
- `research.md` as the spec-local implementation research artifact when research has been completed for that spec

Task generation seeds `task-state.json`. After that, the orchestrator owns lifecycle transitions based on worker reports.

Each task record in `task-state.json` should include:

- `task_id`
- `status`
- `last_role`
- `last_report_path`
- `updated_at`
- `requirement_ids`
- `verification_commands`
- optional `blocked_reason`
- optional `review_result`
- optional `verification_result`
- optional `planned_artifacts`

`paused` is the canonical task status for an interrupted task that should later resume.

Each spec queue entry should also track research preparation state:

- `research_status`
- `research_artifact_path`
- `research_report_path`
- `research_updated_at`
- `planning_batch_id`

`active_spec_id` still names the execution head only. Research metadata is queue-visible preparation state, not execution ownership.

## Interrupt Spec Contract

- `kind = "interrupt"` marks a spec that preempts normal queue execution.
- Interrupt specs always take the next numeric `spec_id`; they are not renumbered into the historical queue.
- Interrupt specs should include:
  - `origin_spec_key` when the bug belongs to an earlier spec, else `null`
  - `origin_task_id` when the bug is traceable to a prior task, else `null`
  - `triggered_by_role`
  - `trigger_report_path`
  - `trigger_summary`
- If `origin_spec_key` is present, use that spec's `epoch_id`; otherwise reuse the currently active epoch.
- Earlier spec, plan, and task artifacts remain immutable; corrective guidance is recorded in `specs/<origin-spec-key>/amendments.md`.

## Resume Contract

- `resume_spec_stack` is the canonical nested interruption stack.
- `resume_spec_id` mirrors the top paused spec for compatibility and quick inspection.
- Each stack entry should retain enough context to restore the paused spec and paused task, including previous status, branch, and report pointers when relevant.

## Event Contract

Each orchestrator-written event must record enough provenance to reconstruct delegation, including:

- the completed worker role
- the worker report path
- the active spec and task
- the resulting next role or stop reason
- the orchestrator run identifier

## Queue Policy

- Strict FIFO is the default rule.
- Interrupt specs preempt normal specs when they exist.
- Only one normal spec may be active at a time.
- Later ready specs may not start while an earlier ready spec remains unfinished.
- Parallelism is forbidden for all roles except batch-scoped `research`.
- Parallel research may improve later spec readiness but must never let a later spec bypass an earlier spec in execution.
- Research batches are limited to specs produced or refreshed together by one orchestrator-led planning pass.

## Git And PR Policy

- Each completed task must end with at least one atomic commit before handoff.
- Multiple commits inside one task are allowed only when each commit is a coherent checkpoint within that same task.
- Git SHAs and commit ranges belong in role reports and git history, not in canonical workflow JSON.
- Review, verification, and release may not advance from a dirty worktree when the active task has already been handed off; a clean worktree is required at those handoff boundaries.
- Review and verification must pass before release completes.
- A spec is not `done` until its PR lifecycle is complete according to project policy.
- The release worker records the PR or merge outcome, and the orchestrator applies the resulting shared-state transition.
