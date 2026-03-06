# Ralph Resume Checklist

When resuming the harness:

1. verify the Ralph scaffold exists in the current repo
2. read `AGENTS.md`
3. read `.ralph/constitution.md`
4. read `.ralph/policy/project-policy.md`
5. read `.ralph/state/workflow-state.json`
6. read `.ralph/state/spec-queue.json`
7. read the latest report referenced by `last_report_path`
8. read active spec files under `specs/<spec-id>-<slug>/`
9. tail only recent events from `.ralph/logs/events.jsonl`
10. choose the next role from spec status, task status, and PR state
11. execute exactly one orchestrator step or one handoff cycle
