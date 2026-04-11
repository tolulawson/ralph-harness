---
name: ralph-execute
description: Resume an already-installed Ralph harness in the current repository by reading the constitution, runtime contract, policy, workflow state, spec queue, execution claims, latest report, and recent events, then draining the queue until it is complete or a human-gated stop condition occurs.
---

# Ralph Execute

Resume and advance an already-installed Ralph harness in the current repository until the queue is empty, lease ownership must transfer, or a documented human-gated stop condition occurs.

The default operating principle is to keep advancing every runnable spec in bounded parallel when dependencies allow, rather than completing one spec and stopping while other runnable specs remain.

Ralph's shipped adapters are Codex, Claude, and Cursor, and all three are expected to support the full delegated topology `launcher thread -> dedicated orchestrator subagent -> delegated role subagents`. Inline worker fallback is not part of the shipped contract.

This public entrypoint is a thin launcher. It should keep the invoking thread focused on Ralph doctrine and immediately hand execution to one dedicated orchestrator peer subagent.

This skill does not install the harness. It assumes the current repository already contains the Ralph harness scaffold.

In this source repository, the shipped scaffold lives under `src/`. Target runtime records are generated after installation or first run rather than copied from repo-root source materials.

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
- `.ralph/state/execution-claims.json`

## Runtime Read Order

1. `AGENTS.md` or `CLAUDE.md`
2. `.ralph/constitution.md`
3. `.ralph/runtime-contract.md`
4. `.ralph/policy/runtime-overrides.md`
5. `.ralph/policy/project-policy.md`
6. `.ralph/state/workflow-state.json`
7. `.ralph/state/spec-queue.json`
8. `.ralph/state/execution-claims.json`
9. the file at `last_report_path`
10. admitted or active spec artifacts under `specs/<spec-id>-<slug>/`
11. a recent tail of `.ralph/logs/events.jsonl`

## Workflow

1. Verify the Ralph harness exists in the current repository.
2. Read the constitution, runtime contract, runtime overrides, project policy, workflow state, spec queue, and execution claims.
3. Immediately spawn a dedicated orchestrator peer subagent with forked context semantics and the canonical Ralph orchestrator config.
4. Keep the invoking thread thin after launch. It may pass the repo path or user request into the orchestrator, wait for completion, and relay the result, but it must not perform orchestration, planning, research, implementation, review, verification, or release inline.
5. Inside the orchestrator subagent, treat `workflow-state.json`, `spec-queue.json`, and `task-state.json` as the canonical machine state. Treat `workflow-state.md` and `specs/INDEX.md` as projections only.
6. Inside the orchestrator subagent, treat the tracked `.ralph/` files that appear inside a spec worktree as checkout artifacts only. Shared-state reads and writes must resolve to the canonical checkout directly or through the generated `.ralph/shared/` overlay.
7. Run a preflight consistency check before selecting the next role:
   - read canonical JSON first and treat `.ralph/state/workflow-state.md` plus `specs/INDEX.md` as derived projections only
   - the runtime must already be on the current multi-spec, lease-capable state shape or clearly require upgrade
   - if `.ralph/state/workflow-state.md` or `specs/INDEX.md` drift from canonical JSON, regenerate them under the lease instead of routing to upgrade
   - the scheduler lock file, execution claims file, and durable intents file must exist and parse
   - the canonical base branch must be resolved in `.ralph/context/project-facts.json` or safely derivable for queued specs
   - `task-state.json` is required for admitted, active, or otherwise execution-ready specs, but planned specs that still need `task-gen` may legitimately lack it
   - if a required `task-state.json` is missing, or `tasks.md` and `task-state.json` disagree semantically, stop and route back to planning or `task-gen` instead of routing to upgrade
   - if an admitted spec is missing its worktree or `.ralph/shared/` overlay and branch ownership is unambiguous, materialize or repair that worktree state under the lease instead of failing preflight
   - admitted specs must have valid worktrees whose branches match the active queue entries after any safe repairs complete
   - admitted spec worktrees must expose a valid `.ralph/shared/` overlay back to the canonical checkout after any safe repairs complete
   - admitted spec worktrees must not carry tracked or untracked edits under canonical shared-control-plane paths
   - active claims must use `execution_mode = native_subagent`; inline compatibility claims are unsupported for Ralph's shipped adapters
   - active non-bootstrap claims must already show `bootstrap_status = passed` and `validation_ready = true`
   - review, verification, release, and completed-task handoffs must not sit on a dirty spec worktree
   - the latest relevant worker report must include `Quality Gate` evidence (`React Effects Audit` and `Deslopify Lite`) before work advances past implementation
   - the latest relevant worker report must include `Commit Evidence` for the checkpoint under handoff before work advances past implementation
8. Classify any preflight issues before continuing:
   - self-heal derived projections, queue mirrors, queue bootstrap summaries, and admitted worktree or overlay drift when ownership is safe and deterministic
   - stop and route to `$ralph-plan` when planning artifacts or `task-state.json` still need to be generated or refreshed
   - stop and route to `$ralph-upgrade` only for actual scaffold drift, mixed-version state, or recorded-baseline mismatch
   - stop and report a hard repair requirement when ownership, branch selection, or lifecycle state is ambiguous enough that Ralph cannot repair it safely
9. Read the latest report and admitted spec artifacts.
10. Read a recent tail of the event log rather than the full history.
11. Determine the next role from current phase, spec status, task lifecycle state, and PR state.
12. Guide the active runtime to use Ralph's queue-lock-plus-claims execution model to:
   - acquire the short-lived global queue write lock only for the current shared-state mutation window
   - use durable intents as the shared inbox for cross-thread requests
   - honor `depends_on_spec_ids` as hard admission blockers
   - admit explicit user-requested ready specs first, then fill the remaining admission window from the ready set up to `queue_policy.normal_execution_limit`
   - ensure admitted specs have dedicated git worktrees plus generated `.ralph/shared/` overlays
   - require `bootstrap` before `implement` or any other execution role begins in a claim that is not yet validation-ready
   - allow bounded same-batch `research` workers only before normal execution resumes across the admitted queue
   - allow multiple orchestrator peers to participate in the same control plane without a permanent scheduler owner
   - for Ralph's shipped adapters, dispatch native worker subagents across the admitted ready set as the required execution posture
   - keep at most one non-research worker per admitted spec and refill freed slots as workers finish
   - record every delegated worker in `.ralph/state/execution-claims.json` with `execution_mode = native_subagent`
   - preserve the canonical analysis-heavy and delivery-heavy role classification
   - route task lifecycle states deterministically: `ready` or `in_progress` -> `implement`, `awaiting_review` or `review_failed` -> `review`, `awaiting_verification` or `verification_failed` -> `verify`, `awaiting_release` or `release_failed` -> `release`
   - classify every release report with one explicit outcome: `pr_created`, `awaiting_review`, `awaiting_merge`, `merge_completed`, `release_failed`, or `human_gate_waiting`
   - wait for completed workers or released claims
   - close completed worker threads before mutating shared state when native subagents were used
   - let workers release their claims and exit after writing role-local outputs
   - update canonical shared state directly in the canonical checkout from the orchestrator instead of copying tracked control-plane files back from the worktree
   - create an interrupt spec automatically for any failing out-of-scope bug
   - pause admitted normal specs at role boundaries and later resume them after the interrupt is released
   - validate outputs
   - update shared state
   - treat `review_failed`, `verification_failed`, and `release_failed` as remediation states rather than terminal stops
   - continue dispatching until the queue is empty, the scheduler lock must be yielded to a healthier peer, or a human-gated runtime-contract stop condition occurs
13. Stop with a concise summary of:
   - what moved
   - what artifacts changed
   - why execution stopped
   - what the next role and next spec are

## Guardrails

- Do not install or reinstall the scaffold here.
- If the harness files are missing, stop and tell the user to use `$ralph-install`.
- Treat the constitution, runtime contract, policy, workflow state, and spec queue as source of truth.
- The invoking thread is a Ralph launcher only. It must not perform orchestration or worker-role duties inline after it has enough context to launch the orchestrator subagent.
- Do not continue execution from mixed-version runtime state or unresolved hard-repair conditions.
- Do not treat stale projections, missing admitted worktrees, or missing `.ralph/shared/` overlays as upgrade blockers when they are safely derivable from canonical queue state.
- Do not route missing or drifted task registries to `$ralph-upgrade`; send those back through planning or `task-gen`.
- Do not rely on tracked worktree copies of shared-control-plane files when a spec worktree is active.
- Keep all parallelism bounded to same-batch `research` plus the scheduler's admitted-spec execution window.
- Require the Ralph launcher plus worker topology: entry thread -> one orchestrator peer subagent -> delegated role subagents.
- Do not accept inline current-session worker execution for Ralph's shipped adapters; if an adapter cannot delegate the full subagent topology, treat it as unsupported instead of falling back.
- Treat `active_spec_ids` as authoritative. Any singular active-spec fields are compatibility mirrors only and must not drive scheduling.
- Keep all role configs at full permissions (`danger-full-access`).
- Do not advance review, verification, or release from a report that lacks `Quality Gate` evidence.
- Do not advance review, verification, or release from a dirty spec worktree or a report that lacks checkpoint traceability.
- Do not let `implement` begin until the current claim has passed `bootstrap` and is validation-ready.
- Use recent events for normal resume; read older logs only if diagnosing a blocker.
- Do not stop after a single spec or handoff unless the runtime contract reaches queue completion, scheduler-lock transfer, or a human-gated boundary.
- Do not stop merely because review, verification, or release failed; keep routing those failures back through orchestrator-managed remediation unless the report names a human blocker.
- If the installed runtime includes the Ralph stop-boundary hook, treat it as a conservative self-check that can recover one safe stop, not as a substitute for reading the queue and runtime state correctly.

## Completion

Stop only when the queue is empty, scheduler-lock transfer is required, or a documented human-gated runtime-contract stop condition occurs. Do not loop indefinitely past the orchestration safety cap; treat that cap as a human review boundary rather than an automatic workflow failure.
