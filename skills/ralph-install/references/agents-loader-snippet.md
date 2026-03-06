# Ralph Loader Snippet

Append a short section to the target repo's `AGENTS.md` that tells Codex:

- this repository uses the Ralph harness
- read `.ralph/constitution.md`
- then read `.ralph/policy/project-policy.md`
- then read `.ralph/state/workflow-state.json`
- then read `.ralph/state/spec-queue.json`
- then read the latest report referenced by `last_report_path`

Do not replace the target repo's entire `AGENTS.md` if it already exists.
