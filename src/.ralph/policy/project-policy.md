# Project Policy

## Runtime

- Runtime: Codex-native multi-agent harness
- Official Codex multi-agent support is required.
- Orchestrator-spawned workers must run with forked context semantics to isolate worker context from orchestrator context.
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

- Scheduling rule: strict FIFO admission by `spec_id`
- Queue unit: numbered spec
- Epochs: grouping layer only
- Normal execution limit: `2`
- Normal-spec execution: bounded admission window with one worker per admitted spec
- hard dependency policy: a spec may not be admitted until every spec in `depends_on_spec_ids` is `released` or `done`
- Bounded planning-time parallelism: allowed only for `research` on specs from the same planning batch
- Automatic preemption: create an interrupt spec for any failing out-of-scope bug
- Interrupt priority: interrupt specs run ahead of normal specs and stay FIFO among themselves by `created_at`
- Resume rule after interruption: pop `resume_spec_stack`, mirror the top item in `resume_spec_id`, and continue the paused spec
- New user-requested specs outside the predetermined queue must be created and scheduled through durable intents; they do not bypass dependencies or admission rules

## Git And PR Policy

- Default flow: one branch per spec
- Branch format: `codex/<spec-key>`
- Optional task branch format: `codex/<spec-key>/<task-id>` when explicitly required
- Admitted specs must execute in dedicated git worktrees under `.ralph/worktrees/`
- The canonical checkout is reserved for scheduler state, projections, logs, lease state, and durable inbox processing
- Atomic commits required before task handoff: yes
- Quality Gate evidence required before review handoff: yes
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
- The parent orchestrator may launch bounded parallel `research` only for specs in the same planning batch.
- The parent orchestrator must spawn workers with `fork_context = true`.
- The parent orchestrator should use `agent_type = "explorer"` for analysis-heavy roles and `agent_type = "worker"` for delivery-heavy roles.
- Child roles must not spawn nested workers.
- The parent orchestrator creates interrupt specs automatically for failing out-of-scope bugs and resumes paused work after release.
- Workers must not update shared workflow state, queue state, lease state, state Markdown, or orchestrator event logs directly.
- Workers execute from their assigned spec worktree and may write spec-local artifacts there, but canonical control-plane updates remain orchestrator-mediated.
- Handoffs past implementation must preserve `Quality Gate` evidence (`React Effects Audit` and `Deslopify Lite`) in the latest relevant report.
- Review and verification should treat the assigned spec branch or PR as the unit under inspection.
- Review should treat missing or failed `Quality Gate`, missing commit evidence, dirty handoffs, or obviously mixed-scope task commits as findings.
