# Source Skills Vs Runtime Skills

Keep the two skill layers distinct:

- `skills/` contains distributable source skills that can be installed by a third-party skill installer
- `.agents/skills/` contains the runtime role skills that belong inside the installed harness scaffold

`ralph-install`, `ralph-interrupt`, `ralph-upgrade`, `ralph-execute`, `ralph-prd`, and `ralph-plan` are public source skills.
The orchestrator and role skills under `.agents/skills/` are internal runtime skills copied into target repos.

Keep the repository layers distinct as well:

- `src/` is the canonical installable scaffold source
- repo root `.ralph/`, `tasks/`, and `specs/` are this repository's live dogfood runtime
- `src/` should stay clean and should not carry this repository's own TODOs, lessons, event history, or bootstrap work records
- target runtime records are generated after the scaffold is copied, rather than copied as authored files from `src/`
- target repos should install from `src/`, not from the root runtime history
