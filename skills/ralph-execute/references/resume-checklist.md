# Ralph Resume Checklist

When resuming the harness:

1. verify the Ralph scaffold exists in the current repo
2. read `AGENTS.md`
3. read `.ralph/constitution.md`
4. read `.ralph/runtime-contract.md`
5. read `.ralph/policy/project-policy.md`
6. read `.ralph/state/workflow-state.json`
7. read `.ralph/state/spec-queue.json`
8. read the latest report referenced by `last_report_path`
9. read active spec files under `specs/<spec-id>-<slug>/`
10. tail only recent events from `.ralph/logs/events.jsonl`
11. check `resume_spec_stack` and `interruption_state` before selecting the next spec
12. choose the next role from spec status, task lifecycle state, interruption state, and PR state
13. continue orchestrating until the queue is empty or a runtime-contract stop condition occurs
