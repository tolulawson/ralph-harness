# Ralph Install Checklist

During installation, make sure Codex:

1. confirms the current repo is the target project
2. treats `src/` as the only scaffold root
3. reads `src/install-manifest.txt`
4. copies only the manifest-listed control-plane files:
   - `AGENTS.md`
   - `.codex/config.toml`
   - `agents/*.toml`
   - `.agents/skills/*`
5. copies the manifest-listed runtime files:
   - `.ralph/constitution.md`
   - `.ralph/policy/*`
   - `.ralph/state/*`
   - `.ralph/templates/*`
   - `specs/INDEX.md`
6. generates the runtime files listed in `src/generated-runtime-manifest.txt`
7. preserves and appends to an existing `AGENTS.md`
8. does not copy the source repo's root dogfood logs, reports, TODOs, lessons, PRD, or numbered spec history
9. rewrites workflow state, spec queue, and policy for the target project
10. creates the first project PRD with epoch framing
11. seeds the numbered spec queue and `specs/INDEX.md`
12. appends initial reports and events
