# Project Policy

## Runtime

- Runtime: Codex-native multi-agent harness
- Official Codex multi-agent support is required.
- Ralph public entrypoints must treat the invoking thread as a thin launcher only. Substantive Ralph work belongs in dedicated subagents, not inline on the entry thread.
- Orchestrator-spawned workers must run with forked context semantics to isolate worker context from orchestrator context.
- `ralph-execute` should launch the orchestrator in a dedicated subagent, while `ralph-prd` and `ralph-plan` should launch dedicated role subagents for those entrypoints.
- All role configs use `sandbox_mode = "danger-full-access"`.
- Codex loader: `AGENTS.md`
- Harness doctrine: `.ralph/constitution.md`, `.ralph/runtime-contract.md`, and `.ralph/policy/runtime-overrides.md`
- Control plane: repo files plus `.codex/config.toml`
- Repo-local skills: `.agents/skills/*`
- External custom tool server: not required for v1
- Shared-state coordination uses a single-writer lease in `.ralph/state/orchestrator-lease.json`.
- Cross-thread scheduler requests use durable intent intake in `.ralph/state/orchestrator-intents.jsonl`.
- Project-specific runtime additions belong in `.ralph/policy/runtime-overrides.md`, not as direct edits to `.ralph/runtime-contract.md`.

## Queue Policy

- Scheduling rule: explicit-first ready-set admission
- Queue unit: numbered spec
- Epochs: grouping layer only
- Default normal execution limit: derive from the runtime thread budget with one thread reserved for the orchestrator
- Default operational mode: run through all runnable specs until the queue is drained or a documented human gate is reached
- Normal-spec execution: bounded admission window with one worker per admitted spec, and the orchestrator should prefer filling every runnable slot in that window
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
- Branch format: `codex/<spec-key>`
- Optional task branch format: `codex/<spec-key>/<task-id>` when explicitly required
- Admitted specs must execute in dedicated git worktrees under `.ralph/worktrees/`
- The canonical checkout is reserved for scheduler state, projections, logs, lease state, and durable inbox processing
- Atomic commits required before task handoff: yes
- Clean worktree required before review, verification, or release: yes
- Base branch: `main`
- Direct-to-main: disabled by default
- GitHub PR required before merge: yes
- Review required before merge: yes
- Verification required before merge: yes
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
  - dependency graphs are acyclic and only target existing specs
  - queue branch and worktree assignments remain unique across specs
  - admitted specs have valid git worktrees and branch alignment
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
- The parent orchestrator must spawn workers with `fork_context = true`.
- The parent orchestrator should use `agent_type = "explorer"` for analysis-heavy roles and `agent_type = "worker"` for delivery-heavy roles.
- Public Ralph entry threads must not perform PRD, planning, research, implementation, review, verification, or release inline; they should launch the appropriate dedicated subagent and then wait or summarize only.
- Child roles must not spawn nested workers.
- The parent orchestrator creates interrupt specs automatically for failing out-of-scope bugs and resumes paused work after release.
- `review_failed`, `verification_failed`, and `release_failed` must route back through orchestrator-managed remediation unless the report names an explicit human-gated blocker.
- Workers must not update shared workflow state, queue state, lease state, state Markdown, or orchestrator event logs directly.
- Workers execute from their assigned spec worktree and may write spec-local artifacts there, but canonical control-plane updates remain orchestrator-mediated.
- Review and verification should treat the assigned spec branch or PR as the unit under inspection.
- Review should treat missing commit evidence, dirty handoffs, or obviously mixed-scope task commits as findings.
