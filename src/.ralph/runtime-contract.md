# Ralph Runtime Contract

This file is the generic installed-runtime doctrine for the Ralph harness.

It defines how an installed target repository should orchestrate worker roles, own shared runtime state, coordinate concurrent user threads, and stop safely while draining a dependency-aware multi-spec queue.

The default operating principle is queue-wide throughput: once orchestration begins, Ralph should keep advancing every runnable spec in bounded parallel when dependencies allow, rather than stopping after a single spec, task, or successful handoff.

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

`AGENTS.md` and `CLAUDE.md` are loader surfaces only. They point the active coding agent at these files.

## Required Runtime Features

- The installed scaffold must ship all supported runtime adapter packs together: Codex, Claude Code, and Cursor local Agent/CLI/IDE surfaces.
- Every supported adapter must support native runtime subagents for substantive Ralph work. Adapters that cannot delegate the full Ralph topology are unsupported by the shipped harness.
- The installed scaffold must also ship repo-local hook surfaces for all supported adapters: `.codex/hooks.json`, `.claude/settings.json`, `.cursor/hooks.json`, and the shared Ralph hook code under `.ralph/hooks/`.
- Public Ralph entrypoints must keep the invoking thread thin and immediately hand off substantive Ralph work to a dedicated subagent instead of doing PRD, planning, research, orchestration, or implementation inline on the entry thread.
- `ralph-execute` must launch exactly one dedicated orchestrator subagent per invocation. `ralph-prd` must launch exactly one dedicated `prd` subagent. `ralph-plan` must launch exactly one dedicated planning coordinator subagent.
- The main thread must never continue as the PRD or planning coordinator after launcher handoff begins. Queue-wide control-plane coordination belongs only to the orchestrator, and adapters that cannot spawn the required `ralph-prd` or `ralph-plan` subagent are unsupported rather than allowed to fall back to inline execution.
- Supported adapters must run the Ralph topology `launcher thread -> dedicated coordinator or orchestrator subagent -> delegated role subagents`.
- Supported adapters must delegate `prd`, `specify`, `research`, `plan`, `task_gen`, `plan_check`, `bootstrap`, `implement`, `review`, `verify`, and `release` to native subagents rather than executing those roles inline on the launching or coordinating thread.
- The orchestrator must fill the admitted-spec execution window with bounded worker subagents rather than collapsing into one claimed role at a time.
- Ralph-managed Codex config must allow exactly one launcher-to-role nesting layer plus one worker layer (`agents.max_depth = 3`), and deeper fan-out remains forbidden.
- The canonical role classification remains:
  - analysis-heavy roles: `research`, `plan_check`, `review`
  - delivery-heavy roles: `prd`, `specify`, `plan`, `task_gen`, `bootstrap`, `implement`, `verify`, `release`
- Child roles must not spawn nested workers beyond the active runtime's Ralph-managed delegation policy.
- The orchestrator may persist only validated worker outputs and reports into shared runtime state; worker chain-of-thought or scratch deliberation must not be copied into shared artifacts.
- `research` may run in bounded parallel only for specs produced or refreshed in the same planning batch.
- At most one non-research worker role may be active per admitted spec at any time.
- When multiple normal specs are dependency-satisfied, the orchestrator should prefer filling the bounded admission window before idling or stopping.
- For supported installed runtimes, native worker spawning is the required execution posture for `bootstrap`, `implement`, `review`, `verify`, and `release`, and the planning coordinator must likewise delegate `specify`, same-batch `research`, `plan`, `task_gen`, and `plan_check`.
- Explicit user-requested scheduling targets should outrank creation order whenever those targets are dependency-satisfied.
- The scheduler must coordinate through a single-writer lease stored in `.ralph/state/orchestrator-lease.json`.
- Cross-runtime worker execution must coordinate through `.ralph/state/worker-claims.json`.
- A healthy held lease blocks concurrent shared-state mutation; expired or malformed held leases must be recovered to `idle` before mutation resumes.
- A healthy held worker claim blocks another runtime from taking the same spec role slot until the claim is released or expires.
- Cross-thread operator requests must be recorded durably in `.ralph/state/orchestrator-intents.jsonl`.
- Admitted specs must execute in dedicated git worktrees under `.ralph/worktrees/`, while the canonical control-plane checkout remains the only shared-state owner.
- Each admitted spec worktree must get a generated `.ralph/shared/` overlay that symlinks shared artifacts back to the canonical checkout for convenience.
- Lease ownership is ephemeral and mutation-scoped rather than resident for one long-lived orchestrator thread. Any eligible runtime session may briefly hold the lease to admit work, reconcile finished work, recover stale claims, or record pause or resume transitions.
- `bootstrap` is a first-class delivery role. A claim must pass `bootstrap` and set `validation_ready = true` before `implement` or any other execution role begins in that session.
- Product files and spec-local implementation artifacts must be authored only from the assigned spec worktree.
- Shared-state reads and writes must resolve to the canonical checkout, either directly or through the generated `.ralph/shared/` overlay. Workers must never rely on worktree-local tracked copies of shared artifacts.
- Hard spec dependencies declared in `depends_on_spec_ids` must be satisfied before a normal spec is admitted.
- Ralph-managed Codex role configs run with `sandbox_mode = "danger-full-access"` for maximum execution latitude.
- Interrupt specs may preempt normal specs when a failing out-of-scope bug is discovered.
- Completed tasks must be handed off through atomic git commits rather than dirty worktree state.
- Handoffs past implementation must include `Quality Gate` evidence in the latest relevant worker report.
- Review, verification, and release failures are remediation signals, not stop conditions.
- Supported runtimes should use the shipped stop-boundary hook so the orchestrator re-checks whether it is truly done or human-blocked before stopping.
- The stop-boundary hook may auto-continue only once per stop chain, only for the top-level orchestrator, and only when the stop is not clearly human-gated.
- No delegated worker role besides the active Ralph coordinator may mutate shared queue state, workflow state, lease state, projections, promoted learnings, or event logs.
- Runtime sessions may mutate `.ralph/state/worker-claims.json` only to acquire, heartbeat, record bootstrap lifecycle, or release their own active claim.
- Direct edits to `.ralph/runtime-contract.md` are scaffold drift and should be moved into `.ralph/policy/runtime-overrides.md`, `.ralph/policy/project-policy.md`, or `.ralph/context/project-facts.json` extension fields such as `canonical_control_plane` and `control_plane_versioning`; upgrade preflight may block if the base contract no longer matches its recorded canonical baseline.
- Ralph-managed runtime skill directories under `.agents/skills/` are scaffold-owned. Project-specific control-plane changes must live in `.ralph/policy/runtime-overrides.md`, `.ralph/policy/project-policy.md`, or a non-managed project skill directory instead of patching a Ralph-managed skill in place.

## Artifact Classes

- Canonical shared control plane:
  - `.ralph/state/`
  - `.ralph/logs/`
  - `.ralph/reports/`
  - `.ralph/context/`
  - `.ralph/policy/`
  - `.ralph/constitution.md`
  - `.ralph/runtime-contract.md`
  - `specs/INDEX.md`
- Scheduler-owned artifacts stored under a spec directory, such as `task-state.json`, remain canonical shared state even when they live under `specs/<spec-key>/`.
- Spec-owned branch artifacts:
  - product source files
  - spec-local implementation artifacts such as `spec.md`, `plan.md`, `research.md`, and optional review or verification summaries
- Project-owned helper skills may live under `.agents/skills/` only when they use a non-managed directory name. Ralph-managed skill directories remain upgrade-owned scaffold content.
- `.ralph/shared/` inside a spec worktree is a generated convenience overlay only. It is not a branch-owned source of truth and must never be committed as replacement content.

## Core Loop

1. read `.ralph/state/workflow-state.json`
2. read `.ralph/policy/runtime-overrides.md`
3. read `.ralph/policy/project-policy.md`
4. read `.ralph/context/project-truths.md`
5. read `.ralph/context/project-facts.json`
6. read `.ralph/context/learning-summary.md`
7. read `.ralph/state/spec-queue.json`
8. read `.ralph/state/orchestrator-lease.json`
9. read `.ralph/state/worker-claims.json`
10. tail only the recent window of `.ralph/state/orchestrator-intents.jsonl`
11. attempt to acquire the single-writer lease only for the current shared-state mutation window
12. if another healthy lease-holder exists, stop after recording or acknowledging the caller's durable intent
13. re-read workflow, queue, lease, claim, and intent state after the lease is held
14. materialize new-spec or scheduling intents into numbered spec queue entries without bypassing hard dependencies
15. determine the admission window:
   - active interrupt spec
   - oldest ready interrupt spec by `created_at`
   - else explicit user-requested normal specs whose dependencies are satisfied, in requested order, up to `queue_policy.normal_execution_limit`
   - then remaining dependency-satisfied normal specs, ordered for fairness by `last_dispatch_at`, then `created_at`, then `spec_id`, until the admission window is full
16. prefer filling every open slot in that admission window with a runnable spec before considering any stop path
17. ensure every admitted spec has a dedicated git worktree, branch, and generated `.ralph/shared/` overlay
18. load admitted spec-local artifacts from the assigned worktrees, but load shared control-plane artifacts only from the canonical checkout or the generated overlay
19. choose the next task for each admitted spec in this order:
   - first `in_progress`
   - else first `paused`
   - else first `ready`
   - else first `awaiting_review`
   - else first `review_failed`
   - else first `awaiting_verification`
   - else first `verification_failed`
   - else first `awaiting_release`
   - else first `release_failed`
   - else advance the spec using explicit release outcomes and completion rules
20. after a PRD-to-spec pass, identify the planning batch whose specs were created or refreshed together
21. if that batch contains specs with valid `spec.md` files and `research_status` needing work, delegate bounded parallel `research` through native subagents and record those workers in `.ralph/state/worker-claims.json`
22. wait for the research batch to finish, close or release the completed research workers, and validate every spec-local `research.md` plus report before mutating shared state
23. outside the batch-scoped research step, decide the next role for each admitted spec from lifecycle state, PR state, dependency status, next action, and bootstrap readiness using this default routing:
   - spec `plan_check_failed` returns to `plan` or `task_gen`, depending on the latest plan-check findings
   - task `ready` or `in_progress` routes to `implement`
   - task `awaiting_review` or `review_failed` routes to `review`
   - task `awaiting_verification` or `verification_failed` routes to `verify`
   - task `awaiting_release` or `release_failed` routes to `release`
24. make each runnable spec role slot visible through `.ralph/state/worker-claims.json` for cross-runtime coordination, but keep one orchestrator responsible for the whole invocation
25. if the next execution role for a spec has not yet passed `bootstrap`, dispatch or claim `bootstrap` first
26. on supported adapters, spawn bounded worker subagents across the full admitted ready set up to the admission window and available worker-thread budget, keeping at most one non-research worker per admitted spec
27. as workers finish, refill freed execution slots from the remaining admitted ready set before considering any stop path
28. record every delegated worker in `.ralph/state/worker-claims.json` with `execution_mode = native_subagent`; do not execute worker roles inline on the orchestrator thread
29. ensure every worker receives one spec, one worktree path, one report path, one execution mode, and one claim heartbeat window
30. wait for completed workers or released claims, and validate outputs from the assigned spec worktrees, including bootstrap evidence, `Quality Gate`, `Commit Evidence`, clean-worktree handoff requirements, and absence of worktree-local shared-control-plane edits
31. classify each release report with one explicit outcome: `pr_created`, `awaiting_review`, `awaiting_merge`, `merge_completed`, `release_failed`, or `human_gate_waiting`
32. if review, verification, or release reports a fixable failure without an explicit human-gated blocker, update the task lifecycle, route the spec back to the next remediation role, and keep draining the queue
33. treat worker outputs as spec-local only; workers release their claims and exit, and the orchestrator alone acquires or renews the lease as needed, mutates canonical shared state directly in the canonical checkout, refreshes projections, and dispatches the next role
34. if a worker failed or blocked on an out-of-scope bug, create a new interrupt spec, freeze new normal admissions, and pause in-flight normal specs at the current role boundary
35. write the orchestrator report
36. append one orchestrator-owned event
37. update shared state and projections
38. after a released interrupt spec completes, pop `resume_spec_stack`, thaw normal admissions, and resume paused specs in ready-set order
39. continue dispatching until execution is complete, lease ownership must transfer, or a human-gated boundary is reached

## Stop Conditions

The orchestrator may stop only when one of these is true:

- the queue is empty
- every admitted spec is blocked on a human-gated issue
- a credential, approval, or external human decision is required
- another healthy lease-holder should take over
- the orchestration safety cap is reached and a human should decide whether to resume with a fresh run

The orchestrator must not stop merely because one worker claim finished, one worker handed off successfully, or the next role is now clear while other runnable admitted work remains.

The default orchestration safety cap is `200` role handoffs in one invocation.

Project facts should also preserve:

- `orchestrator_stop_hook`
- `worktree_bootstrap_commands`
- `bootstrap_env_files`
- `bootstrap_copy_exclude_globs`

`bootstrap_env_files` is an allowlist only. Local dependency, cache, and build artifacts should stay excluded by default; bootstrap should recreate them through commands instead of copying them from another checkout.

Each admitted spec worktree should regenerate `.ralph/shared/` whenever the worktree is created, reused after upgrade, or repaired after drift.

## Shared-State Ownership

The canonical shared control plane lives only in the canonical checkout. Only the active Ralph coordinator may update:

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

`.ralph/state/worker-claims.json` is the only shared coordination file that non-orchestrator runtime sessions may update directly, and only for their own claim lifecycle, bootstrap lifecycle, heartbeat, and release metadata.

Worker roles must not read or write shared artifacts through the tracked copies that happen to exist inside a git worktree checkout. They must resolve shared paths to the canonical checkout directly or use the generated `.ralph/shared/` overlay.

## Worker Ownership

- `research`: `research.md` plus a role-local report authored from the assigned spec worktree
- `bootstrap`: bootstrap-local artifacts plus a `bootstrap.md` report authored from the assigned spec worktree
- `implement`: product files, in-scope spec artifacts, and an `implement.md` report authored from the assigned spec worktree
- `review`: `review.md` and an optional spec review artifact authored from the assigned spec worktree
- `verify`: `verify.md` and an optional spec verification artifact authored from the assigned spec worktree
- `release`: PR or merge artifacts plus a `release.md` report authored from the assigned spec worktree

Worker reports should be recorded in the canonical checkout at `.ralph/reports/<run-id>/<spec-key>/<role>.md`, typically by writing through `.ralph/shared/reports/` from the assigned spec worktree. The orchestrator report remains `.ralph/reports/<run-id>/orchestrator.md`.

## Scheduler Contract

The queue is the durable scheduler state.

Top-level queue fields must include:

- `active_spec_ids`
- `active_interrupt_spec_id`
- `worker_claims_path`
- `queue_policy.normal_execution_limit`

Each spec queue entry must include:

- `depends_on_spec_ids`
- `admission_status`
- `admitted_at`
- `worktree_name`
- `worktree_path`
- `branch_name`
- `base_branch`
- `bootstrap_status`
- `bootstrap_last_claim_id`
- `bootstrap_last_report_path`
- `bootstrap_last_completed_at`
- `slot_status`
- `active_task_id`
- `task_status`
- `assigned_role`
- `active_pr_number`
- `active_pr_url`
- `last_dispatch_at`

`active_spec_id`, `active_spec_key`, `active_task_id`, `task_status`, `assigned_role`, `current_branch`, `active_pr_number`, and `active_pr_url` are compatibility mirrors only. They may reflect one admitted spec for legacy tooling, but `active_spec_ids` is the only authoritative active-spec set and those mirrors must never drive scheduling.

`branch_name`, `worktree_name`, and `worktree_path` must remain unique across specs. Upgrade or migration steps may reassign safely-derivable worktree metadata, but duplicate branch ownership is a repair error.

## Worker Claim Contract

- `.ralph/state/worker-claims.json` is the canonical machine-readable worker claim registry.
- Each claim record must include:
  - `claim_id`
  - `spec_id`
  - `spec_key`
  - `task_id`
  - `role`
  - `runtime`
  - `session_id`
  - `thread_id`
  - `holder`
  - `execution_mode`
  - `worktree_path`
  - `status`
  - `claimed_at`
  - `heartbeat_at`
  - `expires_at`
  - `bootstrap_status`
  - `bootstrap_started_at`
  - `bootstrap_completed_at`
  - `bootstrap_report_path`
  - `validation_ready`
- Valid `runtime` values are `codex`, `claude`, and `cursor`.
- Valid `execution_mode` values are `native_subagent`.
- Healthy claims block another runtime from taking the same spec role slot.
- Expired or malformed claims must be recovered to `released` or `expired` before reassignment.
- Claim acquisition and release may happen without the scheduler lease, but claim records never replace orchestrator ownership of shared queue state.
- Valid `bootstrap_status` values are `required`, `in_progress`, `passed`, and `failed`.
- Any active non-bootstrap claim must already show `bootstrap_status = passed` and `validation_ready = true`.
- Workers release their own claims after writing their role-local outputs; that release does not grant them ownership of shared-state reconciliation.

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
- The scheduler should keep that bounded admission window filled with every runnable spec before concluding that orchestration is done.
- Supported adapters must fill that admission window with delegated worker subagents; inline worker execution is not a supported queue-drain mode.
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
- Release reports must record one explicit outcome: `pr_created`, `awaiting_review`, `awaiting_merge`, `merge_completed`, `release_failed`, or `human_gate_waiting`.
- The orchestrator maps that explicit release outcome into the canonical queue, task, and spec lifecycle state.
- A spec is not `done` until its PR lifecycle is complete according to project policy.
- The release worker records the PR or merge outcome from the assigned spec worktree, and the orchestrator applies the resulting shared-state transition in the canonical checkout.
