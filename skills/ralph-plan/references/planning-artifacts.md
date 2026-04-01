# Ralph Planning Artifacts

The standard planning set is:

1. `tasks/prd-<project>.md`
2. `.ralph/state/spec-queue.json`
3. `specs/INDEX.md`
4. `specs/<spec-id>-<slug>/spec.md`
5. `specs/<spec-id>-<slug>/plan.md`
6. `specs/<spec-id>-<slug>/tasks.md`

Expectations:

- the PRD frames ordered epochs
- the queue records numbered specs plus `depends_on_spec_ids`, without inventing queue-head priority when dependencies are absent
- `spec.md` explains behavior and constraints for one numbered spec
- `plan.md` records the intended implementation approach for that spec
- `tasks.md` is dependency-ordered and execution-ready
- planning should stop before code changes begin
