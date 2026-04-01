# Ralph Resume Checklist

When resuming the harness:

1. verify the Ralph scaffold exists in the current repo
2. read `AGENTS.md` or `CLAUDE.md`
3. read `.ralph/constitution.md`
4. read `.ralph/runtime-contract.md`
5. read `.ralph/policy/runtime-overrides.md`
6. read `.ralph/policy/project-policy.md`
7. read `.ralph/state/workflow-state.json`
8. read `.ralph/state/spec-queue.json`
9. read `.ralph/state/orchestrator-lease.json`
10. read `.ralph/state/worker-claims.json`
11. tail only a recent window of `.ralph/state/orchestrator-intents.jsonl`
12. read the latest report referenced by `last_report_path`
13. read admitted spec files under `specs/<spec-id>-<slug>/`
14. tail only recent events from `.ralph/logs/events.jsonl`
15. treat `workflow-state.json`, `spec-queue.json`, `worker-claims.json`, `orchestrator-lease.json`, and `task-state.json` as canonical machine state
16. verify `workflow-state.md` and `specs/INDEX.md` still match their canonical JSON projections
17. when operating from an admitted spec worktree, resolve shared-state reads and report reads to the canonical checkout directly or through `.ralph/shared/`
18. verify admitted spec worktrees still match their queue branches
19. confirm review, verification, and release handoffs are on clean spec worktrees and the latest relevant worker report includes `Quality Gate` plus `Commit Evidence`
20. check `active_spec_ids`, `active_interrupt_spec_id`, `resume_spec_stack`, `interruption_state`, worker claims, durable intents, and lease health before selecting the next spec
21. confirm deprecated compatibility mirrors in `workflow-state.json` still match one admitted spec when they are present, but do not use them for scheduling
22. choose the next role from spec status, task lifecycle state, interruption state, dependency state, PR state, and any explicit scheduling targets
23. prefer explicit ready targets first, then fill every remaining runnable slot in the bounded admission window before concluding that orchestration should stop
24. keep new user requests inside the durable intent flow; do not bypass scheduler admission or hard dependencies
25. treat `review_failed`, `verification_failed`, and `release_failed` as remediation states and continue orchestrating until the queue is empty, lease ownership must transfer, or a human-gated runtime-contract stop condition occurs
