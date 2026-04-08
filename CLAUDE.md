# Ralph Harness Source Repo

This repository is the source repository for the Ralph multi-agent runtime.

The installable scaffold lives in `src/`. Repo root contains source-repo docs, validation scripts, release tooling, and public source-entry skills. It is not an installed Ralph runtime.

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

The live shipped implementation belongs in `src/`. Keep public entry skills in `skills/` and supporting tooling in `scripts/` aligned with that shipped scaffold, and do not recreate a repo-root installed runtime unless the task explicitly asks for one.

Make implementation changes in `src/`.
