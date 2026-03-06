# Lessons

## 2026-03-05

- Build this harness as a Codex-native system first. Do not dilute the design for cross-runtime portability unless the user asks for it.
- Prefer Codex primitives plus file contracts over custom tools in v1. Add helper tools only when repeated workflow friction proves they are necessary.
- Keep orchestration in the parent agent and make sub-agents transient workers with one role, one report, and bounded inputs.
- Keep `README.md` as the overview and usage guide. Move long installation procedures into a separate installation markdown file and link to it from the README.
- When the user names a source skill as the quality bar, adapt the local role skill closely to that source instead of stopping at a lightweight summary.
- Treat `AGENTS.md` as the Codex-facing loader, not the full harness doctrine. Put the durable harness rules in `.ralph/constitution.md` and tell installation flows to append a Ralph section to an existing project `AGENTS.md` instead of overwriting it.
- Keep the repo narrative centered on its real job: it is a reference template for installing the harness into other projects. Any local bootstrap artifacts are examples, not the primary mission.
- Use the `ralph-*` naming convention for public skills. Keep the external entry surface small but useful: `ralph-install`, `ralph-prd`, `ralph-plan`, and `ralph-execute` are the main public skills, while `.agents/skills` stays reserved for runtime role skills that live inside installed projects.
- Model the durable execution queue at the numbered spec level, not the feature-slug level. PRDs define epochs, epochs group specs, and the orchestrator advances one numbered spec at a time through branch, review, verification, and PR completion.
- When the user corrects wording in a documentation request, preserve the intended concept in the artifact and avoid echoing the typo back into repo-facing language.
- Keep `src/` as the only installable scaffold source and keep the repo root as the live dogfood runtime. Installation flows should follow `src/install-manifest.txt` and must never copy the root runtime history into target projects.
