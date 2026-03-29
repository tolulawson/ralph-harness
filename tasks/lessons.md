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
- Treat `src/` as shipped output, not as the workshop. Do not store this repository's own TODOs, lessons, event logs, or bootstrap work records inside `src/`; those belong at the root dogfood layer and target runtime records should be generated during install or first run.
- Root `AGENTS.md` and root `.ralph/constitution.md` must describe the fixed ground truth of this source repository. Do not blur source-repo truth with generic installed-scaffold language; let the `src/` copies stay generic and adapt them during installation.
- Do not maintain an automatic source-to-root update model. `src/` stays pure, and root changes happen only when explicitly requested for the dogfood runtime or source-repo documents.
- When adding or changing harness capabilities, target the shipped scaffold under `src/` unless the user explicitly asks to change root source-repo doctrine or dogfood runtime files. Do not overfit product features to this repository's own implementation layer.
- When `src/` changes the install surface or loader behavior, update `INSTALLATION.md` in the same change. The install guide is the operational contract LLMs follow, so it must stay in lockstep with the shipped scaffold.
- Keep exactly one install authority. `INSTALLATION.md` owns the install workflow; manifests are subordinate contracts, and `ralph-install` must stay a thin execution adapter rather than a second install spec.
- Do not frame `ralph-install` as a prerequisite in `INSTALLATION.md`. The guide itself must be sufficient for installation, and the skill should be documented only as an optional helper.
- Do not commit local filesystem paths like `/Users/...` into installation docs or prompts. Shipped install instructions must use repo-relative references or the public repository URL so they are portable and do not leak local environment details.
- In committed docs, prefer GitHub repository URLs for file links over local absolute paths. The docs should work for anyone reading the repo remotely, not just from this workspace.

## 2026-03-07

- Treat official Codex multi-agent support as the required orchestration runtime. Prompt-only delegation language is not enough when the harness claims deterministic worker spawning and waiting.
- Keep the generic installed-runtime doctrine separate from the project-specific constitution so upgrades can refresh shared harness behavior without overwriting project mission or policy.
- Use a managed Ralph block inside `AGENTS.md` for installs and upgrades. Refresh only that block in existing repos instead of replacing the whole loader file.
- Version the shipped scaffold surface with a canonical `VERSION` file, then record the installed tag and resolved commit in `.ralph/harness-version.json`.
- Keep upgrades scaffold-only by default. Policies, states, specs, tasks, reports, logs, and other project-owned runtime records should stay outside the automatic overwrite surface unless a named migration explicitly targets them.

## 2026-03-26

- Before publishing any Ralph release from this source repository, run an explicit drift pass across the control-plane doctrine, supporting docs, public skills, and role or sub-agent instructions so every support surface matches the latest control-plane contract.
- When a doctrine change alters control-plane ownership, bootstrap flow, lease semantics, or worktree rules, audit not just `src/.ralph/*` but also README, install or upgrade guides, public `ralph-*` entry skills, generated runtime adapters, and dogfood learning records before tagging the release.

## 2026-03-28

- A control-plane doctrine change is not complete until every shipped role skill, public `ralph-*` skill, adapter reference, verifier, and supporting doctrine file uses the same ownership language for `.ralph/state`, `.ralph/reports`, and `.ralph/shared/`.
- Generic references to `.ralph/state/*` or report paths are not enough once worktree overlays exist. Worker-facing docs must say whether the path is canonical shared state, canonical report output, or a convenience view exposed through `.ralph/shared/`.
- Treat doctrine misalignment across skills, docs, and control services as a release blocker. Even small wording drift can make workers mutate tracked worktree copies instead of the canonical control plane.
