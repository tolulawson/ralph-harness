# Project Policy

## Runtime

- Runtime: Codex-native multi-agent harness
- Official Codex multi-agent support is required.
- Codex loader: `AGENTS.md`
- Harness doctrine: `.ralph/constitution.md` plus `.ralph/runtime-contract.md`
- Control plane: repo files plus `.codex/config.toml`
- Repo-local skills: `.agents/skills/*`
- External custom tool server: not required for v1

## Queue Policy

- Scheduling rule: strict FIFO by `spec_id`
- Queue unit: numbered spec
- Epochs: grouping layer only
- Automatic preemption: create an interrupt spec for any failing out-of-scope bug
- Interrupt priority: interrupt specs run ahead of normal specs and stay FIFO among themselves by `created_at`
- Resume rule after interruption: pop `resume_spec_stack`, mirror the top item in `resume_spec_id`, and continue the paused spec

## Git And PR Policy

- Default flow: one branch per spec
- Branch format: `codex/<spec-key>`
- Optional task branch format: `codex/<spec-key>/<task-id>` when explicitly required
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
- Stronger checks may be added by spec-specific tasks.
- Project-specific gate commands should be encoded here rather than hard-coded into the harness loop.

## Logging Policy

- Append exactly one JSON event for each completed role transition.
- Reports live in `.ralph/reports/<run-id>/`.
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
- The parent orchestrator creates interrupt specs automatically for failing out-of-scope bugs and resumes paused work after release.
- Workers must not update shared workflow state, queue state, state Markdown, or orchestrator event logs directly.
- Review and verification should treat the active spec branch or PR as the unit under inspection.
