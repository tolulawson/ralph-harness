# Ralph Runtime Contract

Source of truth for an installed harness:

1. `AGENTS.md` as the Codex loader
2. `.ralph/constitution.md` as the project-specific mission layer
3. `.ralph/runtime-contract.md` as the generic installed-runtime doctrine
4. `.ralph/policy/project-policy.md` as the repo-specific workflow policy
5. `.ralph/state/workflow-state.json` as the canonical runtime state
6. `.ralph/state/spec-queue.json` as the canonical spec queue
7. `.ralph/state/orchestrator-lease.json` as the single-writer lease record
8. `.ralph/state/orchestrator-intents.jsonl` as the durable cross-thread inbox
9. `resume_spec_stack` and `interruption_state` inside workflow state as the interruption-resume context
10. `specs/<spec-key>/task-state.json` as canonical per-spec task lifecycle when it exists
11. `workflow-state.md` and `specs/INDEX.md` as human-readable projections of canonical JSON state
12. `.ralph/reports/` as the role handoff history and checkpoint traceability layer
13. `.ralph/logs/events.jsonl` as the append-only audit trail
