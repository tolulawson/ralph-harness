# Project Policy

## Runtime

- Runtime: Ralph multi-agent runtime
- Supported first-class runtime adapters: Codex, Claude Code, and Cursor local Agent/CLI/IDE surfaces
- Supported adapters must be able to run the full Ralph topology `launcher thread -> dedicated coordinator or orchestrator subagent -> delegated role subagents`. Adapters that cannot delegate substantive Ralph work are unsupported.
- Ralph public entrypoints must treat the invoking thread as a thin launcher only. Substantive Ralph work belongs in dedicated subagents, not inline on the entry thread.
- `ralph-execute` should launch exactly one orchestrator subagent per invocation. Parallel execution comes from worker fan-out across admitted specs, not from spawning multiple orchestrators.
- `ralph-prd` should launch exactly one dedicated `prd` subagent, and `ralph-plan` should launch exactly one planning coordinator subagent that delegates `specify`, same-batch `research`, `plan`, `task-gen`, and `plan-check`.
- Loader surfaces: `AGENTS.md` and `CLAUDE.md`
- Runtime-native adapter packs: `.codex/`, `.claude/`, and `.cursor/`
- Ralph-managed Codex role configs use `sandbox_mode = "danger-full-access"`.
- `ralph-execute` should launch the orchestrator in a dedicated subagent, while `ralph-prd` and `ralph-plan` should launch dedicated role subagents for those entrypoints.
- Harness doctrine: `.ralph/constitution.md`, `.ralph/runtime-contract.md`, and `.ralph/policy/runtime-overrides.md`
- Control plane: repo files plus runtime-native adapter packs
- Canonical shared control plane lives in the canonical checkout; spec worktrees get a generated `.ralph/shared/` overlay for shared reads and canonical report writes
- Repo-local skills: `.agents/skills/*`
- External custom tool server: not required for v1
- Shared-state coordination uses a single-writer lease in `.ralph/state/orchestrator-lease.json`.
- Cross-runtime worker coordination uses `.ralph/state/worker-claims.json`.
- Cross-thread scheduler requests use durable intent intake in `.ralph/state/orchestrator-intents.jsonl`.
- Project-specific runtime additions belong in `.ralph/policy/runtime-overrides.md`, not as direct edits to `.ralph/runtime-contract.md`.

## Queue Policy

- Scheduling rule: explicit-first ready-set admission
- Queue unit: numbered spec
- Epochs: grouping layer only
- Default normal execution limit: derive from the runtime thread budget with one thread reserved for the orchestrator
- Default operational mode: run through all runnable specs until the queue is drained or a documented human gate is reached
- Normal-spec execution: bounded admission window with one worker per admitted spec, and the orchestrator should prefer filling every runnable slot in that window
- For supported adapters, the default posture is native worker fan-out across the admitted window up to the available worker-thread budget. Inline one-role-at-a-time worker execution is not a supported fallback.
- Parallel execution: encouraged for dependency-independent specs within `normal_execution_limit`
- Explicit user-requested specs should be admitted first when they are unblocked
- Remaining ready specs should be chosen by fairness order: `last_dispatch_at`, then `created_at`, then `spec_id`
- hard dependency policy: a spec may not be admitted until every spec in `depends_on_spec_ids` is `released` or `done`
- Bounded planning-time parallelism: allowed only for `research` on specs from the same planning batch
- Automatic preemption: create an interrupt spec for any failing out-of-scope bug
- Interrupt priority: interrupt specs run ahead of normal specs and stay FIFO among themselves by `created_at`
- Resume rule after interruption: pop `resume_spec_stack`, mirror the top item in `resume_spec_id`, and continue the paused spec
- New user-requested specs outside the predetermined queue must be created and scheduled through durable intents; they do not bypass dependencies or admission rules
- `schedule_spec` intents may carry ordered explicit target spec ids so user direction survives lease contention and is honored on the next orchestration pass

## Git And PR Policy

- Default flow: one branch per spec
- Branch prefix: `ralph`
- Branch format: `ralph/<spec-key>`
- Optional task branch format: `ralph/<spec-key>/<task-id>` when explicitly required
- Admitted specs must execute in dedicated git worktrees under `.ralph/worktrees/`
- The canonical checkout is reserved for scheduler state, projections, logs, lease state, and durable inbox processing
- All spec execution must happen from the assigned spec worktree, never from the canonical checkout
- Shared-state reads and writes must resolve to the canonical checkout directly or through `.ralph/shared/`; worktree-local tracked copies of shared-control-plane files must not be used
- Atomic commits required before task handoff: yes
- Quality Gate evidence required before review handoff: yes
- Clean worktree required before review, verification, or release: yes
- Canonical base branch: resolve from `.ralph/context/project-facts.json` and persist it during installation, upgrade, or the next lease-held reconciliation pass
- Direct-to-main: disabled by default
- GitHub PR required before merge: yes
- Review required before merge: yes
- Verification required before merge: yes
- Release reports must record one explicit outcome: `pr_created`, `awaiting_review`, `awaiting_merge`, `merge_completed`, `release_failed`, or `human_gate_waiting`
- Merge required before spec status `done`: yes
- Push after successful release report: allowed

## Verification Policy

- Minimum checks for every workflow change:
  - TOML parses successfully
  - JSON parses successfully
  - JSONL parses successfully
  - required scaffold files exist
  - state Markdown matches the JSON state semantically
  - spec queue JSON and `specs/INDEX.md` agree semantically
  - task-state JSON agrees semantically with `tasks.md` when `task-state.json` exists
  - interruption fields and resume-stack projections agree semantically across queue, workflow state, and spec index
  - research metadata agrees semantically with queue state and role outputs
  - lease file validity and heartbeat freshness are enforced
  - healthy held leases block concurrent shared-state mutation, and stale held leases must be recovered before validation passes
  - durable intent records remain replay-safe and parseable
  - worker-claim records remain replay-safe, parseable, and expiration-aware
  - dependency graphs are acyclic and only target existing specs
  - queue branch and worktree assignments remain unique across specs
  - admitted specs have valid git worktrees and branch alignment
  - admitted specs have a valid `.ralph/shared/` overlay that resolves back to the canonical checkout
  - spec worktrees do not carry tracked or untracked edits under canonical shared-control-plane paths
  - canonical checkout cleanliness rules are enforced separately from spec worktree cleanliness
- Stronger checks may be added by spec-specific tasks.
- Project-specific gate commands should be encoded here rather than hard-coded into the harness loop.

## Logging Policy

- Append exactly one JSON event for each completed role transition.
- Orchestrator reports live in `.ralph/reports/<run-id>/`.
- Spec-owned worker reports live in `.ralph/reports/<run-id>/<spec-key>/`.
- Use recent events for normal resume.
- Use older logs only for blocker diagnosis or audit reconstruction.

## Learning Policy

- Explicit human instructions belong in `.ralph/context/project-truths.md`.
- Candidate implicit learnings append to `.ralph/context/learning-log.jsonl` with evidence and role attribution.
- Promoted stable learnings belong in `.ralph/context/learning-summary.md`.
- Structured project facts belong in `.ralph/context/project-facts.json` only when they actually apply to the target repo.
- Do not invent facts for categories that are not relevant to the project.
- When a learning is uncertain or one-off, keep it in the append-only log instead of promoting it.

## Role Policy

- One primary skill per role run.
- Helper skills are allowlisted by role.
- A role stops when its assigned artifact and report are complete.
- The parent orchestrator updates shared state after validating outputs.
- The parent orchestrator drains the queue until a documented stop condition occurs.
- The parent orchestrator should not stop after a single spec or successful handoff when other admitted or dependency-satisfied specs are still runnable.
- The parent orchestrator should prefer explicit ready targets first, then fill the remaining admission window from the ready set.
- The parent orchestrator may launch bounded parallel `research` only for specs in the same planning batch.
- Supported adapters must delegate every substantive Ralph role through runtime-native subagents. Inline current-session execution of `prd`, `specify`, `research`, `plan`, `task-gen`, `plan-check`, `bootstrap`, `implement`, `review`, `verify`, or `release` is unsupported.
- Public Ralph entry threads must not perform PRD, planning, research, implementation, review, verification, or release inline; they should launch the appropriate dedicated subagent and then wait or summarize only.
- A claimed session must pass `bootstrap` before `implement` or any other execution role begins locally.
- Task lifecycle routing should remain deterministic: `ready` or `in_progress` -> `implement`, `awaiting_review` or `review_failed` -> `review`, `awaiting_verification` or `verification_failed` -> `verify`, `awaiting_release` or `release_failed` -> `release`.
- Child roles must not spawn nested workers beyond the runtime's Ralph-managed delegation policy.
- The parent orchestrator creates interrupt specs automatically for failing out-of-scope bugs and resumes paused work after release.
- `review_failed`, `verification_failed`, and `release_failed` must route back through orchestrator-managed remediation unless the report names an explicit human-gated blocker.
- Workers must not update shared workflow state, queue state, lease state, state Markdown, or orchestrator event logs directly.
- Runtime sessions may update `.ralph/state/worker-claims.json` only to acquire, heartbeat, record bootstrap lifecycle, or release their own worker claim.
- Workers execute from their assigned spec worktree and may write spec-local artifacts there, but canonical control-plane updates remain orchestrator-mediated after the worker releases its claim and exits.
- Workers must use the generated `.ralph/shared/` overlay or an equivalent canonical-path resolver for shared inputs and canonical report writes.
- The orchestrator alone may acquire the lease to reconcile validated worker outputs back into canonical control-plane state.
- Handoffs past implementation must preserve `Quality Gate` evidence (`React Effects Audit` and `Deslopify Lite`) in the latest relevant report.
- Review and verification should treat the assigned spec branch or PR as the unit under inspection.
- Review should treat missing or failed `Quality Gate`, missing commit evidence, dirty handoffs, or obviously mixed-scope task commits as findings.
