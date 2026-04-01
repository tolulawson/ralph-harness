# Ralph Runtime Contract

This file is the generic installed-runtime doctrine for the Ralph harness.

It defines how an installed target repository should orchestrate worker roles, own shared runtime state, coordinate concurrent user threads, and stop safely while draining a dependency-aware multi-spec queue.

This base runtime contract is scaffold-owned. Project-specific runtime extensions belong in `.ralph/policy/runtime-overrides.md` rather than direct edits to this file.

## Runtime Priority

Interpret an installed Ralph harness in this order:

1. `.ralph/constitution.md`
2. this runtime contract
3. `.ralph/policy/runtime-overrides.md`
4. `.ralph/policy/project-policy.md`
5. `.ralph/context/project-truths.md`
6. `.ralph/context/project-facts.json`
7. `.ralph/context/learning-summary.md`
8. `.ralph/state/workflow-state.json`
9. `.ralph/state/spec-queue.json`
10. active spec artifacts and latest role reports

`AGENTS.md` is only the Codex loader that points Codex to these files.

## Required Runtime Features

- Official Codex multi-agent support is required.
- Public Ralph entrypoints must keep the invoking thread thin and immediately hand off substantive Ralph work to a dedicated subagent rather than doing PRD, planning, research, orchestration, or implementation inline on the entry thread.
- `ralph-execute` must launch a dedicated orchestrator subagent. `ralph-prd` and `ralph-plan` must launch dedicated role subagents for those entrypoints.
- The orchestrator must use built-in Codex agent controls such as `spawn_agent` and `wait` rather than narrating delegation without actually delegating.
- The orchestrator must spawn every worker with forked context semantics (`fork_context = true`) so child deliberation stays isolated from the main orchestration context.
- The orchestrator must map analysis-heavy roles (`research`, `plan_check`, `review`) to `agent_type = "explorer"` and delivery-heavy roles (`prd`, `specify`, `plan`, `task_gen`, `implement`, `verify`, `release`) to `agent_type = "worker"`.
- Ralph-managed Codex config must allow exactly one launcher-to-role nesting layer plus one worker layer (`agents.max_depth = 3`), and deeper fan-out remains forbidden.
- Child roles must not spawn nested workers.
- The orchestrator may persist only validated worker outputs and reports into shared runtime state; worker chain-of-thought or scratch deliberation must not be copied into shared artifacts.
- `research` may run in bounded parallel only for specs produced or refreshed in the same planning batch.
- At most one non-research worker role may be active per admitted spec at any time.
- Explicit user-requested scheduling targets should outrank creation order whenever those targets are dependency-satisfied.
- The scheduler must coordinate through a single-writer lease stored in `.ralph/state/orchestrator-lease.json`.
- A healthy held lease blocks concurrent shared-state mutation; expired or malformed held leases must be recovered to `idle` before mutation resumes.
- Cross-thread operator requests must be recorded durably in `.ralph/state/orchestrator-intents.jsonl`.
- Admitted specs must execute in dedicated git worktrees under `.ralph/worktrees/`, while the canonical control-plane checkout remains the only shared-state owner.
- Hard spec dependencies declared in `depends_on_spec_ids` must be satisfied before a normal spec is admitted.
- All role configs run with `sandbox_mode = "danger-full-access"` for maximum execution latitude.
- Interrupt specs may preempt normal specs when a failing out-of-scope bug is discovered.
- Completed tasks must be handed off through atomic git commits rather than dirty worktree state.
- Review, verification, and release failures are remediation signals, not stop conditions.
- No role besides the orchestrator may mutate shared queue state, workflow state, lease state, projections, promoted learnings, or event logs.
- Direct edits to `.ralph/runtime-contract.md` are scaffold drift and should be moved into `.ralph/policy/runtime-overrides.md`; upgrade preflight may block if the base contract no longer matches its recorded canonical baseline.

## Core Loop

1. read `.ralph/state/workflow-state.json`
2. read `.ralph/policy/runtime-overrides.md`
3. read `.ralph/policy/project-policy.md`
4. read `.ralph/context/project-truths.md`
5. read `.ralph/context/project-facts.json`
6. read `.ralph/context/learning-summary.md`
7. read `.ralph/state/spec-queue.json`
8. read `.ralph/state/orchestrator-lease.json`
9. tail only the recent window of `.ralph/state/orchestrator-intents.jsonl`
10. attempt to acquire or renew the single-writer lease before mutating canonical shared state
11. if another healthy lease-holder exists, stop after recording or acknowledging the caller's durable intent
12. re-read workflow, queue, lease, and intent state after the lease is held
13. materialize new-spec or scheduling intents into numbered spec queue entries without bypassing hard dependencies
14. determine the admission window:
   - active interrupt spec
   - oldest ready interrupt spec by `created_at`
   - else explicit user-requested normal specs whose dependencies are satisfied, in requested order, up to `queue_policy.normal_execution_limit`
   - then remaining dependency-satisfied normal specs, ordered for fairness by `last_dispatch_at`, then `created_at`, then `spec_id`, until the admission window is full
15. ensure every admitted spec has a dedicated git worktree and branch
16. load only the admitted spec artifacts, `task-state.json`, and the latest relevant reports
17. choose the next task for each admitted spec in this order:
   - first `in_progress`
   - else first `paused`
   - else first `ready`
   - else first `review_failed`
   - else first `verification_failed`
   - else first `plan_check_failed`
   - else advance the spec toward PR, merge, or completion
18. after a PRD-to-spec pass, identify the planning batch whose specs were created or refreshed together
19. if that batch contains specs with valid `spec.md` files and `research_status` needing work, spawn bounded parallel `research` workers only for those specs with `fork_context = true` and `agent_type = "explorer"`
20. wait for the research batch to finish, close the completed research workers, and validate every spec-local `research.md` plus report before mutating shared state
21. outside the batch-scoped research step, decide the next role for each admitted spec from lifecycle state, PR state, dependency status, and next action
22. spawn bounded non-research workers only for admitted specs that do not already have a worker in flight
23. assign each worker a single spec, a single worktree path, a single report path, `fork_context = true`, and the role-appropriate `agent_type`
24. wait for completed workers, close their worker threads, and validate outputs from the assigned spec worktrees
25. synchronize validated control-plane artifacts from worker worktrees back into the canonical checkout before updating shared state
26. if review, verification, or release reports a fixable failure without an explicit human-gated blocker, update the task lifecycle, route the spec back to the next remediation role, and keep draining the queue
27. if a worker failed or blocked on an out-of-scope bug, create a new interrupt spec, freeze new normal admissions, and pause in-flight normal specs at the current role boundary
28. write the orchestrator report
29. append one orchestrator-owned event
30. update shared state and projections
31. after a released interrupt spec completes, pop `resume_spec_stack`, thaw normal admissions, and resume paused specs in ready-set order
32. continue dispatching until execution is complete, lease ownership must transfer, or a human-gated boundary is reached

## Stop Conditions

The orchestrator may stop only when one of these is true:

- the queue is empty
- every admitted spec is blocked on a human-gated issue
- a credential, approval, or external human decision is required
- another healthy lease-holder should take over
- the orchestration safety cap is reached and a human should decide whether to resume with a fresh run

The default orchestration safety cap is `200` role handoffs in one invocation.

## Shared-State Ownership

Only the orchestrator may update:

- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/state/orchestrator-lease.json`
- `.ralph/state/orchestrator-intents.jsonl` once intents are drained or acknowledged
- `.ralph/state/workflow-state.md`
- `.ralph/logs/events.jsonl`
- `specs/INDEX.md`
- lifecycle transitions inside `specs/<spec-id>-<slug>/task-state.json`
- promoted learning summaries or truths
- `specs/<origin-spec-key>/amendments.md`

Worker roles must not silently mutate shared queue state or append orchestrator events.

## Worker Ownership

- `research`: `research.md` plus role-local report in the assigned spec worktree
- `implement`: product files, in-scope spec artifacts, and `implement.md` in the assigned spec worktree
- `review`: `review.md` and optional spec review artifact in the assigned spec worktree
- `verify`: `verify.md` and optional spec verification artifact in the assigned spec worktree
- `release`: PR or merge artifacts plus `release.md` in the assigned spec worktree

Worker reports should be recorded at `.ralph/reports/<run-id>/<spec-key>/<role>.md`. The orchestrator report remains `.ralph/reports/<run-id>/orchestrator.md`.

## Scheduler Contract

The queue is the durable scheduler state.

Top-level queue fields must include:

- `active_spec_ids`
- `active_interrupt_spec_id`
- `queue_policy.normal_execution_limit`

Each spec queue entry must include:

- `depends_on_spec_ids`
- `admission_status`
- `admitted_at`
- `worktree_name`
- `worktree_path`
- `slot_status`
- `active_task_id`
- `task_status`
- `assigned_role`
- `active_pr_number`
- `active_pr_url`
- `last_dispatch_at`

`active_spec_id`, `active_spec_key`, `active_task_id`, `task_status`, `assigned_role`, `current_branch`, `active_pr_number`, and `active_pr_url` remain deprecated compatibility mirrors for one release. They may reflect one admitted spec for legacy tooling, but `active_spec_ids` is the only authoritative active-spec set and those mirrors must never drive scheduling.

`branch_name`, `worktree_name`, and `worktree_path` must remain unique across specs. Upgrade or migration steps may reassign safely-derivable worktree metadata, but duplicate branch ownership is a repair error.

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
- When an interrupt is admitted, freeze new normal admissions immediately and let in-flight normal workers stop only at role boundaries before pause is recorded.

## Resume Contract

- `resume_spec_stack` is the canonical nested interruption stack.
- `resume_spec_id` mirrors the top paused spec for compatibility and quick inspection.
- Each stack entry should retain enough context to restore the paused spec and paused task, including previous status, branch, worktree path, and report pointers when relevant.

## Event Contract

Each orchestrator-written event must record enough provenance to reconstruct delegation, including:

- the completed worker role
- the worker report path
- the active spec and task
- the resulting next role or stop reason
- the orchestrator run identifier

## Queue Policy

- Explicit-first ready-set admission is the default rule for normal specs.
- Interrupt specs preempt normal specs when they exist.
- Scheduling intents may name one or more target spec ids; when those specs are dependency-satisfied, Ralph should honor the requested order before admitting other ready normal specs.
- When no explicit target is waiting, remaining ready normal specs should be admitted by fairness order: `last_dispatch_at`, then `created_at`, then `spec_id`.
- The default `queue_policy.normal_execution_limit` should be derived from the active runtime thread budget, reserving one thread for the orchestrator.
- Normal specs may run concurrently only inside the bounded admission window.
- Hard dependencies block admission until every required spec is `released` or `done`.
- Later ready specs may not bypass an earlier eligible spec in admission order.
- Parallel research may improve later spec readiness but must never let a later spec bypass an earlier spec in normal admission.
- Research batches are limited to specs produced or refreshed together by one orchestrator-led planning pass.

## Git And PR Policy

- Each admitted spec must have one dedicated git worktree plus one branch per spec.
- Each completed task must end with at least one atomic commit before handoff.
- Multiple commits inside one task are allowed only when each commit is a coherent checkpoint within that same task.
- Git SHAs and commit ranges belong in role reports and git history, not in canonical workflow JSON.
- Review, verification, and release may not advance from a dirty spec worktree when the active task has already been handed off; a clean worktree is required at those handoff boundaries.
- Review and verification must pass before release completes.
- A spec is not `done` until its PR lifecycle is complete according to project policy.
- The release worker records the PR or merge outcome from the assigned spec worktree, and the orchestrator applies the resulting shared-state transition in the canonical checkout.
