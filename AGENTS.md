# Ralph Harness Source Repo

This repository is the source repository for the Ralph multi-agent runtime.

The installable scaffold lives in `src/`. Repo root contains source-repo docs, validation scripts, release tooling, and public source-entry skills. It is not an installed Ralph runtime.

## Read Order

Before doing substantial work, read these files in order:

1. `README.md`
2. `INSTALLATION.md`
3. `UPGRADING.md`
4. `src/AGENTS.md`
5. `src/CLAUDE.md`
6. `src/.ralph/constitution.md`
7. `src/.ralph/runtime-contract.md`
8. `src/.ralph/policy/runtime-overrides.md`
9. `src/.ralph/policy/project-policy.md`
10. `src/install-manifest.txt`
11. `src/generated-runtime-manifest.txt`
12. `src/upgrade-manifest.txt`

## Operating Rule

Do not treat conversational memory as the source of truth when the repository files already contain the needed contract or install surface.

- make shipped harness behavior, templates, adapter packs, and runtime skills changes in `src/`
- make implementation changes in `src/`
- keep public source-entry skills in `skills/` aligned with the shipped scaffold contract
- keep install, upgrade, validation, and migration tooling in `scripts/` aligned with the shipped scaffold contract
- update `README.md`, `INSTALLATION.md`, and `UPGRADING.md` when the shipped surface or workflow changes
- do not recreate a repo-root installed-runtime control plane unless a task explicitly asks for an example or fixture
