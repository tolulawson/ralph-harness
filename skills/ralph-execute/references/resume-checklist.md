# Ralph Resume Checklist

When resuming the harness:

1. verify the Ralph scaffold exists in the current repo
2. read `AGENTS.md`
3. read `.ralph/constitution.md`
4. read `.ralph/runtime-contract.md`
5. read `.ralph/policy/project-policy.md`
6. read `.ralph/state/workflow-state.json`
7. read `.ralph/state/spec-queue.json`
8. read `.ralph/state/orchestrator-lease.json`
9. tail only a recent window of `.ralph/state/orchestrator-intents.jsonl`
10. read the latest report referenced by `last_report_path`
11. read admitted spec files under `specs/<spec-id>-<slug>/`
12. tail only recent events from `.ralph/logs/events.jsonl`
13. treat `workflow-state.json`, `spec-queue.json`, `orchestrator-lease.json`, and `task-state.json` as canonical machine state
14. verify `workflow-state.md` and `specs/INDEX.md` still match their canonical JSON projections
15. verify admitted spec worktrees still match their queue branches
16. confirm review, verification, and release handoffs are on clean spec worktrees and the latest relevant worker report includes `Commit Evidence`
17. check `active_spec_ids`, `active_interrupt_spec_id`, `resume_spec_stack`, `interruption_state`, durable intents, and lease health before selecting the next spec
18. confirm deprecated compatibility mirrors in `workflow-state.json` still match slot `0` or the most recently dispatched spec when they are present
19. choose the next role from spec status, task lifecycle state, interruption state, dependency state, and PR state
20. keep new user requests inside the durable intent flow; do not bypass scheduler admission or hard dependencies
21. continue orchestrating until the queue is empty or a runtime-contract stop condition occurs
