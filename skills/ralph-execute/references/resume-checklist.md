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
9. read `.ralph/state/scheduler-lock.json`
10. read `.ralph/state/execution-claims.json`
11. tail only a recent window of `.ralph/state/scheduler-intents.jsonl`
12. read the latest report referenced by `last_report_path`
13. read admitted spec files under `specs/<spec-id>-<slug>/`
14. tail only recent events from `.ralph/logs/events.jsonl`
15. treat `workflow-state.json`, `spec-queue.json`, `execution-claims.json`, `scheduler-lock.json`, and `task-state.json` as canonical machine state
16. verify `workflow-state.md` and `specs/INDEX.md` still match their canonical JSON projections
17. when operating from an admitted spec worktree, resolve shared-state reads and report reads to the canonical checkout directly or through `.ralph/shared/`
18. verify admitted spec worktrees still match their queue branches
19. confirm review, verification, and release handoffs are on clean spec worktrees and the latest relevant worker report includes `Quality Gate` plus `Commit Evidence`
20. check `active_spec_ids`, `active_interrupt_spec_id`, `resume_spec_stack`, `interruption_state`, execution claims, durable intents, and scheduler-lock health before selecting the next spec
21. confirm deprecated compatibility mirrors in `workflow-state.json` still match one admitted spec when they are present, but do not use them for scheduling
22. choose the next role from spec status, task lifecycle state, interruption state, dependency state, PR state, and any explicit scheduling targets
23. route task lifecycle states deterministically: `ready` or `in_progress` -> `implement`, `awaiting_review` or `review_failed` -> `review`, `awaiting_verification` or `verification_failed` -> `verify`, `awaiting_release` or `release_failed` -> `release`
24. classify every release report with one explicit outcome: `pr_created`, `awaiting_review`, `awaiting_merge`, `merge_completed`, `release_failed`, or `human_gate_waiting`
25. prefer explicit ready targets first, then fill every remaining runnable slot in the bounded admission window before concluding that orchestration should stop
26. record delegated workers in `.ralph/state/execution-claims.json` with `execution_mode = native_subagent`; do not execute worker roles inline on supported adapters
27. after a worker finishes, let it release its claim and exit, then let any orchestrator peer reacquire the scheduler lock as needed, validate outputs, update shared state, and dispatch the next role
28. keep new user requests inside the durable intent flow; do not bypass scheduler admission or hard dependencies
29. treat `review_failed`, `verification_failed`, and `release_failed` as remediation states and continue orchestrating until the queue is empty, lease ownership must transfer, or a human-gated runtime-contract stop condition occurs
