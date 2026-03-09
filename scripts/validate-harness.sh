#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 - <<'PY'
import json
import pathlib

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib  # type: ignore

root = pathlib.Path(".")

json_paths = [
    *sorted((root / ".ralph").rglob("*.json")),
    *sorted((root / "src/.ralph").rglob("*.json")),
]

jsonl_paths = [
    *sorted((root / ".ralph").rglob("*.jsonl")),
    *sorted((root / "src/.ralph").rglob("*.jsonl")),
]

def parse_toml(path: pathlib.Path) -> dict:
    return tomllib.loads(path.read_text())

def resolve_agent_targets(config_path: pathlib.Path) -> list[pathlib.Path]:
    config = parse_toml(config_path)
    if not config.get("features", {}).get("multi_agent"):
        raise SystemExit(f"{config_path} must enable multi_agent")
    targets = []
    for name, entry in (config.get("agents") or {}).items():
        if not isinstance(entry, dict) or not isinstance(entry.get("config_file"), str):
            continue
        target = config_path.parent / entry["config_file"]
        if not target.exists():
            raise SystemExit(f"{config_path} points `{name}` at missing file {target}")
        parse_toml(target)
        targets.append(target)
    if not targets:
        raise SystemExit(f"{config_path} must declare at least one agent config_file target")
    return targets

for legacy_dir in (root / "agents", root / "src/agents"):
    if legacy_dir.exists():
        raise SystemExit(f"legacy agent directory must not exist: {legacy_dir}")

config_paths = [root / ".codex/config.toml", root / "src/.codex/config.toml"]
toml_paths = []
for config_path in config_paths:
    parse_toml(config_path)
    toml_paths.append(config_path)
    toml_paths.extend(resolve_agent_targets(config_path))

for path in json_paths:
    json.loads(path.read_text())

for path in jsonl_paths:
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if line.strip():
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{lineno}: {exc}") from exc

current_version = (root / "VERSION").read_text().strip()
current_tag = f"v{current_version}"

changelog_path = root / "CHANGELOG.md"
if not changelog_path.exists():
    raise SystemExit("CHANGELOG.md must exist")

changelog_text = changelog_path.read_text()
if f"## {current_tag}" not in changelog_text:
    raise SystemExit(f"CHANGELOG.md must contain a section for {current_tag}")

for path in [root / "README.md", root / "INSTALLATION.md", root / "UPGRADING.md"]:
    if current_tag not in path.read_text():
        raise SystemExit(f"{path} must reference current tag {current_tag}")
PY

scripts/render-release-notes.sh "v$(tr -d '[:space:]' < VERSION)" >/dev/null
scripts/verify-installation-contract.sh
scripts/verify-atomic-commit-contract.sh
scripts/verify-interruption-contract.sh
scripts/verify-parallel-research-contract.sh
scripts/verify-upgrade-contract.sh

if grep -Fq -- '--generate-notes' .github/workflows/release.yml; then
  echo "validate-harness: release workflow must not use --generate-notes" >&2
  exit 1
fi

if ! grep -Fq -- 'scripts/render-release-notes.sh' .github/workflows/release.yml; then
  echo "validate-harness: release workflow must render notes from CHANGELOG.md" >&2
  exit 1
fi

scripts/smoke-test-install-upgrade.sh

echo "validate-harness: ok"
