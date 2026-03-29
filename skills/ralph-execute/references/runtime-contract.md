# Ralph Runtime Contract

Source of truth for an installed harness:

1. `AGENTS.md` or `CLAUDE.md` as the Ralph loader surface
2. `.ralph/constitution.md` as the project-specific mission layer
3. `.ralph/runtime-contract.md` as the generic installed-runtime doctrine
4. `.ralph/policy/runtime-overrides.md` as the preserved project-owned runtime extension layer
5. `.ralph/policy/project-policy.md` as the repo-specific workflow policy
6. `.ralph/state/workflow-state.json` as the canonical runtime state
7. `.ralph/state/spec-queue.json` as the canonical spec queue
8. `.ralph/state/orchestrator-lease.json` as the single-writer lease record
9. `.ralph/state/orchestrator-intents.jsonl` as the durable cross-thread inbox
10. `resume_spec_stack` and `interruption_state` inside workflow state as the interruption-resume context
11. `specs/<spec-key>/task-state.json` as canonical per-spec task lifecycle when it exists
12. `workflow-state.md` and `specs/INDEX.md` as human-readable projections of canonical JSON state
13. `.ralph/reports/` as the role handoff history and checkpoint traceability layer
14. `.ralph/logs/events.jsonl` as the append-only audit trail
15. `.ralph/shared/` inside an admitted spec worktree as a generated convenience overlay back to the canonical shared control plane, never as a branch-owned source of truth

Shared-state reads and writes must resolve to the canonical checkout directly or through `.ralph/shared/`. Tracked shared-control-plane copies inside a spec worktree are checkout artifacts only, not authoritative runtime state.
