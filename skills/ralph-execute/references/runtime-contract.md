# Ralph Runtime Contract

Source of truth for an installed harness:

1. `AGENTS.md` as the Codex loader
2. `.ralph/constitution.md` as the project-specific mission layer
3. `.ralph/runtime-contract.md` as the generic installed-runtime doctrine
4. `.ralph/policy/project-policy.md` as the repo-specific workflow policy
5. `.ralph/state/workflow-state.json` as the canonical runtime state
6. `.ralph/state/spec-queue.json` as the canonical spec queue
7. `resume_spec_stack` and `interruption_state` inside workflow state as the interruption-resume context
8. `specs/INDEX.md` as the human-readable spec register
9. `.ralph/reports/` as the role handoff history
10. `.ralph/logs/events.jsonl` as the append-only audit trail
